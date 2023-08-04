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
from typing import TYPE_CHECKING, List

import pytest
import pytest_asyncio
from argilla.server.enums import ResponseStatusFilter
from argilla.server.models import Dataset, User
from argilla.server.search_engine import Query as SearchQuery
from argilla.server.search_engine import (
    SearchEngine,
    TextQuery,
    UserResponseStatusFilter,
)
from opensearchpy import OpenSearch, RequestError, helpers
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
    UserFactory,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture(scope="function")
async def dataset_for_pagination(opensearch: OpenSearch):
    dataset = await DatasetFactory.create(fields=[], questions=[])
    records = await RecordFactory.create_batch(size=100, dataset=dataset)
    await dataset.awaitable_attrs.records
    index_name = f"rg.{dataset.id}"

    opensearch.indices.create(index=index_name, body={"mappings": {"properties": {"id": {"type": "keyword"}}}})

    bulk_actions = [
        {
            "_op_type": "index",
            "_id": record.id,
            "_index": index_name,
            "id": record.id,
            "fields": {"text": "The same text for all documents"},
        }
        for record in records
    ]

    helpers.bulk(client=opensearch, actions=bulk_actions)

    opensearch.indices.refresh(index=index_name)

    yield dataset

    opensearch.indices.delete(index=index_name)


@pytest_asyncio.fixture(scope="function")
@pytest.mark.asyncio
async def test_banking_sentiment_dataset(elastic_search_engine: SearchEngine) -> Dataset:
    text_question = await TextQuestionFactory()
    rating_question = await RatingQuestionFactory()

    dataset = await DatasetFactory.create(
        fields=[
            await TextFieldFactory.create(name="textId"),
            await TextFieldFactory.create(name="text"),
            await TextFieldFactory.create(name="label"),
        ],
        questions=[text_question, rating_question],
    )

    await elastic_search_engine.create_index(dataset)

    await elastic_search_engine.add_records(
        dataset,
        records=[
            await RecordFactory.create(
                dataset=dataset,
                fields={"textId": "00000", "text": "My card payment had the wrong exchange rate", "label": "negative"},
                responses=[],
            ),
            await RecordFactory.create(
                dataset=dataset,
                fields={
                    "textId": "00001",
                    "text": "I believe that a card payment I made was cancelled.",
                    "label": "neutral",
                },
                responses=[],
            ),
            await RecordFactory.create(
                dataset=dataset,
                fields={
                    "textId": "00002",
                    "text": "I tried to make a payment with my card and it was declined.",
                    "label": "negative",
                },
                responses=[],
            ),
            await RecordFactory.create(
                dataset=dataset,
                fields={
                    "textId": "00003",
                    "text": "My credit card was declined when I tried to make a payment.",
                    "label": "negative",
                },
                responses=[],
            ),
            await RecordFactory.create(
                dataset=dataset,
                fields={
                    "textId": "00004",
                    "text": "I made a successful payment towards my mortgage loan earlier today.",
                    "label": "positive",
                },
                responses=[],
            ),
            await RecordFactory.create(
                dataset=dataset,
                fields={
                    "textId": "00005",
                    "text": "Please confirm the receipt of my payment for the credit card bill due on the 15th.",
                    "label": "neutral",
                },
                responses=[],
            ),
            await RecordFactory.create(
                dataset=dataset,
                fields={
                    "textId": "00006",
                    "text": "Why was I charged for getting cash?",
                    "label": "neutral",
                },
                responses=[],
            ),
            await RecordFactory.create(
                dataset=dataset,
                fields={"textId": "00007", "text": "Why was I charged for getting cash?", "label": "neutral"},
                responses=[],
            ),
            await RecordFactory.create(
                dataset=dataset,
                fields={
                    "textId": "00008",
                    "text": "I deposited cash into my account a week ago and it is still not available,"
                    " please tell me why? I need the cash back now.",
                    "label": "negative",
                },
                responses=[],
            ),
        ],
    )
    await dataset.awaitable_attrs.records

    return dataset


