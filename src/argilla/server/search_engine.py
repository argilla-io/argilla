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
from typing import Any, AsyncGenerator, Dict, Iterable, List, Optional, Union
from uuid import UUID

from opensearchpy import AsyncOpenSearch, helpers
from pydantic import BaseModel
from pydantic.utils import GetterDict

from argilla.server.enums import ResponseStatusFilter
from argilla.server.models import (
    Dataset,
    Field,
    FieldType,
    Question,
    QuestionType,
    Record,
    Response,
    ResponseStatus,
    User,
)
from argilla.server.settings import settings


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


class UserResponse(BaseModel):
    values: Optional[Dict[str, Any]]
    status: ResponseStatus


class SearchDocument(BaseModel):
    id: UUID
    fields: Dict[str, Any]

    responses: Optional[Dict[str, UserResponse]]

    class Config:
        orm_mode = True
        getter_dict = SearchDocumentGetter


@dataclasses.dataclass
class TextQuery:
    q: str
    field: Optional[str] = None


@dataclasses.dataclass
class Query:
    text: TextQuery


@dataclasses.dataclass
class UserResponseStatusFilter:
    user: User
    status: ResponseStatusFilter


@dataclasses.dataclass
class SearchResponseItem:
    record_id: UUID
    score: Optional[float]


@dataclasses.dataclass
class SearchResponses:
    items: List[SearchResponseItem]
    total: int = 0


@dataclasses.dataclass
class SearchEngine:
    config: Dict[str, Any]

    es_number_of_shards: int
    es_number_of_replicas: int

    def __post_init__(self):
        self.client = AsyncOpenSearch(**self.config)

    async def create_index(self, dataset: Dataset):
        mappings = {
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic.html#dynamic-parameters
            "dynamic": "strict",
            "dynamic_templates": self._dynamic_templates_for_question_responses(dataset.questions),
            "properties": {
                # See https://www.elastic.co/guide/en/elasticsearch/reference/current/explicit-mapping.html
                "id": {"type": "keyword"},
                "responses": {"dynamic": True, "type": "object"},
                **self._mapping_for_fields(dataset.fields),
            },
        }

        settings = {
            "number_of_shards": self.es_number_of_shards,
            "number_of_replicas": self.es_number_of_replicas,
        }

        index_name = self._index_name_for_dataset(dataset)
        await self.client.indices.create(index=index_name, body=dict(settings=settings, mappings=mappings))

    async def delete_index(self, dataset: Dataset):
        index_name = self._index_name_for_dataset(dataset)
        await self.client.indices.delete(index_name, ignore=[404], ignore_unavailable=True)

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

        _, errors = await helpers.async_bulk(client=self.client, actions=bulk_actions, raise_on_error=False)
        if errors:
            raise RuntimeError(errors)

    async def update_record_response(self, response: Response):
        record = response.record
        index_name = await self._get_index_or_raise(record.dataset)

        es_response = UserResponse(
            values={k: v["value"] for k, v in response.values.items()} if response.values else None,
            status=response.status,
        )

        await self.client.update(
            index=index_name,
            id=record.id,
            body={"doc": {"responses": {response.user.username: es_response.dict()}}},
        )

    async def delete_record_response(self, response: Response):
        record = response.record
        index_name = await self._get_index_or_raise(record.dataset)

        await self.client.update(
            index=index_name,
            id=record.id,
            body={"script": f'ctx._source["responses"].remove("{response.user.username}")'},
        )

    async def search(
        self,
        dataset: Dataset,
        query: Union[Query, str],
        user_response_status_filter: Optional[UserResponseStatusFilter] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> SearchResponses:
        # See https://www.elastic.co/guide/en/elasticsearch/reference/current/search-search.html

        if isinstance(query, str):
            query = Query(text=TextQuery(q=query))

        text_query = self._text_query_builder(dataset, text=query.text)

        bool_query: dict = {"must": [text_query]}
        if user_response_status_filter:
            bool_query["filter"] = self._response_status_filter_builder(user_response_status_filter)

        body = {
            "_source": False,
            "query": {"bool": bool_query},
            # "sort": [{"_score": "desc"}, {"id": "asc"}],
        }

        response = await self.client.search(
            index=self._index_name_for_dataset(dataset),
            body=body,
            from_=offset,
            size=limit,
            _source=False,
            sort="_score:desc,id:asc",
            track_total_hits=True,
        )

        items = [
            SearchResponseItem(record_id=UUID(hit["_id"]), score=hit["_score"]) for hit in response["hits"]["hits"]
        ]
        total = response["hits"]["total"]["value"]

        return SearchResponses(items=items, total=total)

    @staticmethod
    def _text_query_builder(dataset: Dataset, text: TextQuery) -> dict:
        if not text.field:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-multi-match-query.html
            field_names = [
                f"fields.{field.name}" for field in dataset.fields if field.settings.get("type") == FieldType.text
            ]
            return {"multi_match": {"query": text.q, "fields": field_names, "operator": "and"}}
        else:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-query.html
            return {"match": {f"fields.{text.field}": {"query": text.q, "operator": "and"}}}

    def _mapping_for_fields(self, fields: List[Field]):
        return {f"fields.{field.name}": self._es_mapping_for_field(field) for field in fields}

    def _dynamic_templates_for_question_responses(self, questions: List[Question]) -> List[dict]:
        # See https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic-templates.html
        return [
            {"status_responses": {"path_match": f"responses.*.status", "mapping": {"type": "keyword"}}},
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

    @staticmethod
    def _es_mapping_for_field(field: Field):
        field_type = field.settings["type"]

        if field_type == FieldType.text:
            return {"type": "text"}
        else:
            raise ValueError(f"ElasticSearch mappings for Field of type {field_type} cannot be generated")

    async def _get_index_or_raise(self, dataset: Dataset):
        index_name = self._index_name_for_dataset(dataset)
        if not await self.client.indices.exists(index=index_name):
            raise ValueError(f"Cannot access to index for dataset {dataset.id}: the specified index does not exist")

        return index_name

    @staticmethod
    def _index_name_for_dataset(dataset: Dataset):
        return f"rg.{dataset.id}"

    def _response_status_filter_builder(self, status_filter: UserResponseStatusFilter):
        user_response_field = f"responses.{status_filter.user.username}"

        if status_filter.status == ResponseStatusFilter.missing:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-exists-query.html
            return [{"bool": {"must_not": {"exists": {"field": user_response_field}}}}]
        else:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-terms-query.html
            return [{"term": {f"{user_response_field}.status": status_filter.status}}]


async def get_search_engine() -> AsyncGenerator[SearchEngine, None]:
    config = dict(
        hosts=settings.elasticsearch,
        verify_certs=settings.elasticsearch_ssl_verify,
        ca_certs=settings.elasticsearch_ca_path,
        retry_on_timeout=True,
        max_retries=5,
    )
    search_engine = SearchEngine(
        config,
        es_number_of_shards=settings.es_records_index_shards,
        es_number_of_replicas=settings.es_records_index_shards,
    )
    try:
        yield search_engine
    finally:
        await search_engine.client.close()
