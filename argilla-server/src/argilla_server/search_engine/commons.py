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

import dataclasses
import logging
from abc import abstractmethod
from typing import Any, Dict, Iterable, List, Optional, Union
from uuid import UUID

from elasticsearch8 import AsyncElasticsearch
from opensearchpy import AsyncOpenSearch

from argilla_server.enums import MetadataPropertyType, RecordSortField, ResponseStatusFilter, SimilarityOrder
from argilla_server.models import (
    Dataset,
    Field,
    MetadataProperty,
    Question,
    QuestionType,
    Record,
    Response,
    Suggestion,
    Vector,
    VectorSettings,
)
from argilla_server.search_engine.base import (
    AndFilter,
    Filter,
    FilterScope,
    FloatMetadataMetrics,
    IntegerMetadataMetrics,
    MetadataFilterScope,
    MetadataMetrics,
    Order,
    RangeFilter,
    RecordFilterScope,
    ResponseFilterScope,
    SearchEngine,
    SearchResponseItem,
    SearchResponses,
    SuggestionFilterScope,
    TermsFilter,
    TermsMetadataMetrics,
    TextQuery,
)


def es_index_name_for_dataset(dataset: Dataset):
    return f"rg.{dataset.id}"


def es_terms_query(field_name: str, values: List[str]) -> dict:
    return {"terms": {field_name: values}}


def es_term_query(field_name: str, value: str) -> dict:
    return {"term": {field_name: value}}


def es_range_query(field_name: str, gte: Optional[Any] = None, lte: Optional[Any] = None) -> dict:
    query = {}
    if gte is not None:
        query["gte"] = gte
    if lte is not None:
        query["lte"] = lte
    return {"range": {field_name: query}}


def es_bool_query(
    *,
    must: Optional[Any] = None,
    must_not: Optional[Any] = None,
    should: Optional[List[dict]] = None,
    minimum_should_match: Optional[Union[int, str]] = None,
) -> Dict[str, Any]:
    bool_query = {}

    if must:
        bool_query["must"] = must
    if should:
        bool_query["should"] = should
    if must_not:
        bool_query["must_not"] = must_not

    if minimum_should_match:
        bool_query["minimum_should_match"] = minimum_should_match

    return {"bool": bool_query}


def es_exists_field_query(field: str) -> dict:
    return {"exists": {"field": field}}


def es_ids_query(ids: List[str]) -> dict:
    return {"ids": {"values": ids}}


def es_simple_query_string(field_name: str, query: str) -> dict:
    # See https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-simple-query-string-query.html
    return {
        "simple_query_string": {
            "query": query,
            "fields": [field_name],
            "default_operator": "AND",
            "analyze_wildcard": False,
            "auto_generate_synonyms_phrase_query": False,
            "fuzzy_max_expansions": 10,
            "fuzzy_transpositions": False,
        }
    }


def es_nested_query(path: str, query: dict) -> dict:
    return {
        "nested": {
            "path": path,
            "query": query,
            "score_mode": "avg",
        }
    }


def es_field_for_suggestion_property(question: str, property: str) -> str:
    return f"suggestions.{question}.{property}"


def es_field_for_vector_settings(vector_settings: VectorSettings) -> str:
    return f"vectors.{es_path_for_vector_settings(vector_settings)}"


def es_field_for_record_property(property: str) -> str:
    return property


def es_field_for_metadata_property(metadata_property: Union[str, MetadataProperty]) -> str:
    if isinstance(metadata_property, MetadataProperty):
        property_name = metadata_property.name
    else:
        property_name = metadata_property

    return f"metadata.{property_name}"


def es_field_for_record_field(field_name: str) -> str:
    return f"fields.{field_name}"


def es_field_for_response_property(property: str) -> str:
    return f"responses.{property}"


def es_mapping_for_field(field: Field) -> dict:
    field_type = field.settings["type"]

    if field.is_text:
        return {es_field_for_record_field(field.name): {"type": "text"}}
    elif field.is_chat:
        es_field = {
            "type": "object",
            "properties": {
                "content": {"type": "text"},
                "role": {"type": "keyword"},
            },
        }
        return {es_field_for_record_field(field.name): es_field}
    elif field.is_custom:
        return {
            es_field_for_record_field(field.name): {
                "type": "text",
            }
        }
    elif field.is_image:
        return {
            es_field_for_record_field(field.name): {
                "type": "object",
                "enabled": False,
            }
        }
    else:
        raise Exception(f"Index configuration for field of type {field_type} cannot be generated")


