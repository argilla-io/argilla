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
from typing import Any, Dict
from uuid import UUID, uuid4

import pytest
from argilla_v1.client.feedback.schemas.records import FeedbackRecord, ResponseSchema, SuggestionSchema
from argilla_v1.client.feedback.schemas.remote.records import (
    RemoteFeedbackRecord,
    RemoteResponseSchema,
    RemoteSuggestionSchema,
)
from argilla_v1.client.sdk.v1.datasets.models import (
    FeedbackItemModel,
    FeedbackRankingValueModel,
    FeedbackResponseModel,
    FeedbackSuggestionModel,
    FeedbackValueModel,
)


@pytest.mark.parametrize(
    "schema_kwargs, server_payload",
    [
        (
            {
                "question_id": UUID("00000000-0000-0000-0000-000000000000"),
                "question_name": "question-1",
                "type": "human",
                "score": 0.5,
                "value": "a",
                "agent": "b",
            },
            {
                "question_id": "00000000-0000-0000-0000-000000000000",
                "type": "human",
                "score": 0.5,
                "value": "a",
                "agent": "b",
            },
        ),
        (
            {
                "question_id": UUID("00000000-0000-0000-0000-000000000000"),
                "question_name": "question-1",
                "type": "model",
                "score": 1.0,
                "value": "a",
                "agent": "b",
            },
            {
                "question_id": "00000000-0000-0000-0000-000000000000",
                "type": "model",
                "score": 1.0,
                "value": "a",
                "agent": "b",
            },
        ),
    ],
)
def test_remote_suggestion_schema(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    suggestion = RemoteSuggestionSchema(**schema_kwargs)
    assert (
        suggestion.to_server_payload(question_name_to_id={schema_kwargs["question_name"]: schema_kwargs["question_id"]})
        == server_payload
    )

    local_suggestion = suggestion.to_local()
    assert isinstance(local_suggestion, SuggestionSchema)
    assert (
        local_suggestion.to_server_payload(
            question_name_to_id={schema_kwargs["question_name"]: schema_kwargs["question_id"]}
        )
        == server_payload
    )


@pytest.mark.parametrize(
    "payload",
    [
        FeedbackSuggestionModel(
            id=uuid4(),
            question_id=str(uuid4()),
            type="human",
            score=0.5,
            value="a",
            agent="b",
        ),
        FeedbackSuggestionModel(
            id=uuid4(),
            question_id=str(uuid4()),
            type="model",
            score=1.0,
            value="a",
            agent="b",
        ),
    ],
)
def test_remote_suggestion_schema_from_api(payload: FeedbackSuggestionModel) -> None:
    suggestion = RemoteSuggestionSchema.from_api(payload, question_id_to_name={UUID(payload.question_id): "question-1"})
    assert suggestion.to_server_payload(question_name_to_id={"question-1": payload.question_id}) == payload.dict(
        exclude={"id"}
    )


@pytest.mark.parametrize(
    "schema_kwargs, server_payload",
    [
        (
            {
                "user_id": UUID("00000000-0000-0000-0000-000000000000"),
                "values": {
                    "question-1": {"value": "a"},
                    "question-2": {"value": 1},
                    "question-3": {"value": ["a", "b"]},
                    "question-4": {"value": [{"value": "a", "rank": 1}, {"value": "b", "rank": 2}]},
                },
                "status": "submitted",
                "inserted_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "user_id": UUID("00000000-0000-0000-0000-000000000000"),
                "values": {
                    "question-1": {"value": "a"},
                    "question-2": {"value": 1},
                    "question-3": {"value": ["a", "b"]},
                    "question-4": {"value": [{"value": "a", "rank": 1}, {"value": "b", "rank": 2}]},
                },
                "status": "submitted",
            },
        ),
        (
            {
                "user_id": UUID("00000000-0000-0000-0000-000000000000"),
                "values": {"question-1": {"value": "a"}},
                "status": "draft",
                "inserted_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "user_id": UUID("00000000-0000-0000-0000-000000000000"),
                "values": {"question-1": {"value": "a"}},
                "status": "draft",
            },
        ),
        (
            {
                "user_id": UUID("00000000-0000-0000-0000-000000000000"),
                "values": None,
                "status": "discarded",
                "inserted_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "user_id": UUID("00000000-0000-0000-0000-000000000000"),
                "values": None,
                "status": "discarded",
            },
        ),
    ],
)
def test_remote_response_schema(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    response = RemoteResponseSchema(**schema_kwargs)
    assert response.to_server_payload() == server_payload

    local_response = response.to_local()
    assert isinstance(local_response, ResponseSchema)
    assert local_response.to_server_payload() == server_payload


@pytest.mark.parametrize(
    "payload",
    [
        FeedbackResponseModel(
            id=uuid4(),
            values={
                "question-1": FeedbackValueModel(value="a"),
                "question-2": FeedbackValueModel(value=1),
                "question-3": FeedbackValueModel(value=["a", "b"]),
                "question-4": FeedbackValueModel(
                    value=[FeedbackRankingValueModel(value="a", rank=1), FeedbackRankingValueModel(value="b", rank=2)]
                ),
                "question-5": FeedbackValueModel(value=[{"start": 0, "end": 1, "label": "a"}]),
            },
            status="submitted",
            user_id=uuid4(),
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        FeedbackResponseModel(
            id=uuid4(),
            values={"question-1": FeedbackValueModel(value="a")},
            status="draft",
            user_id=uuid4(),
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        FeedbackResponseModel(
            id=uuid4(),
            values={"span-question": FeedbackValueModel(value=[{"start": 0, "end": 1, "label": "a"}])},
            status="discarded",
            user_id=uuid4(),
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ],
)
def test_remote_response_schema_from_api(payload: FeedbackResponseModel) -> None:
    response = RemoteResponseSchema.from_api(payload)
    assert response.to_server_payload() == payload.dict(exclude={"id", "inserted_at", "updated_at"})

    local_response = response.to_local()
    assert isinstance(local_response, ResponseSchema)
    assert local_response.to_server_payload() == payload.dict(exclude={"id", "inserted_at", "updated_at"})


@pytest.mark.parametrize(
    "schema_kwargs, server_payload",
    [
        (
            {
                "id": UUID("00000000-0000-0000-0000-000000000000"),
                "fields": {"text": "This is the first record", "label": "positive", "optional": None},
                "metadata": {"first": True, "nested": {"more": "stuff"}},
                "responses": [
                    {
                        "values": {"question-1": {"value": "This is the first answer"}, "question-2": {"value": 5}},
                        "status": "submitted",
                        "inserted_at": datetime.now(),
                        "updated_at": datetime.now(),
                    },
                ],
                "suggestions": [
                    {
                        "question_id": UUID("00000000-0000-0000-0000-000000000000"),
                        "question_name": "question-1",
                        "type": "model",
                        "score": 0.9,
                        "value": "This is the first suggestion",
                        "agent": "agent-1",
                    },
                ],
                "vectors": {
                    "vector-1": [1.0, 2.0, 3.0],
                    "vector-2": [1.0, 2.0, 3.0, 4.0],
                },
                "external_id": "entry-1",
            },
            {
                "fields": {"text": "This is the first record", "label": "positive"},
                "metadata": {"first": True, "nested": {"more": "stuff"}},
                "responses": [
                    {
                        "user_id": None,
                        "values": {"question-1": {"value": "This is the first answer"}, "question-2": {"value": 5}},
                        "status": "submitted",
                    },
                ],
                "suggestions": [
                    {
                        "question_id": "00000000-0000-0000-0000-000000000000",
                        "type": "model",
                        "score": 0.9,
                        "value": "This is the first suggestion",
                        "agent": "agent-1",
                    },
                ],
                "vectors": {
                    "vector-1": [1.0, 2.0, 3.0],
                    "vector-2": [1.0, 2.0, 3.0, 4.0],
                },
                "external_id": "entry-1",
            },
        ),
    ],
)
def test_remote_feedback_record(schema_kwargs: Dict[str, Any], server_payload: Dict[str, Any]) -> None:
    record = RemoteFeedbackRecord(
        **schema_kwargs, question_name_to_id={"question-1": UUID("00000000-0000-0000-0000-000000000000")}
    )
    assert (
        record.to_server_payload(question_name_to_id={"question-1": UUID("00000000-0000-0000-0000-000000000000")})
        == server_payload
    )

    local_record = record.to_local()
    assert isinstance(local_record, FeedbackRecord)
    assert (
        local_record.to_server_payload(question_name_to_id={"question-1": UUID("00000000-0000-0000-0000-000000000000")})
        == server_payload
    )


@pytest.mark.parametrize(
    "payload",
    [
        FeedbackItemModel(
            id=uuid4(),
            fields={"text": "This is the first record", "label": "positive"},
            metadata={"first": True, "nested": {"more": "stuff"}},
            external_id="entry-1",
            responses=[
                FeedbackResponseModel(
                    id=uuid4(),
                    values={
                        "question-1": FeedbackValueModel(value="This is the first answer"),
                    },
                    status="submitted",
                    user_id=uuid4(),
                    inserted_at=datetime.now(),
                    updated_at=datetime.now(),
                ),
            ],
            suggestions=[
                FeedbackSuggestionModel(
                    id=uuid4(),
                    question_id=str(uuid4()),
                    type="model",
                    score=0.9,
                    value="This is the first suggestion",
                    agent="agent-1",
                )
            ],
            vectors={
                "vector-1": [1.0, 2.0, 3.0],
                "vector-2": [1.0, 2.0, 3.0, 4.0],
            },
            inserted_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ],
)
def test_remote_feedback_record_schema_from_api(payload: FeedbackItemModel) -> None:
    record = RemoteFeedbackRecord.from_api(
        payload, question_id_to_name={UUID(payload.suggestions[0].question_id): "question-1"}
    )
    # Skipping `suggestions` temporarily as it's now a tuple internally formatted and the type is not preserved
    assert record.dict(
        exclude={
            "client": ...,
            "responses": {"__all__": {"id", "client"}},
            "suggestions": ...,
            "inserted_at": ...,
            "updated_at": ...,
        }
    ) == payload.dict(
        exclude={
            "responses": {"__all__": {"id"}},
            "suggestions": ...,
            "inserted_at": ...,
            "updated_at": ...,
        }
    )

    local_record = record.to_local()
    assert isinstance(local_record, FeedbackRecord)
    assert local_record.to_server_payload(
        question_name_to_id={"question-1": payload.suggestions[0].question_id}
    ) == payload.dict(
        exclude={
            "id": ...,
            "responses": {"__all__": {"id", "inserted_at", "updated_at"}},
            "suggestions": {"__all__": {"id"}},
            "inserted_at": ...,
            "updated_at": ...,
        }
    )
