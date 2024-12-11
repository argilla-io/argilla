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
from huggingface_hub import HfApi
from datasets import load_dataset, get_dataset_config_names, get_dataset_split_names

from argilla_server.contexts import hub
from argilla_server.contexts.hub import HubDatasetExporter
from argilla_server.enums import DatasetStatus, FieldType, QuestionType, ResponseStatus, MetadataPropertyType

from tests.database import SyncTestSession
from tests.factories import (
    DatasetSyncFactory,
    FieldSyncFactory,
    QuestionSyncFactory,
    RecordSyncFactory,
    ResponseSyncFactory,
    AnnotatorSyncFactory,
    MetadataPropertySyncFactory,
    SuggestionSyncFactory,
    VectorSettingsSyncFactory,
    VectorSyncFactory,
)

HF_ORGANIZATION = "argilla-internal-testing"
HF_TOKEN = os.environ.get("HF_TOKEN_ARGILLA_INTERNAL_TESTING")

IMAGE_URL = "https://argilla.io/brand-assets/argilla/argilla-logo-color-black.png"
IMAGE_DATA_URL = "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="


@pytest.fixture
def sync_test_session(mocker):
    session = SyncTestSession()

    def override_get_sync_db():
        yield session

    mocker.patch.object(hub, "get_sync_db", override_get_sync_db)

    yield session


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
    def test_export_to(self, sync_test_session, hf_api: HfApi, hf_dataset_name: str):
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

    @pytest.mark.skip(reason="the Hub is ignoring for some reason the subset and using default instead")
    def test_export_to_with_custom_subset(self, sync_test_session, hf_dataset_name: str):
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

    def test_export_to_with_custom_split(self, sync_test_session, hf_dataset_name: str):
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

    def test_export_to_with_private_dataset(self, sync_test_session, hf_api: HfApi, hf_dataset_name: str):
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

    def test_export_to_with_chat_field(self, sync_test_session, hf_dataset_name: str):
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

    def test_export_to_with_custom_field(self, sync_test_session, hf_dataset_name: str):
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

    def test_export_to_with_image_field_as_url(self, sync_test_session, hf_dataset_name: str):
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

    def test_export_to_with_image_field_as_data_url(self, sync_test_session, hf_dataset_name: str):
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

    def test_export_to_with_text_question(self, sync_test_session, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)
        annotators = AnnotatorSyncFactory.create_batch(2, workspaces=[dataset.workspace])

        FieldSyncFactory.create(name="text", settings={"type": FieldType.text, "use_markdown": False}, dataset=dataset)
        QuestionSyncFactory.create(
            name="text-question",
            settings={
                "type": QuestionType.text,
                "use_markdown": False,
            },
            dataset=dataset,
        )

        record = RecordSyncFactory.create(fields={"text": "Hello World"}, dataset=dataset)
        ResponseSyncFactory.create(
            values={
                "text-question": {
                    "value": "This is a response",
                },
            },
            record=record,
            user=annotators[0],
        )
        ResponseSyncFactory.create(
            values={
                "text-question": {
                    "value": "This is another response",
                },
            },
            record=record,
            user=annotators[1],
        )

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        exported_dataset = load_dataset(path=hf_dataset_name, name="default", split="train")

        assert exported_dataset[0] == {
            "id": record.external_id,
            "status": record.status,
            "_server_id": str(record.id),
            "text": "Hello World",
            "text-question.responses": ["This is a response", "This is another response"],
            "text-question.responses.status": [ResponseStatus.submitted, ResponseStatus.submitted],
            "text-question.responses.users": [str(annotators[0].id), str(annotators[1].id)],
        }

    def test_export_to_with_text_question_and_suggestion(self, sync_test_session, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)
        annotators = AnnotatorSyncFactory.create_batch(2, workspaces=[dataset.workspace])

        FieldSyncFactory.create(name="text", settings={"type": FieldType.text, "use_markdown": False}, dataset=dataset)
        question = QuestionSyncFactory.create(
            name="text-question",
            settings={
                "type": QuestionType.text,
                "use_markdown": False,
            },
            dataset=dataset,
        )

        record = RecordSyncFactory.create(fields={"text": "Hello World"}, dataset=dataset)
        ResponseSyncFactory.create(
            values={
                "text-question": {
                    "value": "This is a response",
                },
            },
            record=record,
            user=annotators[0],
        )
        ResponseSyncFactory.create(
            values={
                "text-question": {
                    "value": "This is another response",
                },
            },
            record=record,
            user=annotators[1],
        )
        SuggestionSyncFactory.create(
            value="This is a suggested response",
            record=record,
            question=question,
            agent="suggestion-agent",
            score=0.5,
        )

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        exported_dataset = load_dataset(path=hf_dataset_name, name="default", split="train")

        assert exported_dataset[0] == {
            "id": record.external_id,
            "status": record.status,
            "_server_id": str(record.id),
            "text": "Hello World",
            "text-question.responses": ["This is a response", "This is another response"],
            "text-question.responses.status": [ResponseStatus.submitted, ResponseStatus.submitted],
            "text-question.responses.users": [str(annotators[0].id), str(annotators[1].id)],
            "text-question.suggestion": "This is a suggested response",
            "text-question.suggestion.agent": "suggestion-agent",
            "text-question.suggestion.score": 0.5,
        }

    def test_export_to_with_rating_question(self, sync_test_session, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)
        annotators = AnnotatorSyncFactory.create_batch(2, workspaces=[dataset.workspace])

        FieldSyncFactory.create(name="text", settings={"type": FieldType.text, "use_markdown": False}, dataset=dataset)
        QuestionSyncFactory.create(
            name="rating-question",
            settings={
                "type": QuestionType.rating,
                "options": [
                    {"value": 0},
                    {"value": 1},
                    {"value": 2},
                    {"value": 3},
                ],
            },
            dataset=dataset,
        )

        record = RecordSyncFactory.create(fields={"text": "Hello World"}, dataset=dataset)
        ResponseSyncFactory.create(
            values={
                "rating-question": {
                    "value": 2,
                },
            },
            record=record,
            user=annotators[0],
        )
        ResponseSyncFactory.create(
            values={
                "rating-question": {
                    "value": 0,
                },
            },
            record=record,
            user=annotators[1],
        )

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        exported_dataset = load_dataset(path=hf_dataset_name, name="default", split="train")

        assert exported_dataset[0] == {
            "id": record.external_id,
            "status": record.status,
            "_server_id": str(record.id),
            "text": "Hello World",
            "rating-question.responses": [2, 0],
            "rating-question.responses.status": [ResponseStatus.submitted, ResponseStatus.submitted],
            "rating-question.responses.users": [str(annotators[0].id), str(annotators[1].id)],
        }

    def test_export_to_with_rating_question_and_suggestion(self, sync_test_session, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)
        annotators = AnnotatorSyncFactory.create_batch(2, workspaces=[dataset.workspace])

        FieldSyncFactory.create(name="text", settings={"type": FieldType.text, "use_markdown": False}, dataset=dataset)
        question = QuestionSyncFactory.create(
            name="rating-question",
            settings={
                "type": QuestionType.rating,
                "options": [
                    {"value": 0},
                    {"value": 1},
                    {"value": 2},
                    {"value": 3},
                ],
            },
            dataset=dataset,
        )

        record = RecordSyncFactory.create(fields={"text": "Hello World"}, dataset=dataset)
        ResponseSyncFactory.create(
            values={
                "rating-question": {
                    "value": 2,
                },
            },
            record=record,
            user=annotators[0],
        )
        ResponseSyncFactory.create(
            values={
                "rating-question": {
                    "value": 0,
                },
            },
            record=record,
            user=annotators[1],
        )
        SuggestionSyncFactory.create(
            value=1,
            record=record,
            question=question,
            agent="suggestion-agent",
            score=0.9,
        )

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        exported_dataset = load_dataset(path=hf_dataset_name, name="default", split="train")

        assert exported_dataset[0] == {
            "id": record.external_id,
            "status": record.status,
            "_server_id": str(record.id),
            "text": "Hello World",
            "rating-question.responses": [2, 0],
            "rating-question.responses.status": [ResponseStatus.submitted, ResponseStatus.submitted],
            "rating-question.responses.users": [str(annotators[0].id), str(annotators[1].id)],
            "rating-question.suggestion": 1,
            "rating-question.suggestion.agent": "suggestion-agent",
            "rating-question.suggestion.score": 0.9,
        }

    def test_export_to_with_label_question(self, sync_test_session, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)
        annotators = AnnotatorSyncFactory.create_batch(2, workspaces=[dataset.workspace])

        FieldSyncFactory.create(name="text", settings={"type": FieldType.text, "use_markdown": False}, dataset=dataset)
        QuestionSyncFactory.create(
            name="label-question",
            settings={
                "type": QuestionType.label_selection,
                "options": [
                    {"value": "label-a", "text": "Label A"},
                    {"value": "label-b", "text": "Label B"},
                    {"value": "label-c", "text": "Label C"},
                ],
            },
            dataset=dataset,
        )

        record = RecordSyncFactory.create(fields={"text": "Hello World"}, dataset=dataset)
        ResponseSyncFactory.create(
            values={
                "label-question": {
                    "value": "label-b",
                },
            },
            record=record,
            user=annotators[0],
        )
        ResponseSyncFactory.create(
            values={
                "label-question": {
                    "value": "label-a",
                },
            },
            record=record,
            user=annotators[1],
        )

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        exported_dataset = load_dataset(path=hf_dataset_name, name="default", split="train")

        assert exported_dataset[0] == {
            "id": record.external_id,
            "status": record.status,
            "_server_id": str(record.id),
            "text": "Hello World",
            "label-question.responses": ["label-b", "label-a"],
            "label-question.responses.status": [ResponseStatus.submitted, ResponseStatus.submitted],
            "label-question.responses.users": [str(annotators[0].id), str(annotators[1].id)],
        }

    def test_export_to_with_label_question_and_suggestion(self, sync_test_session, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)
        annotators = AnnotatorSyncFactory.create_batch(2, workspaces=[dataset.workspace])

        FieldSyncFactory.create(name="text", settings={"type": FieldType.text, "use_markdown": False}, dataset=dataset)
        question = QuestionSyncFactory.create(
            name="label-question",
            settings={
                "type": QuestionType.label_selection,
                "options": [
                    {"value": "label-a", "text": "Label A"},
                    {"value": "label-b", "text": "Label B"},
                    {"value": "label-c", "text": "Label C"},
                ],
            },
            dataset=dataset,
        )

        record = RecordSyncFactory.create(fields={"text": "Hello World"}, dataset=dataset)
        ResponseSyncFactory.create(
            values={
                "label-question": {
                    "value": "label-b",
                },
            },
            record=record,
            user=annotators[0],
        )
        ResponseSyncFactory.create(
            values={
                "label-question": {
                    "value": "label-a",
                },
            },
            record=record,
            user=annotators[1],
        )
        SuggestionSyncFactory.create(
            value="label-c",
            record=record,
            question=question,
            agent="suggestion-agent",
            score=0.3,
        )

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        exported_dataset = load_dataset(path=hf_dataset_name, name="default", split="train")

        assert exported_dataset[0] == {
            "id": record.external_id,
            "status": record.status,
            "_server_id": str(record.id),
            "text": "Hello World",
            "label-question.responses": ["label-b", "label-a"],
            "label-question.responses.status": [ResponseStatus.submitted, ResponseStatus.submitted],
            "label-question.responses.users": [str(annotators[0].id), str(annotators[1].id)],
            "label-question.suggestion": "label-c",
            "label-question.suggestion.agent": "suggestion-agent",
            "label-question.suggestion.score": 0.3,
        }

    def test_export_to_with_multi_label_question(self, sync_test_session, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)
        annotators = AnnotatorSyncFactory.create_batch(2, workspaces=[dataset.workspace])

        FieldSyncFactory.create(name="text", settings={"type": FieldType.text, "use_markdown": False}, dataset=dataset)
        QuestionSyncFactory.create(
            name="multi-label-question",
            settings={
                "type": QuestionType.multi_label_selection,
                "options": [
                    {"value": "label-a", "text": "Label A"},
                    {"value": "label-b", "text": "Label B"},
                    {"value": "label-c", "text": "Label C"},
                ],
            },
            dataset=dataset,
        )

        record = RecordSyncFactory.create(fields={"text": "Hello World"}, dataset=dataset)
        ResponseSyncFactory.create(
            values={
                "multi-label-question": {
                    "value": ["label-a", "label-b"],
                },
            },
            record=record,
            user=annotators[0],
        )
        ResponseSyncFactory.create(
            values={
                "multi-label-question": {
                    "value": ["label-c", "label-a"],
                },
            },
            record=record,
            user=annotators[1],
        )

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        exported_dataset = load_dataset(path=hf_dataset_name, name="default", split="train")

        assert exported_dataset[0] == {
            "id": record.external_id,
            "status": record.status,
            "_server_id": str(record.id),
            "text": "Hello World",
            "multi-label-question.responses": [["label-a", "label-b"], ["label-c", "label-a"]],
            "multi-label-question.responses.status": [ResponseStatus.submitted, ResponseStatus.submitted],
            "multi-label-question.responses.users": [str(annotators[0].id), str(annotators[1].id)],
        }

    def test_export_to_with_multi_label_question_and_suggestion(self, sync_test_session, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)
        annotators = AnnotatorSyncFactory.create_batch(2, workspaces=[dataset.workspace])

        FieldSyncFactory.create(name="text", settings={"type": FieldType.text, "use_markdown": False}, dataset=dataset)
        question = QuestionSyncFactory.create(
            name="multi-label-question",
            settings={
                "type": QuestionType.multi_label_selection,
                "options": [
                    {"value": "label-a", "text": "Label A"},
                    {"value": "label-b", "text": "Label B"},
                    {"value": "label-c", "text": "Label C"},
                ],
            },
            dataset=dataset,
        )

        record = RecordSyncFactory.create(fields={"text": "Hello World"}, dataset=dataset)
        ResponseSyncFactory.create(
            values={
                "multi-label-question": {
                    "value": ["label-a", "label-b"],
                },
            },
            record=record,
            user=annotators[0],
        )
        ResponseSyncFactory.create(
            values={
                "multi-label-question": {
                    "value": ["label-c", "label-a"],
                },
            },
            record=record,
            user=annotators[1],
        )
        SuggestionSyncFactory.create(
            value=["label-a", "label-c"],
            record=record,
            question=question,
            agent="suggestion-agent",
            score=[0.8, 0.7],
        )

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        exported_dataset = load_dataset(path=hf_dataset_name, name="default", split="train")

        assert exported_dataset[0] == {
            "id": record.external_id,
            "status": record.status,
            "_server_id": str(record.id),
            "text": "Hello World",
            "multi-label-question.responses": [["label-a", "label-b"], ["label-c", "label-a"]],
            "multi-label-question.responses.status": [ResponseStatus.submitted, ResponseStatus.submitted],
            "multi-label-question.responses.users": [str(annotators[0].id), str(annotators[1].id)],
            "multi-label-question.suggestion": ["label-a", "label-c"],
            "multi-label-question.suggestion.agent": "suggestion-agent",
            "multi-label-question.suggestion.score": [0.8, 0.7],
        }

    def test_export_to_with_ranking_question(self, sync_test_session, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)
        annotators = AnnotatorSyncFactory.create_batch(2, workspaces=[dataset.workspace])

        FieldSyncFactory.create(name="text", settings={"type": FieldType.text, "use_markdown": False}, dataset=dataset)
        QuestionSyncFactory.create(
            name="ranking-question",
            settings={
                "type": QuestionType.ranking,
                "options": [
                    {"value": "ranking-a", "text": "Ranking A"},
                    {"value": "ranking-b", "text": "Ranking B"},
                    {"value": "ranking-c", "text": "Ranking C"},
                    {"value": "ranking-d", "text": "Ranking D"},
                ],
            },
            dataset=dataset,
        )

        record = RecordSyncFactory.create(fields={"text": "Hello World"}, dataset=dataset)
        ResponseSyncFactory.create(
            values={
                "ranking-question": {
                    "value": [
                        {"value": "ranking-a", "rank": 0},
                        {"value": "ranking-d", "rank": 0},
                        {"value": "ranking-b", "rank": 1},
                    ],
                },
            },
            record=record,
            user=annotators[0],
        )
        ResponseSyncFactory.create(
            values={
                "ranking-question": {
                    "value": [
                        {"value": "ranking-b"},
                        {"value": "ranking-c"},
                        {"value": "ranking-a"},
                    ],
                },
            },
            record=record,
            user=annotators[1],
        )

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        exported_dataset = load_dataset(path=hf_dataset_name, name="default", split="train")

        assert exported_dataset[0] == {
            "id": record.external_id,
            "status": record.status,
            "_server_id": str(record.id),
            "text": "Hello World",
            "ranking-question.responses": [
                [
                    {"value": "ranking-a", "rank": 0},
                    {"value": "ranking-d", "rank": 0},
                    {"value": "ranking-b", "rank": 1},
                ],
                [
                    {"value": "ranking-b", "rank": None},
                    {"value": "ranking-c", "rank": None},
                    {"value": "ranking-a", "rank": None},
                ],
            ],
            "ranking-question.responses.status": [ResponseStatus.submitted, ResponseStatus.submitted],
            "ranking-question.responses.users": [str(annotators[0].id), str(annotators[1].id)],
        }

    def test_export_to_with_ranking_question_and_suggestion(self, sync_test_session, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)
        annotators = AnnotatorSyncFactory.create_batch(2, workspaces=[dataset.workspace])

        FieldSyncFactory.create(name="text", settings={"type": FieldType.text, "use_markdown": False}, dataset=dataset)
        question = QuestionSyncFactory.create(
            name="ranking-question",
            settings={
                "type": QuestionType.ranking,
                "options": [
                    {"value": "ranking-a", "text": "Ranking A"},
                    {"value": "ranking-b", "text": "Ranking B"},
                    {"value": "ranking-c", "text": "Ranking C"},
                    {"value": "ranking-d", "text": "Ranking D"},
                ],
            },
            dataset=dataset,
        )

        record = RecordSyncFactory.create(fields={"text": "Hello World"}, dataset=dataset)
        ResponseSyncFactory.create(
            values={
                "ranking-question": {
                    "value": [
                        {"value": "ranking-a", "rank": 0},
                        {"value": "ranking-d", "rank": 0},
                        {"value": "ranking-b", "rank": 1},
                    ],
                },
            },
            record=record,
            user=annotators[0],
        )
        ResponseSyncFactory.create(
            values={
                "ranking-question": {
                    "value": [
                        {"value": "ranking-b"},
                        {"value": "ranking-c"},
                        {"value": "ranking-a"},
                    ],
                },
            },
            record=record,
            user=annotators[1],
        )
        SuggestionSyncFactory.create(
            value=[
                {"value": "ranking-a", "rank": 0},
                {"value": "ranking-b", "rank": 1},
                {"value": "ranking-c", "rank": 2},
                {"value": "ranking-d", "rank": 3},
            ],
            record=record,
            question=question,
            agent="suggestion-agent",
            score=[0.5, 0.4, 0.3, 0.2],
        )

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        exported_dataset = load_dataset(path=hf_dataset_name, name="default", split="train")

        assert exported_dataset[0] == {
            "id": record.external_id,
            "status": record.status,
            "_server_id": str(record.id),
            "text": "Hello World",
            "ranking-question.responses": [
                [
                    {"value": "ranking-a", "rank": 0},
                    {"value": "ranking-d", "rank": 0},
                    {"value": "ranking-b", "rank": 1},
                ],
                [
                    {"value": "ranking-b", "rank": None},
                    {"value": "ranking-c", "rank": None},
                    {"value": "ranking-a", "rank": None},
                ],
            ],
            "ranking-question.responses.status": [ResponseStatus.submitted, ResponseStatus.submitted],
            "ranking-question.responses.users": [str(annotators[0].id), str(annotators[1].id)],
            "ranking-question.suggestion": [
                {"value": "ranking-a", "rank": 0},
                {"value": "ranking-b", "rank": 1},
                {"value": "ranking-c", "rank": 2},
                {"value": "ranking-d", "rank": 3},
            ],
            "ranking-question.suggestion.agent": "suggestion-agent",
            "ranking-question.suggestion.score": [0.5, 0.4, 0.3, 0.2],
        }

    def test_export_to_with_span_question(self, sync_test_session, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)
        annotators = AnnotatorSyncFactory.create_batch(2, workspaces=[dataset.workspace])

        FieldSyncFactory.create(name="text", settings={"type": FieldType.text, "use_markdown": False}, dataset=dataset)
        QuestionSyncFactory.create(
            name="span-question",
            settings={
                "type": QuestionType.span,
                "field": "text",
                "options": [
                    {"value": "label-a", "text": "Label A"},
                    {"value": "label-b", "text": "Label B"},
                    {"value": "label-c", "text": "Label C"},
                    {"value": "label-d", "text": "Label D"},
                ],
            },
            dataset=dataset,
        )

        record = RecordSyncFactory.create(fields={"text": "Hello World"}, dataset=dataset)
        ResponseSyncFactory.create(
            values={
                "span-question": {
                    "value": [
                        {"label": "label-b", "start": 0, "end": 2},
                        {"label": "label-a", "start": 3, "end": 5},
                    ],
                },
            },
            record=record,
            user=annotators[0],
        )
        ResponseSyncFactory.create(
            values={
                "span-question": {
                    "value": [
                        {"label": "label-c", "start": 2, "end": 6},
                    ],
                },
            },
            record=record,
            user=annotators[1],
        )

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        exported_dataset = load_dataset(path=hf_dataset_name, name="default", split="train")

        assert exported_dataset[0] == {
            "id": record.external_id,
            "status": record.status,
            "_server_id": str(record.id),
            "text": "Hello World",
            "span-question.responses": [
                [
                    {"label": "label-b", "start": 0, "end": 2},
                    {"label": "label-a", "start": 3, "end": 5},
                ],
                [
                    {"label": "label-c", "start": 2, "end": 6},
                ],
            ],
            "span-question.responses.status": [ResponseStatus.submitted, ResponseStatus.submitted],
            "span-question.responses.users": [str(annotators[0].id), str(annotators[1].id)],
        }

    def test_export_to_with_span_question_and_suggestion(self, sync_test_session, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)
        annotators = AnnotatorSyncFactory.create_batch(2, workspaces=[dataset.workspace])

        FieldSyncFactory.create(name="text", settings={"type": FieldType.text, "use_markdown": False}, dataset=dataset)
        question = QuestionSyncFactory.create(
            name="span-question",
            settings={
                "type": QuestionType.span,
                "field": "text",
                "options": [
                    {"value": "label-a", "text": "Label A"},
                    {"value": "label-b", "text": "Label B"},
                    {"value": "label-c", "text": "Label C"},
                    {"value": "label-d", "text": "Label D"},
                ],
            },
            dataset=dataset,
        )

        record = RecordSyncFactory.create(fields={"text": "Hello World"}, dataset=dataset)
        ResponseSyncFactory.create(
            values={
                "span-question": {
                    "value": [
                        {"label": "label-b", "start": 0, "end": 2},
                        {"label": "label-a", "start": 3, "end": 5},
                    ],
                },
            },
            record=record,
            user=annotators[0],
        )
        ResponseSyncFactory.create(
            values={
                "span-question": {
                    "value": [
                        {"label": "label-c", "start": 2, "end": 6},
                    ],
                },
            },
            record=record,
            user=annotators[1],
        )
        SuggestionSyncFactory.create(
            value=[
                {"label": "label-a", "start": 0, "end": 3},
                {"label": "label-d", "start": 2, "end": 6},
            ],
            record=record,
            question=question,
            agent="suggestion-agent",
            score=[0.7, 0.6],
        )

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        exported_dataset = load_dataset(path=hf_dataset_name, name="default", split="train")

        assert exported_dataset[0] == {
            "id": record.external_id,
            "status": record.status,
            "_server_id": str(record.id),
            "text": "Hello World",
            "span-question.responses": [
                [
                    {"label": "label-b", "start": 0, "end": 2},
                    {"label": "label-a", "start": 3, "end": 5},
                ],
                [
                    {"label": "label-c", "start": 2, "end": 6},
                ],
            ],
            "span-question.responses.status": [ResponseStatus.submitted, ResponseStatus.submitted],
            "span-question.responses.users": [str(annotators[0].id), str(annotators[1].id)],
            "span-question.suggestion": [
                {"label": "label-a", "start": 0, "end": 3},
                {"label": "label-d", "start": 2, "end": 6},
            ],
            "span-question.suggestion.agent": "suggestion-agent",
            "span-question.suggestion.score": [0.7, 0.6],
        }

    def test_export_to_with_draft_response(self, sync_test_session, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)
        annotator = AnnotatorSyncFactory.create(workspaces=[dataset.workspace])

        FieldSyncFactory.create(name="text", settings={"type": FieldType.text, "use_markdown": False}, dataset=dataset)
        QuestionSyncFactory.create(
            name="text-question",
            settings={
                "type": QuestionType.text,
                "use_markdown": False,
            },
            dataset=dataset,
        )

        record = RecordSyncFactory.create(fields={"text": "Hello World"}, dataset=dataset)
        ResponseSyncFactory.create(
            status=ResponseStatus.draft,
            record=record,
            user=annotator,
        )

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        exported_dataset = load_dataset(path=hf_dataset_name, name="default", split="train")

        assert exported_dataset[0] == {
            "id": record.external_id,
            "status": record.status,
            "_server_id": str(record.id),
            "text": "Hello World",
            "text-question.responses": [None],
            "text-question.responses.status": [ResponseStatus.draft],
            "text-question.responses.users": [str(annotator.id)],
        }

    def test_export_to_with_discarded_response(self, sync_test_session, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)
        annotator = AnnotatorSyncFactory.create(workspaces=[dataset.workspace])

        FieldSyncFactory.create(name="text", settings={"type": FieldType.text, "use_markdown": False}, dataset=dataset)
        QuestionSyncFactory.create(
            name="text-question",
            settings={
                "type": QuestionType.text,
                "use_markdown": False,
            },
            dataset=dataset,
        )

        record = RecordSyncFactory.create(fields={"text": "Hello World"}, dataset=dataset)
        ResponseSyncFactory.create(
            status=ResponseStatus.discarded,
            record=record,
            user=annotator,
        )

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        exported_dataset = load_dataset(path=hf_dataset_name, name="default", split="train")

        assert exported_dataset[0] == {
            "id": record.external_id,
            "status": record.status,
            "_server_id": str(record.id),
            "text": "Hello World",
            "text-question.responses": [None],
            "text-question.responses.status": [ResponseStatus.discarded],
            "text-question.responses.users": [str(annotator.id)],
        }

    def test_export_to_with_metadata(self, sync_test_session, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)

        FieldSyncFactory.create(name="text", settings={"type": FieldType.text, "use_markdown": False}, dataset=dataset)

        MetadataPropertySyncFactory.create(
            name="metadata-terms",
            title="Metadata Terms",
            settings={
                "type": MetadataPropertyType.terms,
                "values": ["term-a", "term-b", "term-c"],
            },
            dataset=dataset,
        )

        MetadataPropertySyncFactory.create(
            name="metadata-integer",
            title="Metadata Integer",
            settings={
                "type": MetadataPropertyType.integer,
            },
            dataset=dataset,
        )

        MetadataPropertySyncFactory.create(
            name="metadata-float",
            title="Metadata Float",
            settings={
                "type": MetadataPropertyType.float,
            },
            dataset=dataset,
        )

        RecordSyncFactory.create(
            fields={"text": "Hello World"},
            metadata_={
                "metadata-terms": ["term-c", "term-b"],
                "metadata-integer": 42,
                "metadata-float": 3.14,
            },
            dataset=dataset,
        )

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        exported_dataset = load_dataset(path=hf_dataset_name, name="default", split="train")

        assert exported_dataset[0]["metadata.metadata-terms"] == ["term-c", "term-b"]
        assert exported_dataset[0]["metadata.metadata-integer"] == 42
        assert exported_dataset[0]["metadata.metadata-float"] == 3.14

    def test_export_to_with_vectors(self, sync_test_session, hf_dataset_name: str):
        dataset = DatasetSyncFactory.create(status=DatasetStatus.ready)

        FieldSyncFactory.create(name="text", settings={"type": FieldType.text, "use_markdown": False}, dataset=dataset)
        record = RecordSyncFactory.create(fields={"text": "Hello World"}, dataset=dataset)

        vector_settings_a = VectorSettingsSyncFactory.create(
            name="vector-a",
            title="Vector A",
            dimensions=3,
            dataset=dataset,
        )
        vector_settings_b = VectorSettingsSyncFactory.create(
            name="vector-b",
            title="Vector B",
            dimensions=2,
            dataset=dataset,
        )
        VectorSettingsSyncFactory.create(
            name="vector-c",
            title="Vector C",
            dimensions=4,
            dataset=dataset,
        )

        VectorSyncFactory.create(
            value=[1.0, 2.0, 3.0],
            record=record,
            vector_settings=vector_settings_a,
        )

        VectorSyncFactory.create(
            value=[3.14, 3.15],
            record=record,
            vector_settings=vector_settings_b,
        )

        HubDatasetExporter(dataset).export_to(
            name=hf_dataset_name,
            subset="default",
            split="train",
            private=False,
            token=HF_TOKEN,
        )

        exported_dataset = load_dataset(path=hf_dataset_name, name="default", split="train")

        assert exported_dataset[0]["vector.vector-a"] == [1.0, 2.0, 3.0]
        assert exported_dataset[0]["vector.vector-b"] == [3.14, 3.15]
        assert exported_dataset[0]["vector.vector-c"] == None