def es_mapping_for_metadata_property(metadata_property: MetadataProperty) -> dict:
    property_type = metadata_property.type

    if property_type == MetadataPropertyType.terms:
        return {es_field_for_metadata_property(metadata_property): {"type": "keyword"}}
    elif property_type == MetadataPropertyType.integer:
        return {es_field_for_metadata_property(metadata_property): {"type": "long"}}
    elif property_type == MetadataPropertyType.float:
        return {es_field_for_metadata_property(metadata_property): {"type": "float"}}
    else:
        raise Exception(f"Index configuration for metadata property of type {property_type} cannot be generated")


def es_mapping_for_question(question: Question) -> dict:
    question_type = question.type

    if question_type == QuestionType.rating:
        # See https://www.elastic.co/guide/en/elasticsearch/reference/current/number.html
        return {"type": "integer"}
    elif question_type in [QuestionType.label_selection, QuestionType.multi_label_selection]:
        return {"type": "keyword"}
    else:
        # The rest of the question types will be ignored for now. Once we have a filters feat we can design
        # the proper mappings.
        # See https://www.elastic.co/guide/en/elasticsearch/reference/current/enabled.html#enabled
        return {"type": "object", "enabled": False}


def es_mapping_for_question_suggestion(question: Question) -> dict:
    return {
        f"suggestions.{question.name}": {
            "type": "object",
            "properties": {
                "value": es_mapping_for_question(question),
                "score": {"type": "float"},
                "agent": {"type": "keyword"},
                "type": {"type": "keyword"},
            },
        }
    }


def es_path_for_vector_settings(vector_settings: VectorSettings) -> str:
    return str(vector_settings.id)


def es_path_for_question_response(question_name: str) -> str:
    return f"{question_name}"


