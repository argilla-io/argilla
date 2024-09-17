# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import random
import uuid
from string import ascii_lowercase
from tempfile import TemporaryDirectory
from time import sleep
from typing import Any, List

import argilla as rg
import pytest
from argilla._exceptions import ConflictError, SettingsError
from datasets import Dataset as HFDataset, Value, Features, ClassLabel
from huggingface_hub.utils._errors import BadRequestError, FileMetadataError, HfHubHTTPError

_RETRIES = 5


@pytest.fixture
def dataset(client) -> rg.Dataset:
    mock_dataset_name = "".join(random.choices(ascii_lowercase, k=16))
    settings = rg.Settings(
        fields=[
            rg.TextField(name="text"),
            rg.ImageField(name="image"),
        ],
        questions=[
            rg.LabelQuestion(name="label", labels=["positive", "negative"]),
        ],
    )
    dataset = rg.Dataset(
        name=mock_dataset_name,
        settings=settings,
        client=client,
    )
    dataset.create()
    yield dataset
    dataset.delete()


@pytest.fixture
def mock_data() -> List[dict[str, Any]]:
    return [
        {
            "text": "Hello World, how are you?",
            "image": "http://mock.url/image",
            "label": "positive",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "image": "http://mock.url/image",
            "label": "negative",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "image": "http://mock.url/image",
            "label": "positive",
            "id": uuid.uuid4(),
        },
    ]


@pytest.fixture
def token():
    return os.getenv("HF_TOKEN_ARGILLA_INTERNAL_TESTING")


@pytest.mark.flaky(retries=_RETRIES, only_on=[OSError])  # I/O consistency CICD pipline
@pytest.mark.parametrize("with_records_export", [True, False])
class TestDiskImportExportMixin:
    def test_export_dataset_to_disk(
        self, dataset: rg.Dataset, mock_data: List[dict[str, Any]], with_records_export: bool
    ):
        dataset.records.log(records=mock_data)

        with TemporaryDirectory() as temp_dir:
            output_dir = dataset.to_disk(path=temp_dir, with_records=with_records_export)

            records_path = os.path.join(output_dir, rg.Dataset._DEFAULT_RECORDS_PATH)
            if with_records_export:
                assert os.path.exists(records_path)
                with open(records_path, "r") as f:
                    exported_records = json.load(f)

                assert len(exported_records) == len(mock_data)
                assert exported_records[0]["fields"]["text"] == "Hello World, how are you?"
                assert exported_records[0]["suggestions"]["label"]["value"] == "positive"
            else:
                assert not os.path.exists(records_path)

            settings_path = os.path.join(output_dir, rg.Dataset._DEFAULT_SETTINGS_PATH)
            assert os.path.exists(settings_path)
            with open(settings_path, "r") as f:
                exported_settings = json.load(f)

            dataset_path = os.path.join(output_dir, rg.Dataset._DEFAULT_DATASET_PATH)
            assert os.path.exists(dataset_path)
            with open(dataset_path, "r") as f:
                exported_dataset = json.load(f)

        assert exported_settings["fields"][0]["name"] == "text"
        assert exported_settings["fields"][1]["name"] == "image"
        assert exported_settings["questions"][0]["name"] == "label"

        assert exported_dataset["name"] == dataset.name

    @pytest.mark.parametrize("with_records_import", [True, False])
    def test_import_dataset_from_disk(
        self,
        dataset: rg.Dataset,
        client,
        mock_data: List[dict[str, Any]],
        with_records_export: bool,
        with_records_import: bool,
    ):
        dataset.records.log(records=mock_data)

        with TemporaryDirectory() as temp_dir:
            output_dir = dataset.to_disk(path=temp_dir, with_records=with_records_export)
            new_dataset = rg.Dataset.from_disk(
                output_dir, client=client, with_records=with_records_import, name=f"test_{uuid.uuid4()}"
            )

        if with_records_export and with_records_import:
            for i, record in enumerate(new_dataset.records(with_suggestions=True)):
                assert record.fields["text"] == mock_data[i]["text"]
                assert record.fields["image"] == mock_data[i]["image"]
                assert record.suggestions["label"].value == mock_data[i]["label"]
        else:
            assert len(new_dataset.records.to_list()) == 0

        assert new_dataset.settings.fields[0].name == "text"
        assert new_dataset.settings.fields[1].name == "image"
        assert new_dataset.settings.questions[0].name == "label"


