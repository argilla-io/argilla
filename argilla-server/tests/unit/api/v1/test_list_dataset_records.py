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

from typing import List, Optional, Tuple, Type, Union
from uuid import uuid4

import pytest
from argilla_server.apis.v1.handlers.datasets.records import LIST_DATASET_RECORDS_LIMIT_DEFAULT
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.enums import RecordInclude, RecordSortField, ResponseStatus, UserRole
from argilla_server.models import Dataset, Question, Record, Response, Suggestion, User, Workspace
from argilla_server.search_engine import (
    FloatMetadataFilter,
    IntegerMetadataFilter,
    MetadataFilter,
    SearchEngine,
    SearchResponseItem,
    SearchResponses,
    SortBy,
    TermsMetadataFilter,
)
from httpx import AsyncClient

from tests.factories import (
    AdminFactory,
    AnnotatorFactory,
    DatasetFactory,
    LabelSelectionQuestionFactory,
    MetadataPropertyFactory,
    RecordFactory,
    ResponseFactory,
    SuggestionFactory,
    TermsMetadataPropertyFactory,
    TextFieldFactory,
    TextQuestionFactory,
    UserFactory,
    VectorFactory,
    VectorSettingsFactory,
    WorkspaceFactory,
)


@pytest.mark.asyncio
class TestSuiteListDatasetRecords:
    @pytest.mark.skip(reason="Factory integration with search engine")
    async def test_list_dataset_records(self, async_client: "AsyncClient", owner_auth_header: dict):
        dataset = await DatasetFactory.create()
        record_a = await RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
        record_b = await RecordFactory.create(
            fields={"record_b": "value_b"}, metadata_={"unit": "test"}, dataset=dataset
        )
        record_c = await RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "total": 3,
            "items": [
                {
                    "id": str(record_a.id),
                    "fields": {"record_a": "value_a"},
                    "metadata": None,
                    "external_id": record_a.external_id,
                    "inserted_at": record_a.inserted_at.isoformat(),
                    "updated_at": record_a.updated_at.isoformat(),
                },
                {
                    "id": str(record_b.id),
                    "fields": {"record_b": "value_b"},
                    "metadata": {"unit": "test"},
                    "external_id": record_b.external_id,
                    "inserted_at": record_b.inserted_at.isoformat(),
                    "updated_at": record_b.updated_at.isoformat(),
                },
                {
                    "id": str(record_c.id),
                    "fields": {"record_c": "value_c"},
                    "metadata": None,
                    "external_id": record_c.external_id,
                    "inserted_at": record_c.inserted_at.isoformat(),
                    "updated_at": record_c.updated_at.isoformat(),
                },
            ],
        }

    @pytest.mark.parametrize(
        "includes",
        [[RecordInclude.responses], [RecordInclude.suggestions], [RecordInclude.responses, RecordInclude.suggestions]],
    )
    async def test_list_dataset_records_with_include(
        self, async_client: "AsyncClient", owner: User, owner_auth_header: dict, includes: List[RecordInclude]
    ):
        workspace = await WorkspaceFactory.create()
        dataset, questions, records, responses, suggestions = await self.create_dataset_with_user_responses(
            owner, workspace
        )
        record_a, record_b, record_c = records
        response_a_user, response_b_user = responses[1], responses[3]
        suggestion_a, suggestion_b = suggestions

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        expected = {
            "total": len(records),
            "items": [
                {
                    "id": str(record_a.id),
                    "fields": {"input": "value_a"},
                    "metadata": None,
                    "external_id": record_a.external_id,
                    "inserted_at": record_a.inserted_at.isoformat(),
                    "updated_at": record_a.updated_at.isoformat(),
                },
                {
                    "id": str(record_b.id),
                    "fields": {"input": "value_b"},
                    "metadata": {"unit": "test"},
                    "external_id": record_b.external_id,
                    "inserted_at": record_b.inserted_at.isoformat(),
                    "updated_at": record_b.updated_at.isoformat(),
                },
                {
                    "id": str(record_c.id),
                    "fields": {"input": "value_c"},
                    "metadata": None,
                    "external_id": record_c.external_id,
                    "inserted_at": record_c.inserted_at.isoformat(),
                    "updated_at": record_c.updated_at.isoformat(),
                },
            ],
        }

        if RecordInclude.responses in includes:
            expected["items"][0]["responses"] = [
                {
                    "id": str(response_a_user.id),
                    "values": None,
                    "status": "discarded",
                    "user_id": str(owner.id),
                    "inserted_at": response_a_user.inserted_at.isoformat(),
                    "updated_at": response_a_user.updated_at.isoformat(),
                }
            ]
            expected["items"][1]["responses"] = [
                {
                    "id": str(response_b_user.id),
                    "values": {
                        "input_ok": {"value": "no"},
                        "output_ok": {"value": "no"},
                    },
                    "status": "submitted",
                    "user_id": str(owner.id),
                    "inserted_at": response_b_user.inserted_at.isoformat(),
                    "updated_at": response_b_user.updated_at.isoformat(),
                },
            ]
            expected["items"][2]["responses"] = []

        if RecordInclude.suggestions in includes:
            expected["items"][0]["suggestions"] = [
                {
                    "id": str(suggestion_a.id),
                    "value": "option-1",
                    "score": None,
                    "agent": None,
                    "type": None,
                    "question_id": str(questions[0].id),
                }
            ]
            expected["items"][1]["suggestions"] = [
                {
                    "id": str(suggestion_b.id),
                    "value": "option-2",
                    "score": 0.75,
                    "agent": "unit-test-agent",
                    "type": "model",
                    "question_id": str(questions[0].id),
                }
            ]
            expected["items"][2]["suggestions"] = []

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/records",
            params={"include": RecordInclude.responses.value},
            headers=owner_auth_header,
        )

        assert response.status_code == 200

    @pytest.mark.skip(reason="Factory integration with search engine")
    async def test_list_dataset_records_with_include_vectors(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        record_a = await RecordFactory.create(dataset=dataset)
        record_b = await RecordFactory.create(dataset=dataset)
        record_c = await RecordFactory.create(dataset=dataset)
        vector_settings_a = await VectorSettingsFactory.create(name="vector-a", dimensions=3, dataset=dataset)
        vector_settings_b = await VectorSettingsFactory.create(name="vector-b", dimensions=2, dataset=dataset)

        await VectorFactory.create(value=[1.0, 2.0, 3.0], vector_settings=vector_settings_a, record=record_a)
        await VectorFactory.create(value=[4.0, 5.0], vector_settings=vector_settings_b, record=record_a)
        await VectorFactory.create(value=[1.0, 2.0], vector_settings=vector_settings_b, record=record_b)

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/records",
            params={"include": RecordInclude.vectors.value},
            headers=owner_auth_header,
        )

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "id": str(record_a.id),
                    "fields": {"text": "This is a text", "sentiment": "neutral"},
                    "metadata": None,
                    "external_id": record_a.external_id,
                    "vectors": {
                        "vector-a": [1.0, 2.0, 3.0],
                        "vector-b": [4.0, 5.0],
                    },
                    "inserted_at": record_a.inserted_at.isoformat(),
                    "updated_at": record_a.updated_at.isoformat(),
                },
                {
                    "id": str(record_b.id),
                    "fields": {"text": "This is a text", "sentiment": "neutral"},
                    "metadata": None,
                    "external_id": record_b.external_id,
                    "vectors": {
                        "vector-b": [1.0, 2.0],
                    },
                    "inserted_at": record_b.inserted_at.isoformat(),
                    "updated_at": record_b.updated_at.isoformat(),
                },
                {
                    "id": str(record_c.id),
                    "fields": {"text": "This is a text", "sentiment": "neutral"},
                    "metadata": None,
                    "external_id": record_c.external_id,
                    "vectors": {},
                    "inserted_at": record_c.inserted_at.isoformat(),
                    "updated_at": record_c.updated_at.isoformat(),
                },
            ],
            "total": 3,
        }

    @pytest.mark.skip(reason="Factory integration with search engine")
    async def test_list_dataset_records_with_include_specific_vectors(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        record_a = await RecordFactory.create(dataset=dataset)
        record_b = await RecordFactory.create(dataset=dataset)
        record_c = await RecordFactory.create(dataset=dataset)
        vector_settings_a = await VectorSettingsFactory.create(name="vector-a", dimensions=3, dataset=dataset)
        vector_settings_b = await VectorSettingsFactory.create(name="vector-b", dimensions=2, dataset=dataset)
        vector_settings_c = await VectorSettingsFactory.create(name="vector-c", dimensions=4, dataset=dataset)

        await VectorFactory.create(value=[1.0, 2.0, 3.0], vector_settings=vector_settings_a, record=record_a)
        await VectorFactory.create(value=[4.0, 5.0], vector_settings=vector_settings_b, record=record_a)
        await VectorFactory.create(value=[6.0, 7.0, 8.0, 9.0], vector_settings=vector_settings_c, record=record_a)
        await VectorFactory.create(value=[1.0, 2.0], vector_settings=vector_settings_b, record=record_b)
        await VectorFactory.create(value=[10.0, 11.0, 12.0, 13.0], vector_settings=vector_settings_c, record=record_b)
        await VectorFactory.create(value=[14.0, 15.0, 16.0, 17.0], vector_settings=vector_settings_c, record=record_c)

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/records",
            params={"include": f"{RecordInclude.vectors.value}:{vector_settings_a.name},{vector_settings_b.name}"},
            headers=owner_auth_header,
        )

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "id": str(record_a.id),
                    "fields": {"text": "This is a text", "sentiment": "neutral"},
                    "metadata": None,
                    "external_id": record_a.external_id,
                    "vectors": {
                        "vector-a": [1.0, 2.0, 3.0],
                        "vector-b": [4.0, 5.0],
                    },
                    "inserted_at": record_a.inserted_at.isoformat(),
                    "updated_at": record_a.updated_at.isoformat(),
                },
                {
                    "id": str(record_b.id),
                    "fields": {"text": "This is a text", "sentiment": "neutral"},
                    "metadata": None,
                    "external_id": record_b.external_id,
                    "vectors": {
                        "vector-b": [1.0, 2.0],
                    },
                    "inserted_at": record_b.inserted_at.isoformat(),
                    "updated_at": record_b.updated_at.isoformat(),
                },
                {
                    "id": str(record_c.id),
                    "fields": {"text": "This is a text", "sentiment": "neutral"},
                    "metadata": None,
                    "external_id": record_c.external_id,
                    "vectors": {},
                    "inserted_at": record_c.inserted_at.isoformat(),
                    "updated_at": record_c.updated_at.isoformat(),
                },
            ],
            "total": 3,
        }

    @pytest.mark.skip(reason="Factory integration with search engine")
    async def test_list_dataset_records_with_offset(self, async_client: "AsyncClient", owner_auth_header: dict):
        dataset = await DatasetFactory.create()
        await RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
        await RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
        record_c = await RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, params={"offset": 2}
        )

        assert response.status_code == 200

        response_body = response.json()
        assert [item["id"] for item in response_body["items"]] == [str(record_c.id)]

    @pytest.mark.skip(reason="Factory integration with search engine")
    async def test_list_dataset_records_with_limit(self, async_client: "AsyncClient", owner_auth_header: dict):
        dataset = await DatasetFactory.create()
        record_a = await RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
        await RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
        await RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, params={"limit": 1}
        )

        assert response.status_code == 200

        response_body = response.json()
        assert [item["id"] for item in response_body["items"]] == [str(record_a.id)]

    @pytest.mark.skip(reason="Factory integration with search engine")
    async def test_list_dataset_records_with_offset_and_limit(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        await RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
        record_c = await RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
        await RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, params={"offset": 1, "limit": 1}
        )

        assert response.status_code == 200

        response_body = response.json()
        assert [item["id"] for item in response_body["items"]] == [str(record_c.id)]

    async def create_records_with_response(
        self,
        num_records: int,
        dataset: Dataset,
        user: User,
        response_status: ResponseStatus,
        response_values: Optional[dict] = None,
    ):
        for record in await RecordFactory.create_batch(size=num_records, dataset=dataset):
            await ResponseFactory.create(record=record, user=user, values=response_values, status=response_status)

    @pytest.mark.parametrize(
        ("property_config", "param_value", "expected_filter_class", "expected_filter_args"),
        [
            (
                {"name": "terms_prop", "settings": {"type": "terms"}},
                "value",
                TermsMetadataFilter,
                dict(values=["value"]),
            ),
            (
                {"name": "terms_prop", "settings": {"type": "terms"}},
                "value1,value2",
                TermsMetadataFilter,
                dict(values=["value1", "value2"]),
            ),
            (
                {"name": "integer_prop", "settings": {"type": "integer"}},
                '{"ge": 10, "le": 20}',
                IntegerMetadataFilter,
                dict(ge=10, le=20),
            ),
            (
                {"name": "integer_prop", "settings": {"type": "integer"}},
                '{"ge": 20}',
                IntegerMetadataFilter,
                dict(ge=20, high=None),
            ),
            (
                {"name": "integer_prop", "settings": {"type": "integer"}},
                '{"le": 20}',
                IntegerMetadataFilter,
                dict(ge=None, le=20),
            ),
            (
                {"name": "float_prop", "settings": {"type": "float"}},
                '{"ge": -1.30, "le": 23.23}',
                FloatMetadataFilter,
                dict(ge=-1.30, le=23.23),
            ),
            (
                {"name": "float_prop", "settings": {"type": "float"}},
                '{"ge": 23.23}',
                FloatMetadataFilter,
                dict(ge=23.23, high=None),
            ),
            (
                {"name": "float_prop", "settings": {"type": "float"}},
                '{"le": 11.32}',
                FloatMetadataFilter,
                dict(ge=None, le=11.32),
            ),
        ],
    )
    async def test_list_dataset_records_with_metadata_filter(
        self,
        async_client: "AsyncClient",
        mock_search_engine: SearchEngine,
        owner: User,
        owner_auth_header: dict,
        property_config: dict,
        param_value: str,
        expected_filter_class: Type[MetadataFilter],
        expected_filter_args: dict,
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, records, _, _ = await self.create_dataset_with_user_responses(owner, workspace)

        metadata_property = await MetadataPropertyFactory.create(
            name=property_config["name"],
            settings=property_config["settings"],
            dataset=dataset,
        )

        mock_search_engine.search.return_value = SearchResponses(
            total=2,
            items=[
                SearchResponseItem(record_id=records[0].id, score=14.2),
                SearchResponseItem(record_id=records[1].id, score=12.2),
            ],
        )

        query_params = {"metadata": [f"{metadata_property.name}:{param_value}"]}
        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/records",
            params=query_params,
            headers=owner_auth_header,
        )
        assert response.status_code == 200

        response_json = response.json()
        assert response_json["total"] == 2

        mock_search_engine.search.assert_called_once_with(
            dataset=dataset,
            query=None,
            metadata_filters=[expected_filter_class(metadata_property=metadata_property, **expected_filter_args)],
            user_response_status_filter=None,
            offset=0,
            limit=LIST_DATASET_RECORDS_LIMIT_DEFAULT,
            sort_by=[SortBy(field=RecordSortField.inserted_at)],
        )

    @pytest.mark.skip(reason="Factory integration with search engine")
    @pytest.mark.parametrize(
        "response_status_filter", ["missing", "pending", "discarded", "submitted", "draft", ["submitted", "draft"]]
    )
    async def test_list_dataset_records_with_response_status_filter(
        self,
        async_client: "AsyncClient",
        owner: "User",
        owner_auth_header: dict,
        response_status_filter: Union[str, List[str]],
    ):
        num_records_per_response_status = 10
        response_values = {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}}

        dataset = await DatasetFactory.create()
        # missing responses
        await RecordFactory.create_batch(size=num_records_per_response_status, dataset=dataset)
        # discarded responses
        await self.create_records_with_response(
            num_records_per_response_status, dataset, owner, ResponseStatus.discarded
        )
        # submitted responses
        await self.create_records_with_response(
            num_records_per_response_status, dataset, owner, ResponseStatus.submitted, response_values
        )
        # drafted responses
        await self.create_records_with_response(
            num_records_per_response_status, dataset, owner, ResponseStatus.draft, response_values
        )

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response_status_filter = (
            [response_status_filter] if isinstance(response_status_filter, str) else response_status_filter
        )
        response_status_filter_url = [
            f"response_status={response_status}" for response_status in response_status_filter
        ]

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/records?{'&'.join(response_status_filter_url)}&include=responses",
            headers=owner_auth_header,
        )

        assert response.status_code == 200
        response_json = response.json()

        assert len(response_json["items"]) == (num_records_per_response_status * len(response_status_filter))

        if "missing" in response_status_filter:
            assert (
                len([record for record in response_json["items"] if len(record["responses"]) == 0])
                >= num_records_per_response_status
            )
        assert all(
            [
                record["responses"][0]["status"] in response_status_filter
                for record in response_json["items"]
                if len(record["responses"]) > 0
            ]
        )

    @pytest.mark.parametrize(
        "sorts",
        [
            [("inserted_at", None)],
            [("inserted_at", "asc")],
            [("inserted_at", "desc")],
            [("updated_at", None)],
            [("updated_at", "asc")],
            [("updated_at", "desc")],
            [("metadata.terms-metadata-property", None)],
            [("metadata.terms-metadata-property", "asc")],
            [("metadata.terms-metadata-property", "desc")],
            [("inserted_at", "asc"), ("updated_at", "desc")],
            [("inserted_at", "desc"), ("updated_at", "asc")],
            [("inserted_at", "asc"), ("metadata.terms-metadata-property", "desc")],
            [("inserted_at", "desc"), ("metadata.terms-metadata-property", "asc")],
            [("updated_at", "asc"), ("metadata.terms-metadata-property", "desc")],
            [("updated_at", "desc"), ("metadata.terms-metadata-property", "asc")],
            [("inserted_at", "asc"), ("updated_at", "desc"), ("metadata.terms-metadata-property", "asc")],
            [("inserted_at", "desc"), ("updated_at", "asc"), ("metadata.terms-metadata-property", "desc")],
            [("inserted_at", "asc"), ("updated_at", "asc"), ("metadata.terms-metadata-property", "desc")],
        ],
    )
    async def test_list_dataset_records_with_sort_by(
        self,
        async_client: "AsyncClient",
        mock_search_engine: SearchEngine,
        owner: "User",
        owner_auth_header: dict,
        sorts: List[Tuple[str, Union[str, None]]],
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, records, _, _ = await self.create_dataset_with_user_responses(owner, workspace)

        expected_sorts_by = []
        for field, order in sorts:
            if field not in ("inserted_at", "updated_at"):
                field = await TermsMetadataPropertyFactory.create(name=field.split(".")[-1], dataset=dataset)
            expected_sorts_by.append(SortBy(field=field, order=order or "asc"))

        mock_search_engine.search.return_value = SearchResponses(
            total=2,
            items=[
                SearchResponseItem(record_id=records[0].id, score=14.2),
                SearchResponseItem(record_id=records[1].id, score=12.2),
            ],
        )

        query_params = {
            "sort_by": [f"{field}:{order}" if order is not None else f"{field}:asc" for field, order in sorts]
        }

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/records",
            params=query_params,
            headers=owner_auth_header,
        )
        assert response.status_code == 200
        assert response.json()["total"] == 2

        mock_search_engine.search.assert_called_once_with(
            dataset=dataset,
            query=None,
            metadata_filters=[],
            user_response_status_filter=None,
            offset=0,
            limit=LIST_DATASET_RECORDS_LIMIT_DEFAULT,
            sort_by=expected_sorts_by,
        )

    async def test_list_dataset_records_with_sort_by_with_wrong_sort_order_value(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/records", params={"sort_by": "inserted_at:wrong"}, headers=owner_auth_header
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": "Provided sort order in 'sort_by' query param 'wrong' for field 'inserted_at' is not valid."
        }

    async def test_list_dataset_records_with_sort_by_with_non_existent_metadata_property(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/records",
            params={"sort_by": "metadata.i-do-not-exist:asc"},
            headers=owner_auth_header,
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": f"Provided metadata property in 'sort_by' query param 'i-do-not-exist' not found in dataset with '{dataset.id}'."
        }

    async def test_list_dataset_records_with_sort_by_with_invalid_field(
        self, async_client: "AsyncClient", owner: "User", owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, _, _, _ = await self.create_dataset_with_user_responses(owner, workspace)

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/records",
            params={"sort_by": "not-valid"},
            headers=owner_auth_header,
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": "Provided sort field in 'sort_by' query param 'not-valid' is not valid. "
            "It must be either 'inserted_at', 'updated_at' or `metadata.metadata-property-name`"
        }

    async def test_list_dataset_records_without_authentication(self, async_client: "AsyncClient"):
        dataset = await DatasetFactory.create()

        response = await async_client.get(f"/api/v1/datasets/{dataset.id}/records")

        assert response.status_code == 401

    async def test_list_dataset_records_as_admin(self, async_client: "AsyncClient"):
        workspace = await WorkspaceFactory.create()
        admin = await AdminFactory.create(workspaces=[workspace])
        dataset = await DatasetFactory.create(workspace=workspace)

        await RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
        await RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
        await RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/records", headers={API_KEY_HEADER_NAME: admin.api_key}
        )
        assert response.status_code == 200

    async def test_list_dataset_records_as_annotator(self, async_client: "AsyncClient"):
        workspace = await WorkspaceFactory.create()
        annotator = await AnnotatorFactory.create(workspaces=[workspace])
        dataset = await DatasetFactory.create(workspace=workspace)

        await RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
        await RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
        await RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(
            f"/api/v1/datasets/{dataset.id}/records", headers={API_KEY_HEADER_NAME: annotator.api_key}
        )
        assert response.status_code == 403

    async def create_dataset_with_user_responses(
        self, user: User, workspace: Workspace
    ) -> Tuple[Dataset, List[Question], List[Record], List[Response], List[Suggestion]]:
        dataset = await DatasetFactory.create(workspace=workspace)
        await TextFieldFactory.create(name="input", dataset=dataset)
        await TextFieldFactory.create(name="output", dataset=dataset)

        annotator = await AnnotatorFactory.create(workspaces=[dataset.workspace])

        questions = [
            await LabelSelectionQuestionFactory.create(dataset=dataset),
            await TextQuestionFactory.create(name="input_ok", dataset=dataset),
            await TextQuestionFactory.create(name="output_ok", dataset=dataset),
        ]

        records = [
            await RecordFactory.create(fields={"input": "input_a", "output": "output_a"}, dataset=dataset),
            await RecordFactory.create(
                fields={"input": "input_b", "output": "output_b"}, metadata_={"unit": "test"}, dataset=dataset
            ),
            await RecordFactory.create(fields={"input": "input_c", "output": "output_c"}, dataset=dataset),
        ]

        responses = [
            await ResponseFactory.create(
                values={
                    "input_ok": {"value": "yes"},
                    "output_ok": {"value": "yes"},
                },
                record=records[0],
                user=annotator,
            ),
            await ResponseFactory.create(status="discarded", record=records[0], user=user),
            await ResponseFactory.create(
                values={
                    "input_ok": {"value": "yes"},
                    "output_ok": {"value": "no"},
                },
                record=records[1],
                user=annotator,
            ),
            await ResponseFactory.create(
                values={
                    "input_ok": {"value": "no"},
                    "output_ok": {"value": "no"},
                },
                record=records[1],
                user=user,
            ),
            await ResponseFactory.create(
                values={
                    "input_ok": {"value": "yes"},
                    "output_ok": {"value": "yes"},
                },
                record=records[1],
            ),
        ]

        # Add some responses from other users
        await ResponseFactory.create_batch(10, record=records[0], status=ResponseStatus.submitted)

        suggestions = [
            await SuggestionFactory.create(record=records[0], question=questions[0], value="option-1"),
            await SuggestionFactory.create(
                record=records[1],
                question=questions[0],
                value="option-2",
                score=0.75,
                agent="unit-test-agent",
                type="model",
            ),
        ]

        return dataset, questions, records, responses, suggestions

    @pytest.mark.skip(reason="Factory integration with search engine")
    async def test_list_current_user_dataset_records(
        self, async_client: "AsyncClient", owner: User, owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, records, _, _ = await self.create_dataset_with_user_responses(owner, workspace)
        record_a, record_b, record_c = records

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(f"/api/v1/me/datasets/{dataset.id}/records", headers=owner_auth_header)

        assert response.status_code == 200
        assert response.json() == {
            "total": 3,
            "items": [
                {
                    "id": str(record_a.id),
                    "fields": {"input": "input_a", "output": "output_a"},
                    "metadata": None,
                    "external_id": record_a.external_id,
                    "inserted_at": record_a.inserted_at.isoformat(),
                    "updated_at": record_a.updated_at.isoformat(),
                },
                {
                    "id": str(record_b.id),
                    "fields": {"input": "input_b", "output": "output_b"},
                    "metadata": {"unit": "test"},
                    "external_id": record_b.external_id,
                    "inserted_at": record_b.inserted_at.isoformat(),
                    "updated_at": record_b.updated_at.isoformat(),
                },
                {
                    "id": str(record_c.id),
                    "fields": {"input": "input_c", "output": "output_c"},
                    "metadata": None,
                    "external_id": record_c.external_id,
                    "inserted_at": record_c.inserted_at.isoformat(),
                    "updated_at": record_c.updated_at.isoformat(),
                },
            ],
        }

    @pytest.mark.skip(reason="Factory integration with search engine")
    @pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin, UserRole.owner])
    @pytest.mark.parametrize(
        "includes",
        [[RecordInclude.responses], [RecordInclude.suggestions], [RecordInclude.responses, RecordInclude.suggestions]],
    )
    async def test_list_current_user_dataset_records_with_include(
        self, async_client: "AsyncClient", role: UserRole, includes: List[RecordInclude]
    ):
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create(workspaces=[workspace], role=role)
        dataset, questions, records, responses, suggestions = await self.create_dataset_with_user_responses(
            user, workspace
        )
        record_a, record_b, record_c = records
        response_a_user, response_b_user = responses[1], responses[3]
        suggestion_a, suggestion_b = suggestions

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        params = [("include", include.value) for include in includes]
        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/records", params=params, headers={API_KEY_HEADER_NAME: user.api_key}
        )

        expected = {
            "total": 3,
            "items": [
                {
                    "id": str(record_a.id),
                    "fields": {"input": "input_a", "output": "output_a"},
                    "metadata": None,
                    "external_id": record_a.external_id,
                    "inserted_at": record_a.inserted_at.isoformat(),
                    "updated_at": record_a.updated_at.isoformat(),
                },
                {
                    "id": str(record_b.id),
                    "fields": {"input": "input_b", "output": "output_b"},
                    "metadata": {"unit": "test"},
                    "external_id": record_b.external_id,
                    "inserted_at": record_b.inserted_at.isoformat(),
                    "updated_at": record_b.updated_at.isoformat(),
                },
                {
                    "id": str(record_c.id),
                    "fields": {"input": "input_c", "output": "output_c"},
                    "metadata": None,
                    "external_id": record_c.external_id,
                    "inserted_at": record_c.inserted_at.isoformat(),
                    "updated_at": record_c.updated_at.isoformat(),
                },
            ],
        }

        if RecordInclude.responses in includes:
            expected["items"][0]["responses"] = [
                {
                    "id": str(response_a_user.id),
                    "values": None,
                    "status": "discarded",
                    "user_id": str(user.id),
                    "inserted_at": response_a_user.inserted_at.isoformat(),
                    "updated_at": response_a_user.updated_at.isoformat(),
                }
            ]
            expected["items"][1]["responses"] = [
                {
                    "id": str(response_b_user.id),
                    "values": {
                        "input_ok": {"value": "no"},
                        "output_ok": {"value": "no"},
                    },
                    "status": "submitted",
                    "user_id": str(user.id),
                    "inserted_at": response_b_user.inserted_at.isoformat(),
                    "updated_at": response_b_user.updated_at.isoformat(),
                },
            ]
            expected["items"][2]["responses"] = []

        if RecordInclude.suggestions in includes:
            expected["items"][0]["suggestions"] = [
                {
                    "id": str(suggestion_a.id),
                    "value": "option-1",
                    "score": None,
                    "agent": None,
                    "type": None,
                    "question_id": str(questions[0].id),
                }
            ]
            expected["items"][1]["suggestions"] = [
                {
                    "id": str(suggestion_b.id),
                    "value": "option-2",
                    "score": 0.75,
                    "agent": "unit-test-agent",
                    "type": "model",
                    "question_id": str(questions[0].id),
                }
            ]
            expected["items"][2]["suggestions"] = []

        assert response.status_code == 200
        assert response.json() == expected

    @pytest.mark.skip(reason="Factory integration with search engine")
    async def test_list_current_user_dataset_records_with_include_vectors(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        record_a = await RecordFactory.create(dataset=dataset)
        record_b = await RecordFactory.create(dataset=dataset)
        record_c = await RecordFactory.create(dataset=dataset)
        vector_settings_a = await VectorSettingsFactory.create(name="vector-a", dimensions=3, dataset=dataset)
        vector_settings_b = await VectorSettingsFactory.create(name="vector-b", dimensions=2, dataset=dataset)

        await VectorFactory.create(value=[1.0, 2.0, 3.0], vector_settings=vector_settings_a, record=record_a)
        await VectorFactory.create(value=[4.0, 5.0], vector_settings=vector_settings_b, record=record_a)
        await VectorFactory.create(value=[1.0, 2.0], vector_settings=vector_settings_b, record=record_b)

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/records",
            params={"include": RecordInclude.vectors.value},
            headers=owner_auth_header,
        )

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "id": str(record_a.id),
                    "fields": {"text": "This is a text", "sentiment": "neutral"},
                    "metadata": None,
                    "external_id": record_a.external_id,
                    "vectors": {
                        "vector-a": [1.0, 2.0, 3.0],
                        "vector-b": [4.0, 5.0],
                    },
                    "inserted_at": record_a.inserted_at.isoformat(),
                    "updated_at": record_a.updated_at.isoformat(),
                },
                {
                    "id": str(record_b.id),
                    "fields": {"text": "This is a text", "sentiment": "neutral"},
                    "metadata": None,
                    "external_id": record_b.external_id,
                    "vectors": {
                        "vector-b": [1.0, 2.0],
                    },
                    "inserted_at": record_b.inserted_at.isoformat(),
                    "updated_at": record_b.updated_at.isoformat(),
                },
                {
                    "id": str(record_c.id),
                    "fields": {"text": "This is a text", "sentiment": "neutral"},
                    "metadata": None,
                    "external_id": record_c.external_id,
                    "vectors": {},
                    "inserted_at": record_c.inserted_at.isoformat(),
                    "updated_at": record_c.updated_at.isoformat(),
                },
            ],
            "total": 3,
        }

    @pytest.mark.skip(reason="Factory integration with search engine")
    async def test_list_current_user_dataset_records_with_include_specific_vectors(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        record_a = await RecordFactory.create(dataset=dataset)
        record_b = await RecordFactory.create(dataset=dataset)
        record_c = await RecordFactory.create(dataset=dataset)
        vector_settings_a = await VectorSettingsFactory.create(name="vector-a", dimensions=3, dataset=dataset)
        vector_settings_b = await VectorSettingsFactory.create(name="vector-b", dimensions=2, dataset=dataset)
        vector_settings_c = await VectorSettingsFactory.create(name="vector-c", dimensions=4, dataset=dataset)

        await VectorFactory.create(value=[1.0, 2.0, 3.0], vector_settings=vector_settings_a, record=record_a)
        await VectorFactory.create(value=[4.0, 5.0], vector_settings=vector_settings_b, record=record_a)
        await VectorFactory.create(value=[6.0, 7.0, 8.0, 9.0], vector_settings=vector_settings_c, record=record_a)
        await VectorFactory.create(value=[1.0, 2.0], vector_settings=vector_settings_b, record=record_b)
        await VectorFactory.create(value=[10.0, 11.0, 12.0, 13.0], vector_settings=vector_settings_c, record=record_b)
        await VectorFactory.create(value=[14.0, 15.0, 16.0, 17.0], vector_settings=vector_settings_c, record=record_c)

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/records",
            params={"include": f"{RecordInclude.vectors.value}:{vector_settings_a.name},{vector_settings_b.name}"},
            headers=owner_auth_header,
        )

        assert response.status_code == 200
        assert response.json() == {
            "items": [
                {
                    "id": str(record_a.id),
                    "fields": {"text": "This is a text", "sentiment": "neutral"},
                    "metadata": None,
                    "external_id": record_a.external_id,
                    "vectors": {
                        "vector-a": [1.0, 2.0, 3.0],
                        "vector-b": [4.0, 5.0],
                    },
                    "inserted_at": record_a.inserted_at.isoformat(),
                    "updated_at": record_a.updated_at.isoformat(),
                },
                {
                    "id": str(record_b.id),
                    "fields": {"text": "This is a text", "sentiment": "neutral"},
                    "metadata": None,
                    "external_id": record_b.external_id,
                    "vectors": {
                        "vector-b": [1.0, 2.0],
                    },
                    "inserted_at": record_b.inserted_at.isoformat(),
                    "updated_at": record_b.updated_at.isoformat(),
                },
                {
                    "id": str(record_c.id),
                    "fields": {"text": "This is a text", "sentiment": "neutral"},
                    "metadata": None,
                    "external_id": record_c.external_id,
                    "vectors": {},
                    "inserted_at": record_c.inserted_at.isoformat(),
                    "updated_at": record_c.updated_at.isoformat(),
                },
            ],
            "total": 3,
        }

    @pytest.mark.skip(reason="Factory integration with search engine")
    async def test_list_current_user_dataset_records_with_offset(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        await RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
        await RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
        record_c = await RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/records", headers=owner_auth_header, params={"offset": 2}
        )

        assert response.status_code == 200

        response_body = response.json()
        assert [item["id"] for item in response_body["items"]] == [str(record_c.id)]

    @pytest.mark.skip(reason="Factory integration with search engine")
    async def test_list_current_user_dataset_records_with_limit(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        record_a = await RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
        await RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
        await RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/records", headers=owner_auth_header, params={"limit": 1}
        )

        assert response.status_code == 200

        response_body = response.json()
        assert [item["id"] for item in response_body["items"]] == [str(record_a.id)]

    @pytest.mark.skip(reason="Factory integration with search engine")
    async def test_list_current_user_dataset_records_with_offset_and_limit(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()
        await RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
        record_c = await RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
        await RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/records", headers=owner_auth_header, params={"offset": 1, "limit": 1}
        )

        assert response.status_code == 200

        response_body = response.json()
        assert [item["id"] for item in response_body["items"]] == [str(record_c.id)]

    @pytest.mark.parametrize(
        ("property_config", "param_value", "expected_filter_class", "expected_filter_args"),
        [
            (
                {"name": "terms_prop", "settings": {"type": "terms"}},
                "value",
                TermsMetadataFilter,
                dict(values=["value"]),
            ),
            (
                {"name": "terms_prop", "settings": {"type": "terms"}},
                "value1,value2",
                TermsMetadataFilter,
                dict(values=["value1", "value2"]),
            ),
            (
                {"name": "integer_prop", "settings": {"type": "integer"}},
                '{"ge": 10, "le": 20}',
                IntegerMetadataFilter,
                dict(ge=10, le=20),
            ),
            (
                {"name": "integer_prop", "settings": {"type": "integer"}},
                '{"ge": 20}',
                IntegerMetadataFilter,
                dict(ge=20, le=None),
            ),
            (
                {"name": "integer_prop", "settings": {"type": "integer"}},
                '{"le": 20}',
                IntegerMetadataFilter,
                dict(ge=None, le=20),
            ),
            (
                {"name": "float_prop", "settings": {"type": "float"}},
                '{"ge": -1.30, "le": 23.23}',
                FloatMetadataFilter,
                dict(ge=-1.30, le=23.23),
            ),
            (
                {"name": "float_prop", "settings": {"type": "float"}},
                '{"ge": 23.23}',
                FloatMetadataFilter,
                dict(ge=23.23, le=None),
            ),
            (
                {"name": "float_prop", "settings": {"type": "float"}},
                '{"le": 11.32}',
                FloatMetadataFilter,
                dict(ge=None, le=11.32),
            ),
        ],
    )
    async def test_list_current_user_dataset_records_with_metadata_filter(
        self,
        async_client: "AsyncClient",
        mock_search_engine: SearchEngine,
        owner: User,
        owner_auth_header: dict,
        property_config: dict,
        param_value: str,
        expected_filter_class: Type[MetadataFilter],
        expected_filter_args: dict,
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, records, _, _ = await self.create_dataset_with_user_responses(owner, workspace)

        metadata_property = await MetadataPropertyFactory.create(
            name=property_config["name"],
            settings=property_config["settings"],
            dataset=dataset,
        )

        mock_search_engine.search.return_value = SearchResponses(
            total=2,
            items=[
                SearchResponseItem(record_id=records[0].id, score=14.2),
                SearchResponseItem(record_id=records[1].id, score=12.2),
            ],
        )

        query_params = {"metadata": [f"{metadata_property.name}:{param_value}"]}
        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/records",
            params=query_params,
            headers=owner_auth_header,
        )
        assert response.status_code == 200

        response_json = response.json()
        assert response_json["total"] == 2

        mock_search_engine.search.assert_called_once_with(
            dataset=dataset,
            query=None,
            metadata_filters=[expected_filter_class(metadata_property=metadata_property, **expected_filter_args)],
            user_response_status_filter=None,
            offset=0,
            limit=LIST_DATASET_RECORDS_LIMIT_DEFAULT,
            sort_by=None,
            user_id=owner.id,
        )

    @pytest.mark.skip(reason="Factory integration with search engine")
    @pytest.mark.parametrize("response_status_filter", ["missing", "pending", "discarded", "submitted", "draft"])
    async def test_list_current_user_dataset_records_with_response_status_filter(
        self, async_client: "AsyncClient", owner: "User", owner_auth_header: dict, response_status_filter: str
    ):
        num_responses_per_status = 10
        response_values = {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}}

        dataset = await DatasetFactory.create()
        # missing responses
        await RecordFactory.create_batch(size=num_responses_per_status, dataset=dataset)
        # discarded responses
        await self.create_records_with_response(num_responses_per_status, dataset, owner, ResponseStatus.discarded)
        # submitted responses
        await self.create_records_with_response(
            num_responses_per_status, dataset, owner, ResponseStatus.submitted, response_values
        )
        # drafted responses
        await self.create_records_with_response(
            num_responses_per_status, dataset, owner, ResponseStatus.draft, response_values
        )

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/records?response_status={response_status_filter}&include=responses",
            headers=owner_auth_header,
        )

        assert response.status_code == 200
        response_json = response.json()

        assert len(response_json["items"]) == num_responses_per_status

        if response_status_filter in ["missing", "pending"]:
            assert all([len(record["responses"]) == 0 for record in response_json["items"]])
        else:
            assert all(
                [record["responses"][0]["status"] == response_status_filter for record in response_json["items"]]
            )

    @pytest.mark.parametrize(
        "sorts",
        [
            [("inserted_at", None)],
            [("inserted_at", "asc")],
            [("inserted_at", "desc")],
            [("updated_at", None)],
            [("updated_at", "asc")],
            [("updated_at", "desc")],
            [("metadata.terms-metadata-property", None)],
            [("metadata.terms-metadata-property", "asc")],
            [("metadata.terms-metadata-property", "desc")],
            [("inserted_at", "asc"), ("updated_at", "desc")],
            [("inserted_at", "desc"), ("updated_at", "asc")],
            [("inserted_at", "asc"), ("metadata.terms-metadata-property", "desc")],
            [("inserted_at", "desc"), ("metadata.terms-metadata-property", "asc")],
            [("updated_at", "asc"), ("metadata.terms-metadata-property", "desc")],
            [("updated_at", "desc"), ("metadata.terms-metadata-property", "asc")],
            [("inserted_at", "asc"), ("updated_at", "desc"), ("metadata.terms-metadata-property", "asc")],
            [("inserted_at", "desc"), ("updated_at", "asc"), ("metadata.terms-metadata-property", "desc")],
            [("inserted_at", "asc"), ("updated_at", "asc"), ("metadata.terms-metadata-property", "desc")],
        ],
    )
    async def test_list_current_user_dataset_records_with_sort_by(
        self,
        async_client: "AsyncClient",
        mock_search_engine: SearchEngine,
        owner: "User",
        owner_auth_header: dict,
        sorts: List[Tuple[str, Union[str, None]]],
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, records, _, _ = await self.create_dataset_with_user_responses(owner, workspace)

        expected_sorts_by = []
        for field, order in sorts:
            if field not in ("inserted_at", "updated_at"):
                field = await TermsMetadataPropertyFactory.create(name=field.split(".")[-1], dataset=dataset)
            expected_sorts_by.append(SortBy(field=field, order=order or "asc"))

        mock_search_engine.search.return_value = SearchResponses(
            total=2,
            items=[
                SearchResponseItem(record_id=records[0].id, score=14.2),
                SearchResponseItem(record_id=records[1].id, score=12.2),
            ],
        )

        query_params = {
            "sort_by": [f"{field}:{order}" if order is not None else f"{field}:asc" for field, order in sorts]
        }

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/records",
            params=query_params,
            headers=owner_auth_header,
        )
        assert response.status_code == 200
        assert response.json()["total"] == 2

        mock_search_engine.search.assert_called_once_with(
            dataset=dataset,
            query=None,
            metadata_filters=[],
            user_response_status_filter=None,
            offset=0,
            limit=LIST_DATASET_RECORDS_LIMIT_DEFAULT,
            sort_by=expected_sorts_by,
            user_id=owner.id,
        )

    async def test_list_current_user_dataset_records_with_sort_by_with_wrong_sort_order_value(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/records",
            params={"sort_by": "inserted_at:wrong"},
            headers=owner_auth_header,
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": "Provided sort order in 'sort_by' query param 'wrong' for field 'inserted_at' is not valid."
        }

    async def test_list_current_user_dataset_records_with_sort_by_with_non_existent_metadata_property(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create()

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/records",
            params={"sort_by": "metadata.i-do-not-exist:asc"},
            headers=owner_auth_header,
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": f"Provided metadata property in 'sort_by' query param 'i-do-not-exist' not found in dataset with '{dataset.id}'."
        }

    async def test_list_current_user_dataset_records_with_sort_by_with_invalid_field(
        self, async_client: "AsyncClient", owner: "User", owner_auth_header: dict
    ):
        workspace = await WorkspaceFactory.create()
        dataset, _, _, _, _ = await self.create_dataset_with_user_responses(owner, workspace)

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/records",
            params={"sort_by": "not-valid"},
            headers=owner_auth_header,
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": "Provided sort field in 'sort_by' query param 'not-valid' is not valid. It must be either 'inserted_at', 'updated_at' or `metadata.metadata-property-name`"
        }

    async def test_list_current_user_dataset_records_without_authentication(self, async_client: "AsyncClient"):
        dataset = await DatasetFactory.create()

        response = await async_client.get(f"/api/v1/me/datasets/{dataset.id}/records")

        assert response.status_code == 401

    @pytest.mark.skip(reason="Factory integration with search engine")
    @pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
    async def test_list_current_user_dataset_records_as_restricted_user(
        self, async_client: "AsyncClient", role: UserRole
    ):
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create(workspaces=[workspace], role=role)
        dataset = await DatasetFactory.create(workspace=workspace)
        record_a = await RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
        record_b = await RecordFactory.create(
            fields={"record_b": "value_b"}, metadata_={"unit": "test"}, dataset=dataset
        )
        record_c = await RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)
        expected_records = [record_a, record_b, record_c]

        other_dataset = await DatasetFactory.create()
        await RecordFactory.create_batch(size=2, dataset=other_dataset)

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/records", headers={API_KEY_HEADER_NAME: user.api_key}
        )

        assert response.status_code == 200

        response_items = response.json()["items"]

        for expected_record in expected_records:
            found_items = [item for item in response_items if item["id"] == str(expected_record.id)]
            assert found_items, expected_record

            assert found_items[0] == {
                "id": str(expected_record.id),
                "fields": expected_record.fields,
                "metadata": expected_record.metadata_,
                "external_id": expected_record.external_id,
                "inserted_at": expected_record.inserted_at.isoformat(),
                "updated_at": expected_record.updated_at.isoformat(),
            }

    @pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
    async def test_list_current_user_dataset_records_as_restricted_user_from_different_workspace(
        self, async_client: "AsyncClient", role: UserRole
    ):
        dataset = await DatasetFactory.create()
        workspace = await WorkspaceFactory.create()
        user = await UserFactory.create(workspaces=[workspace], role=role)

        response = await async_client.get(
            f"/api/v1/me/datasets/{dataset.id}/records", headers={API_KEY_HEADER_NAME: user.api_key}
        )

        assert response.status_code == 403

    async def test_list_current_user_dataset_records_with_nonexistent_dataset_id(
        self, async_client: "AsyncClient", owner_auth_header: dict
    ):
        await DatasetFactory.create()

        response = await async_client.get(f"/api/v1/me/datasets/{uuid4()}/records", headers=owner_auth_header)

        assert response.status_code == 404
