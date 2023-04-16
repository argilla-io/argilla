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
from typing import Any, Dict

from elasticsearch8 import AsyncElasticsearch as AsyncElasticsearch8x

from argilla.server.models import Annotation, AnnotationType, Dataset
from argilla.server.settings import settings


@dataclasses.dataclass
class ElasticSearchEngine:
    config: Dict[str, Any]

    def __post_init__(self):
        self.client = AsyncElasticsearch8x(**self.config)

    async def create_index(self, dataset: Dataset):
        fields = {}

        for annotation in dataset.annotations:
            fields[annotation.name] = self._field_mapping_for_annotation(annotation)

        # See https://www.elastic.co/guide/en/elasticsearch/reference/current/explicit-mapping.html
        mappings = {
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic.html#dynamic-parameters
            "dynamic": "strict",
            "properties": fields,
        }

        index_name = f"rg.{dataset.id}"
        await self.client.indices.create(index=index_name, mappings=mappings)

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


async def get_engine():
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
