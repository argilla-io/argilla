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

from pydantic import BaseModel
from pydantic.utils import GetterDict

from argilla.server.enums import FieldType, MetadataPropertyType, ResponseStatusFilter
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
    IntegerMetadataFilter,
    MetadataFilter,
    SearchEngine,
    SearchResponseItem,
    SearchResponses,
    StringQuery,
    TermsMetadataFilter,
    UserResponse,
    UserResponseStatusFilter,
)


class SearchDocumentGetter(GetterDict):
    def get(self, key: Any, default: Any = None) -> Any:
        if key == "responses":
            return {
                response.user.username: UserResponse(
                    values={k: v["value"] for k, v in response.values.items()} if response.values else None,
                    status=response.status,
                )
                for response in self._obj.responses
            }
        elif key == "metadata":
            if self._obj.metadata_ is None:
                return {}

            dataset = self._obj.dataset
            return {
                str(metadata_property.id): self._obj.metadata_.get(metadata_property.name)
                for metadata_property in dataset.metadata_properties
                if self._obj.metadata_.get(metadata_property.name) is not None
            }

        return super().get(key, default)


class SearchDocument(BaseModel):
    id: UUID
    fields: Dict[str, Any]

    metadata: Optional[Dict[str, Any]] = None
    responses: Optional[Dict[str, UserResponse]]

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


def _mapping_for_metadata_property(metadata_property: MetadataProperty) -> dict:
    property_type = metadata_property.settings["type"]

    if property_type == MetadataPropertyType.terms:
        return {f"metadata.{metadata_property.id}": {"type": "keyword"}}
    elif property_type == MetadataPropertyType.integer:
        return {f"metadata.{metadata_property.id}": {"type": "long"}}
    elif property_type == MetadataPropertyType.float:
        return {f"metadata.{metadata_property.id}": {"type": "float"}}
    else:
        raise ValueError(f"Index configuration for metadata property of type {property_type} cannot be generated")


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

    async def create_index(self, dataset: Dataset):
        settings = self._configure_index_settings()
        mappings = self._configure_index_mappings(dataset)

        index_name = index_name_for_dataset(dataset)
        await self._create_index_request(index_name, mappings, settings)

    async def configure_metadata_property(self, metadata_property: MetadataProperty):
        mapping = _mapping_for_metadata_property(metadata_property)
        index_name = await self._get_index_or_raise(metadata_property.dataset)

        await self.put_index_mapping_request(index_name, mapping)

    async def delete_index(self, dataset: Dataset):
        index_name = index_name_for_dataset(dataset)

        await self._delete_index_request(index_name)

    async def add_records(self, dataset: Dataset, records: Iterable[Record]):
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

    async def delete_records(self, dataset: Dataset, records: Iterable[Record]):
        index_name = await self._get_index_or_raise(dataset)

        bulk_actions = [{"_op_type": "delete", "_id": record.id, "_index": index_name} for record in records]

        await self._bulk_op_request(bulk_actions)

    async def delete_record_response(self, response: Response):
        record = response.record
        index_name = await self._get_index_or_raise(record.dataset)

        await self._update_document_request(
            index_name, id=record.id, body={"script": f'ctx._source["responses"].remove("{response.user.username}")'}
        )

    async def search(
        self,
        dataset: Dataset,
        query: Union[StringQuery, str],
        user_response_status_filter: Optional[UserResponseStatusFilter] = None,
        metadata_filters: Optional[List[MetadataFilter]] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> SearchResponses:
        # See https://www.elastic.co/guide/en/elasticsearch/reference/current/search-search.html

        if isinstance(query, str):
            query = StringQuery(q=query)

        text_query = self._text_query_builder(dataset, text=query)

        bool_query = {"must": [text_query]}

        query_filters = []

        if metadata_filters:
            query_filters.extend(self._build_metadata_filters(metadata_filters))
        if user_response_status_filter and user_response_status_filter.statuses:
            query_filters.append(self._build_response_status_filter(user_response_status_filter))
        if query_filters:
            bool_query["filter"] = {"bool": {"should": query_filters, "minimum_should_match": "100%"}}

        query = {"bool": bool_query}
        index = await self._get_index_or_raise(dataset)

        response = await self._index_search_request(index, query=query, size=limit, from_=offset)
        return await self._process_search_response(response)

    def _configure_index_mappings(self, dataset: Dataset) -> dict:
        return {
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic.html#dynamic-parameters
            "dynamic": "strict",
            "dynamic_templates": self._dynamic_templates_for_question_responses(dataset.questions),
            "properties": {
                # See https://www.elastic.co/guide/en/elasticsearch/reference/current/explicit-mapping.html
                "id": {"type": "keyword"},
                "responses": {"dynamic": True, "type": "object"},
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
    def _text_query_builder(dataset: Dataset, text: StringQuery) -> dict:
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
            {"status_responses": {"path_match": "responses.*.status", "mapping": {"type": "keyword"}}},
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
            if isinstance(metadata_property_filter, TermsMetadataFilter):
                query_filter = {
                    "terms": {
                        f"metadata.{metadata_property_filter.metadata_property.id}": metadata_property_filter.values
                    }
                }
            elif isinstance(metadata_property_filter, (IntegerMetadataFilter, FloatMetadataFilter)):
                query = {}

                if metadata_property_filter.low:
                    query["gte"] = metadata_property_filter.low
                if metadata_property_filter.high:
                    query["lte"] = metadata_property_filter.high

                query_filter = {"range": {f"metadata.{metadata_property_filter.metadata_property.id}": query}}
            else:
                raise ValueError(f"Wrong metadata property type {metadata_property_filter.metadata_property.type}")
            filters.append(query_filter)
        return filters

    def _build_response_status_filter(self, status_filter: UserResponseStatusFilter) -> Dict[str, Any]:
        user_response_field = f"responses.{status_filter.user.username}"

        statuses = [
            ResponseStatus(status).value for status in status_filter.statuses if status != ResponseStatusFilter.missing
        ]

        filters = []
        if ResponseStatusFilter.missing in status_filter.statuses:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-exists-query.html
            filters.append({"bool": {"must_not": {"exists": {"field": user_response_field}}}})

        if statuses:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-terms-query.html
            filters.append({"terms": {f"{user_response_field}.status": statuses}})

        return {"bool": {"should": filters, "minimum_should_match": 1}}

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
    async def _index_search_request(self, index: str, query: dict, size: int, from_: int) -> dict:
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