@pytest.mark.flaky(
    retries=_RETRIES, only_on=[BadRequestError, FileMetadataError, HfHubHTTPError, OSError, FileNotFoundError]
)  # Hub consistency CICD pipline
@pytest.mark.skipif(
    not os.getenv("HF_TOKEN_ARGILLA_INTERNAL_TESTING"),
    reason="You are missing a token to write to `argilla-internal-testing` org on the Hugging Face Hub",
)
@pytest.mark.parametrize("with_records_export", [True, False])
class TestHubImportExportMixin:
    def test_export_dataset_to_hub(
        self, token: str, dataset: rg.Dataset, mock_data: List[dict[str, Any]], with_records_export: bool
    ):
        repo_id = f"argilla-internal-testing/test_export_dataset_to_hub_with_records_{with_records_export}"
        dataset.records.log(records=mock_data)
        dataset.to_hub(repo_id=repo_id, with_records=with_records_export, token=token)

    @pytest.mark.parametrize("with_records_import", [True, False])
    def test_import_dataset_from_hub(
        self,
        token: str,
        dataset: rg.Dataset,
        client,
        mock_data: List[dict[str, Any]],
        with_records_export: bool,
        with_records_import: bool,
    ):
        repo_id = f"argilla-internal-testing/test_import_dataset_from_hub_with_records_{with_records_export}"
        dataset.records.log(records=mock_data)

        dataset.to_hub(repo_id=repo_id, with_records=with_records_export, token=token)

        if with_records_import and not with_records_export:
            with pytest.warns(
                expected_warning=UserWarning,
                match="Trying to load a dataset `with_records=True` but dataset does not contain any records.",
            ):
                new_dataset = rg.Dataset.from_hub(
                    repo_id=repo_id,
                    client=client,
                    with_records=with_records_import,
                    token=token,
                    name=f"test_{uuid.uuid4()}",
                )
        else:
            new_dataset = rg.Dataset.from_hub(
                repo_id=repo_id,
                client=client,
                with_records=with_records_import,
                token=token,
                name=f"test_{uuid.uuid4()}",
            )

        if with_records_import and with_records_export:
            for i, record in enumerate(new_dataset.records(with_suggestions=True)):
                assert record.fields["text"] == mock_data[i]["text"]
                assert record.fields["image"] == mock_data[i]["image"]
                assert record.suggestions["label"].value == mock_data[i]["label"]
        else:
            assert len(new_dataset.records.to_list()) == 0

        assert new_dataset.settings.fields[0].name == "text"
        assert new_dataset.settings.fields[1].name == "image"
        assert new_dataset.settings.questions[0].name == "label"

    @pytest.mark.parametrize("with_records_import", [True, False])
    def test_import_dataset_from_hub_using_settings(
        self,
        token: str,
        dataset: rg.Dataset,
        client,
        mock_data: List[dict[str, Any]],
        with_records_export: bool,
        with_records_import: bool,
    ):
        repo_id = (
            f"argilla-internal-testing/test_import_dataset_from_hub_using_settings_with_records{with_records_export}"
        )
        mock_dataset_name = f"test_import_dataset_from_hub_using_settings_{uuid.uuid4()}"
        dataset.records.log(records=mock_data)

        dataset.to_hub(repo_id=repo_id, with_records=with_records_export, token=token)
        settings = rg.Settings(
            fields=[
                rg.TextField(name="text"),
            ],
            questions=[
                rg.LabelQuestion(name="label", labels=["positive", "negative"]),
                rg.LabelQuestion(name="extra_label", labels=["extra_positive", "extra_negative"]),
            ],
        )
        if with_records_import and not with_records_export:
            with pytest.warns(
                expected_warning=UserWarning,
                match="Trying to load a dataset `with_records=True` but dataset does not contain any records.",
            ):
                new_dataset = rg.Dataset.from_hub(
                    repo_id=repo_id,
                    client=client,
                    with_records=with_records_import,
                    token=token,
                    settings=settings,
                    name=mock_dataset_name,
                )
        else:
            new_dataset = rg.Dataset.from_hub(
                repo_id=repo_id,
                client=client,
                with_records=with_records_import,
                token=token,
                settings=settings,
                name=mock_dataset_name,
            )

        if with_records_import and with_records_export:
            for i, record in enumerate(new_dataset.records(with_suggestions=True)):
                assert record.fields["text"] == mock_data[i]["text"]
                assert record.suggestions["label"].value == mock_data[i]["label"]
        else:
            assert len(new_dataset.records.to_list()) == 0

        assert new_dataset.settings.fields[0].name == "text"
        assert new_dataset.settings.questions[0].name == "label"

    @pytest.mark.parametrize("with_records_import", [True, False])
    def test_import_dataset_from_hub_using_settings(
        self,
        token: str,
        dataset: rg.Dataset,
        client,
        mock_data: List[dict[str, Any]],
        with_records_export: bool,
        with_records_import: bool,
    ):
        repo_id = (
            f"argilla-internal-testing/test_import_dataset_from_hub_using_settings_with_records{with_records_export}"
        )
        mock_dataset_name = f"test_import_dataset_from_hub_using_settings_{uuid.uuid4()}"
        dataset.records.log(records=mock_data)

        dataset.to_hub(repo_id=repo_id, with_records=with_records_export, token=token)
        settings = rg.Settings(
            fields=[
                rg.TextField(name="text"),
                rg.ImageField(name="image"),
            ],
            questions=[
                rg.LabelQuestion(name="label", labels=["positive", "negative"]),
                rg.LabelQuestion(name="extra_label", labels=["extra_positive", "extra_negative"]),
            ],
        )
        if with_records_import and not with_records_export:
            with pytest.warns(
                expected_warning=UserWarning,
                match="Trying to load a dataset `with_records=True` but dataset does not contain any records.",
            ):
                new_dataset = rg.Dataset.from_hub(
                    repo_id=repo_id,
                    client=client,
                    with_records=with_records_import,
                    token=token,
                    settings=settings,
                    name=mock_dataset_name,
                )
        else:
            new_dataset = rg.Dataset.from_hub(
                repo_id=repo_id,
                client=client,
                with_records=with_records_import,
                token=token,
                settings=settings,
                name=mock_dataset_name,
            )

        if with_records_import and with_records_export:
            for i, record in enumerate(new_dataset.records(with_suggestions=True)):
                assert record.fields["text"] == mock_data[i]["text"]
                assert record.suggestions["label"].value == mock_data[i]["label"]
        else:
            assert len(new_dataset.records.to_list()) == 0

        assert new_dataset.settings.fields[0].name == "text"
        assert new_dataset.settings.questions[0].name == "label"
        assert new_dataset.settings.questions[1].name == "extra_label"
        assert len(new_dataset.settings.questions[1].labels) == 2
        assert new_dataset.settings.questions[1].labels[0] == "extra_positive"
        assert new_dataset.settings.questions[1].labels[1] == "extra_negative"
        assert new_dataset.name == mock_dataset_name

    def test_import_dataset_from_hub_using_wrong_settings(
        self,
        token: str,
        dataset: rg.Dataset,
        client,
        mock_data: List[dict[str, Any]],
        with_records_export: bool,
    ):
        repo_id = f"argilla-internal-testing/test_import_dataset_from_hub_using_wrong_settings_with_records_{with_records_export}"
        dataset.records.log(records=mock_data)
        mock_dataset_name = f"test_import_dataset_from_hub_using_wrong_settings_{uuid.uuid4()}"
        dataset.to_hub(repo_id=repo_id, with_records=with_records_export, token=token)
        settings = rg.Settings(
            fields=[
                rg.TextField(name="text"),
            ],
            questions=[
                rg.RatingQuestion(name="label", values=[1, 2, 3, 4, 5]),
            ],
        )
        if with_records_export:
            with pytest.raises(SettingsError):
                rg.Dataset.from_hub(
                    repo_id=repo_id, client=client, token=token, settings=settings, name=mock_dataset_name
                )
        else:
            rg.Dataset.from_hub(repo_id=repo_id, client=client, token=token, settings=settings, name=mock_dataset_name)

    def test_import_dataset_from_hub_with_automatic_settings(
        self, token: str, dataset: rg.Dataset, client, mock_data: List[dict[str, Any]], with_records_export: bool
    ):
        repo_id = f"argilla-internal-testing/test_import_dataset_from_hub_with_classlabel_{with_records_export}"
        mock_dataset_name = f"test_import_dataset_from_hub_with_automatic_settings_{uuid.uuid4()}"
        hf_dataset = HFDataset.from_dict(
            {
                "text": [record["text"] for record in mock_data],
                "label": [record["label"] for record in mock_data],
            },
            features=Features(
                {
                    "text": Value("string"),
                    "label": ClassLabel(names=["positive", "negative"]),
                }
            ),
        )

        hf_dataset.push_to_hub(repo_id=repo_id, token=token)

        for _ in range(10):
            try:
                rg_dataset = rg.Dataset.from_hub(
                    repo_id=repo_id,
                    client=client,
                    token=token,
                    name=mock_dataset_name,
                    with_records=with_records_export,
                )
                break
            except Exception as e:
                sleep(10)

        if with_records_export:
            for i, record in enumerate(rg_dataset.records(with_suggestions=True)):
                assert record.fields["text"] == mock_data[i]["text"]
                assert record.suggestions["label"].value == mock_data[i]["label"]
