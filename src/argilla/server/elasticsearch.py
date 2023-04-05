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

from elasticsearch import Elasticsearch

from argilla.server.models import Annotation, AnnotationType, Dataset


@dataclasses.dataclass
class ElasticSearchEngine:
    config: Dict[str, Any]

    def __post_init__(self):
        self._client = Elasticsearch(**self.config)

    def create_dataset_index(self, dataset: Dataset) -> str:
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
        self._client.indices.create(index=index_name, body={"mappings": mappings})

        return index_name

    def _field_mapping_for_annotation(self, annotation_task: Annotation):
        if annotation_task.type == AnnotationType.rating:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/number.html
            return {"type": "integer"}
        elif annotation_task.type == AnnotationType.text:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/text.html
            return {"type": "text"}
        else:
            raise ValueError(f"Annotation of type {annotation_task.type} cannot be processed")
