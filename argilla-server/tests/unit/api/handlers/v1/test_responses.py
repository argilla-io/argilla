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
from typing import TYPE_CHECKING, Any, Type
from uuid import uuid4

import pytest
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.models import DatasetStatus, Response, ResponseStatus, UserRole
from argilla_server.search_engine import SearchEngine
from sqlalchemy import func, select

from tests.factories import (
    AdminFactory,
    AnnotatorFactory,
    DatasetFactory,
    LabelSelectionQuestionFactory,
    MultiLabelSelectionQuestionFactory,
    RankingQuestionFactory,
    RatingQuestionFactory,
    RecordFactory,
    ResponseFactory,
    TextQuestionFactory,
    UserFactory,
    WorkspaceFactory,
)

if TYPE_CHECKING:
    from argilla_server.models import User
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

    from tests.factories import QuestionFactory


@pytest.mark.asyncio
class TestSuiteResponses:
    @pytest.mark.parametrize(
        "response_json",
        [
            {
                "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
                "status": "submitted",
            },
            {
                "values": {"input_ok": {"value": "yes"}},
                "status": "submitted",
            },
            {
                "values": {"output_ok": {"value": "yes"}},
                "status": "draft",
            },
        ],
    )
    async def test_update_response(
        self,
        async_client: "AsyncClient",
        db: "AsyncSession",
        mock_search_engine: SearchEngine,
        owner_auth_header: dict,
        response_json: dict,
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        await TextQuestionFactory.create(name="input_ok", dataset=dataset, required=True)
        await TextQuestionFactory.create(name="output_ok", dataset=dataset)
        record = await RecordFactory.create(dataset=dataset)

        response = await ResponseFactory.create(
            record=record,
            values={"input_ok": {"value": "no"}, "output_ok": {"value": "no"}},
            status=ResponseStatus.submitted,
        )

        dataset_previous_last_activity_at = dataset.last_activity_at
        dataset_previous_updated_at = dataset.updated_at

        resp = await async_client.put(f"/api/v1/responses/{response.id}", headers=owner_auth_header, json=response_json)

        assert resp.status_code == 200
        assert (await db.get(Response, response.id)).values == response_json["values"]

        resp_body = resp.json()
        assert resp_body == {
            "id": str(response.id),
            "values": response_json["values"],
            "status": response_json["status"],
            "record_id": str(response.record_id),
            "user_id": str(response.user_id),
            "inserted_at": response.inserted_at.isoformat(),
            "updated_at": datetime.fromisoformat(resp_body["updated_at"]).isoformat(),
        }

        await db.refresh(dataset)
        assert dataset.last_activity_at > dataset_previous_last_activity_at
        assert dataset.updated_at == dataset_previous_updated_at

        mock_search_engine.update_record_response.assert_called_once_with(response)

    async def test_update_response_without_authentication(self, async_client: "AsyncClient", db: "AsyncSession"):
        response = await ResponseFactory.create(
            values={
                "input_ok": {"value": "no"},
                "output_ok": {"value": "no"},
            },
            status="submitted",
        )
        response_json = {
            "values": {
                "input_ok": {"value": "yes"},
                "output_ok": {"value": "yes"},
            },
            "status": "submitted",
        }

        resp = await async_client.put(f"/api/v1/responses/{response.id}", json=response_json)

        assert resp.status_code == 401
        assert (await db.get(Response, response.id)).values == {
            "input_ok": {"value": "no"},
            "output_ok": {"value": "no"},
        }

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
    async def test_update_response_to_submitted_status(
        self,
        async_client: "AsyncClient",
        QuestionFactory: Type["QuestionFactory"],
        response_value: ResponseStatus,
        owner: "User",
        owner_auth_header: dict,
    ):
        question = await QuestionFactory.create()
        record = await RecordFactory.create(dataset=question.dataset)
        response = await ResponseFactory.create(record=record, user=owner, status=ResponseStatus.draft)

        response_json = {"values": {question.name: {"value": response_value}}, "status": ResponseStatus.submitted}
        resp = await async_client.put(f"/api/v1/responses/{response.id}", headers=owner_auth_header, json=response_json)

        assert resp.status_code == 200
        assert resp.json() == {
            "id": str(response.id),
            "record_id": str(record.id),
            "values": {question.name: {"value": response_value}},
            "status": ResponseStatus.submitted.value,
            "user_id": str(owner.id),
            "inserted_at": response.inserted_at.isoformat(),
            "updated_at": response.updated_at.isoformat(),
        }

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
            (
                RankingQuestionFactory,
                [
                    {"value": "completion-a", "rank": 1},
                    {"value": "completion-b", "rank": None},
                    {"value": "completion-c", "rank": None},
                ],
            ),
        ],
    )
    @pytest.mark.parametrize("response_status", [ResponseStatus.draft, ResponseStatus.discarded])
    async def test_update_response_to_non_submitted_status(
        self,
        async_client: "AsyncClient",
        QuestionFactory: Type["QuestionFactory"],
        response_value: Any,
        response_status: ResponseStatus,
        owner: "User",
        owner_auth_header: dict,
    ):
        question = await QuestionFactory.create()
        record = await RecordFactory.create(dataset=question.dataset)
        response = await ResponseFactory.create(record=record, user=owner, status=ResponseStatus.submitted)

        response_json = {"values": {question.name: {"value": response_value}}, "status": response_status}
        resp = await async_client.put(f"/api/v1/responses/{response.id}", headers=owner_auth_header, json=response_json)

        assert resp.status_code == 200
        assert resp.json() == {
            "id": str(response.id),
            "record_id": str(record.id),
            "values": {question.name: {"value": response_value}},
            "status": response_status.value,
            "user_id": str(owner.id),
            "inserted_at": response.inserted_at.isoformat(),
            "updated_at": response.updated_at.isoformat(),
        }

    @pytest.mark.parametrize(
        "QuestionFactory, response_value",
        [
            (TextQuestionFactory, False),
            (RatingQuestionFactory, "wrong-rating-value"),
            (LabelSelectionQuestionFactory, False),
            (MultiLabelSelectionQuestionFactory, "wrong-type"),
            (MultiLabelSelectionQuestionFactory, ["option4", "option5"]),
            (MultiLabelSelectionQuestionFactory, []),
            (RankingQuestionFactory, "wrong-type"),
            (RankingQuestionFactory, []),
            (RankingQuestionFactory, [{"value": "completion-b", "rank": 1}]),
            (
                RankingQuestionFactory,
                [
                    {"value": "completion-b", "rank": 1},
                    {"value": "completion-c", "rank": 2},
                    {"value": "completion-a", "rank": 3},
                    {"value": "completion-z", "rank": 4},
                ],
            ),
            (
                RankingQuestionFactory,
                [
                    {"value": "completion-b", "rank": 1},
                    {"value": "completion-c", "rank": 2},
                    {"value": "completion-a", "rank": 4},
                ],
            ),
            (
                RankingQuestionFactory,
                [
                    {"value": "completion-z", "rank": 1},
                    {"value": "completion-c", "rank": 2},
                    {"value": "completion-a", "rank": 3},
                ],
            ),
            (
                RankingQuestionFactory,
                [
                    {"value": "completion-a", "rank": 1},
                    {"value": "completion-c", "rank": 2},
                    {"value": "completion-a", "rank": 3},
                ],
            ),
        ],
    )
    async def test_update_response_with_wrong_response_value(
        self,
        async_client: "AsyncClient",
        QuestionFactory: Type["QuestionFactory"],
        response_value: Any,
        owner: "User",
        owner_auth_header: dict,
    ):
        question = await QuestionFactory.create()
        record = await RecordFactory.create(dataset=question.dataset)
        response = await ResponseFactory.create(record=record, user=owner, status=ResponseStatus.draft)

        response_json = {"values": {question.name: {"value": response_value}}, "status": ResponseStatus.submitted}
        resp = await async_client.put(f"/api/v1/responses/{response.id}", headers=owner_auth_header, json=response_json)

        assert resp.status_code == 422

    async def test_update_response_as_annotator(self, async_client: "AsyncClient", db: "AsyncSession"):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)
        await TextQuestionFactory.create(name="input_ok", dataset=dataset)
        await TextQuestionFactory.create(name="output_ok", dataset=dataset)
        record = await RecordFactory.create(dataset=dataset)
        annotator = await AnnotatorFactory.create()

        response = await ResponseFactory.create(
            record=record,
            values={
                "input_ok": {"value": "no"},
                "output_ok": {"value": "no"},
            },
            status="submitted",
            user=annotator,
        )
        response_json = {
            "values": {
                "input_ok": {"value": "yes"},
                "output_ok": {"value": "yes"},
            },
            "status": "submitted",
        }

        resp = await async_client.put(
            f"/api/v1/responses/{response.id}", headers={API_KEY_HEADER_NAME: annotator.api_key}, json=response_json
        )

        assert resp.status_code == 200
        assert (await db.get(Response, response.id)).values == {
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        }

        resp_body = resp.json()
        assert resp_body == {
            "id": str(response.id),
            "values": {
                "input_ok": {"value": "yes"},
                "output_ok": {"value": "yes"},
            },
            "status": "submitted",
            "record_id": str(response.record_id),
            "user_id": str(response.user_id),
            "inserted_at": response.inserted_at.isoformat(),
            "updated_at": datetime.fromisoformat(resp_body["updated_at"]).isoformat(),
        }

    async def test_update_response_as_annotator_for_different_user_response(
        self, async_client: "AsyncClient", db: "AsyncSession"
    ):
        annotator = await AnnotatorFactory.create()
        response = await ResponseFactory.create(
            values={
                "input_ok": {"value": "no"},
                "output_ok": {"value": "no"},
            },
            status="submitted",
        )
        response_json = {
            "values": {
                "input_ok": {"value": "yes"},
                "output_ok": {"value": "yes"},
            },
            "status": "submitted",
        }

        resp = await async_client.put(
            f"/api/v1/responses/{response.id}", headers={API_KEY_HEADER_NAME: annotator.api_key}, json=response_json
        )

        assert resp.status_code == 403
        assert (await db.get(Response, response.id)).values == {
            "input_ok": {"value": "no"},
            "output_ok": {"value": "no"},
        }

    async def test_update_response_with_nonexistent_response_id(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        response_id = uuid4()

        response = await ResponseFactory.create(
            values={
                "input_ok": {"value": "no"},
                "output_ok": {"value": "no"},
            },
            status="submitted",
        )

        resp = await async_client.put(
            f"/api/v1/responses/{response_id}",
            headers=owner_auth_header,
            json={
                "values": {
                    "input_ok": {"value": "yes"},
                    "output_ok": {"value": "yes"},
                },
                "status": "submitted",
            },
        )

        assert resp.status_code == 404
        assert resp.json() == {"detail": f"Response with id `{response_id}` not found"}

        assert (await db.get(Response, response.id)).values == {
            "input_ok": {"value": "no"},
            "output_ok": {"value": "no"},
        }

    async def test_delete_response(
        self, async_client: "AsyncClient", mock_search_engine: SearchEngine, db: "AsyncSession", owner_auth_header: dict
    ):
        response = await ResponseFactory.create()
        dataset = response.record.dataset

        dataset_previous_last_activity_at = dataset.last_activity_at
        dataset_previous_updated_at = dataset.updated_at

        resp = await async_client.delete(f"/api/v1/responses/{response.id}", headers=owner_auth_header)

        assert resp.status_code == 200
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

        await db.refresh(dataset)
        assert dataset.last_activity_at > dataset_previous_last_activity_at
        assert dataset.updated_at == dataset_previous_updated_at

        mock_search_engine.delete_record_response.assert_called_once_with(response)

    async def test_delete_response_without_authentication(self, async_client: "AsyncClient", db: "AsyncSession"):
        response = await ResponseFactory.create()

        resp = await async_client.delete(f"/api/v1/responses/{response.id}")

        assert resp.status_code == 401
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 1

    @pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
    async def test_delete_response_as_restricted_user(
        self, async_client: "AsyncClient", db: "AsyncSession", role: UserRole
    ):
        user = await UserFactory.create(role=role)
        response = await ResponseFactory.create(user=user)

        resp = await async_client.delete(
            f"/api/v1/responses/{response.id}", headers={API_KEY_HEADER_NAME: user.api_key}
        )

        assert resp.status_code == 200
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    async def test_delete_response_as_admin_for_different_user_response(
        self, async_client: "AsyncClient", db: "AsyncSession"
    ):
        workspace = await WorkspaceFactory.create()
        admin = await AdminFactory.create(workspaces=[workspace])
        dataset = await DatasetFactory.create(workspace=workspace)
        record = await RecordFactory.create(dataset=dataset)
        response = await ResponseFactory.create(record=record)

        resp = await async_client.delete(
            f"/api/v1/responses/{response.id}", headers={API_KEY_HEADER_NAME: admin.api_key}
        )

        assert resp.status_code == 200
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 0

    async def test_delete_response_as_annotator_for_different_user_response(
        self, async_client: "AsyncClient", db: "AsyncSession"
    ):
        annotator = await AnnotatorFactory.create()
        response = await ResponseFactory.create()

        resp = await async_client.delete(
            f"/api/v1/responses/{response.id}", headers={API_KEY_HEADER_NAME: annotator.api_key}
        )

        assert resp.status_code == 403
        assert (await db.execute(select(func.count(Response.id)))).scalar() == 1

    async def test_delete_response_with_nonexistent_response_id(
        self, async_client: "AsyncClient", db: "AsyncSession", owner_auth_header: dict
    ):
        response_id = uuid4()

        await ResponseFactory.create()

        resp = await async_client.delete(
            f"/api/v1/responses/{response_id}",
            headers=owner_auth_header,
        )

        assert resp.status_code == 404
        assert resp.json() == {"detail": f"Response with id `{response_id}` not found"}

        assert (await db.execute(select(func.count(Response.id)))).scalar() == 1
