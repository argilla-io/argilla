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
from abc import abstractmethod
from typing import Any, Dict, Iterable, List, Optional, Union
from uuid import UUID

from argilla_server.enums import FieldType, MetadataPropertyType, RecordSortField, ResponseStatusFilter, SimilarityOrder
from argilla_server.models import (
    Dataset,
    Field,
    MetadataProperty,
    Question,
    QuestionType,
    Record,
    Response,
    Suggestion,
    User,
    Vector,
    VectorSettings,
)
from argilla_server.search_engine.base import (
    AndFilter,
    Filter,
    FilterScope,
    FloatMetadataFilter,
    FloatMetadataMetrics,
    IntegerMetadataFilter,
    IntegerMetadataMetrics,
    MetadataFilter,
    MetadataFilterScope,
    MetadataMetrics,
    Order,
    RangeFilter,
    RecordFilterScope,
    ResponseFilterScope,
    SearchEngine,
    SearchResponseItem,
    SearchResponses,
    SortBy,
    SuggestionFilterScope,
    TermsFilter,
    TermsMetadataFilter,
    TermsMetadataMetrics,
    TextQuery,
    UserResponseStatusFilter,
)

ALL_RESPONSES_STATUSES_FIELD = "all_responses_statuses"


def es_index_name_for_dataset(dataset: Dataset):
    return f"rg.{dataset.id}"


def es_terms_query(field_name: str, values: List[str]) -> dict:
    return {"terms": {field_name: values}}


def es_range_query(field_name: str, gte: Optional[float] = None, lte: Optional[float] = None) -> dict:
    query = {}
    if gte is not None:
        query["gte"] = gte
    if lte is not None:
        query["lte"] = lte
    return {"range": {field_name: query}}


def es_bool_query(
    *,
    must_not: Optional[List[dict]] = None,
    should: Optional[List[dict]] = None,
    minimum_should_match: Optional[Union[int, str]] = None,
) -> Dict[str, Any]:
    bool_query = {}

    if should:
        bool_query["should"] = should
    if must_not:
        bool_query["must_not"] = must_not

    if not bool_query:
        raise ValueError("Cannot build a boolean query without any clause")

    if minimum_should_match:
        bool_query["minimum_should_match"] = minimum_should_match

    return {"bool": bool_query}


def es_ids_query(ids: List[str]) -> dict:
    return {"ids": {"values": ids}}


def es_field_for_response_value(user: User, question: str) -> str:
    return f"responses.{es_path_for_user(user)}.values.{question}"


def es_field_for_response_status(user: User) -> str:
    return f"responses.{es_path_for_user(user)}.status"


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


def es_mapping_for_field(field: Field) -> dict:
    field_type = field.settings["type"]

    if field_type == FieldType.text:
        return {es_field_for_record_field(field.name): {"type": "text"}}
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


def es_script_for_delete_user_response(user: User) -> str:
    return f'ctx._source["responses"].remove("{es_path_for_user(user)}")'


def es_path_for_user(user: User) -> str:
    return str(user.id)


def es_path_for_vector_settings(vector_settings: VectorSettings) -> str:
    return str(vector_settings.id)


# This function will be moved once the `metadata_filters` argument is removed from search and similarity_search methods
def _unify_metadata_filters_with_filter(metadata_filters: List[MetadataFilter], filter: Optional[Filter]) -> Filter:
    filters = []
    if filter:
        filters.append(filter)

    for metadata_filter in metadata_filters:
        metadata_scope = MetadataFilterScope(metadata_property=metadata_filter.metadata_property.name)
        if isinstance(metadata_filter, TermsMetadataFilter):
            new_filter = TermsFilter(scope=metadata_scope, values=metadata_filter.values)
        elif isinstance(metadata_filter, (IntegerMetadataFilter, FloatMetadataFilter)):
            new_filter = RangeFilter(scope=metadata_scope, ge=metadata_filter.ge, le=metadata_filter.le)
        else:
            raise ValueError(f"Cannot process request for metadata filter {metadata_filter}")
        filters.append(new_filter)

    return AndFilter(filters=filters)


# This function will be moved once the response status filter is removed from search and similarity_search methods
def _unify_user_response_status_filter_with_filter(
    user_response_status_filter: UserResponseStatusFilter, filter: Optional[Filter] = None
) -> Filter:
    scope = ResponseFilterScope(user=user_response_status_filter.user, property="status")
    response_filter = TermsFilter(scope=scope, values=[status.value for status in user_response_status_filter.statuses])

    if filter:
        return AndFilter(filters=[filter, response_filter])
    else:
        return response_filter