@dataclasses.dataclass
class BaseElasticAndOpenSearchEngine(SearchEngine):
    """
    Since both ElasticSearch and OpenSearch engines implementations share a lot of code,
    this class create an abstraction for the commons part of the code, letting each child
    resolve their own implementation details.

    All method for SearchEngine interface are implemented here. This abstract class defines
    some abstract method mostly for:
        1. Requesting data from the engine, since the client signatures may differ
        2. Prepare mappings for vector-related configuration (once is included)
        3. Searching records based on similarity search

    The rest of the code will be shared by both implementation
    """

    number_of_shards: int
    number_of_replicas: int

    # See https://www.elastic.co/guide/en/elasticsearch/reference/current/search-settings.html#search-settings-max-buckets
    max_terms_size: int = 2**14
    # See https://www.elastic.co/guide/en/elasticsearch/reference/5.1/index-modules.html#dynamic-index-settings
    max_result_window: int = 500000
    # See https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-settings-limit.html#mapping-settings-limit
    default_total_fields_limit: int = 2000

    client: Union[AsyncElasticsearch, AsyncOpenSearch] = dataclasses.field(init=False)

    _LOGGER = logging.getLogger(__name__)

    async def create_index(self, dataset: Dataset):
        settings = self._configure_index_settings()
        mappings = self._configure_index_mappings(dataset)

        index_name = es_index_name_for_dataset(dataset)
        await self._create_index_request(index_name, mappings, settings)

    async def delete_index(self, dataset: Dataset):
        index_name = es_index_name_for_dataset(dataset)

        await self._delete_index_request(index_name)

    async def configure_metadata_property(self, dataset: Dataset, metadata_property: MetadataProperty):
        mapping = es_mapping_for_metadata_property(metadata_property)
        index_name = es_index_name_for_dataset(dataset)

        await self.put_index_mapping_request(index_name, mapping)

    async def configure_index_vectors(self, vector_settings: VectorSettings) -> None:
        index = es_index_name_for_dataset(vector_settings.dataset)

        mappings = self._mapping_for_vector_settings(vector_settings)
        await self.put_index_mapping_request(index, mappings)

    async def index_records(self, dataset: Dataset, records: Iterable[Record]):
        index_name = es_index_name_for_dataset(dataset)

        bulk_actions = [
            {
                # If document exist, we update source with latest version
                "_op_type": "index",  # TODO: Review and maybe change to partial update
                "_id": record.id,
                "_index": index_name,
                **self._map_record_to_es_document(record),
            }
            for record in records
        ]

        await self._bulk_op_request(bulk_actions)

    async def partial_record_update(self, record: Record, **update):
        index_name = es_index_name_for_dataset(record.dataset)
        await self._update_document_request(index_name=index_name, id=str(record.id), body={"doc": update})

    async def delete_records(self, dataset: Dataset, records: Iterable[Record]):
        index_name = es_index_name_for_dataset(dataset)

        bulk_actions = [{"_op_type": "delete", "_id": record.id, "_index": index_name} for record in records]

        await self._bulk_op_request(bulk_actions)

    async def update_record_response(self, response: Response) -> None:
        record = response.record
        index_name = es_index_name_for_dataset(record.dataset)

        await self._update_document_request(
            index_name,
            id=str(record.id),
            body={
                "script": {
                    "source": """
                            if (ctx._source.responses == null) {
                                ctx._source.responses = []
                            }

                            for (int i=ctx._source.responses.length-1; i>=0; i--) {
                                if (ctx._source.responses[i].id == params.response.id) {
                                    ctx._source.responses.remove(i);
                                }
                            }

                            ctx._source.responses.add(params.response)
                        """,
                    "params": {"response": self._map_record_response_to_es(response)},
                }
            },
        )

    async def delete_record_response(self, response: Response) -> None:
        record = response.record
        index_name = es_index_name_for_dataset(record.dataset)

        await self._update_document_request(
            index_name,
            id=str(record.id),
            body={
                "script": {
                    "source": """
                            if (ctx._source.responses != null) {
                                for (int i=ctx._source.responses.length-1; i>=0; i--) {
                                    if (ctx._source.responses[i].id == params.response.id) {
                                        ctx._source.responses.remove(i);
                                    }
                                }
                            }
                        """,
                    "params": {"response": self._map_record_response_to_es(response)},
                }
            },
        )

    async def update_record_suggestion(self, suggestion: Suggestion):
        index_name = es_index_name_for_dataset(suggestion.record.dataset)

        es_suggestions = self._map_record_suggestions_to_es([suggestion])

        await self._update_document_request(
            index_name,
            id=str(suggestion.record_id),
            body={"doc": {"suggestions": es_suggestions}},
        )

    async def delete_record_suggestion(self, suggestion: Suggestion):
        index_name = es_index_name_for_dataset(suggestion.record.dataset)

        await self._update_document_request(
            index_name,
            id=str(suggestion.record_id),
            body={"script": f'ctx._source["suggestions"].remove("{suggestion.question.name}")'},
        )

    async def search(
        self,
        dataset: Dataset,
        query: Optional[Union[TextQuery, str]] = None,
        filter: Optional[Filter] = None,
        sort: Optional[List[Order]] = None,
        offset: int = 0,
        limit: int = 100,
        user_id: Optional[str] = None,
    ) -> SearchResponses:
        # See https://www.elastic.co/guide/en/elasticsearch/reference/current/search-search.html
        index = es_index_name_for_dataset(dataset)

        text_query = self._build_text_query(dataset, text=query)
        bool_query: Dict[str, Any] = {"must": [text_query]}

        if filter:
            bool_query["filter"] = self.build_elasticsearch_filter(filter)

        es_query = {"bool": bool_query}

        if user_id:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-function-score-query.html#function-random
            # If an `user_id` is provided we use it as seed for the `random_score` function to sort the records for the
            # user in a "random" and different way for each user, but still deterministic for the same user.
            es_query = {
                "function_score": {
                    "query": es_query,
                    "functions": [{"random_score": {"seed": str(user_id), "field": "_seq_no"}}],
                }
            }

        es_sort = self.build_elasticsearch_sort(sort) if sort else None
        response = await self._index_search_request(index, query=es_query, size=limit, from_=offset, sort=es_sort)

        return self._process_search_response(response)

    async def similarity_search(
        self,
        dataset: Dataset,
        vector_settings: VectorSettings,
        value: Optional[List[float]] = None,
        record: Optional[Record] = None,
        query: Optional[Union[TextQuery, str]] = None,
        filter: Optional[Filter] = None,
        max_results: int = 100,
        order: SimilarityOrder = SimilarityOrder.most_similar,
        threshold: Optional[float] = None,
    ) -> SearchResponses:
        if bool(value) == bool(record):
            raise ValueError("Must provide either vector value or record to compute the similarity search")

        index = es_index_name_for_dataset(dataset)
        vector_value = value
        record_id = None

        if not vector_value:
            record_id = record.id
            vector_value = record.vector_value_by_vector_settings(vector_settings)

        if not vector_value:
            raise ValueError("Cannot find a vector value to apply with provided info")

        if order == SimilarityOrder.least_similar:
            vector_value = self._inverse_vector(vector_value)

        query_filters = []
        if filter:
            query_filters = [self.build_elasticsearch_filter(filter)]

        if query:
            query_filters.append(self._build_text_query(dataset, text=query))

        response = await self._request_similarity_search(
            index=index,
            vector_settings=vector_settings,
            value=vector_value,
            k=max_results,
            excluded_id=record_id,
            query_filters=query_filters,
        )

        return self._process_search_response(response, threshold)

    async def compute_metrics_for(self, metadata_property: MetadataProperty) -> MetadataMetrics:
        index_name = es_index_name_for_dataset(metadata_property.dataset)

        if metadata_property.type == MetadataPropertyType.terms:
            return await self._metrics_for_terms_property(index_name, metadata_property)

        if metadata_property.type in [MetadataPropertyType.float, MetadataPropertyType.integer]:
            return await self._metrics_for_numeric_property(index_name, metadata_property)

    def build_elasticsearch_filter(self, filter: Filter) -> Dict[str, Any]:
        if isinstance(filter, AndFilter):
            filters = [self.build_elasticsearch_filter(f) for f in filter.filters]
            return es_bool_query(must=filters)

        if isinstance(filter.scope, ResponseFilterScope):
            return self._response_filter_to_es_filter(filter)
        else:
            es_field = self._scope_to_elasticsearch_field(filter.scope)
            return self._map_filter_to_es_filter(filter, es_field)

    def build_elasticsearch_sort(self, sort: List[Order]) -> List[dict]:
        sort_config = []

        for order in sort:
            if isinstance(order.scope, ResponseFilterScope):
                sort_config.append(self._response_order_to_es_order(order))
            else:
                sort_field_name = self._scope_to_elasticsearch_field(order.scope)
                sort_config.append({sort_field_name: order.order})

        return sort_config

    @staticmethod
    def _scope_to_elasticsearch_field(scope: FilterScope) -> str:
        if isinstance(scope, MetadataFilterScope):
            return es_field_for_metadata_property(scope.metadata_property)
        elif isinstance(scope, SuggestionFilterScope):
            return es_field_for_suggestion_property(question=scope.question, property=scope.property)
        elif isinstance(scope, RecordFilterScope):
            return es_field_for_record_property(scope.property)
        raise ValueError(f"Cannot process request for search scope {scope}")

    @staticmethod
    def _map_filter_to_es_filter(filter: Filter, es_field: str) -> dict:
        if isinstance(filter, TermsFilter):
            return es_terms_query(es_field, values=filter.values)
        elif isinstance(filter, RangeFilter):
            return es_range_query(es_field, gte=filter.ge, lte=filter.le)
        else:
            raise ValueError(f"Cannot process request for filter {filter}")

    @staticmethod
    def _inverse_vector(vector_value: List[float]) -> List[float]:
        return [vector_value[i] * -1 for i in range(0, len(vector_value))]

    def _map_record_to_es_document(self, record: Record) -> Dict[str, Any]:
        dataset = record.dataset

        document = {
            "id": str(record.id),
            "external_id": record.external_id,
            "fields": self._map_record_fields_to_es(record.fields, dataset.fields),
            "status": record.status,
            "inserted_at": record.inserted_at,
            "updated_at": record.updated_at,
        }

        if record.metadata_:
            document["metadata"] = self._map_record_metadata_to_es(record.metadata_, dataset.metadata_properties)
        if record.responses:
            document["responses"] = self._map_record_responses_to_es(record.responses)
        if record.suggestions:
            document["suggestions"] = self._map_record_suggestions_to_es(record.suggestions)
        if record.vectors:
            document["vectors"] = self._map_record_vectors_to_es(record.vectors)

        return document

    @staticmethod
    def _map_record_suggestions_to_es(suggestions: List[Suggestion]) -> dict:
        return {
            suggestion.question.name: {
                "type": suggestion.type,
                "agent": suggestion.agent,
                "score": suggestion.score,
                "value": suggestion.value,
            }
            for suggestion in suggestions
        }

    @staticmethod
    def _map_record_vectors_to_es(vectors: List[Vector]) -> Dict[str, List[float]]:
        return {es_path_for_vector_settings(vector.vector_settings): vector.value for vector in vectors}

    @staticmethod
    def _map_record_metadata_to_es(
        metadata: Dict[str, Any], metadata_properties: List[MetadataProperty]
    ) -> Dict[str, Any]:
        search_engine_metadata = {}

        for metadata_property in metadata_properties:
            value = metadata.get(metadata_property.name)
            if value is not None:
                search_engine_metadata[str(metadata_property.name)] = value

        return search_engine_metadata

    def _map_record_responses_to_es(self, responses: List[Response]) -> List[dict]:
        return [self._map_record_response_to_es(response) for response in responses]

    async def _metrics_for_numeric_property(
        self, index_name: str, metadata_property: MetadataProperty, query: Optional[dict] = None
    ) -> Union[IntegerMetadataMetrics, FloatMetadataMetrics]:
        field_name = es_field_for_metadata_property(metadata_property)
        query = query or {"match_all": {}}

        stats = await self.__stats_aggregation(index_name, field_name, query)

        metrics_class = (
            IntegerMetadataMetrics if metadata_property.type == MetadataPropertyType.integer else FloatMetadataMetrics
        )

        return metrics_class(min=stats["min"], max=stats["max"])

    async def _metrics_for_terms_property(
        self, index_name: str, metadata_property: MetadataProperty, query: Optional[dict] = None
    ) -> TermsMetadataMetrics:
        field_name = es_field_for_metadata_property(metadata_property)
        query = query or {"match_all": {}}

        total_terms = await self.__value_count_aggregation(index_name, field_name=field_name, query=query)
        if total_terms == 0:
            return TermsMetadataMetrics(total=total_terms)

        terms_buckets = await self.__terms_aggregation(index_name, field_name=field_name, query=query, size=total_terms)
        terms_values = [
            TermsMetadataMetrics.TermCount(term=bucket["key"], count=bucket["doc_count"]) for bucket in terms_buckets
        ]
        return TermsMetadataMetrics(total=total_terms, values=terms_values)

    def _configure_index_mappings(self, dataset: Dataset) -> dict:
        return {
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic.html#dynamic-parameters
            "dynamic": "strict",
            "_source": {
                # Excluding image fields, which means they won't be even stored. See https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-source-field.html#include-exclude
                "excludes": [es_field_for_record_field(field.name) for field in dataset.fields if field.is_image],
            },
            "properties": {
                # See https://www.elastic.co/guide/en/elasticsearch/reference/current/explicit-mapping.html
                "id": {"type": "keyword"},
                "external_id": {"type": "keyword"},
                "status": {"type": "keyword"},
                RecordSortField.inserted_at.value: {"type": "date_nanos"},
                RecordSortField.updated_at.value: {"type": "date_nanos"},
                **self._mapping_for_fields(dataset.fields),
                **self._mapping_for_metadata_properties(dataset.metadata_properties),
                **self._mapping_for_vectors_settings(dataset.vectors_settings),
                **self._mapping_for_suggestions(dataset.questions),
                **self._mapping_for_responses(dataset.questions),
            },
        }

    @staticmethod
    def _process_search_response(response: dict, score_threshold: Optional[float] = None) -> SearchResponses:
        hits = response["hits"]["hits"]

        if score_threshold is not None:
            hits = filter(lambda hit: hit["_score"] >= score_threshold, hits)

        items = [SearchResponseItem(record_id=UUID(hit["_id"]), score=hit["_score"]) for hit in hits]
        total = response["hits"]["total"]["value"]

        return SearchResponses(items=items, total=total)

    @staticmethod
    def _build_text_query(dataset: Dataset, text: Optional[Union[TextQuery, str]] = None) -> dict:
        if text is None:
            return {"match_all": {}}

        if isinstance(text, str):
            text = TextQuery(q=text)

        if text.field:
            field = dataset.field_by_name(text.field)
            if field is None:
                raise Exception(f"Field {text.field} not found in dataset {dataset.id}")

            if field.is_chat:
                field_name = f"{text.field}.*"
            else:
                field_name = text.field
        else:
            field_name = "*"

        return es_simple_query_string(es_field_for_record_field(field_name), query=text.q)

    @staticmethod
    def _mapping_for_fields(fields: List[Field]) -> dict:
        mappings = {}
        for field in fields:
            mappings.update(es_mapping_for_field(field))

        return mappings

    @staticmethod
    def _mapping_for_metadata_properties(metadata_properties: List[MetadataProperty]) -> dict:
        mappings = {
            # metadata properties without mappings will be ignored
            "metadata": {"dynamic": False, "type": "object"},
        }

        for metadata_property in metadata_properties:
            mappings.update(es_mapping_for_metadata_property(metadata_property))

        return mappings

    @staticmethod
    def _mapping_for_suggestions(questions: List[Question]) -> dict:
        mappings = {}

        for question in questions:
            mappings.update(es_mapping_for_question_suggestion(question))

        return mappings

    @staticmethod
    def _mapping_for_responses(questions: List[Question]) -> dict:
        return {
            "responses": {
                "type": "nested",
                "dynamic": "strict",
                "include_in_root": True,
                "properties": {
                    "id": {"type": "keyword"},
                    "status": {"type": "keyword"},
                    "user_id": {"type": "keyword"},
                    **{
                        es_path_for_question_response(question.name): es_mapping_for_question(question)
                        for question in questions
                    },
                },
            }
        }

    def _mapping_for_vectors_settings(self, vectors_settings: List[VectorSettings]) -> dict:
        mappings = {}
        for vector in vectors_settings:
            mappings.update(self._mapping_for_vector_settings(vector))

        return mappings

    def _configure_index_settings(self) -> dict:
        """Defines settings configuration for the index. Depending on which backend is used, this may differ"""
        return {
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-settings-limit.html#mapping-settings-limit
            "index.mapping.total_fields.limit": self.default_total_fields_limit,
            "max_result_window": self.max_result_window,
            "number_of_shards": self.number_of_shards,
            "number_of_replicas": self.number_of_replicas,
        }

    def _response_filter_to_es_filter(self, filter: Filter) -> dict:
        scope: ResponseFilterScope = filter.scope
        if scope.question:
            return self._response_filter_question_to_es_filter(filter, scope.question)
        elif scope.property == "status" and isinstance(filter, TermsFilter):
            return self._response_status_filter_to_es_filter(filter)
        else:
            raise Exception(f"Cannot process filter scope {scope}")

    @staticmethod
    def _response_filter_question_to_es_filter(filter: Filter, question_name: str) -> dict:
        field_name = es_field_for_response_property(question_name)

        es_filters = []
        if isinstance(filter, RangeFilter):
            es_filters.append(es_range_query(field_name=field_name, gte=filter.ge, lte=filter.le))
        elif isinstance(filter, TermsFilter):
            es_filters.append(es_terms_query(field_name=field_name, values=filter.values))
        else:
            raise Exception(f"Cannot process filter {filter}")

        if filter.scope.user:
            es_filters.append(
                es_terms_query(field_name=es_field_for_response_property("user_id"), values=[str(filter.scope.user.id)])
            )

        return (
            es_nested_query(path="responses", query=es_bool_query(must=es_filters)) if es_filters else {"match_all": {}}
        )

    def _response_status_filter_to_es_filter(self, filter: TermsFilter) -> dict:
        field_name = es_field_for_response_property("status")

        if ResponseStatusFilter.pending in filter.values:
            must_not_query = (
                es_term_query(field_name=es_field_for_response_property("user_id"), value=str(filter.scope.user.id))
                if filter.scope.user
                else es_exists_field_query(field="responses")
            )
            es_filter = es_bool_query(must_not=must_not_query)

            filter.values.remove(ResponseStatusFilter.pending)
            if not filter.values:
                return es_filter

            return es_bool_query(
                should=[es_filter, self._response_status_filter_to_es_filter(filter)],
                minimum_should_match=1,
            )

        es_filters = []
        if filter.values:
            es_filters.append(es_terms_query(field_name=field_name, values=filter.values))

        if filter.scope.user:
            es_filters.append(
                es_terms_query(field_name=es_field_for_response_property("user_id"), values=[str(filter.scope.user.id)])
            )

        return (
            es_nested_query(path="responses", query=es_bool_query(must=es_filters)) if es_filters else {"match_all": {}}
        )

    @staticmethod
    def _response_order_to_es_order(order: Order) -> dict:
        scope: ResponseFilterScope = order.scope
        if scope.question:
            field_name = es_field_for_response_property(scope.question)
        else:
            field_name = es_field_for_response_property(scope.property)

        nested_part = {"path": "responses"}
        if scope.user:
            nested_part["filter"] = es_terms_query(
                field_name=es_field_for_response_property("user_id"), values=[str(scope.user.id)]
            )

        return {
            field_name: {
                "order": order.order,
                "mode": "avg",
                "nested": nested_part,
            }
        }

    @staticmethod
    def _map_record_response_to_es(response: Response) -> Dict[str, Any]:
        return {
            "id": response.id,
            "status": response.status,
            "user_id": response.user_id,
            **{
                es_path_for_question_response(question): value.get("value")
                for question, value in response.values.items()
            },
        }

    @classmethod
    def _map_record_fields_to_es(cls, fields: dict, dataset_fields: List[Field]) -> dict:
        for field in dataset_fields:
            if field.is_image:
                fields[field.name] = None
            elif field.is_custom:
                fields[field.name] = str(fields.get(field.name, ""))
            else:
                fields[field.name] = fields.get(field.name, "")

        return fields

    async def __terms_aggregation(self, index_name: str, field_name: str, query: dict, size: int) -> List[dict]:
        aggregation_name = "terms_agg"

        terms_agg = {aggregation_name: {"terms": {"field": field_name, "size": min(size, self.max_terms_size)}}}

        response = await self._index_search_request(index_name, query=query, aggregations=terms_agg, size=0)
        return response["aggregations"][aggregation_name]["buckets"]

    async def __value_count_aggregation(self, index_name: str, field_name: str, query: dict) -> int:
        aggregation_name = "count_values"

        value_count_agg = {aggregation_name: {"value_count": {"field": field_name}}}

        response = await self._index_search_request(index_name, query=query, aggregations=value_count_agg, size=0)
        return response["aggregations"][aggregation_name]["value"]

    async def __stats_aggregation(self, index_name: str, field_name: str, query: dict) -> dict:
        # See https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-stats-aggregation.html
        aggregation_name = "numeric_stats"

        stats_agg = {aggregation_name: {"stats": {"field": field_name}}}

        response = await self._index_search_request(index_name, query=query, aggregations=stats_agg, size=0)
        return response["aggregations"][aggregation_name]

    @abstractmethod
    def _mapping_for_vector_settings(self, vector_settings: VectorSettings) -> dict:
        """Defines one mapping property configuration for a vector_setting definition"""
        pass

    @abstractmethod
    async def _request_similarity_search(
        self,
        index: str,
        vector_settings: VectorSettings,
        value: List[float],
        k: int,
        excluded_id: Optional[UUID] = None,
        query_filters: Optional[List[dict]] = None,
    ) -> dict:
        """
        Applies the similarity search request based on a vector configuration, a vector value,
        the `k` number of results to retrieve and an optional filter configuration to apply
        """
        pass

    @abstractmethod
    async def _create_index_request(self, index_name: str, mappings: dict, settings: dict) -> None:
        """Executes request for index creation"""
        pass

    @abstractmethod
    async def _delete_index_request(self, index_name: str):
        """Executes request for index deletion"""
        pass

    @abstractmethod
    async def _update_document_request(self, index_name: str, id: str, body: dict):
        """Executes request for index document (partial) update"""
        pass

    @abstractmethod
    async def put_index_mapping_request(self, index: str, mappings: dict):
        """Executes request for index mapping (partial) update"""
        pass

    @abstractmethod
    async def _index_search_request(
        self,
        index: str,
        query: dict,
        size: Optional[int] = None,
        from_: Optional[int] = None,
        sort: Optional[dict] = None,
        aggregations: Optional[dict] = None,
    ) -> dict:
        """Executes request for search documents on a index"""
        pass

    @abstractmethod
    async def _index_exists_request(self, index_name: str) -> bool:
        """Executes request for check if index exists"""
        pass

    @abstractmethod
    async def _bulk_op_request(self, actions: List[Dict[str, Any]]):
        """Executes request for bulk operations"""
        pass
