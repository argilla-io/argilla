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
import datetime
from abc import abstractmethod
from typing import Any, Dict, Iterable, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel
from pydantic.utils import GetterDict

from argilla.server.enums import FieldType, MetadataPropertyType, RecordSortField, ResponseStatusFilter
from argilla.server.models import (
    Dataset,
    Field,
    MetadataProperty,
    Question,
    QuestionType,
    Record,
    Response,
    ResponseStatus,
)
from argilla.server.search_engine.base import (
    FloatMetadataFilter,
    FloatMetadataMetrics,
    IntegerMetadataFilter,
    IntegerMetadataMetrics,
    MetadataFilter,
    MetadataMetrics,
    SearchEngine,
    SearchResponseItem,
    SearchResponses,
    SortBy,
    StringQuery,
    TermsMetadataFilter,
    TermsMetadataMetrics,
    UserResponseStatusFilter,
)

ALL_RESPONSES_STATUSES_FIELD = "all_responses_statuses"


class UserResponse(BaseModel):
    values: Optional[Dict[str, Any]]
    status: ResponseStatus


def _build_metadata_field_payload(dataset: Dataset, metadata: Union[Dict[str, Any], None] = None) -> Dict[str, Any]:
    if metadata is None:
        return {}

    search_engine_metadata = {}
    for metadata_property in dataset.metadata_properties:
        value = metadata.get(metadata_property.name)
        if value is not None:
            search_engine_metadata[str(metadata_property.id)] = value

    return search_engine_metadata


class SearchDocumentGetter(GetterDict):
    def get(self, key: Any, default: Any = None) -> Any:
        if key == "responses":
            # `responses` of the record haven't been loaded, set the default value so when using
            # `SearchDocument(...).dict(exclude_unset=True)` the field is not included.
            if not self._obj.is_relationship_loaded("responses"):
                return default

            return {
                response.user.username: UserResponse(
                    values={k: v["value"] for k, v in response.values.items()} if response.values else None,
                    status=response.status,
                )
                for response in self._obj.responses
            }
        elif key == "metadata":
            return _build_metadata_field_payload(self._obj.dataset, self._obj.metadata_)

        return super().get(key, default)


class SearchDocument(BaseModel):
    id: UUID
    fields: Dict[str, Any]

    metadata: Optional[Dict[str, Any]] = None
    responses: Optional[Dict[str, UserResponse]]

    inserted_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True
        getter_dict = SearchDocumentGetter


def index_name_for_dataset(dataset: Dataset):
    return f"rg.{dataset.id}"


def _mapping_for_field(field: Field) -> dict:
    field_type = field.settings["type"]

    if field_type == FieldType.text:
        return {f"fields.{field.name}": {"type": "text"}}
    else:
        raise ValueError(f"Index configuration for field of type {field_type} cannot be generated")


def _mapping_key_for_metadata_property(metadata_property: MetadataProperty) -> str:
    return f"metadata.{metadata_property.id}"


def _mapping_for_metadata_property(metadata_property: MetadataProperty) -> dict:
    property_type = metadata_property.settings["type"]

    if property_type == MetadataPropertyType.terms:
        return {_mapping_key_for_metadata_property(metadata_property): {"type": "keyword"}}
    elif property_type == MetadataPropertyType.integer:
        return {_mapping_key_for_metadata_property(metadata_property): {"type": "long"}}
    elif property_type == MetadataPropertyType.float:
        return {_mapping_key_for_metadata_property(metadata_property): {"type": "float"}}
    else:
        raise ValueError(f"Index configuration for metadata property of type {property_type} cannot be generated")


