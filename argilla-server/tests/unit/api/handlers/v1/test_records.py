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

from datetime import datetime
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Type
from unittest.mock import call
from uuid import UUID, uuid4

import pytest

from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.enums import RecordStatus, ResponseStatus
from argilla_server.models import Dataset, Record, Response, Suggestion, User, UserRole
from argilla_server.search_engine import SearchEngine
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from tests.factories import (
    DatasetFactory,
    FloatMetadataPropertyFactory,
    IntegerMetadataPropertyFactory,
    LabelSelectionQuestionFactory,
    MetadataPropertyFactory,
    MultiLabelSelectionQuestionFactory,
    QuestionFactory,
    RankingQuestionFactory,
    RatingQuestionFactory,
    RecordFactory,
    ResponseFactory,
    SuggestionFactory,
    TermsMetadataPropertyFactory,
    TextQuestionFactory,
    UserFactory,
    VectorFactory,
    VectorSettingsFactory,
    WorkspaceFactory,
    TextFieldFactory,
)

if TYPE_CHECKING:
    from argilla_server.models import Dataset
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


async def create_text_questions(dataset: "Dataset") -> None:
    await TextQuestionFactory.create(name="input_ok", dataset=dataset, required=True)
    await TextQuestionFactory.create(name="output_ok", dataset=dataset)


async def create_rating_questions(dataset: "Dataset") -> None:
    await RatingQuestionFactory.create(name="rating_question_1", dataset=dataset, required=True)
    await RatingQuestionFactory.create(name="rating_question_2", dataset=dataset)


async def create_label_selection_questions(dataset: "Dataset") -> None:
    await LabelSelectionQuestionFactory.create(name="label_selection_question_1", dataset=dataset, required=True)
    await LabelSelectionQuestionFactory.create(name="label_selection_question_2", dataset=dataset)


async def create_multi_label_selection_questions(dataset: "Dataset") -> None:
    await MultiLabelSelectionQuestionFactory.create(
        name="multi_label_selection_question_1", dataset=dataset, required=True
    )
    await MultiLabelSelectionQuestionFactory.create(name="multi_label_selection_question_2", dataset=dataset)


async def create_ranking_question(dataset: "Dataset") -> None:
    await RankingQuestionFactory.create(name="ranking_question_1", dataset=dataset, required=True)
    await RankingQuestionFactory.create(name="ranking_question_2", dataset=dataset)