@pytest.mark.asyncio
class TestSuiteElasticSearchEngine:
    async def test_get_index_or_raise(self, elastic_search_engine: SearchEngine):
        dataset = await DatasetFactory.create()
        with pytest.raises(
            ValueError, match=f"Cannot access to index for dataset {dataset.id}: the specified index does not exist"
        ):
            await elastic_search_engine._get_index_or_raise(dataset)

    async def test_create_index_for_dataset(
        self, elastic_search_engine: SearchEngine, db: "AsyncSession", opensearch: OpenSearch
    ):
        dataset = await DatasetFactory.create()
        await dataset.awaitable_attrs.fields
        await dataset.awaitable_attrs.questions
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
        text_fields = await TextFieldFactory.create_batch(5)
        dataset = await DatasetFactory.create(fields=text_fields)
        await dataset.awaitable_attrs.fields
        await dataset.awaitable_attrs.questions

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
        text_ann_size: int,
        rating_ann_size: int,
    ):
        text_questions = await TextQuestionFactory.create_batch(size=text_ann_size)
        rating_questions = await RatingQuestionFactory.create_batch(size=rating_ann_size)
        label_questions = await LabelSelectionQuestionFactory.create_batch(size=text_ann_size)
        multilabel_questions = await MultiLabelSelectionQuestionFactory.create_batch(size=rating_ann_size)

        all_questions = text_questions + rating_questions + label_questions + multilabel_questions
        dataset = await DatasetFactory.create(questions=all_questions)
        await dataset.awaitable_attrs.fields

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
        dataset = await DatasetFactory.create()
        await dataset.awaitable_attrs.fields
        await dataset.awaitable_attrs.questions
        await elastic_search_engine.create_index(dataset)

        index_name = f"rg.{dataset.id}"
        assert opensearch.indices.exists(index=index_name)

        with pytest.raises(RequestError, match="resource_already_exists_exception"):
            await elastic_search_engine.create_index(dataset)

    @pytest.mark.parametrize(
        ("query", "expected_items"),
        [
            ("card", 5),
            ("account", 1),
            ("payment", 6),
            ("cash", 3),
            ("negative", 4),
            ("00000", 1),
            ("card payment", 5),
            ("nothing", 0),
            (SearchQuery(text=TextQuery(q="card")), 5),
            (SearchQuery(text=TextQuery(q="account")), 1),
            (SearchQuery(text=TextQuery(q="payment")), 6),
            (SearchQuery(text=TextQuery(q="cash")), 3),
            (SearchQuery(text=TextQuery(q="card payment")), 5),
            (SearchQuery(text=TextQuery(q="nothing")), 0),
            (SearchQuery(text=TextQuery(q="negative", field="label")), 4),
            (SearchQuery(text=TextQuery(q="00000", field="textId")), 1),
            (SearchQuery(text=TextQuery(q="card payment", field="text")), 5),
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
        assert result.total == expected_items

        scores = [item.score > 0 for item in result.items]
        assert all(map(lambda s: s > 0, scores))

        sorted_scores = scores.copy()
        sorted_scores.sort(reverse=True)

        assert scores == sorted_scores

    @pytest.mark.parametrize(
        "statuses, expected_items",
        [
            ([], 6),
            ([ResponseStatusFilter.missing], 6),
            ([ResponseStatusFilter.draft], 2),
            ([ResponseStatusFilter.submitted], 2),
            ([ResponseStatusFilter.discarded], 2),
            ([ResponseStatusFilter.missing, ResponseStatusFilter.draft], 6),
            ([ResponseStatusFilter.submitted, ResponseStatusFilter.discarded], 4),
            ([ResponseStatusFilter.missing, ResponseStatusFilter.draft, ResponseStatusFilter.discarded], 6),
        ],
    )
    async def test_search_with_response_status_filter(
        self,
        elastic_search_engine: SearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset: Dataset,
        statuses: List[ResponseStatusFilter],
        expected_items: int,
    ):
        user = await UserFactory.create()

        await self._configure_record_responses(opensearch, test_banking_sentiment_dataset, statuses, user)

        result = await elastic_search_engine.search(
            test_banking_sentiment_dataset,
            query=SearchQuery(text=TextQuery(q="payment")),
            user_response_status_filter=UserResponseStatusFilter(user=user, statuses=statuses),
        )
        assert len(result.items) == expected_items
        assert result.total == expected_items

    async def test_search_with_response_status_filter_does_not_affect_the_result_scores(
        self, elastic_search_engine: SearchEngine, opensearch: OpenSearch, test_banking_sentiment_dataset: Dataset
    ):
        user = await UserFactory.create()

        all_statuses = [ResponseStatusFilter.missing, ResponseStatusFilter.draft, ResponseStatusFilter.discarded]
        await self._configure_record_responses(opensearch, test_banking_sentiment_dataset, all_statuses, user)

        no_filter_results = await elastic_search_engine.search(
            test_banking_sentiment_dataset,
            query=SearchQuery(text=TextQuery(q="payment")),
        )
        results = await elastic_search_engine.search(
            test_banking_sentiment_dataset,
            query=SearchQuery(text=TextQuery(q="payment")),
            user_response_status_filter=UserResponseStatusFilter(user=user, statuses=all_statuses),
        )
        assert len(no_filter_results.items) == len(results.items)
        assert no_filter_results.total == results.total
        assert [item.score for item in no_filter_results.items] == [item.score for item in results.items]

    @pytest.mark.parametrize(("offset", "limit"), [(0, 50), (10, 5), (0, 0), (90, 100)])
    async def test_search_with_pagination(
        self,
        elastic_search_engine: SearchEngine,
        opensearch: OpenSearch,
        dataset_for_pagination: Dataset,
        offset: int,
        limit: int,
    ):
        results = await elastic_search_engine.search(
            dataset_for_pagination, query="documents", offset=offset, limit=limit
        )

        assert len(results.items) == min(len(dataset_for_pagination.records) - offset, limit)
        assert results.total == 100

        records = sorted(dataset_for_pagination.records, key=lambda r: r.id)
        assert [record.id for record in records[offset : offset + limit]] == [item.record_id for item in results.items]

    async def test_add_records(self, elastic_search_engine: SearchEngine, opensearch: OpenSearch):
        text_fields = await TextFieldFactory.create_batch(5)
        dataset = await DatasetFactory.create(fields=text_fields, questions=[])
        records = await RecordFactory.create_batch(
            size=10,
            dataset=dataset,
            fields={field.name: f"This is the value for {field.name}" for field in text_fields},
            responses=[],
        )

        await elastic_search_engine.create_index(dataset)
        await elastic_search_engine.add_records(dataset, records)

        index_name = f"rg.{dataset.id}"
        opensearch.indices.refresh(index=index_name)

        es_docs = [hit["_source"] for hit in opensearch.search(index=index_name)["hits"]["hits"]]
        assert es_docs == [{"id": str(record.id), "fields": record.fields, "responses": {}} for record in records]

    async def test_delete_records(self, elastic_search_engine: SearchEngine, opensearch: OpenSearch):
        text_fields = await TextFieldFactory.create_batch(5)
        dataset = await DatasetFactory.create(fields=text_fields, questions=[])
        records = await RecordFactory.create_batch(
            size=10,
            dataset=dataset,
            fields={field.name: f"This is the value for {field.name}" for field in text_fields},
            responses=[],
        )

        await elastic_search_engine.create_index(dataset)
        await elastic_search_engine.add_records(dataset, records)

        records_to_delete, records_to_keep = records[:5], records[5:]
        await elastic_search_engine.delete_records(dataset, records_to_delete)

        index_name = f"rg.{dataset.id}"
        opensearch.indices.refresh(index=index_name)

        deleted_docs = [
            hit["_source"]
            for hit in opensearch.search(
                index=index_name, body={"query": {"ids": {"values": [str(record.id) for record in records_to_delete]}}}
            )["hits"]["hits"]
        ]
        assert len(deleted_docs) == 0

        es_docs = [
            hit["_source"]
            for hit in opensearch.search(
                index=index_name, body={"query": {"ids": {"values": [str(record.id) for record in records_to_keep]}}}
            )["hits"]["hits"]
        ]
        assert len(records_to_keep) == 5

    async def test_update_record_response(
        self,
        elastic_search_engine: SearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset: Dataset,
    ):
        record = test_banking_sentiment_dataset.records[0]
        question = test_banking_sentiment_dataset.questions[0]

        response = await ResponseFactory.create(record=record, values={question.name: {"value": "test"}})
        record = await response.awaitable_attrs.record
        await record.awaitable_attrs.dataset
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

        response = await ResponseFactory.create(record=record, values={question.name: {"value": "test"}})
        record = await response.awaitable_attrs.record
        await record.awaitable_attrs.dataset
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

    async def _configure_record_responses(
        self, opensearch: OpenSearch, dataset: Dataset, response_status: List[ResponseStatusFilter], user: User
    ):
        index_name = f"rg.{dataset.id}"
        another_user = await UserFactory.create()

        # Create two responses with the same status (one in each record)
        for i, status in enumerate(response_status):
            if status == ResponseStatusFilter.missing:
                continue
            offset = i * 2
            for record in dataset.records[offset : offset + 2]:
                users_responses = {
                    f"{user.username}.status": status.value,
                    f"{another_user.username}.status": status.value,
                }
                opensearch.update(index_name, id=record.id, body={"doc": {"responses": users_responses}})
        opensearch.indices.refresh(index=index_name)
