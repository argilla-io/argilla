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
from typing import Any, List

import argilla as rg
import pytest
from huggingface_hub.utils._errors import BadRequestError, FileMetadataError, HfHubHTTPError

_RETRIES = 5


@pytest.fixture
def dataset(client) -> rg.Dataset:
    mock_dataset_name = "".join(random.choices(ascii_lowercase, k=16))
    settings = rg.Settings(
        fields=[
            rg.TextField(name="text"),
        ],
        questions=[
            rg.TextQuestion(name="label", use_markdown=False),
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
            "label": "positive",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
            "label": "negative",
            "id": uuid.uuid4(),
        },
        {
            "text": "Hello World, how are you?",
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
            new_dataset = rg.Dataset.from_disk(output_dir, client=client, with_records=with_records_import)

        if with_records_export and with_records_import:
            for i, record in enumerate(new_dataset.records(with_suggestions=True)):
                assert record.fields["text"] == mock_data[i]["text"]
                assert record.suggestions["label"].value == mock_data[i]["label"]
        else:
            assert len(new_dataset.records.to_list()) == 0

        assert new_dataset.settings.fields[0].name == "text"
        assert new_dataset.settings.questions[0].name == "label"


@pytest.mark.flaky(
    retries=_RETRIES, only_on=[BadRequestError, FileMetadataError, HfHubHTTPError]
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
                    repo_id=repo_id, client=client, with_records=with_records_import, token=token
                )
        else:
            new_dataset = rg.Dataset.from_hub(
                repo_id=repo_id, client=client, with_records=with_records_import, token=token
            )

        if with_records_import and with_records_export:
            for i, record in enumerate(new_dataset.records(with_suggestions=True)):
                assert record.fields["text"] == mock_data[i]["text"]
                assert record.suggestions["label"].value == mock_data[i]["label"]
        else:
            assert len(new_dataset.records.to_list()) == 0

        assert new_dataset.settings.fields[0].name == "text"
        assert new_dataset.settings.questions[0].name == "label"
