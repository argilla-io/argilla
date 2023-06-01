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

import random

import pytest
import pytest_asyncio
from argilla.server.models import Dataset
from argilla.server.search_engine import Query as SearchQuery
from argilla.server.search_engine import SearchEngine, TextQuery
from opensearchpy import OpenSearch, RequestError
from sqlalchemy.orm import Session

from tests.factories import (
    DatasetFactory,
    RatingQuestionFactory,
    RecordFactory,
    TextFieldFactory,
    TextQuestionFactory,
)


@pytest_asyncio.fixture()
async def test_banking_sentiment_dataset(search_engine: SearchEngine):
    text_question = TextQuestionFactory()
    rating_question = RatingQuestionFactory()

    dataset = DatasetFactory.create(
        fields=[TextFieldFactory(name="textId"), TextFieldFactory(name="text"), TextFieldFactory(name="label")],
        questions=[text_question, rating_question],
    )

    await search_engine.create_index(dataset)

    await search_engine.add_records(
        dataset,
        records=[
            RecordFactory(
                dataset=dataset,
                fields={"textId": "00000", "text": "My card payment had the wrong exchange rate", "label": "negative"},
            ),
            RecordFactory(
                dataset=dataset,
                fields={
                    "textId": "00001",
                    "text": "I believe that a card payment I made was cancelled.",
                    "label": "neutral",
                },
            ),
            RecordFactory(
                dataset=dataset,
                fields={"textId": "00002", "text": "Why was I charged for getting cash?", "label": "neutral"},
            ),
            RecordFactory(
                dataset=dataset,
                fields={
                    "textId": "00003",
                    "text": "I deposited cash into my account a week ago and it is still not available,"
                    " please tell me why? I need the cash back now.",
                    "label": "negative",
                },
            ),
        ],
    )

    return dataset


@pytest.mark.asyncio
class TestSuiteElasticSearchEngine:
    async def test_create_index_for_dataset(self, search_engine: SearchEngine, opensearch: OpenSearch):
        dataset = DatasetFactory.create()
        await search_engine.create_index(dataset)

        index_name = f"rg.{dataset.id}"
        assert opensearch.indices.exists(index=index_name)

        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"] == {
            "dynamic": "strict",
            "dynamic_templates": [],
            "properties": {
                "id": {"type": "keyword"},
                "responses": {"dynamic": "true", "type": "object"},
            },
        }

    async def test_create_index_for_dataset_with_fields(
        self,
        search_engine: SearchEngine,
        opensearch: OpenSearch,
        db: Session,
    ):
        text_fields = TextFieldFactory.create_batch(5)
        dataset = DatasetFactory.create(fields=text_fields)

        await search_engine.create_index(dataset)

        index_name = f"rg.{dataset.id}"
        assert opensearch.indices.exists(index=index_name)

        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"] == {
            "dynamic": "strict",
            "dynamic_templates": [],
            "properties": {
                "id": {"type": "keyword"},
                "fields": {"properties": {field.name: {"type": "text"} for field in dataset.fields}},
                "responses": {"type": "object", "dynamic": "true"},
            },
        }

    @pytest.mark.parametrize(
        argnames=("text_ann_size", "rating_ann_size"),
        argvalues=[(random.randint(1, 9), random.randint(1, 9)) for _ in range(1, 5)],
    )
    async def test_create_index_for_dataset_with_questions(
        self,
        search_engine: SearchEngine,
        opensearch: OpenSearch,
        db: Session,
        text_ann_size: int,
        rating_ann_size: int,
    ):
        text_questions = TextQuestionFactory.create_batch(size=text_ann_size)
        rating_questions = RatingQuestionFactory.create_batch(size=rating_ann_size)

        dataset = DatasetFactory.create(questions=text_questions + rating_questions)

        await search_engine.create_index(dataset)

        index_name = f"rg.{dataset.id}"
        assert opensearch.indices.exists(index=index_name)

        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"] == {
            "dynamic": "strict",
            "properties": {
                "id": {"type": "keyword"},
                "responses": {"dynamic": "true", "type": "object"},
            },
            "dynamic_templates": [
                *[
                    config
                    for question in text_questions
                    for config in [
                        {
                            f"{question.name}_responses": {
                                "mapping": {"type": "text", "index": False},
                                "path_match": f"responses.*.values.{question.name}",
                            }
                        },
                    ]
                ],
                *[
                    config
                    for question in rating_questions
                    for config in [
                        {
                            f"{question.name}_responses": {
                                "mapping": {"type": "integer"},
                                "path_match": f"responses.*.values.{question.name}",
                            }
                        },
                    ]
                ],
            ],
        }

    async def test_create_index_with_existing_index(
        self, search_engine: SearchEngine, opensearch: OpenSearch, db: Session
    ):
        dataset = DatasetFactory.create()
        await search_engine.create_index(dataset)

        index_name = f"rg.{dataset.id}"
        assert opensearch.indices.exists(index=index_name)

        with pytest.raises(RequestError, match="resource_already_exists_exception"):
            await search_engine.create_index(dataset)

    @pytest.mark.parametrize(
        ("query", "expected_items"),
        [
            ("card", 2),
            ("account", 1),
            ("payment", 2),
            ("cash", 2),
            ("negative", 2),
            ("00000", 1),
            ("card payment", 2),
            ("nothing", 0),
            (SearchQuery(text=TextQuery(q="card")), 2),
            (SearchQuery(text=TextQuery(q="account")), 1),
            (SearchQuery(text=TextQuery(q="payment")), 2),
            (SearchQuery(text=TextQuery(q="cash")), 2),
            (SearchQuery(text=TextQuery(q="card payment")), 2),
            (SearchQuery(text=TextQuery(q="nothing")), 0),
            (SearchQuery(text=TextQuery(q="negative", field="label")), 2),
            (SearchQuery(text=TextQuery(q="00000", field="textId")), 1),
            (SearchQuery(text=TextQuery(q="card payment", field="text")), 2),
        ],
    )
    async def test_search_with_query_string(
        self,
        search_engine: SearchEngine,
        opensearch: OpenSearch,
        db: Session,
        test_banking_sentiment_dataset: Dataset,
        query: str,
        expected_items: int,
    ):
        opensearch.indices.refresh(index=f"rg.{test_banking_sentiment_dataset.id}")

        result = await search_engine.search(test_banking_sentiment_dataset, query=query)
        assert len(result.items) == expected_items

        scores = [item.score > 0 for item in result.items]
        assert all(map(lambda s: s > 0, scores))

        sorted_scores = scores.copy()
        sorted_scores.sort(reverse=True)

        assert scores == sorted_scores
