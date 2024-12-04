#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import pytest

from PIL import Image
from uuid import uuid4
from typing import Generator
from datasets import load_dataset, get_dataset_config_names, get_dataset_split_names
from huggingface_hub import HfApi

from argilla_server.contexts.hub import HubDatasetExporter
from argilla_server.enums import DatasetStatus, FieldType

from tests.factories import DatasetSyncFactory, FieldSyncFactory, RecordSyncFactory

HF_ORGANIZATION = "argilla-internal-testing"
HF_TOKEN = os.environ.get("HF_TOKEN_ARGILLA_INTERNAL_TESTING")

IMAGE_URL = "https://argilla.io/brand-assets/argilla/argilla-logo-color-black.png"
IMAGE_DATA_URL = "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="


@pytest.fixture
def hf_api() -> HfApi:
    return HfApi(token=HF_TOKEN)


@pytest.fixture
def hf_dataset_name(hf_api: HfApi) -> Generator[str, None, None]:
    hf_dataset_name = f"{HF_ORGANIZATION}/argilla-server-dataset-test-{uuid4()}"

    yield hf_dataset_name

    hf_api.delete_repo(hf_dataset_name, repo_type="dataset", missing_ok=True)


@pytest.mark.skipif(HF_TOKEN is None, reason="HF_TOKEN_ARGILLA_INTERNAL_TESTING is not defined")
class TestHubDatasetExporter:
    def test_export_to(self, async_client, hf_api: HfApi, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)

        FieldSyncFactory.create(name="text", settings={"type": FieldType.text, "use_markdown": False}, dataset=dataset)
        record = RecordSyncFactory.create(fields={"text": "Hello World"}, dataset=dataset)

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        exported_dataset = load_dataset(path=hf_dataset_name, name="default", split="train")

        assert hf_api.dataset_info(hf_dataset_name).private == False
        assert exported_dataset[0] == {
            "id": record.external_id,
            "status": record.status,
            "_server_id": str(record.id),
            "text": "Hello World",
        }

    def test_export_to_with_custom_subset(self, async_client, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)

        FieldSyncFactory.create(name="text", settings={"type": FieldType.text, "use_markdown": False}, dataset=dataset)
        RecordSyncFactory.create(fields={"text": "Hello World"}, dataset=dataset)

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="custom",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        assert get_dataset_config_names(hf_dataset_name) == ["custom"]

    def test_export_to_with_custom_split(self, async_client, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)

        FieldSyncFactory.create(name="text", settings={"type": FieldType.text, "use_markdown": False}, dataset=dataset)
        RecordSyncFactory.create(fields={"text": "Hello World"}, dataset=dataset)

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="custom",
            private=False,
            token=HF_TOKEN,
        )

        assert get_dataset_split_names(hf_dataset_name) == ["custom"]

    def test_export_to_with_private_dataset(self, async_client, hf_api: HfApi, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)

        FieldSyncFactory.create(name="text", settings={"type": FieldType.text, "use_markdown": False}, dataset=dataset)
        RecordSyncFactory.create(fields={"text": "Hello World"}, dataset=dataset)

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=True,
            token=HF_TOKEN,
        )

        assert hf_api.dataset_info(hf_dataset_name).private == True

    def test_export_to_with_chat_field(self, async_client, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)

        chat_record_value = [
            {"role": "user", "content": "Hello"},
            {"role": "agent", "content": "Hello human!"},
        ]

        FieldSyncFactory.create(name="chat", settings={"type": FieldType.chat, "use_markdown": False}, dataset=dataset)
        RecordSyncFactory.create(fields={"chat": chat_record_value}, dataset=dataset)

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        exported_dataset = load_dataset(path=hf_dataset_name, name="default", split="train")

        assert exported_dataset[0]["chat"] == chat_record_value

    def test_export_to_with_custom_field(self, async_client, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)

        FieldSyncFactory.create(
            name="custom",
            settings={
                "type": FieldType.custom,
                "template": "",
                "advanced_mode": False,
            },
            dataset=dataset,
        )
        RecordSyncFactory.create(fields={"custom": "custom-value"}, dataset=dataset)

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        exported_dataset = load_dataset(path=hf_dataset_name, name="default", split="train")

        assert exported_dataset[0]["custom"] == "custom-value"

    def test_export_to_with_image_field_as_url(self, async_client, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)

        FieldSyncFactory.create(name="image", settings={"type": FieldType.image}, dataset=dataset)
        RecordSyncFactory.create(fields={"image": IMAGE_URL}, dataset=dataset)

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        exported_dataset = load_dataset(path=hf_dataset_name, name="default", split="train")

        assert exported_dataset[0]["image"] == IMAGE_URL

    def test_export_to_with_image_field_as_data_url(self, async_client, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)

        FieldSyncFactory.create(name="image", settings={"type": FieldType.image}, dataset=dataset)
        RecordSyncFactory.create(fields={"image": IMAGE_DATA_URL}, dataset=dataset)

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        exported_dataset = load_dataset(path=hf_dataset_name, name="default", split="train")

        assert isinstance(exported_dataset[0]["image"], Image.Image)