@pytest.mark.asyncio
class TestSuiteRecords:
    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin, UserRole.annotator])
    async def test_get_record(self, async_client: "AsyncClient", role: UserRole):
        dataset = await DatasetFactory.create()
        record = await RecordFactory.create(dataset=dataset)
        user = await UserFactory.create(workspaces=[dataset.workspace], role=role)

        response = await async_client.get(f"/api/v1/records/{record.id}", headers={API_KEY_HEADER_NAME: user.api_key})

        assert response.status_code == 200
        assert response.json() == {
            "id": str(record.id),
            "status": RecordStatus.pending,
            "fields": {"text": "This is a text", "sentiment": "neutral"},
            "metadata": None,
            "external_id": record.external_id,
            "responses": [],
            "suggestions": [],
            "vectors": {},
            "dataset_id": str(dataset.id),
            "inserted_at": record.inserted_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
        }

    async def test_get_records_with_suggestions(self, async_client: "AsyncClient", owner_auth_header: dict):
        record = await RecordFactory.create()
        question = await TextQuestionFactory.create(dataset=record.dataset)
        suggestion = await SuggestionFactory.create(question=question, record=record)

        response = await async_client.get(f"/api/v1/records/{record.id}", headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "id": str(record.id),
            "status": RecordStatus.pending,
            "fields": {"text": "This is a text", "sentiment": "neutral"},
            "metadata": None,
            "external_id": record.external_id,
            "responses": [],
            "suggestions": [
                {
                    "id": str(suggestion.id),
                    "type": None,
                    "score": None,
                    "value": suggestion.value,
                    "agent": None,
                    "question_id": str(question.id),
                    "inserted_at": suggestion.inserted_at.isoformat(),
                    "updated_at": suggestion.updated_at.isoformat(),
                }
            ],
            "vectors": {},
            "dataset_id": str(record.dataset_id),
            "inserted_at": record.inserted_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
        }

    async def test_get_record_with_responses(self, async_client: "AsyncClient", owner_auth_header: dict):
        record = await RecordFactory.create()
        user_response = await ResponseFactory.create(record=record)

        response = await async_client.get(f"/api/v1/records/{record.id}", headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "id": str(record.id),
            "status": RecordStatus.pending,
            "fields": {"text": "This is a text", "sentiment": "neutral"},
            "metadata": None,
            "external_id": record.external_id,
            "responses": [
                {
                    "id": str(user_response.id),
                    "values": user_response.values,
                    "status": user_response.status,
                    "record_id": str(record.id),
                    "user_id": str(user_response.user_id),
                    "inserted_at": user_response.inserted_at.isoformat(),
                    "updated_at": user_response.updated_at.isoformat(),
                }
            ],
            "suggestions": [],
            "vectors": {},
            "dataset_id": str(record.dataset_id),
            "inserted_at": record.inserted_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
        }

    async def test_get_record_with_vectors(self, async_client: "AsyncClient", owner_auth_header: dict):
        record = await RecordFactory.create()
        vector_settings = await VectorSettingsFactory.create(dataset=record.dataset, dimensions=5)
        vector = await VectorFactory.create(record=record, vector_settings=vector_settings, value=[1, 1, 1, 1, 1])

        response = await async_client.get(f"/api/v1/records/{record.id}", headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "id": str(record.id),
            "status": RecordStatus.pending,
            "fields": {"text": "This is a text", "sentiment": "neutral"},
            "metadata": None,
            "external_id": record.external_id,
            "responses": [],
            "suggestions": [],
            "vectors": {vector_settings.name: vector.value},
            "dataset_id": str(record.dataset_id),
            "inserted_at": record.inserted_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
        }

    async def test_get_record_without_authentication(self, async_client: "AsyncClient"):
        record = await RecordFactory.create()

        response = await async_client.get(f"/api/v1/records/{record.id}")

        assert response.status_code == 401

    @pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
    async def test_get_record_as_restricted_user_from_different_workspace(
        self, async_client: "AsyncClient", role: UserRole
    ):
        dataset = await DatasetFactory.create()
        record = await RecordFactory.create(dataset=dataset)
        user = await UserFactory.create(role=role)

        response = await async_client.get(f"/api/v1/records/{record.id}", headers={API_KEY_HEADER_NAME: user.api_key})

        assert response.status_code == 403

    async def test_get_record_with_nonexistent_record_id(self, async_client: "AsyncClient", owner_auth_header: dict):
        record_id = uuid4()

        await RecordFactory.create()

        response = await async_client.get(
            f"/api/v1/records/{record_id}",
            headers=owner_auth_header,
        )

        assert response.status_code == 404
        assert response.json() == {"detail": f"Record with id `{record_id}` not found"}

    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_update_record(self, async_client: "AsyncClient", mock_search_engine: SearchEngine, role: UserRole):
        dataset = await DatasetFactory.create()
        user = await UserFactory.create(workspaces=[dataset.workspace], role=role)
        question_0 = await TextQuestionFactory.create(dataset=dataset)
        question_1 = await TextQuestionFactory.create(dataset=dataset)
        question_2 = await TextQuestionFactory.create(dataset=dataset)
        await TermsMetadataPropertyFactory.create(name="terms-metadata-property", dataset=dataset)
        await IntegerMetadataPropertyFactory.create(name="integer-metadata-property", dataset=dataset)
        await FloatMetadataPropertyFactory.create(name="float-metadata-property", dataset=dataset)
        record = await RecordFactory.create(
            dataset=dataset,
            metadata_={"terms-metadata-property": "a", "integer-metadata-property": 1, "float-metadata-property": 1.0},
        )
        await SuggestionFactory.create(question=question_0, record=record, value="suggestion 1")
        await SuggestionFactory.create(question=question_1, record=record, value="suggestion 2")
        await SuggestionFactory.create(question=question_2, record=record, value="suggestion 3")
        vector_settings_0 = await VectorSettingsFactory.create(dataset=dataset, dimensions=5)
        vector_settings_1 = await VectorSettingsFactory.create(dataset=dataset, dimensions=5)
        vector_settings_2 = await VectorSettingsFactory.create(dataset=dataset, dimensions=5)
        await VectorFactory.create(record=record, vector_settings=vector_settings_0, value=[1, 1, 1, 1, 1])
        await VectorFactory.create(record=record, vector_settings=vector_settings_1, value=[2, 2, 2, 2, 2])

        response = await async_client.patch(
            f"/api/v1/records/{record.id}",
            headers={API_KEY_HEADER_NAME: user.api_key},
            json={
                "metadata": {
                    "terms-metadata-property": "c",
                    "integer-metadata-property": 9999,
                    "float-metadata-property": 9999.0,
                    "extra-metadata": "yes",
                },
                "suggestions": [
                    {
                        "question_id": str(question_0.id),
                        "value": "suggestion updated 1",
                    },
                    {
                        "question_id": str(question_1.id),
                        "value": "suggestion updated 2",
                    },
                ],
                "vectors": {
                    vector_settings_0.name: [10, 10, 10, 10, 10],
                    vector_settings_2.name: [3, 3, 3, 3, 3],
                },
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(record.id),
            "status": RecordStatus.pending,
            "fields": {"text": "This is a text", "sentiment": "neutral"},
            "metadata": {
                "terms-metadata-property": "c",
                "integer-metadata-property": 9999,
                "float-metadata-property": 9999.0,
                "extra-metadata": "yes",
            },
            "external_id": record.external_id,
            "responses": [],
            "suggestions": [
                {
                    "id": str(record.suggestions[0].id),
                    "type": None,
                    "score": None,
                    "value": "suggestion updated 1",
                    "agent": None,
                    "question_id": str(question_0.id),
                    "inserted_at": record.suggestions[0].inserted_at.isoformat(),
                    "updated_at": record.suggestions[0].updated_at.isoformat(),
                },
                {
                    "id": str(record.suggestions[1].id),
                    "type": None,
                    "score": None,
                    "value": "suggestion updated 2",
                    "agent": None,
                    "question_id": str(question_1.id),
                    "inserted_at": record.suggestions[1].inserted_at.isoformat(),
                    "updated_at": record.suggestions[1].updated_at.isoformat(),
                },
            ],
            "vectors": {
                vector_settings_0.name: [10.0, 10.0, 10.0, 10.0, 10.0],
                vector_settings_1.name: [2.0, 2.0, 2.0, 2.0, 2.0],
                vector_settings_2.name: [3.0, 3.0, 3.0, 3.0, 3.0],
            },
            "dataset_id": str(dataset.id),
            "inserted_at": record.inserted_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
        }
        assert record.updated_at > record.inserted_at

        mock_search_engine.index_records.assert_called_once_with(dataset, [record])

    async def test_update_record_fields(
        self, async_client: "AsyncClient", db: "AsyncSession", mock_search_engine: SearchEngine, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status="ready")
        await TextFieldFactory.create(dataset=dataset, name="text", required=True)
        await TextFieldFactory.create(dataset=dataset, name="sentiment", required=False)
        record = await RecordFactory.create(dataset=dataset, fields={"text": "This is a text"})

        response = await async_client.patch(
            f"/api/v1/records/{record.id}",
            headers=owner_auth_header,
            json={"fields": {"text": "Updated text", "sentiment": "positive"}},
        )

        assert response.status_code == 200, response.json()
        assert response.json() == {
            "id": str(record.id),
            "status": RecordStatus.pending,
            "fields": {"text": "Updated text", "sentiment": "positive"},
            "metadata": None,
            "external_id": record.external_id,
            "responses": [],
            "suggestions": [],
            "vectors": {},
            "dataset_id": str(dataset.id),
            "inserted_at": record.inserted_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
        }
        assert record.updated_at > record.inserted_at
        mock_search_engine.index_records.assert_called_once_with(dataset, [record])

    async def test_update_record_fields_with_less_fields(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        await TextFieldFactory.create(dataset=dataset, name="text", required=True)
        await TextFieldFactory.create(dataset=dataset, name="sentiment", required=False)
        record = await RecordFactory.create(dataset=dataset, fields={"text": "This is a text", "sentiment": "neutral"})

        response = await async_client.patch(
            f"/api/v1/records/{record.id}",
            headers=owner_auth_header,
            json={"fields": {"text": "Updated text"}},
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(record.id),
            "status": RecordStatus.pending,
            "fields": {"text": "Updated text"},
            "metadata": None,
            "external_id": record.external_id,
            "responses": [],
            "suggestions": [],
            "vectors": {},
            "dataset_id": str(dataset.id),
            "inserted_at": record.inserted_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
        }
        assert record.updated_at > record.inserted_at
        mock_search_engine.index_records.assert_called_once_with(dataset, [record])

    async def test_update_record_fields_with_empty_fields(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        record = await RecordFactory.create(dataset=dataset)

        response = await async_client.patch(
            f"/api/v1/records/{record.id}",
            headers=owner_auth_header,
            json={"fields": {}},
        )

        assert response.status_code == 422
        assert response.json() == {"detail": "fields cannot be empty"}
        assert record.updated_at == record.inserted_at
        mock_search_engine.index_records.assert_not_called()

    async def test_update_record_with_null_metadata(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        await TermsMetadataPropertyFactory.create(name="terms-metadata-property", dataset=dataset)
        await IntegerMetadataPropertyFactory.create(name="integer-metadata-property", dataset=dataset)
        await FloatMetadataPropertyFactory.create(name="float-metadata-property", dataset=dataset)
        record = await RecordFactory.create(
            dataset=dataset,
            metadata_={"terms-metadata-property": "a", "integer-metadata-property": 1, "float-metadata-property": 1.0},
        )

        response = await async_client.patch(
            f"/api/v1/records/{record.id}",
            headers=owner_auth_header,
            json={"metadata": None},
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(record.id),
            "status": RecordStatus.pending,
            "fields": {"text": "This is a text", "sentiment": "neutral"},
            "metadata": None,
            "external_id": record.external_id,
            "responses": [],
            "suggestions": [],
            "vectors": {},
            "dataset_id": str(dataset.id),
            "inserted_at": record.inserted_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
        }
        assert record.updated_at > record.inserted_at
        mock_search_engine.index_records.assert_called_once_with(dataset, [record])

    async def test_update_record_with_no_metadata(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        record = await RecordFactory.create(dataset=dataset)

        response = await async_client.patch(
            f"/api/v1/records/{record.id}",
            headers=owner_auth_header,
            json={},
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(record.id),
            "status": RecordStatus.pending,
            "fields": {"text": "This is a text", "sentiment": "neutral"},
            "metadata": None,
            "external_id": record.external_id,
            "responses": [],
            "suggestions": [],
            "vectors": {},
            "dataset_id": str(dataset.id),
            "inserted_at": record.inserted_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
        }
        assert record.updated_at == record.inserted_at
        mock_search_engine.index_records.assert_not_called()

    async def test_update_record_with_list_terms_metadata(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        await TermsMetadataPropertyFactory.create(name="terms-metadata-property", dataset=dataset)
        record = await RecordFactory.create(dataset=dataset)

        response = await async_client.patch(
            f"/api/v1/records/{record.id}",
            headers=owner_auth_header,
            json={
                "metadata": {
                    "terms-metadata-property": ["a", "b", "c"],
                },
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(record.id),
            "status": RecordStatus.pending,
            "fields": {"text": "This is a text", "sentiment": "neutral"},
            "metadata": {
                "terms-metadata-property": ["a", "b", "c"],
            },
            "external_id": record.external_id,
            "responses": [],
            "suggestions": [],
            "vectors": {},
            "dataset_id": str(dataset.id),
            "inserted_at": record.inserted_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
        }
        assert record.updated_at > record.inserted_at
        mock_search_engine.index_records.assert_called_once_with(dataset, [record])

    async def test_update_record_with_no_suggestions(
        self, async_client: "AsyncClient", db: "AsyncSession", mock_search_engine: SearchEngine, owner_auth_header: dict
    ):
        suggestion = await SuggestionFactory.create()
        record = suggestion.record

        response = await async_client.patch(
            f"/api/v1/records/{suggestion.record.id}",
            headers=owner_auth_header,
            json={"suggestions": []},
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(record.id),
            "status": RecordStatus.pending,
            "fields": {"text": "This is a text", "sentiment": "neutral"},
            "metadata": None,
            "external_id": record.external_id,
            "responses": [],
            "suggestions": [],
            "vectors": {},
            "dataset_id": str(record.dataset_id),
            "inserted_at": record.inserted_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
        }
        assert record.updated_at > record.inserted_at
        assert (await db.execute(select(Suggestion).where(Suggestion.id == suggestion.id))).scalar_one_or_none() is None

    @pytest.mark.parametrize(
        ["MetadataPropertyFactoryClass", "create_value", "update_value", "expected_error"],
        [
            (
                TermsMetadataPropertyFactory,
                "a",
                "z",
                "metadata is not valid: 'name' metadata property validation failed because 'z' is not an allowed term.",
            ),
            (
                IntegerMetadataPropertyFactory,
                10,
                "wrong-integer",
                "metadata is not valid: 'name' metadata property validation failed because 'wrong-integer' is not an integer.",
            ),
            (
                FloatMetadataPropertyFactory,
                13.3,
                "wrong-float",
                "metadata is not valid: 'name' metadata property validation failed because 'wrong-float' is not a float.",
            ),
        ],
    )
    async def test_update_record_with_not_valid_metadata(
        self,
        async_client: "AsyncClient",
        owner_auth_header: dict,
        MetadataPropertyFactoryClass: Type[MetadataPropertyFactory],
        create_value: Any,
        update_value: Any,
        expected_error: str,
    ):
        dataset = await DatasetFactory.create(allow_extra_metadata=False)
        await MetadataPropertyFactoryClass.create(name="name", dataset=dataset)
        record = await RecordFactory.create(dataset=dataset, metadata_={"name": create_value})

        response = await async_client.patch(
            f"/api/v1/records/{record.id}",
            headers=owner_auth_header,
            json={"metadata": {"name": update_value}},
        )

        assert response.status_code == 422
        assert response.json() == {"detail": expected_error}

    async def test_update_record_with_extra_metadata_not_allowed(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(allow_extra_metadata=False)
        await TermsMetadataPropertyFactory.create(name="terms-metadata-property", dataset=dataset)
        await IntegerMetadataPropertyFactory.create(name="integer-metadata-property", dataset=dataset)
        await FloatMetadataPropertyFactory.create(name="float-metadata-property", dataset=dataset)
        record = await RecordFactory.create(
            dataset=dataset,
            metadata_={"terms-metadata-property": "a", "integer-metadata-property": 1, "float-metadata-property": 1.0},
        )

        response = await async_client.patch(
            f"/api/v1/records/{record.id}",
            headers=owner_auth_header,
            json={
                "metadata": {
                    "terms-metadata-property": "c",
                    "integer-metadata-property": 9999,
                    "float-metadata-property": 9999.0,
                    "extra-metadata": "yes",
                },
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "metadata is not valid: 'extra-metadata' metadata property does not exists for dataset "
            f"'{dataset.id}' and extra metadata is not allowed for this dataset"
        }

    async def test_update_record_with_invalid_suggestion(self, async_client: "AsyncClient", owner_auth_header: dict):
        dataset = await DatasetFactory.create()
        question = await LabelSelectionQuestionFactory.create(dataset=dataset)
        record = await RecordFactory.create(dataset=dataset)

        response = await async_client.patch(
            f"/api/v1/records/{record.id}",
            headers=owner_auth_header,
            json={
                "suggestions": [
                    {"question_id": str(question.id), "value": "not a valid value"},
                ]
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "record does not have valid suggestions: "
            "'not a valid value' is not a valid label for label selection question.\n"
            "Valid labels are: ['option1', 'option2', 'option3']"
        }

    async def test_update_record_with_invalid_vector(self, async_client: "AsyncClient", owner_auth_header: dict):
        dataset = await DatasetFactory.create()
        vector_settings = await VectorSettingsFactory.create(dataset=dataset, dimensions=5)
        record = await RecordFactory.create(dataset=dataset)

        response = await async_client.patch(
            f"/api/v1/records/{record.id}",
            headers=owner_auth_header,
            json={"vectors": {vector_settings.name: [1, 2, 3, 4, 5, 6]}},
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "record does not have valid vectors: "
            f"vector value for vector name={vector_settings.name} "
            f"must have {vector_settings.dimensions} elements, got 6 elements"
        }

    async def test_update_record_with_suggestion_for_nonexistent_question(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        record = await RecordFactory.create(dataset=dataset)

        question_id = uuid4()

        response = await async_client.patch(
            f"/api/v1/records/{record.id}",
            headers=owner_auth_header,
            json={
                "suggestions": [
                    {"question_id": str(question_id), "value": "option-1"},
                ]
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": f"record does not have valid suggestions: question id={question_id} does not exists"
        }

    async def test_update_record_with_nonexistent_vector_settings(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        record = await RecordFactory.create(dataset=dataset)

        response = await async_client.patch(
            f"/api/v1/records/{record.id}",
            headers=owner_auth_header,
            json={"vectors": {"i-do-not-exist": [1, 2, 3, 4, 5, 6]}},
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "record does not have valid vectors: vector with name=i-do-not-exist "
            f"does not exist for dataset_id={dataset.id}"
        }

    async def test_update_record_with_duplicate_suggestions_question_ids(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        question = await TextQuestionFactory.create(dataset=dataset)
        record = await RecordFactory.create(dataset=dataset)

        response = await async_client.patch(
            f"/api/v1/records/{record.id}",
            headers=owner_auth_header,
            json={
                "suggestions": [
                    {"question_id": str(question.id), "value": "a"},
                    {"question_id": str(question.id), "value": "b"},
                ]
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "record does not have valid suggestions: found duplicate suggestions question IDs"
        }

    async def test_update_record_as_admin_from_another_workspace(self, async_client: "AsyncClient"):
        record = await RecordFactory.create()
        user = await UserFactory.create(role=UserRole.admin)

        response = await async_client.patch(
            f"/api/v1/records/{record.id}",
            headers={API_KEY_HEADER_NAME: user.api_key},
            json={
                "metadata": {"new": "yes"},
            },
        )

        assert response.status_code == 403

    async def test_update_record_as_annotator(self, async_client: "AsyncClient"):
        record = await RecordFactory.create()
        user = await UserFactory.create(role=UserRole.annotator, workspaces=[record.dataset.workspace])

        response = await async_client.patch(
            f"/api/v1/records/{record.id}",
            headers={API_KEY_HEADER_NAME: user.api_key},
            json={
                "metadata": {"new": "yes"},
            },
        )

        assert response.status_code == 403

    @pytest.mark.parametrize(
        "response_status", [ResponseStatus.submitted, ResponseStatus.discarded, ResponseStatus.draft]
    )
    async def test_create_record_response_with_required_questions(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        mock_search_engine: SearchEngine,
        owner: User,
        owner_auth_header: dict,
        response_status: ResponseStatus,
    ):
        dataset = await DatasetFactory.create()
        await TextQuestionFactory.create(name="corrected-1", dataset=dataset, required=True)
        await TextQuestionFactory.create(name="corrected-2", dataset=dataset)
        record = await RecordFactory.create(dataset=dataset)

        responses = {"values": {"corrected-1": {"value": "Unit Test 1"}}}
        response_json = {**responses, "status": response_status}
        response = await async_client.post(
            f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
        )

        response_body = response.json()
        assert response.status_code == 201
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 1
        assert await db.get(Response, UUID(response_body["id"]))
        assert response_body == {
            "id": str(UUID(response_body["id"])),
            "values": responses["values"],
            "status": response_status,
            "record_id": str(record.id),
            "user_id": str(owner.id),
            "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
        }

        response = (await db.execute(select(Response).where(Response.record_id == record.id))).scalar_one()
        mock_search_engine.update_record_response.assert_called_once_with(response)

    async def test_create_submitted_record_response_with_missing_required_questions(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        await create_text_questions(dataset)

        record = await RecordFactory.create(dataset=dataset)
        response_json = {
            "values": {"output_ok": {"value": "yes"}},
            "status": "submitted",
        }

        response = await async_client.post(
            f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
        )
        assert response.status_code == 422
        assert response.json() == {"detail": "missing response value for required question with name='input_ok'"}

    @pytest.mark.parametrize("response_status", [ResponseStatus.discarded, ResponseStatus.draft])
    async def test_create_record_response_with_missing_required_questions(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        mock_search_engine: SearchEngine,
        owner: User,
        owner_auth_header: dict,
        response_status: ResponseStatus,
    ):
        dataset = await DatasetFactory.create()
        await TextQuestionFactory.create(name="corrected-1", dataset=dataset, required=True)
        await TextQuestionFactory.create(name="corrected-2", dataset=dataset)
        record = await RecordFactory.create(dataset=dataset)

        responses = {"values": {"corrected-2": {"value": "Unit Test 2"}}}
        response_json = {**responses, "status": response_status}
        response = await async_client.post(
            f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
        )

        response_body = response.json()
        assert response.status_code == 201
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 1
        assert await db.get(Response, UUID(response_body["id"]))
        assert response_body == {
            "id": str(UUID(response_body["id"])),
            "values": responses["values"],
            "status": response_status,
            "record_id": str(record.id),
            "user_id": str(owner.id),
            "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
        }

        response = (await db.execute(select(Response).where(Response.record_id == record.id))).scalar_one()
        mock_search_engine.update_record_response.assert_called_once_with(response)

    @pytest.mark.parametrize(
        "QuestionFactory, response_value",
        [
            (TextQuestionFactory, "Unit Test!"),
            (RatingQuestionFactory, 3),
            (LabelSelectionQuestionFactory, "option1"),
            (MultiLabelSelectionQuestionFactory, ["option1", "option2"]),
            (
                RankingQuestionFactory,
                [
                    {"value": "completion-a", "rank": 1},
                    {"value": "completion-b", "rank": 2},
                    {"value": "completion-c", "rank": 3},
                ],
            ),
        ],
    )
    async def test_create_record_response_with_submitted_status(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        QuestionFactory: Type[QuestionFactory],
        response_value: Any,
        owner: User,
        owner_auth_header: dict,
    ):
        question = await QuestionFactory.create()
        record = await RecordFactory.create(dataset=question.dataset)

        response_json = {"values": {question.name: {"value": response_value}}, "status": ResponseStatus.submitted}

        response = await async_client.post(
            f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
        )

        response_body = response.json()
        assert response.status_code == 201
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 1
        assert response.json() == {
            "id": str(UUID(response_body["id"])),
            "values": {question.name: {"value": response_value}},
            "status": ResponseStatus.submitted,
            "record_id": str(record.id),
            "user_id": str(owner.id),
            "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
        }

    @pytest.mark.parametrize("response_status", [ResponseStatus.discarded, ResponseStatus.draft])
    @pytest.mark.parametrize(
        "QuestionFactory, response_value",
        [
            (TextQuestionFactory, "Unit Test!"),
            (RatingQuestionFactory, 3),
            (LabelSelectionQuestionFactory, "option1"),
            (MultiLabelSelectionQuestionFactory, ["option1", "option2"]),
            (
                RankingQuestionFactory,
                [
                    {"value": "completion-a", "rank": 1},
                    {"value": "completion-b", "rank": 2},
                    {"value": "completion-c", "rank": 3},
                ],
            ),
            (
                RankingQuestionFactory,
                [
                    {"value": "completion-a", "rank": 1},
                ],
            ),
        ],
    )
    async def test_create_record_response_with_non_submitted_status(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        response_status: ResponseStatus,
        QuestionFactory: Type[QuestionFactory],
        response_value: Any,
        owner: User,
        owner_auth_header: dict,
    ):
        question = await QuestionFactory.create()
        record = await RecordFactory.create(dataset=question.dataset)

        response_json = {"values": {question.name: {"value": response_value}}, "status": response_status}

        response = await async_client.post(
            f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 1

        response_body = response.json()
        assert response.json() == {
            "id": str(UUID(response_body["id"])),
            "values": {question.name: {"value": response_value}},
            "status": response_status.value,
            "record_id": str(record.id),
            "user_id": str(owner.id),
            "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
        }

    async def test_create_record_response_with_extra_question_responses(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        await create_text_questions(dataset)
        record = await RecordFactory.create(dataset=dataset)

        response_json = {
            "values": {
                "input_ok": {"value": "yes"},
                "unknown_question": {"value": "Test"},
            },
            "status": "submitted",
        }
        response = await async_client.post(
            f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "found response value for non configured question with name='unknown_question'"
        }

    @pytest.mark.parametrize(
        "create_questions_func, responses, expected_error_msg",
        [
            (
                create_text_questions,
                {
                    "values": {
                        "input_ok": {"value": True},
                        "output_ok": {"value": False},
                    },
                },
                None,
            ),
            (
                create_rating_questions,
                {
                    "values": {
                        "rating_question_1": {"value": "wrong-rating-value"},
                    },
                },
                "'wrong-rating-value' is not a valid rating for rating question.\nValid ratings are: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]",
            ),
            (
                create_label_selection_questions,
                {
                    "values": {
                        "label_selection_question_1": {"value": False},
                    },
                },
                None,
            ),
            (
                create_multi_label_selection_questions,
                {
                    "values": {
                        "multi_label_selection_question_1": {"value": "wrong-type"},
                    },
                },
                "multi label selection questions expects a list of values, found <class 'str'>",
            ),
            (
                create_multi_label_selection_questions,
                {
                    "values": {
                        "multi_label_selection_question_1": {"value": ["option1", "option2", "option1"]},
                    },
                },
                "multi label selection questions expect a list of unique values, but duplicates were found",
            ),
            (
                create_multi_label_selection_questions,
                {
                    "values": {
                        "multi_label_selection_question_1": {"value": ["option4", "option5"]},
                    },
                },
                "['option4', 'option5'] are not valid labels for multi label selection question.\nValid labels are: ['option1', 'option2', 'option3']",
            ),
            (
                create_multi_label_selection_questions,
                {"values": {"multi_label_selection_question_1": {"value": []}}},
                "multi label selection questions expects a list of values, found empty list",
            ),
            (
                create_ranking_question,
                {"values": {"ranking_question_1": {"value": "wrong-type"}}},
                "ranking question expects a list of values, found <class 'str'>",
            ),
            (
                create_ranking_question,
                {"values": {"ranking_question_1": {"value": []}}},
                "ranking question expects a list containing 3 values, found a list of 0 values",
            ),
            (
                create_ranking_question,
                {
                    "values": {
                        "ranking_question_1": {
                            "value": [
                                {"value": "completion-b", "rank": 1},
                            ]
                        }
                    }
                },
                "ranking question expects a list containing 3 values, found a list of 1 values",
            ),
            (
                create_ranking_question,
                {
                    "values": {
                        "ranking_question_1": {
                            "value": [
                                {"value": "completion-b", "rank": 1},
                                {"value": "completion-c", "rank": 2},
                                {"value": "completion-a", "rank": 3},
                                {"value": "completion-z", "rank": 4},
                            ],
                        }
                    }
                },
                "ranking question expects a list containing 3 values, found a list of 4 values",
            ),
            (
                create_ranking_question,
                {
                    "values": {
                        "ranking_question_1": {
                            "value": [
                                {"value": "completion-b", "rank": 1},
                                {"value": "completion-c", "rank": 2},
                                {"value": "completion-a", "rank": 4},
                            ]
                        }
                    }
                },
                "[4] are not valid ranks for ranking question.\nValid ranks are: [1, 2, 3]",
            ),
            (
                create_ranking_question,
                {
                    "values": {
                        "ranking_question_1": {
                            "value": [
                                {"value": "completion-b"},
                                {"value": "completion-c"},
                                {"value": "completion-a"},
                            ]
                        }
                    }
                },
                "[None] are not valid ranks for ranking question.\nValid ranks are: [1, 2, 3]",
            ),
            (
                create_ranking_question,
                {
                    "values": {
                        "ranking_question_1": {
                            "value": [
                                {"value": "completion-invalid", "rank": 1},
                                {"value": "completion-c", "rank": 2},
                                {"value": "completion-a", "rank": 3},
                            ]
                        }
                    }
                },
                "['completion-invalid'] are not valid values for ranking question.\nValid values are: ['completion-a', 'completion-b', 'completion-c']",
            ),
            (
                create_ranking_question,
                {
                    "values": {
                        "ranking_question_1": {
                            "value": [
                                {"value": "completion-a", "rank": 1},
                                {"value": "completion-c", "rank": 2},
                                {"value": "completion-a", "rank": 3},
                            ]
                        }
                    }
                },
                "ranking question expects a list of unique values, but duplicates were found",
            ),
        ],
    )
    async def test_create_record_response_with_wrong_response_value(
        self,
        async_client: "AsyncClient",
        owner_auth_header: dict,
        create_questions_func: Callable[["Dataset"], Awaitable[None]],
        responses: dict,
        expected_error_msg: str,
    ):
        dataset = await DatasetFactory.create()
        await create_questions_func(dataset)
        record = await RecordFactory.create(dataset=dataset)

        response_json = {**responses, "status": "submitted"}
        response = await async_client.post(
            f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
        )

        assert response.status_code == 422

        if expected_error_msg:
            assert response.json() == {"detail": expected_error_msg}

    async def test_create_record_response_without_authentication(self, async_client: "AsyncClient", db: "AsyncSession"):
        record = await RecordFactory.create()
        response_json = {
            "values": {
                "input_ok": {"value": "yes"},
                "output_ok": {"value": "yes"},
            },
            "status": "submitted",
        }

        response = await async_client.post(f"/api/v1/records/{record.id}/responses", json=response_json)

        assert response.status_code == 401
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    @pytest.mark.parametrize("status", ["submitted", "discarded", "draft"])
    async def test_create_record_response(
        self, async_client: "AsyncClient", db: "AsyncSession", owner: User, owner_auth_header: dict, status: str
    ):
        dataset = await DatasetFactory.create()
        await TextQuestionFactory.create(name="input_ok", dataset=dataset)
        await TextQuestionFactory.create(name="output_ok", dataset=dataset)

        record = await RecordFactory.create(dataset=dataset)
        response_json = {
            "values": {
                "input_ok": {"value": "yes"},
                "output_ok": {"value": "yes"},
            },
            "status": status,
        }

        dataset_previous_last_activity_at = dataset.last_activity_at
        dataset_previous_updated_at = dataset.updated_at

        response = await async_client.post(
            f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 1

        assert dataset.last_activity_at > dataset_previous_last_activity_at
        assert dataset.updated_at == dataset_previous_updated_at

        response_body = response.json()
        assert await db.get(Response, UUID(response_body["id"]))
        assert response_body == {
            "id": str(UUID(response_body["id"])),
            "values": {
                "input_ok": {"value": "yes"},
                "output_ok": {"value": "yes"},
            },
            "status": status,
            "record_id": str(record.id),
            "user_id": str(owner.id),
            "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
        }

    @pytest.mark.parametrize(
        "status, expected_status_code, expected_response_count",
        [("submitted", 422, 0), ("discarded", 201, 1), ("draft", 201, 1)],
    )
    async def test_create_record_response_without_values(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        owner: User,
        owner_auth_header: dict,
        status: str,
        expected_status_code: int,
        expected_response_count: int,
    ):
        record = await RecordFactory.create()
        response_json = {"status": status}

        response = await async_client.post(
            f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
        )

        assert response.status_code == expected_status_code
        assert (await db.execute(select(func.count(Response.id)))).scalar() == expected_response_count

        if expected_status_code == 201:
            response_body = response.json()
            assert await db.get(Response, UUID(response_body["id"]))
            assert response_body == {
                "id": str(UUID(response_body["id"])),
                "values": None,
                "status": status,
                "record_id": str(record.id),
                "user_id": str(owner.id),
                "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
                "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
            }

    @pytest.mark.parametrize("status", [ResponseStatus.submitted, ResponseStatus.discarded, ResponseStatus.draft])
    async def test_create_record_response_with_wrong_values(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict, status: ResponseStatus
    ):
        record = await RecordFactory.create()
        response_json = {"status": status, "values": {"wrong_question": {"value": "wrong value"}}}

        response = await async_client.post(
            f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "found response value for non configured question with name='wrong_question'"
        }
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin, UserRole.annotator])
    async def test_create_record_response_for_user_role(self, async_client: "AsyncClient", db: Session, role: UserRole):
        dataset = await DatasetFactory.create()
        await TextQuestionFactory.create(name="input_ok", dataset=dataset)
        await TextQuestionFactory.create(name="output_ok", dataset=dataset)

        record = await RecordFactory.create(dataset=dataset)
        user = await UserFactory.create(workspaces=[record.dataset.workspace], role=role)
        response_json = {
            "values": {
                "input_ok": {"value": "yes"},
                "output_ok": {"value": "yes"},
            },
            "status": "submitted",
        }

        response = await async_client.post(
            f"/api/v1/records/{record.id}/responses", headers={API_KEY_HEADER_NAME: user.api_key}, json=response_json
        )

        assert response.status_code == 201
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 1

        response_body = response.json()
        assert response_body == {
            "id": str(UUID(response_body["id"])),
            "values": {
                "input_ok": {"value": "yes"},
                "output_ok": {"value": "yes"},
            },
            "status": "submitted",
            "record_id": str(record.id),
            "user_id": str(user.id),
            "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
            "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
        }

    @pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
    async def test_create_record_response_as_restricted_user_from_different_workspace(
        self, async_client: "AsyncClient", db: Session, role: UserRole
    ):
        record = await RecordFactory.create()
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create(workspaces=[workspace], role=role)
        response_json = {
            "values": {
                "input_ok": {"value": "yes"},
                "output_ok": {"value": "yes"},
            },
            "status": "submitted",
        }

        response = await async_client.post(
            f"/api/v1/records/{record.id}/responses", headers={API_KEY_HEADER_NAME: user.api_key}, json=response_json
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    async def test_create_record_response_already_created(
        self, async_client: "AsyncClient", db: "AsyncSession", owner: User, owner_auth_header: dict
    ):
        record = await RecordFactory.create()

        await ResponseFactory.create(record=record, user=owner)

        response = await async_client.post(
            f"/api/v1/records/{record.id}/responses",
            headers=owner_auth_header,
            json={
                "values": {
                    "input_ok": {"value": "yes"},
                    "output_ok": {"value": "yes"},
                },
                "status": "submitted",
            },
        )

        assert response.status_code == 409
        assert response.json() == {
            "detail": f"Response already exists for record with id `{record.id}` and by user with id `{owner.id}`"
        }

        assert (await db.execute(select(func.count(Response.id)))).scalar() == 1

    async def test_create_record_response_with_invalid_values(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        record = await RecordFactory.create()
        response_json = {
            "values": "invalid",
            "status": "submitted",
        }

        response = await async_client.post(
            f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    async def test_create_record_response_with_invalid_status(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        record = await RecordFactory.create()
        response_json = {
            "values": {
                "input_ok": {"value": "yes"},
                "output_ok": {"value": "yes"},
            },
            "status": "invalid",
        }

        response = await async_client.post(
            f"/api/v1/records/{record.id}/responses", headers=owner_auth_header, json=response_json
        )

        assert response.status_code == 422
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    async def test_create_record_response_with_nonexistent_record_id(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        record_id = uuid4()

        await RecordFactory.create()

        response = await async_client.post(
            f"/api/v1/records/{record_id}/responses",
            headers=owner_auth_header,
            json={
                "values": {
                    "input_ok": {"value": "yes"},
                    "output_ok": {"value": "yes"},
                },
                "status": "submitted",
            },
        )

        assert response.status_code == 404
        assert response.json() == {"detail": f"Record with id `{record_id}` not found"}

        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    @pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin, UserRole.owner])
    async def test_get_record_suggestions(self, async_client: "AsyncClient", role: UserRole):
        dataset = await DatasetFactory.create()
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])
        record = await RecordFactory.create(dataset=dataset)
        question_a = await TextQuestionFactory.create(dataset=dataset)
        question_b = await TextQuestionFactory.create(dataset=dataset)
        suggestion_a = await SuggestionFactory.create(
            question=question_a, record=record, value="This is a unit test suggestion"
        )
        suggestion_b = await SuggestionFactory.create(
            question=question_b, record=record, value="This is a another unit test suggestion"
        )

        response = await async_client.get(
            f"/api/v1/records/{record.id}/suggestions", headers={API_KEY_HEADER_NAME: user.api_key}
        )

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "id": str(suggestion_a.id),
                    "question_id": str(question_a.id),
                    "type": None,
                    "score": None,
                    "value": "This is a unit test suggestion",
                    "agent": None,
                    "inserted_at": suggestion_a.inserted_at.isoformat(),
                    "updated_at": suggestion_a.updated_at.isoformat(),
                },
                {
                    "id": str(suggestion_b.id),
                    "question_id": str(question_b.id),
                    "type": None,
                    "score": None,
                    "value": "This is a another unit test suggestion",
                    "agent": None,
                    "inserted_at": suggestion_b.inserted_at.isoformat(),
                    "updated_at": suggestion_b.updated_at.isoformat(),
                },
            ]
        }

    @pytest.mark.parametrize(
        "payload",
        [
            {
                "type": "model",
                "score": 1,
                "value": "This is a unit test suggestion",
                "agent": "unit-test-agent",
            },
            {
                "type": None,
                "score": None,
                "value": "This is a unit test suggestion",
                "agent": None,
            },
        ],
    )
    @pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
    async def test_create_record_suggestion(
        self, async_client: "AsyncClient", db: "AsyncSession", role: UserRole, payload: dict
    ):
        dataset = await DatasetFactory.create()
        question = await TextQuestionFactory.create(dataset=dataset)
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])
        record = await RecordFactory.create(dataset=dataset)

        response = await async_client.put(
            f"/api/v1/records/{record.id}/suggestions",
            headers={API_KEY_HEADER_NAME: user.api_key},
            json={"question_id": str(question.id), **payload},
        )

        assert response.status_code == 201

        response_json = response.json()
        payload.update(
            {
                "inserted_at": datetime.fromisoformat(response_json["inserted_at"]).isoformat(),
                "updated_at": datetime.fromisoformat(response_json["updated_at"]).isoformat(),
            }
        )
        assert response_json == {
            "id": response_json["id"],
            "question_id": str(question.id),
            **payload,
        }

        assert (await db.execute(select(func.count(Suggestion.id)))).scalar() == 1

    async def test_create_record_suggestion_update(
        self, async_client: "AsyncClient", db: "AsyncSession", mock_search_engine: SearchEngine, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        question = await TextQuestionFactory.create(dataset=dataset)
        record = await RecordFactory.create(dataset=dataset)
        suggestion = await SuggestionFactory.create(question=question, record=record)

        response = await async_client.put(
            f"/api/v1/records/{record.id}/suggestions",
            headers=owner_auth_header,
            json={"question_id": str(question.id), "value": "Testing updating a suggestion"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(suggestion.id),
            "question_id": str(question.id),
            "type": None,
            "score": None,
            "value": "Testing updating a suggestion",
            "agent": None,
            "inserted_at": suggestion.inserted_at.isoformat(),
            "updated_at": suggestion.updated_at.isoformat(),
        }

        assert (await db.execute(select(func.count(Suggestion.id)))).scalar() == 1

        mock_search_engine.update_record_suggestion.assert_called_once_with(suggestion)

    @pytest.mark.parametrize(
        "payload",
        [
            {},  # missing value
            {
                "value": {"this": "is not valid response for a TextQuestion"},
            },
        ],
    )
    async def test_create_record_suggestion_not_valid(
        self, async_client: "AsyncClient", owner_auth_header: dict, payload: dict
    ):
        dataset = await DatasetFactory.create()
        question = await TextQuestionFactory.create(dataset=dataset)
        record = await RecordFactory.create(dataset=dataset)

        response = await async_client.put(
            f"/api/v1/records/{record.id}/suggestions",
            headers=owner_auth_header,
            json={"question_id": str(question.id), **payload},
        )

        assert response.status_code == 422

    async def test_create_record_suggestion_for_non_existent_question(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        question_id = uuid4()

        record = await RecordFactory.create()

        response = await async_client.put(
            f"/api/v1/records/{record.id}/suggestions",
            headers=owner_auth_header,
            json={
                "question_id": str(question_id),
                "value": "This is a unit test suggestion",
            },
        )

        assert response.status_code == 422
        assert response.json() == {"detail": f"Question with id `{question_id}` not found"}

    async def test_create_record_suggestion_as_annotator(self, async_client: "AsyncClient"):
        annotator = await UserFactory.create(role=UserRole.annotator)
        record = await RecordFactory.create()

        response = await async_client.put(
            f"/api/v1/records/{record.id}/suggestions",
            headers={API_KEY_HEADER_NAME: annotator.api_key},
            json={"question_id": str(uuid4()), "value": "This is a unit test suggestion"},
        )

        assert response.status_code == 403

    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_delete_record(
        self, async_client: "AsyncClient", db: "AsyncSession", mock_search_engine: "SearchEngine", role: UserRole
    ):
        dataset = await DatasetFactory.create()
        record = await RecordFactory.create(dataset=dataset)
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        response = await async_client.delete(
            f"/api/v1/records/{record.id}", headers={API_KEY_HEADER_NAME: user.api_key}
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(record.id),
            "status": RecordStatus.pending,
            "fields": record.fields,
            "metadata": None,
            "external_id": record.external_id,
            "dataset_id": str(record.dataset_id),
            "inserted_at": record.inserted_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
        }
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 0
        mock_search_engine.delete_records.assert_called_once_with(dataset=dataset, records=[record])

    async def test_delete_record_as_admin_from_another_workspace(self, async_client: "AsyncClient", db: "AsyncSession"):
        dataset = await DatasetFactory.create()
        record = await RecordFactory.create(dataset=dataset)
        user = await UserFactory.create(role=UserRole.admin)

        response = await async_client.delete(
            f"/api/v1/records/{record.id}", headers={API_KEY_HEADER_NAME: user.api_key}
        )

        assert response.status_code == 403
        assert (await db.execute(select(func.count(Record.id)))).scalar() == 1

    async def test_delete_record_as_annotator(self, async_client: "AsyncClient"):
        annotator = await UserFactory.create(role=UserRole.annotator)
        record = await RecordFactory.create()

        response = await async_client.delete(
            f"/api/v1/records/{record.id}", headers={API_KEY_HEADER_NAME: annotator.api_key}
        )

        assert response.status_code == 403

    async def test_delete_record_non_existent(self, async_client: "AsyncClient", owner_auth_header: dict):
        record_id = uuid4()

        response = await async_client.delete(
            f"/api/v1/records/{record_id}",
            headers=owner_auth_header,
        )

        assert response.status_code == 404
        assert response.json() == {"detail": f"Record with id `{record_id}` not found"}

    @pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
    async def test_delete_record_suggestions(
        self, async_client: "AsyncClient", db: "AsyncSession", mock_search_engine: SearchEngine, role: UserRole
    ) -> None:
        dataset = await DatasetFactory.create()
        user = await UserFactory.create(workspaces=[dataset.workspace], role=role)
        record = await RecordFactory.create(dataset=dataset)
        suggestions = await SuggestionFactory.create_batch(10, record=record)
        random_uuids = [str(uuid4()) for _ in range(0, 5)]

        suggestions_ids = [str(suggestion.id) for suggestion in suggestions]

        uuids_str = ",".join(suggestions_ids + random_uuids)

        response = await async_client.delete(
            f"/api/v1/records/{record.id}/suggestions",
            headers={API_KEY_HEADER_NAME: user.api_key},
            params={"ids": uuids_str},
        )

        assert response.status_code == 204
        assert (await db.execute(select(func.count(Suggestion.id)))).scalar() == 0

        expected_calls = [call(suggestion) for suggestion in suggestions]
        mock_search_engine.delete_record_suggestion.assert_has_calls(expected_calls)

    async def test_delete_record_suggestions_with_no_ids(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ) -> None:
        record = await RecordFactory.create()

        response = await async_client.delete(
            f"/api/v1/records/{record.id}/suggestions",
            headers=owner_auth_header,
            params={"ids": ""},
        )

        assert response.status_code == 422

    async def test_delete_record_suggestions_exceeding_limit(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ) -> None:
        record = await RecordFactory.create()
        suggestions = await SuggestionFactory.create_batch(200, record=record)

        suggestions_ids = [str(suggestion.id) for suggestion in suggestions]

        response = await async_client.delete(
            f"/api/v1/records/{record.id}/suggestions",
            headers=owner_auth_header,
            params={"ids": ",".join(suggestions_ids)},
        )

        assert response.status_code == 422

    async def test_delete_record_suggestions_from_another_record(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ) -> None:
        record_a = await RecordFactory.create()
        record_b = await RecordFactory.create()
        suggestions_a = await SuggestionFactory.create_batch(10, record=record_a)
        suggestions_b = await SuggestionFactory.create_batch(10, record=record_b)

        suggestions_a_ids = [str(suggestion.id) for suggestion in suggestions_a]
        suggestions_b_ids = [str(suggestion.id) for suggestion in suggestions_b]

        uuids_str = ",".join(suggestions_a_ids + suggestions_b_ids)

        response = await async_client.delete(
            f"/api/v1/records/{record_a.id}/suggestions",
            headers=owner_auth_header,
            params={"ids": uuids_str},
        )

        assert response.status_code == 204
        assert (await db.execute(select(func.count(Suggestion.id)))).scalar() == 10

    async def test_delete_record_suggestions_as_admin_from_another_workspace(self, async_client: "AsyncClient") -> None:
        record = await RecordFactory.create()
        suggestions = await SuggestionFactory.create_batch(10, record=record)
        user = await UserFactory.create(role=UserRole.admin)

        response = await async_client.delete(
            f"/api/v1/records/{record.id}/suggestions",
            headers={API_KEY_HEADER_NAME: user.api_key},
            params={"ids": ",".join([str(suggestion.id) for suggestion in suggestions])},
        )

        assert response.status_code == 403

    async def test_delete_record_suggestions_as_annotator(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ) -> None:
        record = await RecordFactory.create()
        user = await UserFactory.create(role=UserRole.annotator, workspaces=[record.dataset.workspace])

        response = await async_client.delete(
            f"/api/v1/records/{record.id}/suggestions",
            headers={API_KEY_HEADER_NAME: user.api_key},
            params={"ids": ""},
        )

        assert response.status_code == 403
