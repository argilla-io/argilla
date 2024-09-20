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
import uuid
from typing import Any, Dict, List, Optional, Union, Sequence

import pytest
import pytest_asyncio
from opensearchpy import OpenSearch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from argilla_server.enums import (
    MetadataPropertyType,
    QuestionType,
    ResponseStatusFilter,
    SimilarityOrder,
    RecordStatus,
    SortOrder,
)
from argilla_server.models import Dataset, Question, Record, User, VectorSettings, Vector
from argilla_server.search_engine import (
    ResponseFilterScope,
    SuggestionFilterScope,
    TermsFilter,
    TextQuery,
    Filter,
    MetadataFilterScope,
    RangeFilter,
    Order,
    RecordFilterScope,
    AndFilter,
)
from argilla_server.search_engine.commons import (
    BaseElasticAndOpenSearchEngine,
    es_index_name_for_dataset,
    es_field_for_vector_settings,
)
from argilla_server.settings import settings as server_settings
from tests.factories import (
    DatasetFactory,
    FloatMetadataPropertyFactory,
    IntegerMetadataPropertyFactory,
    LabelSelectionQuestionFactory,
    MultiLabelSelectionQuestionFactory,
    QuestionFactory,
    RatingQuestionFactory,
    RecordFactory,
    ResponseFactory,
    SuggestionFactory,
    TermsMetadataPropertyFactory,
    TextFieldFactory,
    TextQuestionFactory,
    UserFactory,
    VectorFactory,
    VectorSettingsFactory,
    ImageFieldFactory,
    ChatFieldFactory,
)


@pytest_asyncio.fixture(scope="function")
async def dataset_for_pagination(opensearch: OpenSearch):
    from opensearchpy import helpers

    dataset = await DatasetFactory.create(fields=[], questions=[])
    records = await RecordFactory.create_batch(size=100, dataset=dataset)
    await dataset.awaitable_attrs.records
    index_name = es_index_name_for_dataset(dataset)

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
async def test_banking_sentiment_dataset_non_indexed():
    text_question = await TextQuestionFactory(name="text")
    rating_question = await RatingQuestionFactory(name="rating")

    dataset = await DatasetFactory.create(
        fields=[
            await TextFieldFactory.create(name="textId"),
            await TextFieldFactory.create(name="text"),
            await TextFieldFactory.create(name="label"),
        ],
        metadata_properties=[
            await TermsMetadataPropertyFactory.create(name="label"),
            await IntegerMetadataPropertyFactory.create(name="textId"),
            await FloatMetadataPropertyFactory.create(name="seq_float"),
        ],
        questions=[text_question, rating_question],
    )

    records = [
        await RecordFactory.create(
            dataset=dataset,
            fields={"textId": "00000", "text": "My card payment had the wrong exchange rate", "label": "negative"},
            metadata_={"label": None, "textId": "00000", "seq_float": 0.13},
            responses=[],
        ),
        await RecordFactory.create(
            dataset=dataset,
            fields={
                "textId": "00001",
                "text": "I believe that a card payment I made was cancelled.",
                "label": "neutral",
            },
            metadata_={"label": "neutral", "textId": "00001", "seq_float": 0.343},
            responses=[],
        ),
        await RecordFactory.create(
            dataset=dataset,
            fields={
                "textId": "00002",
                "text": "I tried to make a payment with my card and it was declined.",
                "label": "negative",
            },
            metadata_={"label": "negative", "textId": "00002", "seq_float": 1.123},
            responses=[],
        ),
        await RecordFactory.create(
            dataset=dataset,
            fields={
                "textId": "00003",
                "text": "My credit card was declined when I tried to make a payment.",
                "label": "negative",
            },
            metadata_={"label": "negative", "textId": "00003", "seq_float": 12.13},
            responses=[],
        ),
        await RecordFactory.create(
            dataset=dataset,
            fields={
                "textId": "00004",
                "text": "I made a successful payment towards my mortgage loan earlier today.",
                "label": "positive",
            },
            metadata_={"label": "positive", "textId": "00004", "seq_float": -120.13},
            responses=[],
        ),
        await RecordFactory.create(
            dataset=dataset,
            fields={
                "textId": "00005",
                "text": "Please confirm the receipt of my payment for the credit card bill due on the 15th.",
                "label": "neutral",
            },
            metadata_={"label": "neutral", "textId": "00005", "seq_float": -149.13},
            responses=[],
        ),
        await RecordFactory.create(
            dataset=dataset,
            fields={
                "textId": "00006",
                "text": "Why was I charged for getting cash?",
                "label": "neutral",
            },
            metadata_={"label": "neutral", "textId": "00006", "seq_float": 200.13},
            responses=[],
        ),
        await RecordFactory.create(
            dataset=dataset,
            fields={
                "textId": "00007",
                "text": "Why was I charged for getting cash?",
                "label": "neutral",
            },
            metadata_={"label": "neutral", "textId": "00007", "seq_float": 20020.13},
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
            metadata_={"label": "negative", "textId": "00008", "seq_float": 120020.13},
            responses=[],
        ),
    ]

    await refresh_dataset(dataset)
    await refresh_records(records)
    await dataset.awaitable_attrs.records

    return dataset


@pytest_asyncio.fixture(scope="function")
@pytest.mark.asyncio
async def test_banking_sentiment_dataset(
    search_engine: BaseElasticAndOpenSearchEngine,
    opensearch: OpenSearch,
    test_banking_sentiment_dataset_non_indexed: Dataset,
) -> Dataset:
    records = test_banking_sentiment_dataset_non_indexed.records

    await search_engine.create_index(test_banking_sentiment_dataset_non_indexed)
    await search_engine.index_records(test_banking_sentiment_dataset_non_indexed, records=records)

    return test_banking_sentiment_dataset_non_indexed