def _aggregation_for_metadata_property(metadata_property: MetadataProperty) -> dict:
    if metadata_property.type == MetadataPropertyType.terms:
        return {f"{metadata_property.id}": {"terms": {"field": _mapping_key_for_metadata_property(metadata_property)}}}
    if metadata_property.type in [MetadataPropertyType.integer, MetadataPropertyType.float]:
        return {f"{metadata_property.id}": {"stats": {"field": _mapping_key_for_metadata_property(metadata_property)}}}
    else:
        raise ValueError(f"Cannot process request for metadata property {metadata_property}")


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
    max_terms_size: int = 2 ^ 14
    # See https://www.elastic.co/guide/en/elasticsearch/reference/5.1/index-modules.html#dynamic-index-settings
    max_result_window: int = 500000

    async def create_index(self, dataset: Dataset):
        settings = self._configure_index_settings()
        mappings = self._configure_index_mappings(dataset)

        index_name = index_name_for_dataset(dataset)
        await self._create_index_request(index_name, mappings, settings)

    async def configure_metadata_property(self, dataset: Dataset, metadata_property: MetadataProperty):
        mapping = _mapping_for_metadata_property(metadata_property)
        index_name = await self._get_index_or_raise(dataset)

        await self.put_index_mapping_request(index_name, mapping)

    async def delete_index(self, dataset: Dataset):
        index_name = index_name_for_dataset(dataset)

        await self._delete_index_request(index_name)

    async def index_records(self, dataset: Dataset, records: Iterable[Record]):
        index_name = await self._get_index_or_raise(dataset)

        bulk_actions = [
            {
                # If document exist, we update source with latest version
                "_op_type": "index",
                "_id": record.id,
                "_index": index_name,
                **SearchDocument.from_orm(record).dict(exclude_unset=True),
            }
            for record in records
        ]

        await self._bulk_op_request(bulk_actions)
        await self._refresh_index_request(index_name)

    async def delete_records(self, dataset: Dataset, records: Iterable[Record]):
        index_name = await self._get_index_or_raise(dataset)

        bulk_actions = [{"_op_type": "delete", "_id": record.id, "_index": index_name} for record in records]

        await self._bulk_op_request(bulk_actions)

    async def update_record_response(self, response: Response):
        record = response.record
        index_name = await self._get_index_or_raise(record.dataset)

        es_response = UserResponse(
            values={k: v["value"] for k, v in response.values.items()} if response.values else None,
            status=response.status,
        )

        await self._update_document_request(
            index_name, id=record.id, body={"doc": {"responses": {response.user.username: es_response.dict()}}}
        )

    async def delete_record_response(self, response: Response):
        record = response.record
        index_name = await self._get_index_or_raise(record.dataset)

        await self._update_document_request(
            index_name, id=record.id, body={"script": f'ctx._source["responses"].remove("{response.user.username}")'}
        )

    async def search(
        self,
        dataset: Dataset,
        query: Optional[Union[StringQuery, str]] = None,
        user_response_status_filter: Optional[UserResponseStatusFilter] = None,
        metadata_filters: Optional[List[MetadataFilter]] = None,
        offset: int = 0,
        limit: int = 100,
        sort_by: Optional[List[SortBy]] = None,
    ) -> SearchResponses:
        # See https://www.elastic.co/guide/en/elasticsearch/reference/current/search-search.html

        if isinstance(query, str):
            query = StringQuery(q=query)

        text_query = self._text_query_builder(dataset, text=query)
        bool_query: Dict[str, Any] = {"must": [text_query]}

        query_filters = []
        if metadata_filters:
            query_filters.extend(self._build_metadata_filters(metadata_filters))
        if user_response_status_filter and user_response_status_filter.statuses:
            query_filters.append(self._build_response_status_filter(user_response_status_filter))
        if query_filters:
            bool_query["filter"] = {"bool": {"should": query_filters, "minimum_should_match": "100%"}}

        _query = {"bool": bool_query}
        index = await self._get_index_or_raise(dataset)

        sort = self._build_sort_configuration(sort_by)
        response = await self._index_search_request(index, query=_query, size=limit, from_=offset, sort=sort)

        return await self._process_search_response(response)

    async def compute_metrics_for(self, metadata_property: MetadataProperty) -> MetadataMetrics:
        index_name = await self._get_index_or_raise(metadata_property.dataset)

        if metadata_property.type == MetadataPropertyType.terms:
            return await self._metrics_for_terms_property(index_name, metadata_property)

        if metadata_property.type in [MetadataPropertyType.float, MetadataPropertyType.integer]:
            return await self._metrics_for_numeric_property(index_name, metadata_property)

    async def _metrics_for_numeric_property(
        self, index_name: str, metadata_property: MetadataProperty, query: Optional[dict] = None
    ) -> Union[IntegerMetadataMetrics, FloatMetadataMetrics]:
        field_name = _mapping_key_for_metadata_property(metadata_property)
        query = query or {"match_all": {}}

        stats = await self.__stats_aggregation(index_name, field_name, query)

        metrics_class = (
            IntegerMetadataMetrics if metadata_property.type == MetadataPropertyType.integer else FloatMetadataMetrics
        )

        return metrics_class(min=stats["min"], max=stats["max"])

    async def _metrics_for_terms_property(
        self, index_name: str, metadata_property: MetadataProperty, query: Optional[dict] = None
    ) -> TermsMetadataMetrics:
        field_name = _mapping_key_for_metadata_property(metadata_property)
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
                # metadata properties without mappings will be ignored
                "metadata": {"dynamic": False, "type": "object"},
                **self._mapping_for_fields(dataset.fields),
                **self._mapping_for_metadata_properties(dataset.metadata_properties),
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
    def _text_query_builder(dataset: Dataset, text: Optional[StringQuery] = None) -> dict:
        if text is None:
            return {"match_all": {}}
        if not text.field:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-multi-match-query.html
            field_names = [
                f"fields.{field.name}" for field in dataset.fields if field.settings.get("type") == FieldType.text
            ]
            return {"multi_match": {"query": text.q, "type": "cross_fields", "fields": field_names, "operator": "and"}}
        else:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-query.html
            return {"match": {f"fields.{text.field}": {"query": text.q, "operator": "and"}}}

    def _mapping_for_fields(self, fields: List[Field]) -> dict:
        mappings = {}
        for field in fields:
            mappings.update(_mapping_for_field(field))

        return mappings

    def _mapping_for_metadata_properties(self, metadata_properties: List[MetadataProperty]) -> dict:
        mappings = {}

        for metadata_property in metadata_properties:
            mappings.update(_mapping_for_metadata_property(metadata_property))

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
                        "mapping": self._field_mapping_for_question(question),
                    },
                }
                for question in questions
            ],
        ]

    def _field_mapping_for_question(self, question: Question):
        settings = question.parsed_settings

        if settings.type == QuestionType.rating:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/number.html
            return {"type": "integer"}
        elif settings.type == QuestionType.text:
            # TODO: Review mapping for label selection. Could make sense to use `keyword` mapping instead.
            #  See https://www.elastic.co/guide/en/elasticsearch/reference/current/keyword.html
            #  See https://www.elastic.co/guide/en/elasticsearch/reference/current/text.html
            return {"type": "text", "index": False}
        elif settings.type in [QuestionType.label_selection, QuestionType.multi_label_selection]:
            return {"type": "keyword"}
        elif settings.type == QuestionType.ranking:
            return {"type": "nested"}
        else:
            raise ValueError(f"ElasticSearch mappings for Question of type {settings.type} cannot be generated")

    async def _get_index_or_raise(self, dataset: Dataset):
        index_name = index_name_for_dataset(dataset)
        if not await self._index_exists_request(index_name):
            raise ValueError(f"Cannot access to index for dataset {dataset.id}: the specified index does not exist")

        return index_name

    def _build_metadata_filters(self, metadata_filters: List[MetadataFilter]) -> List[Dict[str, Any]]:
        filters = []
        for metadata_property_filter in metadata_filters:
            metadata_property = metadata_property_filter.metadata_property
            if isinstance(metadata_property_filter, TermsMetadataFilter):
                query_filter = {
                    "terms": {_mapping_key_for_metadata_property(metadata_property): metadata_property_filter.values}
                }
            elif isinstance(metadata_property_filter, (IntegerMetadataFilter, FloatMetadataFilter)):
                query = {}

                if metadata_property_filter.ge is not None:
                    query["gte"] = metadata_property_filter.ge
                if metadata_property_filter.le is not None:
                    query["lte"] = metadata_property_filter.le

                query_filter = {"range": {_mapping_key_for_metadata_property(metadata_property): query}}
            else:
                raise ValueError(f"Wrong metadata property type {metadata_property.type}")
            filters.append(query_filter)
        return filters

    def _build_response_status_filter(self, status_filter: UserResponseStatusFilter) -> Dict[str, Any]:
        if status_filter.user is None:
            response_field = ALL_RESPONSES_STATUSES_FIELD
        else:
            response_field = f"responses.{status_filter.user.username}.status"

        filters = []
        statuses = [
            ResponseStatus(status).value for status in status_filter.statuses if status != ResponseStatusFilter.missing
        ]
        if ResponseStatusFilter.missing in status_filter.statuses:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-exists-query.html
            filters.append({"bool": {"must_not": {"exists": {"field": response_field}}}})

        if statuses:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-terms-query.html
            filters.append({"terms": {response_field: statuses}})

        return {"bool": {"should": filters, "minimum_should_match": 1}}

    def _build_sort_configuration(self, sort_by: Optional[List[SortBy]] = None) -> Optional[str]:
        if not sort_by:
            return None

        sort_config = []
        for sort in sort_by:
            if isinstance(sort.field, MetadataProperty):
                sort_field_name = _mapping_key_for_metadata_property(sort.field)
            else:
                sort_field_name = sort.field
            sort_config.append(f"{sort_field_name}:{sort.order}")

        return ",".join(sort_config)

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

    @abstractmethod
    def _configure_index_settings(self) -> dict:
        """Defines settings configuration for the index. Depending on which backend is used, this may differ"""
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
