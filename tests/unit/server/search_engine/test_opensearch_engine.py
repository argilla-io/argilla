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
from typing import TYPE_CHECKING, Any, AsyncGenerator, List, Optional, Union

from argilla.server.enums import MetadataPropertyType, ResponseStatusFilter
from argilla.server.models import Record, User, VectorSettings
from argilla.server.search_engine import (
    FloatMetadataFilter,
    IntegerMetadataFilter,
    SortBy,
    StringQuery,
    TermsMetadataFilter,
    UserResponseStatusFilter,
)
from argilla.server.search_engine.commons import ALL_RESPONSES_STATUSES_FIELD, index_name_for_dataset
from argilla.server.settings import settings as server_settings
from opensearchpy import RequestError

from tests.factories import (
    FloatMetadataPropertyFactory,
    IntegerMetadataPropertyFactory,
    LabelSelectionQuestionFactory,
    MultiLabelSelectionQuestionFactory,
    ResponseFactory,
    TermsMetadataPropertyFactory,
    UserFactory,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

import random

import pytest
import pytest_asyncio
from argilla.server.models import Dataset
from argilla.server.search_engine.opensearch import OpenSearchEngine
from opensearchpy import OpenSearch

from tests.factories import (
    DatasetFactory,
    RatingQuestionFactory,
    RecordFactory,
    TextFieldFactory,
    TextQuestionFactory,
    VectorFactory,
    VectorSettingsFactory,
)


@pytest_asyncio.fixture(scope="function")
async def dataset_for_pagination(opensearch: OpenSearch):
    from opensearchpy import helpers

    dataset = await DatasetFactory.create(fields=[], questions=[])
    records = await RecordFactory.create_batch(size=100, dataset=dataset)
    await dataset.awaitable_attrs.records
    index_name = index_name_for_dataset(dataset)

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
async def test_banking_sentiment_dataset(opensearch_engine: OpenSearchEngine, opensearch: OpenSearch) -> Dataset:
    text_question = await TextQuestionFactory.create()
    rating_question = await RatingQuestionFactory.create()

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

    await _refresh_dataset(dataset)
    await opensearch_engine.create_index(dataset)

    await opensearch_engine.index_records(
        dataset,
        records=[
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
        ],
    )
    await dataset.awaitable_attrs.records

    opensearch.indices.refresh(index=index_name_for_dataset(dataset))

    return dataset


@pytest_asyncio.fixture(scope="function")
@pytest.mark.asyncio
async def test_banking_sentiment_dataset_with_vectors(
    opensearch_engine: OpenSearchEngine, opensearch: OpenSearch, test_banking_sentiment_dataset: Dataset
) -> Dataset:
    vectors_settings = await VectorSettingsFactory.create_batch(5, dataset=test_banking_sentiment_dataset)

    for settings in vectors_settings:
        await opensearch_engine.configure_index_vectors(settings)

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

    await opensearch_engine.set_records_vectors(test_banking_sentiment_dataset, vectors=vectors)

    opensearch.indices.refresh(index=index_name_for_dataset(test_banking_sentiment_dataset))

    await test_banking_sentiment_dataset.awaitable_attrs.vectors_settings
    await test_banking_sentiment_dataset.awaitable_attrs.records

    return test_banking_sentiment_dataset


@pytest_asyncio.fixture()
async def opensearch_engine(elasticsearch_config: dict) -> AsyncGenerator[OpenSearchEngine, None]:
    engine = OpenSearchEngine(config=elasticsearch_config, number_of_replicas=0, number_of_shards=1)
    yield engine

    await engine.client.close()


async def _refresh_dataset(dataset: Dataset):
    await dataset.awaitable_attrs.fields
    await dataset.awaitable_attrs.questions
    await dataset.awaitable_attrs.metadata_properties
    await dataset.awaitable_attrs.vectors_settings


@pytest.mark.asyncio
@pytest.mark.skipif(not server_settings.search_engine == "opensearch", reason="Running on opensearch engine")
class TestSuiteOpenSearchEngine:
    async def test_get_index_or_raise(self, opensearch_engine: OpenSearchEngine):
        dataset = await DatasetFactory.create()
        with pytest.raises(
            ValueError, match=f"Cannot access to index for dataset {dataset.id}: the specified index does not exist"
        ):
            await opensearch_engine._get_index_or_raise(dataset)

    async def test_create_index_for_dataset(
        self, opensearch_engine: OpenSearchEngine, db: "AsyncSession", opensearch: OpenSearch
    ):
        dataset = await DatasetFactory.create()

        await _refresh_dataset(dataset)

        await opensearch_engine.create_index(dataset)

        index_name = index_name_for_dataset(dataset)
        assert opensearch.indices.exists(index=index_name)

        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"] == {
            "dynamic": "strict",
            "dynamic_templates": [
                {
                    "status_responses": {
                        "mapping": {"type": "keyword", "copy_to": ALL_RESPONSES_STATUSES_FIELD},
                        "path_match": "responses.*.status",
                    }
                }
            ],
            "properties": {
                "id": {"type": "keyword"},
                "inserted_at": {"type": "date_nanos"},
                "updated_at": {"type": "date_nanos"},
                ALL_RESPONSES_STATUSES_FIELD: {"type": "keyword"},
                "responses": {"dynamic": "true", "type": "object"},
                "metadata": {"dynamic": "false", "type": "object"},
            },
        }
        assert index["settings"]["index"]["knn"] == "false"
        assert index["settings"]["index"]["max_result_window"] == str(opensearch_engine.max_result_window)
        assert index["settings"]["index"]["number_of_shards"] == str(opensearch_engine.number_of_shards)
        assert index["settings"]["index"]["number_of_replicas"] == str(opensearch_engine.number_of_replicas)

    async def test_create_index_for_dataset_with_fields(
        self,
        opensearch_engine: OpenSearchEngine,
        opensearch: OpenSearch,
        db: "AsyncSession",
    ):
        text_fields = await TextFieldFactory.create_batch(5)
        dataset = await DatasetFactory.create(fields=text_fields)

        await _refresh_dataset(dataset)

        await opensearch_engine.create_index(dataset)

        index_name = index_name_for_dataset(dataset)
        assert opensearch.indices.exists(index=index_name)

        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"] == {
            "dynamic": "strict",
            "dynamic_templates": [
                {
                    "status_responses": {
                        "mapping": {"type": "keyword", "copy_to": ALL_RESPONSES_STATUSES_FIELD},
                        "path_match": "responses.*.status",
                    }
                }
            ],
            "properties": {
                "id": {"type": "keyword"},
                "inserted_at": {"type": "date_nanos"},
                "updated_at": {"type": "date_nanos"},
                ALL_RESPONSES_STATUSES_FIELD: {"type": "keyword"},
                "fields": {"properties": {field.name: {"type": "text"} for field in dataset.fields}},
                "responses": {"type": "object", "dynamic": "true"},
                "metadata": {"dynamic": "false", "type": "object"},
            },
        }

    async def test_create_metadata_property(
        self,
        opensearch_engine: OpenSearchEngine,
        opensearch: OpenSearch,
        db: "AsyncSession",
    ):
        text_field = await TextFieldFactory.create(name="field")

        terms_property = await TermsMetadataPropertyFactory.create(name="terms")
        integer_property = await IntegerMetadataPropertyFactory.create(name="integer")
        float_property = await FloatMetadataPropertyFactory.create(name="float")

        metadata_properties = [terms_property, integer_property]

        dataset = await DatasetFactory.create(fields=[text_field], metadata_properties=metadata_properties)

        await _refresh_dataset(dataset)

        await opensearch_engine.create_index(dataset)
        await opensearch_engine.configure_metadata_property(dataset, float_property)

        index_name = index_name_for_dataset(dataset)
        assert opensearch.indices.exists(index=index_name)

        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"]["properties"]["metadata"]["properties"][str(float_property.name)] == {"type": "float"}

    async def test_create_index_for_dataset_with_metadata_properties(
        self,
        opensearch_engine: OpenSearchEngine,
        opensearch: OpenSearch,
        db: "AsyncSession",
    ):
        text_field = await TextFieldFactory.create(name="field")

        terms_property = await TermsMetadataPropertyFactory.create(name="terms")
        integer_property = await IntegerMetadataPropertyFactory.create(name="integer")
        float_property = await FloatMetadataPropertyFactory.create(name="float")

        metadata_properties = [terms_property, integer_property, float_property]

        dataset = await DatasetFactory.create(fields=[text_field], metadata_properties=metadata_properties)

        await _refresh_dataset(dataset)

        await opensearch_engine.create_index(dataset)

        index_name = index_name_for_dataset(dataset)
        assert opensearch.indices.exists(index=index_name)

        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"] == {
            "dynamic": "strict",
            "dynamic_templates": [
                {
                    "status_responses": {
                        "mapping": {"type": "keyword", "copy_to": ALL_RESPONSES_STATUSES_FIELD},
                        "path_match": "responses.*.status",
                    }
                }
            ],
            "properties": {
                "id": {"type": "keyword"},
                "inserted_at": {"type": "date_nanos"},
                "updated_at": {"type": "date_nanos"},
                ALL_RESPONSES_STATUSES_FIELD: {"type": "keyword"},
                "fields": {"properties": {"field": {"type": "text"}}},
                "responses": {"type": "object", "dynamic": "true"},
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
        opensearch_engine: OpenSearchEngine,
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

        await _refresh_dataset(dataset)

        await opensearch_engine.create_index(dataset)

        index_name = index_name_for_dataset(dataset)
        assert opensearch.indices.exists(index=index_name)

        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"] == {
            "dynamic": "strict",
            "properties": {
                "id": {"type": "keyword"},
                "inserted_at": {"type": "date_nanos"},
                "updated_at": {"type": "date_nanos"},
                ALL_RESPONSES_STATUSES_FIELD: {"type": "keyword"},
                "responses": {"dynamic": "true", "type": "object"},
                "metadata": {"dynamic": "false", "type": "object"},
            },
            "dynamic_templates": [
                {
                    "status_responses": {
                        "mapping": {"type": "keyword", "copy_to": ALL_RESPONSES_STATUSES_FIELD},
                        "path_match": "responses.*.status",
                    }
                },
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
        self, opensearch_engine: OpenSearchEngine, opensearch: OpenSearch, db: "AsyncSession"
    ):
        dataset = await DatasetFactory.create()

        await _refresh_dataset(dataset)

        await opensearch_engine.create_index(dataset)

        index_name = index_name_for_dataset(dataset)
        assert opensearch.indices.exists(index=index_name)

        with pytest.raises(RequestError, match="resource_already_exists_exception"):
            await opensearch_engine.create_index(dataset)

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
            (StringQuery(q="card"), 5),
            (StringQuery(q="account"), 1),
            (StringQuery(q="payment"), 6),
            (StringQuery(q="cash"), 3),
            (StringQuery(q="card payment"), 5),
            (StringQuery(q="nothing"), 0),
            (StringQuery(q="rate negative"), 1),  # Terms are found in two different fields
            (StringQuery(q="negative", field="label"), 4),
            (StringQuery(q="00000", field="textId"), 1),
            (StringQuery(q="card payment", field="text"), 5),
        ],
    )
    async def test_search_with_query_string(
        self,
        opensearch_engine: OpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset: Dataset,
        query: Union[str, StringQuery],
        expected_items: int,
    ):
        result = await opensearch_engine.search(test_banking_sentiment_dataset, query=query)

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
        opensearch_engine: OpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset: Dataset,
        statuses: List[ResponseStatusFilter],
        expected_items: int,
    ):
        user = await UserFactory.create()

        await self._configure_record_responses(
            opensearch, test_banking_sentiment_dataset, statuses, expected_items, user
        )

        result = await opensearch_engine.search(
            test_banking_sentiment_dataset,
            query=StringQuery(q="payment"),
            user_response_status_filter=UserResponseStatusFilter(user=user, statuses=statuses),
        )
        assert len(result.items) == expected_items
        assert result.total == expected_items

    @pytest.mark.parametrize(
        "statuses, expected_items",
        [
            ([], 9),
            ([ResponseStatusFilter.missing], 3),
            ([ResponseStatusFilter.draft], 5),
            ([ResponseStatusFilter.submitted], 3),
            ([ResponseStatusFilter.discarded], 2),
            ([ResponseStatusFilter.missing, ResponseStatusFilter.draft], 5),
            ([ResponseStatusFilter.submitted, ResponseStatusFilter.discarded], 3),
            ([ResponseStatusFilter.missing, ResponseStatusFilter.draft, ResponseStatusFilter.discarded], 4),
        ],
    )
    async def test_search_with_response_status_filter_with_no_user(
        self,
        opensearch_engine: OpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset: Dataset,
        statuses: List[ResponseStatusFilter],
        expected_items: int,
    ):
        await self._configure_record_responses(opensearch, test_banking_sentiment_dataset, statuses, expected_items)

        result = await opensearch_engine.search(
            test_banking_sentiment_dataset,
            user_response_status_filter=UserResponseStatusFilter(statuses=statuses, user=None),
        )

        assert len(result.items) == expected_items
        assert result.total == expected_items

    @pytest.mark.parametrize(
        ("metadata_filters_config", "expected_items"),
        [
            ([{"name": "label", "values": ["neutral"]}], 4),
            ([{"name": "label", "values": ["positive"]}], 1),
            ([{"name": "label", "values": ["neutral", "positive"]}], 5),
            ([{"name": "textId", "ge": 3, "le": 4}], 2),
            ([{"name": "textId", "ge": 3, "le": 3}], 1),
            ([{"name": "textId", "ge": 3}], 6),
            ([{"name": "textId", "le": 4}], 5),
            ([{"name": "seq_float", "ge": 0.0, "le": 12.03}], 3),
            ([{"name": "seq_float", "ge": 0.13, "le": 0.13}], 1),
            ([{"name": "seq_float", "ge": 0.0}], 7),
            ([{"name": "seq_float", "le": 12.03}], 5),
        ],
    )
    async def test_search_with_metadata_filter(
        self,
        opensearch_engine: OpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset: Dataset,
        metadata_filters_config: List[dict],
        expected_items: int,
    ):
        metadata_filters = []
        for metadata_filter_config in metadata_filters_config:
            name = metadata_filter_config.pop("name")
            for metadata_property in test_banking_sentiment_dataset.metadata_properties:
                if name == metadata_property.name:
                    if metadata_property.type == MetadataPropertyType.terms:
                        filter_cls = TermsMetadataFilter
                    elif metadata_property.type == MetadataPropertyType.integer:
                        filter_cls = IntegerMetadataFilter
                    else:
                        filter_cls = FloatMetadataFilter
                    metadata_filters.append(filter_cls(metadata_property=metadata_property, **metadata_filter_config))
                    break

        result = await opensearch_engine.search(test_banking_sentiment_dataset, metadata_filters=metadata_filters)
        assert len(result.items) == expected_items
        assert result.total == expected_items

    async def test_search_with_no_query(
        self,
        opensearch_engine: OpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset: Dataset,
    ):
        result = await opensearch_engine.search(test_banking_sentiment_dataset)
        assert len(result.items) == len(test_banking_sentiment_dataset.records)
        assert result.total == len(test_banking_sentiment_dataset.records)

        result_scores = set([item.score for item in result.items])
        assert result_scores == {1.0}

    async def test_search_with_response_status_filter_does_not_affect_the_result_scores(
        self, opensearch_engine: OpenSearchEngine, opensearch: OpenSearch, test_banking_sentiment_dataset: Dataset
    ):
        user = await UserFactory.create()

        all_statuses = [ResponseStatusFilter.missing, ResponseStatusFilter.draft, ResponseStatusFilter.discarded]
        await self._configure_record_responses(
            opensearch, test_banking_sentiment_dataset, all_statuses, len(test_banking_sentiment_dataset.records), user
        )

        no_filter_results = await opensearch_engine.search(
            test_banking_sentiment_dataset, query=StringQuery(q="payment")
        )

        results = await opensearch_engine.search(
            test_banking_sentiment_dataset,
            query=StringQuery(q="payment"),
            user_response_status_filter=UserResponseStatusFilter(user=user, statuses=all_statuses),
        )

        assert len(no_filter_results.items) == len(results.items)
        assert no_filter_results.total == results.total
        assert [item.score for item in no_filter_results.items] == [item.score for item in results.items]

    @pytest.mark.parametrize(("offset", "limit"), [(0, 50), (10, 5), (0, 0), (90, 100)])
    async def test_search_with_pagination(
        self,
        opensearch_engine: OpenSearchEngine,
        opensearch: OpenSearch,
        dataset_for_pagination: Dataset,
        offset: int,
        limit: int,
    ):
        results = await opensearch_engine.search(dataset_for_pagination, query="documents", offset=offset, limit=limit)

        assert len(results.items) == min(len(dataset_for_pagination.records) - offset, limit)
        assert results.total == 100

        records = sorted(dataset_for_pagination.records, key=lambda r: r.id)
        assert [record.id for record in records[offset : offset + limit]] == [item.record_id for item in results.items]

    @pytest.mark.parametrize(
        ("sort_by"),
        [
            SortBy(field="inserted_at"),
            SortBy(field="updated_at"),
            SortBy(field="inserted_at", order="desc"),
            SortBy(field="updated_at", order="desc"),
        ],
    )
    async def test_search_with_sort_by(
        self,
        opensearch_engine: OpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset: Dataset,
        sort_by: SortBy,
    ):
        def _local_sort_by(record: Record) -> Any:
            if isinstance(sort_by.field, str):
                return getattr(record, sort_by.field)
            return record.metadata_[sort_by.field.name]

        results = await opensearch_engine.search(test_banking_sentiment_dataset, sort_by=[sort_by])

        records = test_banking_sentiment_dataset.records
        if sort_by:
            records = sorted(records, key=_local_sort_by, reverse=sort_by.order == "desc")

        assert [item.record_id for item in results.items] == [record.id for record in records]

    async def test_index_records(self, opensearch_engine: OpenSearchEngine, opensearch: OpenSearch):
        text_fields = await TextFieldFactory.create_batch(5)
        dataset = await DatasetFactory.create(fields=text_fields, questions=[])
        records = await RecordFactory.create_batch(
            size=10,
            dataset=dataset,
            fields={field.name: f"This is the value for {field.name}" for field in text_fields},
            responses=[],
        )

        await _refresh_dataset(dataset)

        await opensearch_engine.create_index(dataset)
        await opensearch_engine.index_records(dataset, records)

        index_name = index_name_for_dataset(dataset)
        opensearch.indices.refresh(index=index_name)

        es_docs = [hit["_source"] for hit in opensearch.search(index=index_name)["hits"]["hits"]]
        assert es_docs == [
            {
                "id": str(record.id),
                "fields": record.fields,
                "inserted_at": record.inserted_at.isoformat(),
                "updated_at": record.updated_at.isoformat(),
                "metadata": {},
                "responses": {},
            }
            for record in records
        ]

    async def test_configure_metadata_property(self, opensearch_engine: OpenSearchEngine, opensearch: OpenSearch):
        dataset = await DatasetFactory.create()
        await _refresh_dataset(dataset)

        await opensearch_engine.create_index(dataset)

        terms_property = await TermsMetadataPropertyFactory.create(name="terms")
        await opensearch_engine.configure_metadata_property(dataset, terms_property)

        index_name = index_name_for_dataset(dataset)
        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"]["properties"]["metadata"] == {
            "dynamic": "false",
            "properties": {str(terms_property.name): {"type": "keyword"}},
        }

    async def test_index_records_with_metadata(self, opensearch_engine: OpenSearchEngine, opensearch: OpenSearch):
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

        await _refresh_dataset(dataset)

        await opensearch_engine.create_index(dataset)
        await opensearch_engine.index_records(dataset, records)

        index_name = index_name_for_dataset(dataset)
        opensearch.indices.refresh(index=index_name)

        es_docs = [hit["_source"] for hit in opensearch.search(index=index_name)["hits"]["hits"]]
        assert es_docs == [
            {
                "id": str(record.id),
                "fields": record.fields,
                "inserted_at": record.inserted_at.isoformat(),
                "updated_at": record.updated_at.isoformat(),
                "responses": {},
                "metadata": {
                    str(metadata_prop.name): record.metadata_[metadata_prop.name]
                    for metadata_prop in metadata_properties
                },
            }
            for record in records
        ]

    async def test_index_records_with_vectors(self, opensearch_engine: OpenSearchEngine, opensearch: OpenSearch):
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
            await record.awaitable_attrs.vectors

        await _refresh_dataset(dataset)

        await opensearch_engine.create_index(dataset)
        await opensearch_engine.index_records(dataset, records)

        index_name = index_name_for_dataset(dataset)
        opensearch.indices.refresh(index=index_name)

        es_docs = [hit["_source"] for hit in opensearch.search(index=index_name)["hits"]["hits"]]
        assert es_docs == [
            {
                "id": str(record.id),
                "fields": record.fields,
                "inserted_at": record.inserted_at.isoformat(),
                "updated_at": record.updated_at.isoformat(),
                "responses": {},
                "metadata": {},
                "vectors": {str(vector_settings.id): [1.0, 2.0, 3.0, 4.0, 5.0] for vector_settings in vectors_settings},
            }
            for record in records
        ]

    async def test_delete_records(self, opensearch_engine: OpenSearchEngine, opensearch: OpenSearch):
        text_fields = await TextFieldFactory.create_batch(5)
        dataset = await DatasetFactory.create(fields=text_fields, questions=[])
        records = await RecordFactory.create_batch(
            size=10,
            dataset=dataset,
            fields={field.name: f"This is the value for {field.name}" for field in text_fields},
            responses=[],
        )

        await _refresh_dataset(dataset)

        await opensearch_engine.create_index(dataset)
        await opensearch_engine.index_records(dataset, records)

        records_to_delete, records_to_keep = records[:5], records[5:]
        await opensearch_engine.delete_records(dataset, records_to_delete)

        index_name = index_name_for_dataset(dataset)
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
        opensearch_engine: OpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset: Dataset,
    ):
        record = test_banking_sentiment_dataset.records[0]
        question = test_banking_sentiment_dataset.questions[0]

        response = await ResponseFactory.create(record=record, values={question.name: {"value": "test"}})
        record = await response.awaitable_attrs.record
        await record.awaitable_attrs.dataset
        await opensearch_engine.update_record_response(response)

        index_name = index_name_for_dataset(test_banking_sentiment_dataset)
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
                        "status": {"type": "keyword", "copy_to": [ALL_RESPONSES_STATUSES_FIELD]},
                        "values": {"properties": {question.name: {"index": False, "type": "text"}}},
                    }
                }
            },
        }

    async def test_delete_record_response(
        self,
        opensearch_engine: OpenSearchEngine,
        opensearch: OpenSearch,
        db: "AsyncSession",
        test_banking_sentiment_dataset: Dataset,
    ):
        record = test_banking_sentiment_dataset.records[0]
        question = test_banking_sentiment_dataset.questions[0]

        response = await ResponseFactory.create(record=record, values={question.name: {"value": "test"}})
        record = await response.awaitable_attrs.record
        await record.awaitable_attrs.dataset
        await opensearch_engine.update_record_response(response)

        index_name = index_name_for_dataset(test_banking_sentiment_dataset)

        opensearch.indices.refresh(index=index_name)

        results = opensearch.get(index=index_name, id=record.id)
        assert results["_source"]["responses"] == {
            response.user.username: {
                "values": {question.name: "test"},
                "status": response.status.value,
            }
        }

        await opensearch_engine.delete_record_response(response)

        opensearch.indices.refresh(index=index_name)

        results = opensearch.get(index=index_name, id=record.id)
        assert results["_source"]["responses"] == {}

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
        opensearch_engine: OpenSearchEngine,
        opensearch: OpenSearch,
        db: "AsyncSession",
        test_banking_sentiment_dataset: Dataset,
        property_name: str,
        expected_metrics: dict,
    ):
        for property in test_banking_sentiment_dataset.metadata_properties:
            if property.name == property_name:
                break

        metrics = await opensearch_engine.compute_metrics_for(property)

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
        opensearch_engine: OpenSearchEngine,
        db: "AsyncSession",
        property_type: MetadataPropertyType,
        expected_metrics: dict,
    ):
        dataset = await DatasetFactory.create()

        await _refresh_dataset(dataset)
        await opensearch_engine.create_index(dataset)

        if property_type == MetadataPropertyType.terms:
            property = await TermsMetadataPropertyFactory.create(dataset=dataset)
        elif property_type == MetadataPropertyType.integer:
            property = await IntegerMetadataPropertyFactory.create(dataset=dataset)
        elif property_type == MetadataPropertyType.float:
            property = await FloatMetadataPropertyFactory.create(dataset=dataset)
        else:
            pytest.fail(f"Wrong property type {property_type}")

        metrics = await opensearch_engine.compute_metrics_for(property)

        assert metrics.dict() == {"type": property_type, **expected_metrics}

    async def test_create_dataset_index_with_vectors(self, opensearch_engine: OpenSearchEngine, opensearch: OpenSearch):
        vectors_settings = await VectorSettingsFactory.create_batch(5)
        dataset = await DatasetFactory.create(vectors_settings=vectors_settings)

        await _refresh_dataset(dataset)
        await opensearch_engine.create_index(dataset)

        index_name = index_name_for_dataset(dataset)
        assert opensearch.indices.exists(index=index_name)

        index = opensearch.indices.get(index=index_name)[index_name]
        assert index["mappings"]["properties"]["vectors"]["properties"] == {
            str(settings.id): {
                "type": "knn_vector",
                "dimension": settings.dimensions,
                "method": {
                    "engine": "lucene",
                    "space_type": "l2",
                    "name": "hnsw",
                    "parameters": {"ef_construction": 4, "m": 2},
                },
            }
            for settings in vectors_settings
        }

        assert index["settings"]["index"]["knn"] == "false"

    async def test_similarity_search_with_incomplete_inputs(
        self,
        opensearch_engine: OpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset_with_vectors: Dataset,
    ):
        settings: VectorSettings = test_banking_sentiment_dataset_with_vectors.vectors_settings[0]
        with pytest.raises(
            expected_exception=ValueError, match="Must provide vector value or record to compute the similarity search"
        ):
            await opensearch_engine.similarity_search(
                dataset=test_banking_sentiment_dataset_with_vectors, vector_settings=settings
            )

    async def test_similarity_search_by_vector_value(
        self,
        opensearch_engine: OpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset_with_vectors: Dataset,
    ):
        selected_record = test_banking_sentiment_dataset_with_vectors.records[0]
        selected_vector = selected_record.vectors[0]

        responses = await opensearch_engine.similarity_search(
            dataset=test_banking_sentiment_dataset_with_vectors,
            vector_settings=selected_vector.vector_settings,
            value=selected_vector.value,
            max_results=1,
        )

        assert responses.total == 1
        assert responses.items[0].record_id == selected_record.id

    async def test_similarity_search_by_record(
        self,
        opensearch_engine: OpenSearchEngine,
        opensearch: OpenSearch,
        test_banking_sentiment_dataset_with_vectors: Dataset,
    ):
        selected_record: Record = test_banking_sentiment_dataset_with_vectors.records[0]
        vector_settings: VectorSettings = test_banking_sentiment_dataset_with_vectors.vectors_settings[0]

        responses = await opensearch_engine.similarity_search(
            dataset=test_banking_sentiment_dataset_with_vectors,
            vector_settings=vector_settings,
            record=selected_record,
            max_results=1,
        )

        assert responses.total == 1
        assert responses.items[0].record_id == selected_record.id

    async def _configure_record_responses(
        self,
        opensearch: OpenSearch,
        dataset: Dataset,
        response_status: List[ResponseStatusFilter],
        number_of_answered_records: int,
        user: Optional[User] = None,
    ):
        index_name = index_name_for_dataset(dataset)

        all_statuses = [
            ResponseStatusFilter.draft,
            ResponseStatusFilter.missing,
            ResponseStatusFilter.discarded,
            ResponseStatusFilter.submitted,
        ]
        selected_records = dataset.records[:number_of_answered_records]
        rest_of_the_records = dataset.records[number_of_answered_records:]

        # Create two responses with the same status (one in each record)
        for i, status in enumerate(response_status):
            if status != ResponseStatusFilter.missing:
                await self._update_records_responses(opensearch, index_name, selected_records, status, user)

        for status in all_statuses:
            if status not in response_status and status != ResponseStatusFilter.missing:
                await self._update_records_responses(opensearch, index_name, rest_of_the_records, status, user)

        opensearch.indices.refresh(index=index_name)

    async def _update_records_responses(
        self,
        opensearch: OpenSearch,
        index_name: str,
        records: List[Record],
        status: ResponseStatusFilter,
        user: Optional[User] = None,
    ):
        another_user = await UserFactory.create()

        for record in records:
            users_responses = {f"{another_user.username}.status": status.value}
            if user:
                users_responses.update({f"{user.username}.status": status.value})
            opensearch.update(index_name, id=record.id, body={"doc": {"responses": users_responses}})