@pytest_asyncio.fixture(scope="function")
@pytest.mark.asyncio
async def test_banking_sentiment_dataset_with_vectors(
    search_engine: BaseElasticAndOpenSearchEngine, opensearch: OpenSearch, test_banking_sentiment_dataset: Dataset
) -> Dataset:
    vectors_settings = await VectorSettingsFactory.create_batch(5, dataset=test_banking_sentiment_dataset)

    for settings in vectors_settings:
        await search_engine.configure_index_vectors(settings)

    vectors = []
    for record in test_banking_sentiment_dataset.records:
        for settings in vectors_settings:
            vectors.append(
                await VectorFactory.create(
                    vector_settings=settings,
                    record=record,
                    value=[random.uniform(-10, 10) for _ in range(0, settings.dimensions)],
                )
            )
        await record.awaitable_attrs.vectors

    await set_records_vectors(search_engine, test_banking_sentiment_dataset, vectors=vectors)

    await refresh_dataset(test_banking_sentiment_dataset)
    await test_banking_sentiment_dataset.awaitable_attrs.records

    return test_banking_sentiment_dataset


async def set_records_vectors(
    search_engine: BaseElasticAndOpenSearchEngine, dataset: Dataset, vectors: Sequence[Vector]
):
    index_name = es_index_name_for_dataset(dataset)

    bulk_actions = [
        {
            "_op_type": "update",
            "_id": vector.record_id,
            "_index": index_name,
            "doc": {es_field_for_vector_settings(vector.vector_settings): vector.value},
        }
        for vector in vectors
    ]

    await search_engine._bulk_op_request(bulk_actions)


async def refresh_dataset(dataset: Dataset):
    await dataset.awaitable_attrs.fields
    await dataset.awaitable_attrs.questions
    await dataset.awaitable_attrs.metadata_properties
    await dataset.awaitable_attrs.vectors_settings


async def refresh_records(records: List[Record]):
    for record in records:
        await record.awaitable_attrs.suggestions
        await record.awaitable_attrs.responses
        await record.awaitable_attrs.responses_submitted
        await record.awaitable_attrs.vectors


def _expected_value_for_question(question: Question) -> Dict[str, Any]:
    if question.type in [QuestionType.label_selection, QuestionType.multi_label_selection]:
        return {"type": "keyword"}
    elif question.type == QuestionType.rating:
        return {"type": "integer"}
    else:
        return {"type": "object", "enabled": False}


