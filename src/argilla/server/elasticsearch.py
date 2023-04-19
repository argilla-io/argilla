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
from typing import Any, Dict, Iterable, List, Optional

from elasticsearch8 import AsyncElasticsearch as AsyncElasticsearch8x
from elasticsearch8 import helpers
from pydantic import BaseModel
from pydantic.utils import GetterDict

from argilla.server.models import Annotation, AnnotationType, Dataset, Record
from argilla.server.settings import settings


class ElasticSearchRecordGetter(GetterDict):
    def get(self, key: Any, default: Any = None) -> Any:
        if key == "responses":
            return {response.user.username: response.values for response in self._obj.responses}
        return super().get(key, default)


class ElasticSearchRecord(BaseModel):
    fields: Dict[str, Any]

    responses: Optional[Dict[str, Dict[str, Any]]]

    class Config:
        orm_mode = True
        getter_dict = ElasticSearchRecordGetter


@dataclasses.dataclass
class ElasticSearchEngine:
    config: Dict[str, Any]

    def __post_init__(self):
        self.client = AsyncElasticsearch8x(**self.config)

    async def create_index(self, dataset: Dataset):
        fields = {
            "fields": {"dynamic": True, "type": "object"},
            "responses": {"dynamic": True, "type": "object"},
        }

        # See https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic-templates.html
        dynamic_templates = [
            {
                f"{annotation.name}_responses": {
                    "path_match": f"responses.*.{annotation.name}",
                    "mapping": self._field_mapping_for_annotation(annotation),
                }
            }
            for annotation in dataset.annotations
        ]

        # See https://www.elastic.co/guide/en/elasticsearch/reference/current/explicit-mapping.html
        mappings = {
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic.html#dynamic-parameters
            "dynamic": "strict",
            "dynamic_templates": dynamic_templates,
            "properties": fields,
        }

        index_name = self._index_name_for_dataset(dataset)
        await self.client.indices.create(index=index_name, mappings=mappings)

    async def add_records(self, dataset: Dataset, records: Iterable[Record]):
        index_name = self._index_name_for_dataset(dataset)

        if not await self.client.indices.exists(index=index_name):
            raise ValueError(
                f"Unable to add data records to index for dataset {dataset.id}. The specified index is invalid."
            )

        bulk_actions = [
            {
                "_op_type": "index",  # If document exist, we update source with latest version
                "_id": record.id,
                "_index": index_name,
                **ElasticSearchRecord.from_orm(record).dict(),
            }
            for record in records
        ]

        _, errors = await helpers.async_bulk(client=self.client, actions=bulk_actions, raise_on_error=False)
        if errors:
            raise RuntimeError(errors)

    @staticmethod
    def _index_name_for_dataset(dataset: Dataset):
        return f"rg.{dataset.id}"

    def _field_mapping_for_annotation(self, annotation_task: Annotation):
        settings_type = annotation_task.settings.get("type")

        if settings_type == AnnotationType.rating:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/number.html
            return {"type": "integer"}
        elif settings_type == AnnotationType.text:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/text.html
            return {"type": "text"}
        else:
            raise ValueError(f"ES mappings for Annotation of type {settings_type} cannot be generated")


async def get_search_engine():
    config = dict(
        hosts=settings.elasticsearch,
        verify_certs=settings.elasticsearch_ssl_verify,
        ca_certs=settings.elasticsearch_ca_path,
        retry_on_timeout=True,
        max_retries=5,
    )
    search_engine = ElasticSearchEngine(config)
    try:
        yield search_engine
    finally:
        await search_engine.client.close()
