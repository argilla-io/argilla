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

from pydantic import BaseModel, conint
from pydantic.utils import GetterDict

from argilla.server.enums import FieldType, ResponseStatusFilter
from argilla.server.models import (
    Dataset,
    Field,
    Question,
    QuestionType,
    Record,
    Response,
    ResponseStatus,
    Vector,
    VectorSettings,
)
from argilla.server.search_engine.base import (
    SearchEngine,
    SearchResponseItem,
    SearchResponses,
    StringQuery,
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
        return super().get(key, default)


class SearchDocument(BaseModel):
    id: UUID
    fields: Dict[str, Any]

    responses: Optional[Dict[str, UserResponse]]

    class Config:
        orm_mode = True
        getter_dict = SearchDocumentGetter


def index_name_for_dataset(dataset: Dataset):
    return f"rg.{dataset.id}"


def field_name_for_vector_settings(vector_settings: VectorSettings) -> str:
    return f"vectors.{vector_settings.id}"


def _mapping_for_field(field: Field) -> dict:
    field_type = field.settings["type"]

    if field_type == FieldType.text:
        return {f"fields.{field.name}": {"type": "text"}}
    else:
        raise ValueError(f"Index configuration for field of type {field_type} cannot be generated")


@dataclasses.dataclass
class BaseElasticAndOpenSearchEngine(SearchEngine):
    """
    Since both ElasticSearch and OpenSearch engines implementations share a lot of code,
    this class create an abstraction for the commons part of the code, letting each child
    resolve their own implementation details.

    All method for SearchEngine interface are implemented here. This abstract class defines
    some abstract method mostly for:
        1. Requesting data from the engine, since the client signatures may differ
        2. Prepare mappings for vector-related configuration
        3. Searching records with similarity search

    The rest of the code will be shared by both implementation
    """

    async def create_index(self, dataset: Dataset):
        mappings = self._configure_index_mappings(dataset)
        settings = self._configure_index_settings()

        index_name = index_name_for_dataset(dataset)
        await self._create_index_request(index_name, mappings, settings)

    async def delete_index(self, dataset: Dataset):
        index_name = index_name_for_dataset(dataset)

        await self._delete_index_request(index_name)

    async def add_records(self, dataset: Dataset, records: Iterable[Record]):
        index_name = await self._get_index_or_raise(dataset)

        bulk_actions = [
            {
                "_op_type": "index",  # If document exist, we update source with latest version
                "_id": record.id,
                "_index": index_name,
                **SearchDocument.from_orm(record).dict(),
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

    async def set_records_vectors(self, dataset: Dataset, vectors: Iterable[Vector]):
        index_name = await self._get_index_or_raise(dataset)

        bulk_actions = [
            {
                "_op_type": "update",
                "_id": vector.record_id,
                "_index": index_name,
                "doc": {field_name_for_vector_settings(vector.vector_settings): vector.value},
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
        user_response_status_filter: Optional[UserResponseStatusFilter] = None,
        max_results: conint(ge=2, le=500) = 100,
        threshold: Optional[float] = None,
    ) -> SearchResponses:
        if not (value or record):
            raise ValueError("Must provide vector value or record to compute the similarity search")

        vector_value = value

        if not vector_value:
            for vector in record.vectors:
                if vector.vector_settings_id == vector_settings.id:
                    vector_value = vector.value

        if not vector_value:
            raise ValueError("Cannot find a vector value to apply with provided info")

        index = await self._get_index_or_raise(dataset)
        response = await self._request_similarity_search(
            index=index,
            vector_settings=vector_settings,
            value=vector_value,
            k=max_results,
            user_response_status_filter=user_response_status_filter,
        )

        return await self._process_search_response(response, threshold)

    async def delete_record_response(self, response: Response):
        record = response.record
        index_name = await self._get_index_or_raise(record.dataset)

        await self._update_document_request(
            index_name, id=record.id, body={"script": f'ctx._source["responses"].remove("{response.user.username}")'}
        )

    async def configure_index_vectors(self, vector_settings: VectorSettings) -> None:
        index = await self._get_index_or_raise(vector_settings.dataset)

        mappings = self._mapping_for_vector_settings(vector_settings)
        await self.put_index_mapping_request(index, mappings)

    async def search(
        self,
        dataset: Dataset,
        query: Union[StringQuery, str],
        user_response_status_filter: Optional[UserResponseStatusFilter] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> SearchResponses:
        # See https://www.elastic.co/guide/en/elasticsearch/reference/current/search-search.html

        if isinstance(query, str):
            query = StringQuery(q=query)

        text_query = self._text_query_builder(dataset, text=query)

        bool_query = {"must": [text_query]}
        if user_response_status_filter:
            bool_query["filter"] = self._response_status_filter_builder(user_response_status_filter)

        query = {"bool": bool_query}
        index = await self._get_index_or_raise(dataset)

        response = await self._index_search_request(index, query=query, size=limit, from_=offset)

        return await self._process_search_response(response)

    def _configure_index_mappings(self, dataset) -> dict:
        return {
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic.html#dynamic-parameters
            "dynamic": "strict",
            "dynamic_templates": self._dynamic_templates_for_question_responses(dataset.questions),
            "properties": {
                # See https://www.elastic.co/guide/en/elasticsearch/reference/current/explicit-mapping.html
                "id": {"type": "keyword"},
                "responses": {"dynamic": True, "type": "object"},
                **self._mapping_for_vectors_settings(dataset.vectors_settings),
                **self._mapping_for_fields(dataset.fields),
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

    def _response_status_filter_builder(self, status_filter: UserResponseStatusFilter) -> Optional[Dict[str, Any]]:
        if not status_filter.statuses:
            return None

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

    def _mapping_for_vectors_settings(self, vectors_settings: List[VectorSettings]) -> dict:
        mappings = {}
        for vector in vectors_settings:
            mappings.update(self._mapping_for_vector_settings(vector))

        return mappings

    @abstractmethod
    def _configure_index_settings(self) -> dict:
        """Defines settings configuration for the index. Depending on which backend is used, this may differ"""
        pass

    @abstractmethod
    def _mapping_for_vector_settings(self, vector_settings: VectorSettings) -> dict:
        """Defines one mapping property configuration for a vector_setting definitio"""
        pass

    @abstractmethod
    async def _request_similarity_search(
        self,
        index: str,
        vector_settings: VectorSettings,
        value: List[float],
        k: int,
        user_response_status_filter: Optional[UserResponseStatusFilter] = None,
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
