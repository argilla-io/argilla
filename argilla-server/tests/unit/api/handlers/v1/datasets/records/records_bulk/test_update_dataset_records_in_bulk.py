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

from uuid import UUID

import pytest
from argilla_server.enums import DatasetStatus, QuestionType, SuggestionType
from argilla_server.models.database import Record, Suggestion, User
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import (
    DatasetFactory,
    LabelSelectionQuestionFactory,
    MultiLabelSelectionQuestionFactory,
    RankingQuestionFactory,
    RatingQuestionFactory,
    RecordFactory,
    SpanQuestionFactory,
    TextFieldFactory,
    TextQuestionFactory,
)


@pytest.mark.asyncio
class TestUpdateDatasetRecordsInBulk:
    def url(self, dataset_id: UUID) -> str:
        return f"/api/v1/datasets/{dataset_id}/records/bulk"

    async def test_update_dataset_records(
        self, async_client: AsyncClient, db: AsyncSession, owner: User, owner_auth_header: dict
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await TextFieldFactory.create(name="prompt", dataset=dataset)
        await TextFieldFactory.create(name="response", dataset=dataset)

        text_question = await TextQuestionFactory.create(name="text-question", dataset=dataset)

        label_selection_question = await LabelSelectionQuestionFactory.create(
            name="label-selection-question",
            settings={
                "type": QuestionType.label_selection,
                "options": [
                    {"value": "label-a", "text": "Label A", "description": "Label A description"},
                    {"value": "label-b", "text": "Label B", "description": "Label B description"},
                ],
            },
            dataset=dataset,
        )

        multi_label_selection_question = await MultiLabelSelectionQuestionFactory.create(
            name="multi-label-selection-question",
            settings={
                "type": QuestionType.multi_label_selection,
                "options": [
                    {"value": "label-a", "text": "Label A", "description": "Label A description"},
                    {"value": "label-b", "text": "Label B", "description": "Label B description"},
                    {"value": "label-c", "text": "Label C", "description": "Label C description"},
                ],
            },
            dataset=dataset,
        )

        rating_question = await RatingQuestionFactory.create(
            name="rating-question",
            settings={
                "type": QuestionType.rating,
                "options": [
                    {"value": 1},
                    {"value": 2},
                    {"value": 3},
                ],
            },
            dataset=dataset,
        )

        ranking_question = await RankingQuestionFactory.create(
            name="ranking-question",
            settings={
                "type": QuestionType.ranking,
                "options": [
                    {"value": "ranking-a", "text": "Ranking A", "description": "Ranking A description"},
                    {"value": "ranking-b", "text": "Ranking B", "description": "Ranking B description"},
                ],
            },
            dataset=dataset,
        )

        span_question = await SpanQuestionFactory.create(
            name="span-question",
            settings={
                "type": QuestionType.span,
                "field": "response",
                "options": [
                    {"value": "thing", "text": "Thing", "description": "Thing description"},
                    {"value": "place", "text": "Place", "description": "Place description"},
                ],
            },
            dataset=dataset,
        )

        record = await RecordFactory.create(
            fields={
                "prompt": "Does exercise help reduce stress?",
                "response": "Exercise can definitely help reduce stress.",
            },
            external_id="1",
            dataset=dataset,
        )

        response = await async_client.put(
            self.url(dataset.id),
            headers=owner_auth_header,
            json={
                "items": [
                    {
                        "id": str(record.id),
                        "suggestions": [
                            {
                                "type": SuggestionType.model,
                                "score": 0.5,
                                "value": "suggestion to text question",
                                "question_id": str(text_question.id),
                            },
                            {
                                "type": SuggestionType.model,
                                "score": 0.9,
                                "value": "label-a",
                                "question_id": str(label_selection_question.id),
                            },
                            {
                                "type": SuggestionType.model,
                                "score": [1.0, 0.1],
                                "value": [
                                    "label-a",
                                    "label-b",
                                ],
                                "question_id": str(multi_label_selection_question.id),
                            },
                            {
                                "type": SuggestionType.model,
                                "score": 0.9,
                                "value": 1,
                                "question_id": str(rating_question.id),
                            },
                            {
                                "type": SuggestionType.model,
                                "score": [0.2, 0.5],
                                "value": [
                                    {"value": "ranking-a", "rank": 1},
                                    {"value": "ranking-b", "rank": 2},
                                ],
                                "question_id": str(ranking_question.id),
                            },
                            {
                                "type": SuggestionType.model,
                                "score": [0.5, 0.9],
                                "value": [
                                    {"label": "thing", "start": 0, "end": 5},
                                    {"label": "place", "start": 6, "end": 8},
                                ],
                                "question_id": str(span_question.id),
                            },
                        ],
                    },
                ],
            },
        )

        assert response.status_code == 200

        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 1
        assert (await db.execute(select(func.count(Suggestion.id)))).scalar_one() == 6
