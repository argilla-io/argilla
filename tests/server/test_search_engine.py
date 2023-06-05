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
    LabelSelectionQuestionFactory,
    MultiLabelSelectionQuestionFactory,
    RatingQuestionFactory,
    RecordFactory,
    ResponseFactory,
    TextFieldFactory,
    TextQuestionFactory,
)


@pytest_asyncio.fixture()
async def test_banking_sentiment_dataset(elastic_search_engine: SearchEngine):
    text_question = TextQuestionFactory()
    rating_question = RatingQuestionFactory()

    dataset = DatasetFactory.create(
        fields=[TextFieldFactory(name="textId"), TextFieldFactory(name="text"), TextFieldFactory(name="label")],
        questions=[text_question, rating_question],
    )

    await elastic_search_engine.create_index(dataset)

    await elastic_search_engine.add_records(
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
            RecordFactory(
                dataset=dataset,
                fields={
                    "textId": "00004",
                    "text": "Why was I charged for getting cash?",
                    "label": "neutral",
                },
            ),
            RecordFactory(
                dataset=dataset,
                fields={
                    "textId": "00005",
                    "text": "I tried to make a payment with my card and it was declined.",
                    "label": "negative",
                },
            ),
            RecordFactory(
                dataset=dataset,
                fields={
                    "textId": "00006",
                    "text": "My credit card was declined when I tried to make a payment.",
                    "label": "negative",
                },
            ),
        ],
    )

    return dataset


