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
from typing import Any, Dict, Iterable, Optional

from opensearchpy import AsyncOpenSearch, helpers
from pydantic import BaseModel
from pydantic.utils import GetterDict

from argilla.server.models import (
    Dataset,
    Field,
    FieldType,
    Question,
    QuestionType,
    Record,
    ResponseStatus,
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
    fields: Dict[str, Any]

    responses: Optional[Dict[str, UserResponse]]

    class Config:
        orm_mode = True
        getter_dict = SearchDocumentGetter


@dataclasses.dataclass
class SearchEngine:
    config: Dict[str, Any]

    def __post_init__(self):
        self.client = AsyncOpenSearch(**self.config)

    async def create_index(self, dataset: Dataset):
        fields = {
            "responses": {"dynamic": True, "type": "object"},
        }

        for field in dataset.fields:
            fields[f"fields.{field.name}"] = self._es_mapping_for_field(field)

        # See https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic-templates.html
        dynamic_templates = [
            {
                f"{question.name}_responses": {
                    "path_match": f"responses.*.values.{question.name}",
                    "mapping": self._field_mapping_for_question(question),
                },
            }
            for question in dataset.questions
        ]

        # See https://www.elastic.co/guide/en/elasticsearch/reference/current/explicit-mapping.html
        mappings = {
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic.html#dynamic-parameters
            "dynamic": "strict",
            "dynamic_templates": dynamic_templates,
            "properties": fields,
        }

        index_name = self._index_name_for_dataset(dataset)
        await self.client.indices.create(index=index_name, body=dict(mappings=mappings))

    def _field_mapping_for_question(self, question: Question):
        settings = question.parsed_settings

        if settings.type == QuestionType.rating:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/number.html
            return {"type": "integer"}
        elif settings.type == QuestionType.text:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/text.html
            return {"type": "text", "index": False}
        else:
            raise ValueError(f"ElasticSearch mappings for Question of type {settings.type} cannot be generated")

    def _es_mapping_for_field(self, field: Field):
        field_type = field.settings["type"]

        if field_type == FieldType.text:
            return {"type": "text"}
        else:
            raise ValueError(f"ElasticSearch mappings for Field of type {field_type} cannot be generated")

    async def add_records(self, dataset: Dataset, records: Iterable[Record]):
        index_name = self._index_name_for_dataset(dataset)

        if not await self.client.indices.exists(index=index_name):
            raise ValueError(
                f"Unable to add data records to index for dataset {dataset.id}: the specified index is invalid."
            )

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

    @staticmethod
    def _index_name_for_dataset(dataset: Dataset):
        return f"rg.{dataset.id}"


async def get_search_engine():
    config = dict(
        hosts=settings.elasticsearch,
        verify_certs=settings.elasticsearch_ssl_verify,
        ca_certs=settings.elasticsearch_ca_path,
        retry_on_timeout=True,
        max_retries=5,
    )
    search_engine = SearchEngine(config)
    try:
        yield search_engine
    finally:
        await search_engine.client.close()