@pytest.mark.asyncio
@pytest.mark.skipif(
    server_settings.search_engine not in ["elasticsearch", "opensearch"],
    reason="Running on elasticsearch/opensearch engine",
)
class TestBaseElasticAndOpenSearchEngine:
    """
    This test suite check all common methods for ElasticSearch and OpenSearch engines.

    If you need to test a specific method for one of these engines, you should the
    `test_elasticsearch.py` and `test_opensearch.py` files.

    """

    async def test_create_index_for_dataset(
        self, search_engine: BaseElasticAndOpenSearchEngine, db: "AsyncSession", opensearch: OpenSearch
    ):
        dataset = await DatasetFactory.create()

        await refresh_dataset(dataset)

        await search_engine.create_index(dataset)

        index_name = es_index_name_for_dataset(dataset)
        assert opensearch.indices.exists(index=index_name)

        index = opensearch.indices.get(index=index_name, flat_settings=True)[index_name]
        assert index["mappings"] == {
            "dynamic": "strict",
            "properties": {
                "id": {"type": "keyword"},
                "status": {"type": "keyword"},
                "inserted_at": {"type": "date_nanos"},
                "updated_at": {"type": "date_nanos"},
                "metadata": {"dynamic": "false", "type": "object"},
                "responses": {
                    "dynamic": "strict",
                    "include_in_root": True,
                    "properties": {
                        "id": {"type": "keyword"},
                        "status": {"type": "keyword"},
                        "user_id": {"type": "keyword"},
                    },
                    "type": "nested",
                },
            },
        }

        assert index["settings"]["index.max_result_window"] == str(search_engine.max_result_window)
        assert index["settings"]["index.number_of_shards"] == str(search_engine.number_of_shards)
        assert index["settings"]["index.number_of_replicas"] == str(search_engine.number_of_replicas)
        assert index["settings"]["index.mapping.total_fields.limit"] == str(search_engine.default_total_fields_limit)

    async def test_create_index_for_dataset_with_fields(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        db: Session,
    ):
        text_fields = await TextFieldFactory.create_batch(2)
        image_fields = await ImageFieldFactory.create_batch(2)

        dataset = await DatasetFactory.create(fields=text_fields + image_fields)

        await refresh_dataset(dataset)

        await search_engine.create_index(dataset)

        index_name = es_index_name_for_dataset(dataset)
        assert opensearch.indices.exists(index=index_name)

        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"] == {
            "dynamic": "strict",
            "_source": {"excludes": [f"fields.{field.name}" for field in image_fields]},
            "properties": {
                "id": {"type": "keyword"},
                "status": {"type": "keyword"},
                "inserted_at": {"type": "date_nanos"},
                "updated_at": {"type": "date_nanos"},
                "fields": {
                    "properties": {
                        **{field.name: {"type": "text"} for field in text_fields},
                        **{field.name: {"type": "object", "enabled": False} for field in image_fields},
                    }
                },
                "metadata": {"dynamic": "false", "type": "object"},
                "responses": {
                    "dynamic": "strict",
                    "include_in_root": True,
                    "properties": {
                        "id": {"type": "keyword"},
                        "status": {"type": "keyword"},
                        "user_id": {"type": "keyword"},
                    },
                    "type": "nested",
                },
            },
        }

    async def test_create_metadata_property(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        db: "AsyncSession",
    ):
        text_field = await TextFieldFactory.create(name="field")

        terms_property = await TermsMetadataPropertyFactory.create(name="terms")
        integer_property = await IntegerMetadataPropertyFactory.create(name="integer")
        float_property = await FloatMetadataPropertyFactory.create(name="float")

        metadata_properties = [terms_property, integer_property]

        dataset = await DatasetFactory.create(fields=[text_field], metadata_properties=metadata_properties)

        await refresh_dataset(dataset)

        await search_engine.create_index(dataset)
        await search_engine.configure_metadata_property(dataset, float_property)

        index_name = es_index_name_for_dataset(dataset)
        assert opensearch.indices.exists(index=index_name)

        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"]["properties"]["metadata"]["properties"][str(float_property.name)] == {"type": "float"}

    async def test_create_index_for_dataset_with_metadata_properties(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        db: "AsyncSession",
    ):
        text_field = await TextFieldFactory.create(name="field")

        terms_property = await TermsMetadataPropertyFactory.create(name="terms")
        integer_property = await IntegerMetadataPropertyFactory.create(name="integer")
        float_property = await FloatMetadataPropertyFactory.create(name="float")

        metadata_properties = [terms_property, integer_property, float_property]

        dataset = await DatasetFactory.create(fields=[text_field], metadata_properties=metadata_properties)

        await refresh_dataset(dataset)

        await search_engine.create_index(dataset)

        index_name = es_index_name_for_dataset(dataset)
        assert opensearch.indices.exists(index=index_name)

        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"] == {
            "dynamic": "strict",
            "properties": {
                "id": {"type": "keyword"},
                "status": {"type": "keyword"},
                "inserted_at": {"type": "date_nanos"},
                "updated_at": {"type": "date_nanos"},
                "fields": {"properties": {"field": {"type": "text"}}},
                "responses": {
                    "dynamic": "strict",
                    "include_in_root": True,
                    "properties": {
                        "id": {"type": "keyword"},
                        "status": {"type": "keyword"},
                        "user_id": {"type": "keyword"},
                    },
                    "type": "nested",
                },
                "metadata": {
                    "dynamic": "false",
                    "properties": {
                        str(terms_property.name): {"type": "keyword"},
                        str(integer_property.name): {"type": "long"},
                        str(float_property.name): {"type": "float"},
                    },
                },
            },
        }

    @pytest.mark.parametrize(
        argnames=("text_ann_size", "rating_ann_size"),
        argvalues=[(random.randint(1, 9), random.randint(1, 9)) for _ in range(1, 5)],
    )
    async def test_create_index_for_dataset_with_questions(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
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

        await refresh_dataset(dataset)

        await search_engine.create_index(dataset)

        index_name = es_index_name_for_dataset(dataset)
        assert opensearch.indices.exists(index=index_name)

        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"] == {
            "dynamic": "strict",
            "properties": {
                "id": {"type": "keyword"},
                "status": {"type": "keyword"},
                "inserted_at": {"type": "date_nanos"},
                "updated_at": {"type": "date_nanos"},
                "metadata": {"dynamic": "false", "type": "object"},
                "responses": {
                    "dynamic": "strict",
                    "include_in_root": True,
                    "properties": {
                        "id": {"type": "keyword"},
                        "status": {"type": "keyword"},
                        "user_id": {"type": "keyword"},
                        **{question.name: _expected_value_for_question(question) for question in all_questions},
                    },
                    "type": "nested",
                },
                "suggestions": {
                    "properties": {
                        question.name: {
                            "properties": {
                                "type": {"type": "keyword"},
                                "agent": {"type": "keyword"},
                                "value": _expected_value_for_question(question),
                                "score": {"type": "float"},
                            }
                        }
                        for question in all_questions
                    }
                },
            },
        }

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
            ("cash | negative", 6),  # OR
            ("cash + negative", 1),  # AN
            ("-(cash | negative)", 3),  # NOT
            (TextQuery(q="card"), 5),
            (TextQuery(q="account"), 1),
            (TextQuery(q="payment"), 6),
            (TextQuery(q="cash"), 3),
            (TextQuery(q="card payment"), 5),
            (TextQuery(q="nothing"), 0),
            (TextQuery(q="rate negative"), 1),  # Terms are found in two different fields
            (TextQuery(q="negative", field="label"), 4),
            (TextQuery(q="00000", field="textId"), 1),
            (TextQuery(q="card payment", field="text"), 5),
            (TextQuery(q="cash | negative", field="text"), 3),
            (TextQuery(q="cash + negative", field="text"), 0),
            (TextQuery(q="-(cash | negative)", field="text"), 6),
        ],
    )
    async def test_search_with_query_string(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset: Dataset,
        query: Union[str, TextQuery],
        expected_items: int,
    ):
        result = await search_engine.search(test_banking_sentiment_dataset, query=query)

        assert len(result.items) == expected_items
        assert result.total == expected_items

        scores = [item.score > 0 for item in result.items]
        assert all(map(lambda s: s > 0, scores))

        sorted_scores = scores.copy()
        sorted_scores.sort(reverse=True)

        assert scores == sorted_scores

    async def test_search_for_chat_field(self, search_engine: BaseElasticAndOpenSearchEngine, opensearch: OpenSearch):
        chat_field = await ChatFieldFactory.create(name="field")

        dataset = await DatasetFactory.create(fields=[chat_field])

        records = await RecordFactory.create_batch(
            size=2,
            dataset=dataset,
            fields={chat_field.name: [{"role": "user", "content": "Hello world"}, {"role": "bot", "content": "Hi"}]},
        )

        await refresh_dataset(dataset)
        await refresh_records(records)

        await search_engine.create_index(dataset)
        await search_engine.index_records(dataset, records)

        result = await search_engine.search(dataset, query=TextQuery(q="world", field=chat_field.name))

        assert len(result.items) == 2
        assert result.total == 2

    @pytest.mark.parametrize(
        "statuses, expected_items",
        [
            ([], 6),
            ([ResponseStatusFilter.pending], 6),
            ([ResponseStatusFilter.draft], 2),
            ([ResponseStatusFilter.submitted], 2),
            ([ResponseStatusFilter.discarded], 2),
            ([ResponseStatusFilter.pending, ResponseStatusFilter.draft], 6),
            ([ResponseStatusFilter.submitted, ResponseStatusFilter.discarded], 4),
            ([ResponseStatusFilter.pending, ResponseStatusFilter.draft, ResponseStatusFilter.discarded], 6),
        ],
    )
    async def test_search_with_response_status_filter(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset: Dataset,
        statuses: List[ResponseStatusFilter],
        expected_items: int,
    ):
        user = await UserFactory.create()

        await self._configure_record_responses(
            opensearch, test_banking_sentiment_dataset, statuses, expected_items, user
        )

        result = await search_engine.search(
            test_banking_sentiment_dataset,
            query=TextQuery(q="payment"),
            filter=TermsFilter(scope=ResponseFilterScope(property="status"), values=statuses),
        )
        assert len(result.items) == expected_items
        assert result.total == expected_items

    async def test_search_with_response_value_without_user(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset: Dataset,
    ):
        user = await UserFactory.create()
        await self._configure_record_responses(
            opensearch,
            test_banking_sentiment_dataset,
            [ResponseStatusFilter.draft],
            number_of_answered_records=2,
            user=user,
            rating_value=2,
        )

        another_user = await UserFactory.create()
        await self._configure_record_responses(
            opensearch,
            test_banking_sentiment_dataset,
            [ResponseStatusFilter.draft],
            number_of_answered_records=3,
            user=another_user,
            rating_value=4,
        )

        results_for_user = await search_engine.search(
            test_banking_sentiment_dataset,
            filter=TermsFilter(ResponseFilterScope(question="rating", user=None), values=["2"]),
        )
        assert results_for_user.total == 2

        results_for_another_user = await search_engine.search(
            test_banking_sentiment_dataset,
            filter=TermsFilter(ResponseFilterScope(question="rating", user=None), values=["4"]),
        )
        assert results_for_another_user.total == 3

        combined_results = await search_engine.search(
            test_banking_sentiment_dataset,
            filter=TermsFilter(ResponseFilterScope(question="rating", user=None), values=["2", "4"]),
        )
        assert combined_results.total == 3

    @pytest.mark.parametrize(
        "statuses, expected_items",
        [
            ([], 9),
            ([ResponseStatusFilter.pending], 3),
            ([ResponseStatusFilter.draft], 5),
            ([ResponseStatusFilter.submitted], 3),
            ([ResponseStatusFilter.discarded], 2),
            ([ResponseStatusFilter.pending, ResponseStatusFilter.draft], 5),
            ([ResponseStatusFilter.submitted, ResponseStatusFilter.discarded], 3),
            ([ResponseStatusFilter.pending, ResponseStatusFilter.draft, ResponseStatusFilter.discarded], 4),
        ],
    )
    async def test_search_with_response_status_filter_with_no_user(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset: Dataset,
        statuses: List[ResponseStatusFilter],
        expected_items: int,
    ):
        await self._configure_record_responses(opensearch, test_banking_sentiment_dataset, statuses, expected_items)

        result = await search_engine.search(
            test_banking_sentiment_dataset,
            filter=TermsFilter(ResponseFilterScope(property="status"), values=statuses),
        )

        assert len(result.items) == expected_items
        assert result.total == expected_items

    @pytest.mark.parametrize(
        ("filter", "expected_items"),
        [
            (TermsFilter(scope=MetadataFilterScope(metadata_property="label"), values=["neutral"]), 4),
            (TermsFilter(scope=MetadataFilterScope(metadata_property="label"), values=["positive"]), 1),
            (TermsFilter(scope=MetadataFilterScope(metadata_property="label"), values=["neutral", "positive"]), 5),
            (RangeFilter(scope=MetadataFilterScope(metadata_property="textId"), ge=3, le=4), 2),
            (RangeFilter(scope=MetadataFilterScope(metadata_property="textId"), ge=3, le=3), 1),
            (RangeFilter(scope=MetadataFilterScope(metadata_property="textId"), ge=3), 6),
            (RangeFilter(scope=MetadataFilterScope(metadata_property="textId"), le=4), 5),
            (RangeFilter(scope=MetadataFilterScope(metadata_property="seq_float"), ge=0, le=12.03), 3),
            (RangeFilter(scope=MetadataFilterScope(metadata_property="seq_float"), ge=0.13, le=0.13), 1),
            (RangeFilter(scope=MetadataFilterScope(metadata_property="seq_float"), ge=0.0), 7),
            (RangeFilter(scope=MetadataFilterScope(metadata_property="seq_float"), le=12.03), 5),
            (
                AndFilter(
                    filters=[
                        TermsFilter(scope=MetadataFilterScope(metadata_property="label"), values=["negative"]),
                        RangeFilter(scope=MetadataFilterScope(metadata_property="textId"), ge=3, le=4),
                    ]
                ),
                1,
            ),
        ],
    )
    async def test_search_with_metadata_filter(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset: Dataset,
        filter: Filter,
        expected_items: int,
    ):
        result = await search_engine.search(test_banking_sentiment_dataset, filter=filter)
        assert len(result.items) == expected_items
        assert result.total == expected_items

    async def test_search_with_no_query(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset: Dataset,
    ):
        result = await search_engine.search(test_banking_sentiment_dataset)
        assert len(result.items) == len(test_banking_sentiment_dataset.records)
        assert result.total == len(test_banking_sentiment_dataset.records)

        result_scores = set([item.score for item in result.items])
        assert result_scores == {1.0}

    async def test_search_with_response_status_filter_does_not_affect_the_result_scores(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset: Dataset,
    ):
        user = await UserFactory.create()

        all_statuses = [ResponseStatusFilter.pending, ResponseStatusFilter.draft, ResponseStatusFilter.discarded]
        await self._configure_record_responses(
            opensearch, test_banking_sentiment_dataset, all_statuses, len(test_banking_sentiment_dataset.records), user
        )

        no_filter_results = await search_engine.search(test_banking_sentiment_dataset, query=TextQuery(q="payment"))

        results = await search_engine.search(
            test_banking_sentiment_dataset,
            query=TextQuery(q="payment"),
            filter=TermsFilter(scope=ResponseFilterScope(property="status", user=user), values=all_statuses),
        )

        assert len(no_filter_results.items) == len(results.items)
        assert no_filter_results.total == results.total
        assert [item.score for item in no_filter_results.items] == [item.score for item in results.items]

    @pytest.mark.parametrize(
        "property, filter_match_value, filter_unmatch_value",
        [("value", "A", "C"), ("score", "0.5", "0"), ("agent", "peter", "john"), ("type", "human", "model")],
    )
    async def test_search_with_suggestion_filter(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        property: str,
        filter_match_value: str,
        filter_unmatch_value: str,
    ):
        text_field = await TextFieldFactory.create()
        label_question = await QuestionFactory.create(
            settings={
                "type": QuestionType.label_selection.value,
                "options": [{"value": "A"}, {"value": "B"}],
            }
        )
        dataset = await DatasetFactory.create(fields=[text_field], questions=[label_question])
        records = await RecordFactory.create_batch(
            size=2,
            dataset=dataset,
            fields={text_field.name: f"This is the value for {text_field.name}"},
        )

        await SuggestionFactory.create(
            record=records[0], question=label_question, value="A", type="human", agent="peter", score=0.5
        )
        await SuggestionFactory.create(record=records[1], question=label_question, value="B")

        await refresh_dataset(dataset)
        await refresh_records(records)

        await search_engine.create_index(dataset)
        await search_engine.index_records(dataset, records)

        scope = SuggestionFilterScope(question=label_question.name, property=property)

        await self._check_filter_match(
            dataset, search_engine, filter=TermsFilter(scope=scope, values=[filter_match_value])
        )
        await self._check_filter_unmatch(
            dataset, search_engine, filter=TermsFilter(scope=scope, values=[filter_unmatch_value])
        )

    async def _check_filter_unmatch(
        self, dataset: Dataset, elasticsearch_engine: BaseElasticAndOpenSearchEngine, filter: TermsFilter
    ) -> None:
        result = await elasticsearch_engine.search(dataset, filter=filter)

        assert len(result.items) == 0
        assert result.total == 0

    async def _check_filter_match(
        self, dataset: Dataset, elasticsearch_engine: BaseElasticAndOpenSearchEngine, filter: TermsFilter
    ):
        result = await elasticsearch_engine.search(dataset, filter=filter)

        assert len(result.items) == 1
        assert result.total == 1

    @pytest.mark.parametrize(("offset", "limit"), [(0, 50), (10, 5), (0, 0), (90, 100)])
    async def test_search_with_pagination(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        dataset_for_pagination: Dataset,
        offset: int,
        limit: int,
    ):
        all_results = await search_engine.search(dataset_for_pagination, query="documents", offset=0, limit=100)
        results = await search_engine.search(dataset_for_pagination, query="documents", offset=offset, limit=limit)

        assert len(results.items) == min(len(dataset_for_pagination.records) - offset, limit)
        assert results.total == 100
        assert all_results.items[offset : offset + limit] == results.items

    @pytest.mark.parametrize(
        ("sort_order"),
        [
            Order(scope=RecordFilterScope(property="inserted_at"), order=SortOrder.asc),
            Order(scope=RecordFilterScope(property="updated_at"), order=SortOrder.asc),
            Order(scope=RecordFilterScope(property="inserted_at"), order=SortOrder.desc),
            Order(scope=RecordFilterScope(property="updated_at"), order=SortOrder.desc),
        ],
    )
    async def test_search_with_sort_by(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset: Dataset,
        sort_order: Order,
    ):
        def _local_sort_by(record: Record) -> Any:
            return getattr(record, sort_order.scope.property)

        results = await search_engine.search(test_banking_sentiment_dataset, sort=[sort_order])

        records = test_banking_sentiment_dataset.records
        records = sorted(records, key=_local_sort_by, reverse=sort_order.order == "desc")

        assert [item.record_id for item in results.items] == [record.id for record in records]

    async def test_index_records(self, search_engine: BaseElasticAndOpenSearchEngine, opensearch: OpenSearch):
        text_fields = await TextFieldFactory.create_batch(5)
        image_fields = await ImageFieldFactory.create_batch(5)

        dataset = await DatasetFactory.create(fields=text_fields + image_fields, questions=[])

        record_text_fields = {field.name: f"This is the value for {field.name}" for field in text_fields}
        record_image_fields = {field.name: f"https://random.url/{field.name}" for field in image_fields}

        records = await RecordFactory.create_batch(
            size=10,
            dataset=dataset,
            fields={
                **record_text_fields,
                **record_image_fields,
            },
            responses=[],
        )

        await refresh_dataset(dataset)
        await refresh_records(records)

        await search_engine.create_index(dataset)
        await search_engine.index_records(dataset, records)

        index_name = es_index_name_for_dataset(dataset)

        es_docs = [hit["_source"] for hit in opensearch.search(index=index_name)["hits"]["hits"]]
        assert es_docs == [
            {
                "id": str(record.id),
                "status": RecordStatus.pending,
                "fields": record_text_fields,
                "inserted_at": record.inserted_at.isoformat(),
                "updated_at": record.updated_at.isoformat(),
            }
            for record in records
        ]

    async def test_configure_metadata_property(
        self, search_engine: BaseElasticAndOpenSearchEngine, opensearch: OpenSearch
    ):
        dataset = await DatasetFactory.create()
        await refresh_dataset(dataset)

        await search_engine.create_index(dataset)

        terms_property = await TermsMetadataPropertyFactory.create(name="terms")
        await search_engine.configure_metadata_property(dataset, terms_property)

        index_name = es_index_name_for_dataset(dataset)
        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"]["properties"]["metadata"] == {
            "dynamic": "false",
            "properties": {str(terms_property.name): {"type": "keyword"}},
        }

    async def test_index_records_with_suggestions(
        self, search_engine: BaseElasticAndOpenSearchEngine, opensearch: OpenSearch
    ):
        text_field = await TextFieldFactory.create()
        label_question = await QuestionFactory.create(
            settings={
                "type": QuestionType.label_selection.value,
                "options": [{"value": "A"}, {"value": "B"}],
            }
        )
        dataset = await DatasetFactory.create(fields=[text_field], questions=[label_question])
        records = await RecordFactory.create_batch(
            size=2,
            dataset=dataset,
            fields={text_field.name: f"This is the value for {text_field.name}"},
            responses=[],
        )

        await SuggestionFactory.create(record=records[0], question=label_question, value="A")
        await SuggestionFactory.create(record=records[1], question=label_question, value="B")

        await refresh_dataset(dataset)
        await refresh_records(records)

        await search_engine.create_index(dataset)
        await search_engine.index_records(dataset, records)

        index_name = es_index_name_for_dataset(dataset)

        es_docs = [hit["_source"] for hit in opensearch.search(index=index_name)["hits"]["hits"]]
        assert es_docs == [
            {
                "id": str(records[0].id),
                "status": RecordStatus.pending,
                "fields": records[0].fields,
                "inserted_at": records[0].inserted_at.isoformat(),
                "updated_at": records[0].updated_at.isoformat(),
                "suggestions": {label_question.name: {"agent": None, "score": None, "type": None, "value": "A"}},
            },
            {
                "id": str(records[1].id),
                "status": RecordStatus.pending,
                "fields": records[1].fields,
                "inserted_at": records[1].inserted_at.isoformat(),
                "updated_at": records[1].updated_at.isoformat(),
                "suggestions": {label_question.name: {"agent": None, "score": None, "type": None, "value": "B"}},
            },
        ]

    async def test_index_records_with_metadata(
        self, search_engine: BaseElasticAndOpenSearchEngine, opensearch: OpenSearch
    ):
        text_fields = await TextFieldFactory.create_batch(5)
        metadata_properties = await TermsMetadataPropertyFactory.create_batch(3)

        dataset = await DatasetFactory.create(fields=text_fields, metadata_properties=metadata_properties, questions=[])
        records = await RecordFactory.create_batch(
            size=10,
            dataset=dataset,
            fields={field.name: f"This is the value for {field.name}" for field in text_fields},
            metadata_={metadata_prop.name: "Value for Metadata Property" for metadata_prop in metadata_properties},
            responses=[],
        )

        await refresh_dataset(dataset)
        await refresh_records(records)

        await search_engine.create_index(dataset)
        await search_engine.index_records(dataset, records)

        index_name = es_index_name_for_dataset(dataset)

        es_docs = [hit["_source"] for hit in opensearch.search(index=index_name)["hits"]["hits"]]
        assert es_docs == [
            {
                "id": str(record.id),
                "status": RecordStatus.pending,
                "fields": record.fields,
                "inserted_at": record.inserted_at.isoformat(),
                "updated_at": record.updated_at.isoformat(),
                "metadata": {
                    str(metadata_prop.name): record.metadata_[metadata_prop.name]
                    for metadata_prop in metadata_properties
                },
            }
            for record in records
        ]

    async def test_index_records_with_vectors(
        self, search_engine: BaseElasticAndOpenSearchEngine, opensearch: OpenSearch
    ):
        dataset = await DatasetFactory.create()
        text_fields = await TextFieldFactory.create_batch(size=5, dataset=dataset)
        vectors_settings = await VectorSettingsFactory.create_batch(size=5, dataset=dataset, dimensions=5)
        records = await RecordFactory.create_batch(
            size=5, fields={field.name: f"This is the value for {field.name}" for field in text_fields}, responses=[]
        )

        for record in records:
            for vector_settings in vectors_settings:
                await VectorFactory.create(
                    record=record, vector_settings=vector_settings, value=[1.0, 2.0, 3.0, 4.0, 5.0]
                )

        await refresh_dataset(dataset)
        await refresh_records(records)

        await search_engine.create_index(dataset)
        await search_engine.index_records(dataset, records)

        index_name = es_index_name_for_dataset(dataset)

        es_docs = [hit["_source"] for hit in opensearch.search(index=index_name)["hits"]["hits"]]
        assert es_docs == [
            {
                "id": str(record.id),
                "status": RecordStatus.pending,
                "fields": record.fields,
                "inserted_at": record.inserted_at.isoformat(),
                "updated_at": record.updated_at.isoformat(),
                "vectors": {str(vector_settings.id): [1.0, 2.0, 3.0, 4.0, 5.0] for vector_settings in vectors_settings},
            }
            for record in records
        ]

    async def test_delete_records(self, search_engine: BaseElasticAndOpenSearchEngine, opensearch: OpenSearch):
        text_fields = await TextFieldFactory.create_batch(5)
        dataset = await DatasetFactory.create(fields=text_fields, questions=[])
        records = await RecordFactory.create_batch(
            size=10,
            dataset=dataset,
            fields={field.name: f"This is the value for {field.name}" for field in text_fields},
            responses=[],
        )

        await refresh_dataset(dataset)
        await refresh_records(records)

        await search_engine.create_index(dataset)
        await search_engine.index_records(dataset, records)

        records_to_delete, records_to_keep = records[:5], records[5:]
        await search_engine.delete_records(dataset, records_to_delete)

        index_name = es_index_name_for_dataset(dataset)

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
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset: Dataset,
    ):
        record = test_banking_sentiment_dataset.records[0]
        question = test_banking_sentiment_dataset.questions[0]

        response = await ResponseFactory.create(record=record, values={question.name: {"value": "test"}})
        record = await response.awaitable_attrs.record
        await record.awaitable_attrs.dataset
        await search_engine.update_record_response(response)

        index_name = es_index_name_for_dataset(test_banking_sentiment_dataset)

        results = opensearch.get(index=index_name, id=record.id)

        assert results["_source"]["responses"] == [
            {"id": str(response.id), "status": "submitted", "text": "test", "user_id": str(response.user_id)},
        ]

        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"]["properties"]["responses"] == {
            "dynamic": "strict",
            "include_in_root": True,
            "properties": {
                "id": {"type": "keyword"},
                "rating": {"type": "integer"},
                "status": {"type": "keyword"},
                "text": {"enabled": False, "type": "object"},
                "user_id": {"type": "keyword"},
            },
            "type": "nested",
        }

    @pytest.mark.parametrize("annotators_size", [20, 200, 400])
    async def test_annotators_limits(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset_non_indexed: Dataset,
        annotators_size: int,
    ):
        dataset = test_banking_sentiment_dataset_non_indexed
        records = dataset.records

        annotators = await UserFactory.create_batch(size=annotators_size)

        await search_engine.create_index(dataset)
        await search_engine.index_records(dataset, records)

        record = records[0]
        question = dataset.questions[0]
        index_name = es_index_name_for_dataset(dataset)

        for user in annotators:
            await ResponseFactory.create(record=record, user=user, values={question.name: {"value": "test"}})

        await record.awaitable_attrs.dataset
        await record.awaitable_attrs.responses
        await search_engine.index_records(dataset, [record])

        properties = opensearch.indices.get_mapping(index=index_name)[index_name]["mappings"]["properties"]
        assert properties["responses"] == {
            "dynamic": "strict",
            "include_in_root": True,
            "properties": {
                "id": {"type": "keyword"},
                "status": {"type": "keyword"},
                "user_id": {"type": "keyword"},
                "rating": {"type": "integer"},
                "text": {"enabled": False, "type": "object"},
            },
            "type": "nested",
        }

    @pytest.mark.parametrize("annotators_size", [1000, 2000, 4000])
    async def test_annotator_limits_increasing_default_fields_limit(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset_non_indexed: Dataset,
        annotators_size: int,
    ):
        dataset = test_banking_sentiment_dataset_non_indexed
        records = dataset.records

        annotators = await UserFactory.create_batch(size=annotators_size)

        search_engine.default_total_fields_limit = annotators_size * 5
        await search_engine.create_index(dataset)
        await search_engine.index_records(dataset, records)

        record = records[0]
        question = dataset.questions[0]
        index_name = es_index_name_for_dataset(dataset)

        for user in annotators:
            await ResponseFactory.create(record=record, user=user, values={question.name: {"value": "test"}})

        await record.awaitable_attrs.dataset
        await record.awaitable_attrs.responses
        await search_engine.index_records(dataset, [record])

        properties = opensearch.indices.get_mapping(index=index_name)[index_name]["mappings"]["properties"]

        assert properties["responses"] == {
            "dynamic": "strict",
            "include_in_root": True,
            "properties": {
                "id": {"type": "keyword"},
                "status": {"type": "keyword"},
                "user_id": {"type": "keyword"},
                "rating": {"type": "integer"},
                "text": {"enabled": False, "type": "object"},
            },
            "type": "nested",
        }

    async def test_delete_record_response(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        db: AsyncSession,
        test_banking_sentiment_dataset: Dataset,
    ):
        record = test_banking_sentiment_dataset.records[0]
        question = test_banking_sentiment_dataset.questions[0]

        response = await ResponseFactory.create(record=record, values={question.name: {"value": "test"}})
        record = await response.awaitable_attrs.record
        await record.awaitable_attrs.dataset
        await search_engine.update_record_response(response)

        index_name = es_index_name_for_dataset(test_banking_sentiment_dataset)

        results = opensearch.get(index=index_name, id=record.id)
        assert results["_source"]["responses"] == [
            {
                "id": str(response.id),
                "status": "submitted",
                "text": "test",
                "user_id": str(response.user_id),
            },
        ]

        await search_engine.delete_record_response(response)

        results = opensearch.get(index=index_name, id=record.id)
        assert results["_source"]["responses"] == []

    @pytest.mark.parametrize(
        ("property_name", "expected_metrics"),
        [
            (
                "label",
                {
                    "total": 8,
                    "type": MetadataPropertyType.terms,
                    "values": [
                        {"count": 4, "term": "neutral"},
                        {"count": 3, "term": "negative"},
                        {"count": 1, "term": "positive"},
                    ],
                },
            ),
            ("textId", {"max": 8, "min": 0, "type": MetadataPropertyType.integer}),
            ("seq_float", {"max": 120020.1328125, "min": -149.1300048828125, "type": MetadataPropertyType.float}),
        ],
    )
    async def test_compute_metrics_for(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        db: "AsyncSession",
        test_banking_sentiment_dataset: Dataset,
        property_name: str,
        expected_metrics: dict,
    ):
        for property in test_banking_sentiment_dataset.metadata_properties:
            if property.name == property_name:
                break

        metrics = await search_engine.compute_metrics_for(property)

        assert metrics.type == property.type
        assert metrics.dict() == expected_metrics

    @pytest.mark.parametrize(
        ("property_type", "expected_metrics"),
        [
            (MetadataPropertyType.terms, {"total": 0, "values": []}),
            (MetadataPropertyType.integer, {"min": None, "max": None}),
            (MetadataPropertyType.float, {"min": None, "max": None}),
        ],
    )
    async def test_compute_metrics_for_missing_property(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        db: "AsyncSession",
        property_type: MetadataPropertyType,
        expected_metrics: dict,
    ):
        dataset = await DatasetFactory.create()

        await refresh_dataset(dataset)
        await search_engine.create_index(dataset)

        if property_type == MetadataPropertyType.terms:
            property = await TermsMetadataPropertyFactory.create(dataset=dataset)
        elif property_type == MetadataPropertyType.integer:
            property = await IntegerMetadataPropertyFactory.create(dataset=dataset)
        elif property_type == MetadataPropertyType.float:
            property = await FloatMetadataPropertyFactory.create(dataset=dataset)
        else:
            pytest.fail(f"Wrong property type {property_type}")

        metrics = await search_engine.compute_metrics_for(property)

        assert metrics.dict() == {"type": property_type, **expected_metrics}

    async def test_similarity_search_with_incomplete_inputs(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset_with_vectors: Dataset,
    ):
        settings: VectorSettings = test_banking_sentiment_dataset_with_vectors.vectors_settings[0]
        with pytest.raises(
            expected_exception=ValueError,
            match="Must provide either vector value or record to compute the similarity search",
        ):
            await search_engine.similarity_search(
                dataset=test_banking_sentiment_dataset_with_vectors, vector_settings=settings
            )

    async def test_similarity_search_with_too_much_inputs(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset_with_vectors: Dataset,
    ):
        settings: VectorSettings = test_banking_sentiment_dataset_with_vectors.vectors_settings[0]
        with pytest.raises(
            expected_exception=ValueError,
            match="Must provide either vector value or record to compute the similarity search",
        ):
            await search_engine.similarity_search(
                dataset=test_banking_sentiment_dataset_with_vectors,
                vector_settings=settings,
                value=[1, 2, 3],
                record=test_banking_sentiment_dataset_with_vectors.records[0],
            )

    async def test_similarity_search_by_vector_value(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset_with_vectors: Dataset,
    ):
        selected_record = test_banking_sentiment_dataset_with_vectors.records[0]
        selected_vector = selected_record.vectors[0]

        responses = await search_engine.similarity_search(
            dataset=test_banking_sentiment_dataset_with_vectors,
            vector_settings=selected_vector.vector_settings,
            value=selected_vector.value,
            max_results=1,
        )

        assert responses.total == 1
        assert responses.items[0].record_id == selected_record.id

    async def test_similarity_search_by_vector_value_with_order(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset_with_vectors: Dataset,
    ):
        selected_record: Record = test_banking_sentiment_dataset_with_vectors.records[0]
        vector_settings: VectorSettings = test_banking_sentiment_dataset_with_vectors.vectors_settings[0]

        responses = await search_engine.similarity_search(
            dataset=test_banking_sentiment_dataset_with_vectors,
            vector_settings=vector_settings,
            value=selected_record.vectors[0].value,
            order=SimilarityOrder.least_similar,
            max_results=1,
        )

        assert responses.total == 1
        assert responses.items[0].record_id != selected_record.id

    @pytest.mark.parametrize(
        "statuses",
        [
            [],
            [ResponseStatusFilter.pending, ResponseStatusFilter.draft],
        ],
    )
    async def test_similarity_search_by_record_and_response_status_filter(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset_with_vectors: Dataset,
        statuses: List[ResponseStatusFilter],
    ):
        selected_record: Record = test_banking_sentiment_dataset_with_vectors.records[0]
        vector_settings: VectorSettings = test_banking_sentiment_dataset_with_vectors.vectors_settings[0]

        scope = ResponseFilterScope(property="status")

        if statuses:
            test_user = await UserFactory.create()
            scope.user = test_user

        responses = await search_engine.similarity_search(
            dataset=test_banking_sentiment_dataset_with_vectors,
            vector_settings=vector_settings,
            record=selected_record,
            max_results=1,
            filter=TermsFilter(scope=scope, values=statuses),
        )

        assert responses.total == 1
        assert responses.items[0].record_id != selected_record.id

    async def test_similarity_search_by_record(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset_with_vectors: Dataset,
    ):
        selected_record: Record = test_banking_sentiment_dataset_with_vectors.records[0]
        vector_settings: VectorSettings = test_banking_sentiment_dataset_with_vectors.vectors_settings[0]

        responses = await search_engine.similarity_search(
            dataset=test_banking_sentiment_dataset_with_vectors,
            vector_settings=vector_settings,
            record=selected_record,
            max_results=1,
        )

        assert responses.total == 1
        assert responses.items[0].record_id != selected_record.id

    async def test_similarity_search_by_record_and_response_value_filter(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset_with_vectors: Dataset,
    ):
        user = await UserFactory.create()

        await self._configure_record_responses(
            opensearch,
            test_banking_sentiment_dataset_with_vectors,
            [ResponseStatusFilter.draft],
            number_of_answered_records=len(test_banking_sentiment_dataset_with_vectors.records),
            user=user,
            rating_value=2,
        )

        selected_record: Record = test_banking_sentiment_dataset_with_vectors.records[0]
        vector_settings: VectorSettings = test_banking_sentiment_dataset_with_vectors.vectors_settings[0]

        responses = await search_engine.similarity_search(
            dataset=test_banking_sentiment_dataset_with_vectors,
            vector_settings=vector_settings,
            record=selected_record,
            max_results=1,
            filter=TermsFilter(ResponseFilterScope(question="rating", user=None), values=["2"]),
        )

        assert responses.total == 1

    async def test_similarity_search_by_record_and_response_value_filter_without_responses(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset_with_vectors: Dataset,
    ):
        selected_record: Record = test_banking_sentiment_dataset_with_vectors.records[0]
        vector_settings: VectorSettings = test_banking_sentiment_dataset_with_vectors.vectors_settings[0]

        responses = await search_engine.similarity_search(
            dataset=test_banking_sentiment_dataset_with_vectors,
            vector_settings=vector_settings,
            record=selected_record,
            max_results=1,
            filter=TermsFilter(ResponseFilterScope(question="rating", user=None), values=["2"]),
        )

        assert responses.total == 0

    @pytest.mark.parametrize("query, expected_results", [("payment", 5), ("nothing to find", 0)])
    async def test_similarity_search_with_text_search(
        self,
        search_engine: BaseElasticAndOpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset_with_vectors: Dataset,
        query: str,
        expected_results: int,
    ):
        records = test_banking_sentiment_dataset_with_vectors.records
        selected_record: Record = records[0]
        vector_settings: VectorSettings = test_banking_sentiment_dataset_with_vectors.vectors_settings[0]

        responses = await search_engine.similarity_search(
            dataset=test_banking_sentiment_dataset_with_vectors,
            vector_settings=vector_settings,
            record=selected_record,
            query=TextQuery(q=query),
        )

        assert responses.total == expected_results

        for response in responses.items:
            for record in records:
                if record.id == response.record_id:
                    assert query in "\n".join(record.fields.values())

    async def _configure_record_responses(
        self,
        opensearch: OpenSearch,
        dataset: Dataset,
        response_status: List[ResponseStatusFilter],
        number_of_answered_records: int,
        user: Optional[User] = None,
        rating_value: Optional[int] = None,
    ):
        index_name = es_index_name_for_dataset(dataset)

        all_statuses = [
            ResponseStatusFilter.draft,
            ResponseStatusFilter.pending,
            ResponseStatusFilter.discarded,
            ResponseStatusFilter.submitted,
        ]
        selected_records = dataset.records[:number_of_answered_records]
        rest_of_the_records = dataset.records[number_of_answered_records:]

        # Create two responses with the same status (one in each record)
        for i, status in enumerate(response_status):
            if status != ResponseStatusFilter.pending:
                await self._update_records_responses(
                    opensearch, index_name, selected_records, status, user, rating_value
                )

        for status in all_statuses:
            if status not in response_status and status != ResponseStatusFilter.pending:
                await self._update_records_responses(opensearch, index_name, rest_of_the_records, status, user)

        opensearch.indices.refresh(index=index_name)

    async def _update_records_responses(
        self,
        opensearch: OpenSearch,
        index_name: str,
        records: List[Record],
        status: ResponseStatusFilter,
        user: Optional[User] = None,
        rating_value: Optional[int] = None,
    ):
        another_user = await UserFactory.create()

        for record in records:
            responses = [
                {
                    "id": str(uuid.uuid4()),
                    "status": status.value,
                    "user_id": str(another_user.id),
                    "rating": -1,
                }
            ]
            if user:
                responses.append(
                    {
                        "id": str(uuid.uuid4()),
                        "status": status.value,
                        "user_id": str(user.id),
                        "rating": rating_value or -1,
                    }
                )
            record_responses = opensearch.get(index=index_name, id=record.id)["_source"].get("responses") or []
            record_responses.extend(responses)

            opensearch.update(index_name, id=record.id, body={"doc": {"responses": record_responses}})