# This function will be moved once the `sort_by` argument is removed from search and similarity_search methods
def _unify_sort_by_with_order(sort_by: List[SortBy], order: List[Order]) -> List[Order]:
    if order:
        return order

    new_order = []
    for sort in sort_by:
        if isinstance(sort.field, MetadataProperty):
            scope = MetadataFilterScope(metadata_property=sort.field.name)
        else:
            scope = RecordFilterScope(property=sort.field)

        new_order.append(Order(scope=scope, order=sort.order))

    return new_order


def is_response_status_scope(scope: FilterScope) -> bool:
    return isinstance(scope, ResponseFilterScope) and scope.property == "status" and scope.question is None


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

    async def create_index(self, dataset: Dataset):
        settings = self._configure_index_settings()
        mappings = self._configure_index_mappings(dataset)

        index_name = es_index_name_for_dataset(dataset)
        await self._create_index_request(index_name, mappings, settings)

    async def configure_metadata_property(self, dataset: Dataset, metadata_property: MetadataProperty):
        mapping = es_mapping_for_metadata_property(metadata_property)
        index_name = await self._get_dataset_index(dataset)

        await self.put_index_mapping_request(index_name, mapping)

    async def delete_index(self, dataset: Dataset):
        index_name = es_index_name_for_dataset(dataset)

        await self._delete_index_request(index_name)

    async def index_records(self, dataset: Dataset, records: Iterable[Record]):
        index_name = await self._get_dataset_index(dataset)

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

    async def delete_records(self, dataset: Dataset, records: Iterable[Record]):
        index_name = await self._get_dataset_index(dataset)

        bulk_actions = [{"_op_type": "delete", "_id": record.id, "_index": index_name} for record in records]

        await self._bulk_op_request(bulk_actions)

    async def update_record_response(self, response: Response):
        record = response.record
        index_name = await self._get_dataset_index(record.dataset)

        es_responses = self._map_record_responses_to_es([response])

        await self._update_document_request(index_name, id=record.id, body={"doc": {"responses": es_responses}})

    async def delete_record_response(self, response: Response):
        record = response.record
        index_name = await self._get_dataset_index(record.dataset)

        await self._update_document_request(
            index_name, id=record.id, body={"script": es_script_for_delete_user_response(response.user)}
        )

    async def update_record_suggestion(self, suggestion: Suggestion):
        index_name = await self._get_dataset_index(suggestion.record.dataset)

        es_suggestions = self._map_record_suggestions_to_es([suggestion])

        await self._update_document_request(
            index_name,
            id=suggestion.record_id,
            body={"doc": {"suggestions": es_suggestions}},
        )

    async def delete_record_suggestion(self, suggestion: Suggestion):
        index_name = await self._get_dataset_index(suggestion.record.dataset)

        await self._update_document_request(
            index_name,
            id=suggestion.record_id,
            body={"script": f'ctx._source["suggestions"].remove("{suggestion.question.name}")'},
        )

    async def set_records_vectors(self, dataset: Dataset, vectors: Iterable[Vector]):
        index_name = await self._get_dataset_index(dataset)

        bulk_actions = [
            {
                "_op_type": "update",
                "_id": vector.record_id,
                "_index": index_name,
                "doc": {es_field_for_vector_settings(vector.vector_settings): vector.value},
            }
            for vector in vectors
        ]

        await self._bulk_op_request(bulk_actions)

    async def similarity_search(
        self,
        dataset: Dataset,
        vector_settings: VectorSettings,
        value: Optional[List[float]] = None,
        record: Optional[Record] = None,
        query: Optional[Union[TextQuery, str]] = None,
        filter: Optional[Filter] = None,
        # TODO: remove them and keep filter
        user_response_status_filter: Optional[UserResponseStatusFilter] = None,
        metadata_filters: Optional[List[MetadataFilter]] = None,
        # END TODO
        max_results: int = 100,
        order: SimilarityOrder = SimilarityOrder.most_similar,
        threshold: Optional[float] = None,
    ) -> SearchResponses:
        # TODO: This block will be moved (maybe to contexts/search.py), and only filter and order arguments will be kept
        if metadata_filters:
            filter = _unify_metadata_filters_with_filter(metadata_filters, filter)
        if user_response_status_filter and user_response_status_filter.statuses:
            filter = _unify_user_response_status_filter_with_filter(user_response_status_filter, filter)
        # END TODO

        if bool(value) == bool(record):
            raise ValueError("Must provide either vector value or record to compute the similarity search")

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
            # Wrapping filter in a list to use easily on each engine implementation
            query_filters = [self.build_elasticsearch_filter(filter)]

        if query:
            query_filters.append(self._build_text_query(dataset, text=query))

        index = await self._get_dataset_index(dataset)
        response = await self._request_similarity_search(
            index=index,
            vector_settings=vector_settings,
            value=vector_value,
            k=max_results,
            excluded_id=record_id,
            query_filters=query_filters,
        )

        return await self._process_search_response(response, threshold)

    def build_elasticsearch_filter(self, filter: Filter) -> Dict[str, Any]:
        if isinstance(filter, AndFilter):
            filters = [self.build_elasticsearch_filter(f) for f in filter.filters]
            return es_bool_query(should=filters, minimum_should_match=len(filters))

        # This is a special case for response status filter, since it's compound by multiple filters
        if is_response_status_scope(filter.scope):
            status_filter = UserResponseStatusFilter(
                user=filter.scope.user, statuses=[ResponseStatusFilter(v) for v in filter.values]
            )
            return self._build_response_status_filter(status_filter)

        es_field = self._scope_to_elasticsearch_field(filter.scope)

        if isinstance(filter, TermsFilter):
            return es_terms_query(es_field, values=filter.values)
        elif isinstance(filter, RangeFilter):
            return es_range_query(es_field, gte=filter.ge, lte=filter.le)
        else:
            raise ValueError(f"Cannot process request for filter {filter}")

    def build_elasticsearch_sort(self, sort: List[Order]) -> str:
        sort_config = []

        for order in sort:
            sort_field_name = self._scope_to_elasticsearch_field(order.scope)
            sort_config.append(f"{sort_field_name}:{order.order}")

        return ",".join(sort_config)

    @staticmethod
    def _scope_to_elasticsearch_field(scope: FilterScope) -> str:
        if isinstance(scope, MetadataFilterScope):
            return es_field_for_metadata_property(scope.metadata_property)
        elif isinstance(scope, SuggestionFilterScope):
            return es_field_for_suggestion_property(question=scope.question, property=scope.property)
        elif isinstance(scope, ResponseFilterScope):
            return es_field_for_response_value(scope.user, question=scope.question)
        elif isinstance(scope, RecordFilterScope):
            return es_field_for_record_property(scope.property)
        raise ValueError(f"Cannot process request for search scope {scope}")

    @staticmethod
    def _build_response_status_filter(status_filter: UserResponseStatusFilter) -> Dict[str, Any]:
        if status_filter.user is None:
            response_field = ALL_RESPONSES_STATUSES_FIELD
        else:
            response_field = es_field_for_response_status(status_filter.user)

        filters = []
        if status_filter.has_pending_status:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-exists-query.html
            filters.append({"bool": {"must_not": {"exists": {"field": response_field}}}})

        if status_filter.response_statuses:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-terms-query.html
            filters.append(es_terms_query(response_field, values=status_filter.response_statuses))

        return {"bool": {"should": filters, "minimum_should_match": 1}}

    def _inverse_vector(self, vector_value: List[float]) -> List[float]:
        return [vector_value[i] * -1 for i in range(0, len(vector_value))]

    def _map_record_to_es_document(self, record: Record) -> Dict[str, Any]:
        document = {
            "id": str(record.id),
            "fields": record.fields,
            "inserted_at": record.inserted_at,
            "updated_at": record.updated_at,
        }

        if record.metadata_:
            document["metadata"] = self._map_record_metadata_to_es(record.metadata_, record.dataset.metadata_properties)
        if record.responses:
            document["responses"] = self._map_record_responses_to_es(record.responses)
        if record.suggestions:
            document["suggestions"] = self._map_record_suggestions_to_es(record.suggestions)
        if record.vectors:
            document["vectors"] = self._map_record_vectors_to_es(record.vectors)

        return document

    @staticmethod
    def _map_record_responses_to_es(responses: List[Response]) -> Dict[str, Any]:
        return {
            es_path_for_user(response.user): {
                "values": {k: v["value"] for k, v in response.values.items()} if response.values else None,
                "status": response.status,
            }
            for response in responses
        }

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

    async def configure_index_vectors(self, vector_settings: VectorSettings) -> None:
        index = await self._get_dataset_index(vector_settings.dataset)

        mappings = self._mapping_for_vector_settings(vector_settings)
        await self.put_index_mapping_request(index, mappings)

    async def search(
        self,
        dataset: Dataset,
        query: Optional[Union[TextQuery, str]] = None,
        filter: Optional[Filter] = None,
        sort: Optional[List[Order]] = None,
        # TODO: Remove these arguments
        user_response_status_filter: Optional[UserResponseStatusFilter] = None,
        metadata_filters: Optional[List[MetadataFilter]] = None,
        sort_by: Optional[List[SortBy]] = None,
        # END TODO
        offset: int = 0,
        limit: int = 100,
        user_id: Optional[str] = None,
    ) -> SearchResponses:
        # See https://www.elastic.co/guide/en/elasticsearch/reference/current/search-search.html

        # TODO: This block will be moved (maybe to contexts/search.py), and only filter and order arguments will be kept
        if metadata_filters:
            filter = _unify_metadata_filters_with_filter(metadata_filters, filter)
        if user_response_status_filter and user_response_status_filter.statuses:
            filter = _unify_user_response_status_filter_with_filter(user_response_status_filter, filter)

        if sort_by:
            sort = _unify_sort_by_with_order(sort_by, sort)
        # END TODO

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

        index = await self._get_dataset_index(dataset)

        es_sort = self.build_elasticsearch_sort(sort) if sort else None
        response = await self._index_search_request(index, query=es_query, size=limit, from_=offset, sort=es_sort)

        return await self._process_search_response(response)

    async def compute_metrics_for(self, metadata_property: MetadataProperty) -> MetadataMetrics:
        index_name = await self._get_dataset_index(metadata_property.dataset)

        if metadata_property.type == MetadataPropertyType.terms:
            return await self._metrics_for_terms_property(index_name, metadata_property)

        if metadata_property.type in [MetadataPropertyType.float, MetadataPropertyType.integer]:
            return await self._metrics_for_numeric_property(index_name, metadata_property)

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
            "dynamic_templates": self._dynamic_templates_for_question_responses(dataset.questions),
            "properties": {
                # See https://www.elastic.co/guide/en/elasticsearch/reference/current/explicit-mapping.html
                "id": {"type": "keyword"},
                RecordSortField.inserted_at.value: {"type": "date_nanos"},
                RecordSortField.updated_at.value: {"type": "date_nanos"},
                "responses": {"dynamic": True, "type": "object"},
                ALL_RESPONSES_STATUSES_FIELD: {"type": "keyword"},  # To add all users responses
                **self._mapping_for_fields(dataset.fields),
                **self._mapping_for_suggestions(dataset.questions),
                **self._mapping_for_metadata_properties(dataset.metadata_properties),
                **self._mapping_for_vectors_settings(dataset.vectors_settings),
            },
        }

    async def _process_search_response(
        self, response: dict, score_threshold: Optional[float] = None
    ) -> SearchResponses:
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

        if not text.field:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-multi-match-query.html
            field_names = [
                es_field_for_record_field(field.name)
                for field in dataset.fields
                if field.settings.get("type") == FieldType.text
            ]
            return {"multi_match": {"query": text.q, "type": "cross_fields", "fields": field_names, "operator": "and"}}
        else:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-query.html
            return {"match": {es_field_for_record_field(text.field): {"query": text.q, "operator": "and"}}}

    def _mapping_for_fields(self, fields: List[Field]) -> dict:
        mappings = {}
        for field in fields:
            mappings.update(es_mapping_for_field(field))

        return mappings

    def _mapping_for_metadata_properties(self, metadata_properties: List[MetadataProperty]) -> dict:
        mappings = {
            # metadata properties without mappings will be ignored
            "metadata": {"dynamic": False, "type": "object"},
        }

        for metadata_property in metadata_properties:
            mappings.update(es_mapping_for_metadata_property(metadata_property))

        return mappings

    def _mapping_for_suggestions(self, questions: List[Question]) -> dict:
        mappings = {}

        for question in questions:
            mappings.update(es_mapping_for_question_suggestion(question))

        return mappings

    def _dynamic_templates_for_question_responses(self, questions: List[Question]) -> List[dict]:
        # See https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic-templates.html
        return [
            {
                "status_responses": {
                    "path_match": "responses.*.status",
                    "mapping": {"type": "keyword", "copy_to": ALL_RESPONSES_STATUSES_FIELD},
                }
            },
            *[
                {
                    f"{question.name}_responses": {
                        "path_match": f"responses.*.values.{question.name}",
                        "mapping": es_mapping_for_question(question),
                    },
                }
                for question in questions
            ],
        ]

    async def _get_dataset_index(self, dataset: Dataset):
        index_name = es_index_name_for_dataset(dataset)

        return index_name

    def _mapping_for_vectors_settings(self, vectors_settings: List[VectorSettings]) -> dict:
        mappings = {}
        for vector in vectors_settings:
            mappings.update(self._mapping_for_vector_settings(vector))

        return mappings

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
        aggregation_name = f"numeric_stats"

        stats_agg = {aggregation_name: {"stats": {"field": field_name}}}

        response = await self._index_search_request(index_name, query=query, aggregations=stats_agg, size=0)
        return response["aggregations"][aggregation_name]

    def _configure_index_settings(self) -> dict:
        """Defines settings configuration for the index. Depending on which backend is used, this may differ"""
        return {
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-settings-limit.html#mapping-settings-limit
            "index.mapping.total_fields.limit": self.default_total_fields_limit,
            "max_result_window": self.max_result_window,
            "number_of_shards": self.number_of_shards,
            "number_of_replicas": self.number_of_replicas,
        }

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
        sort: Optional[str] = None,
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

    @abstractmethod
    async def _refresh_index_request(self, index_name: str):
        pass