@pytest.mark.asyncio
class TestSuiteElasticSearchEngine:
    async def test_get_index_or_raise(self, elastic_search_engine: SearchEngine):
        dataset = DatasetFactory.create()
        with pytest.raises(
            ValueError, match=f"Cannot access to index for dataset {dataset.id}: the specified index does not exist"
        ):
            await elastic_search_engine._get_index_or_raise(dataset)

    async def test_create_index_for_dataset(self, elastic_search_engine: SearchEngine, opensearch: OpenSearch):
        dataset = DatasetFactory.create()
        await elastic_search_engine.create_index(dataset)

        index_name = f"rg.{dataset.id}"
        assert opensearch.indices.exists(index=index_name)

        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"] == {
            "dynamic": "strict",
            "dynamic_templates": [
                {"status_responses": {"mapping": {"type": "keyword"}, "path_match": "responses.*.status"}}
            ],
            "properties": {
                "id": {"type": "keyword"},
                "responses": {"dynamic": "true", "type": "object"},
            },
        }
        assert index["settings"]["index"]["number_of_shards"] == str(elastic_search_engine.es_number_of_shards)
        assert index["settings"]["index"]["number_of_replicas"] == str(elastic_search_engine.es_number_of_replicas)

    async def test_create_index_for_dataset_with_fields(
        self,
        elastic_search_engine: SearchEngine,
        opensearch: OpenSearch,
        db: Session,
    ):
        text_fields = TextFieldFactory.create_batch(5)
        dataset = DatasetFactory.create(fields=text_fields)

        await elastic_search_engine.create_index(dataset)

        index_name = f"rg.{dataset.id}"
        assert opensearch.indices.exists(index=index_name)

        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"] == {
            "dynamic": "strict",
            "dynamic_templates": [
                {"status_responses": {"mapping": {"type": "keyword"}, "path_match": "responses.*.status"}}
            ],
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
        elastic_search_engine: SearchEngine,
        opensearch: OpenSearch,
        db: Session,
        text_ann_size: int,
        rating_ann_size: int,
    ):
        text_questions = TextQuestionFactory.create_batch(size=text_ann_size)
        rating_questions = RatingQuestionFactory.create_batch(size=rating_ann_size)
        label_questions = LabelSelectionQuestionFactory.create_batch(size=text_ann_size)
        multilabel_questions = MultiLabelSelectionQuestionFactory.create_batch(size=rating_ann_size)

        all_questions = text_questions + rating_questions + label_questions + multilabel_questions
        dataset = DatasetFactory.create(questions=all_questions)

        await elastic_search_engine.create_index(dataset)

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
                {"status_responses": {"mapping": {"type": "keyword"}, "path_match": "responses.*.status"}},
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
                *[
                    config
                    for question in label_questions + multilabel_questions
                    for config in [
                        {
                            f"{question.name}_responses": {
                                "mapping": {"type": "keyword"},
                                "path_match": f"responses.*.values.{question.name}",
                            }
                        },
                    ]
                ],
            ],
        }

    async def test_create_index_with_existing_index(
        self, elastic_search_engine: SearchEngine, opensearch: OpenSearch, db: Session
    ):
        dataset = DatasetFactory.create()
        await elastic_search_engine.create_index(dataset)

        index_name = f"rg.{dataset.id}"
        assert opensearch.indices.exists(index=index_name)

        with pytest.raises(RequestError, match="resource_already_exists_exception"):
            await elastic_search_engine.create_index(dataset)

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
        elastic_search_engine: SearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset: Dataset,
        query: str,
        expected_items: int,
    ):
        opensearch.indices.refresh(index=f"rg.{test_banking_sentiment_dataset.id}")

        result = await elastic_search_engine.search(test_banking_sentiment_dataset, query=query)

        assert len(result.items) == expected_items

        scores = [item.score > 0 for item in result.items]
        assert all(map(lambda s: s > 0, scores))

        sorted_scores = scores.copy()
        sorted_scores.sort(reverse=True)

        assert scores == sorted_scores

    async def test_search_with_offset_and_limit(
        self, elastic_search_engine: SearchEngine, opensearch: OpenSearch, test_banking_sentiment_dataset: Dataset
    ):
        opensearch.indices.refresh(index=f"rg.{test_banking_sentiment_dataset.id}")

        query = SearchQuery(text=TextQuery(q="card", field="text"))

        first_search = await elastic_search_engine.search(
            test_banking_sentiment_dataset, query=query, offset=0, limit=2
        )

        assert len(first_search.items) == 2

        second_search = await elastic_search_engine.search(
            test_banking_sentiment_dataset, query=query, offset=2, limit=2
        )

        assert len(second_search.items) == 2
        first_search_ids = [item.record_id for item in first_search.items]
        first_search_scores = [item.score for item in first_search.items]
        for item in second_search.items:
            assert item.record_id not in first_search_ids
            assert all(item.score < score for score in first_search_scores)

    async def test_add_records(self, elastic_search_engine: SearchEngine, opensearch: OpenSearch):
        text_fields = TextFieldFactory.create_batch(5)
        dataset = DatasetFactory.create(fields=text_fields)

        records = RecordFactory.create_batch(
            size=10,
            dataset=dataset,
            fields={field.name: f"This is the value for {field.name}" for field in text_fields},
        )
        await elastic_search_engine.create_index(dataset)
        await elastic_search_engine.add_records(dataset, records)

        index_name = f"rg.{dataset.id}"
        opensearch.indices.refresh(index=index_name)

        es_docs = [hit["_source"] for hit in opensearch.search(index=index_name)["hits"]["hits"]]
        assert es_docs == [{"id": str(record.id), "fields": record.fields, "responses": {}} for record in records]

    async def test_update_record_response(
        self,
        elastic_search_engine: SearchEngine,
        opensearch: OpenSearch,
        db: Session,
        test_banking_sentiment_dataset: Dataset,
    ):
        record = test_banking_sentiment_dataset.records[0]
        question = test_banking_sentiment_dataset.questions[0]

        response = ResponseFactory.create(record=record, values={question.name: {"value": "test"}})
        await elastic_search_engine.update_record_response(response)

        index_name = f"rg.{test_banking_sentiment_dataset.id}"
        opensearch.indices.refresh(index=index_name)

        results = opensearch.get(index=index_name, id=record.id)

        assert results["_source"]["responses"] == {
            response.user.username: {
                "values": {question.name: "test"},
                "status": response.status.value,
            }
        }

        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"]["properties"]["responses"] == {
            "dynamic": "true",
            "properties": {
                response.user.username: {
                    "properties": {
                        "status": {"type": "keyword"},
                        "values": {"properties": {question.name: {"index": False, "type": "text"}}},
                    }
                }
            },
        }

    async def test_delete_record_response(
        self,
        elastic_search_engine: SearchEngine,
        opensearch: OpenSearch,
        db: Session,
        test_banking_sentiment_dataset: Dataset,
    ):
        record = test_banking_sentiment_dataset.records[0]
        question = test_banking_sentiment_dataset.questions[0]

        response = ResponseFactory.create(record=record, values={question.name: {"value": "test"}})
        await elastic_search_engine.update_record_response(response)

        index_name = f"rg.{test_banking_sentiment_dataset.id}"

        opensearch.indices.refresh(index=index_name)

        results = opensearch.get(index=index_name, id=record.id)
        assert results["_source"]["responses"] == {
            response.user.username: {
                "values": {question.name: "test"},
                "status": response.status.value,
            }
        }

        await elastic_search_engine.delete_record_response(response)

        opensearch.indices.refresh(index=index_name)

        results = opensearch.get(index=index_name, id=record.id)
        assert results["_source"]["responses"] == {}
