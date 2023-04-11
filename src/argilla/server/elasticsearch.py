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
from typing import Any, Dict, List

from elasticsearch import Elasticsearch, helpers

from argilla.server.models import Annotation, AnnotationType, Dataset
from argilla.server.schemas.v1.records import RecordCreate


@dataclasses.dataclass
class ElasticSearchEngine:
    config: Dict[str, Any]

    def __post_init__(self):
        self._client = Elasticsearch(**self.config)

    def create_index(self, dataset: Dataset):
        fields = {
            "fields": {"dynamic": False, "type": "object"},
            "annotations": {"dynamic": True, "type": "object"},
            "predictions": {"dynamic": True, "type": "object"},
            "metadata": {"dynamic": False, "type": "object"},
            "vectors": {"dynamic": False, "type": "object"},
        }

        dynamic_templates = []
        # See https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic-templates.html
        for annotation in dataset.annotations:
            for field_prefix in ["annotations", "predictions"]:
                dynamic_templates.extend(
                    [
                        {
                            f"{annotation.name}_{field_prefix}": {
                                "path_match": f"{field_prefix}.*.{annotation.name}.value",
                                "mapping": self._field_mapping_for_annotation(annotation),
                            }
                        }
                    ]
                )

        mappings = {
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic.html#dynamic-parameters
            "dynamic": "strict",
            "dynamic_templates": dynamic_templates,
            "properties": fields,
        }

        index_name = self._index_name_for_dataset(dataset)
        self._client.indices.create(index=index_name, body={"mappings": mappings})

    def add_data_batch(self, dataset: Dataset, batch: List[RecordCreate]):
        index_name = self._index_name_for_dataset(dataset)

        if not self._client.indices.exists(index=index_name):
            raise RuntimeError(f"Unable to add data batch to {dataset}. The specified index is invalid.")

        bulk_actions = [
            {"_op_type": "create", "_id": r.id, "_index": index_name, **r.dict(exclude={"id"}, exclude_none=True)}
            for r in batch
        ]

        _, errors = helpers.bulk(client=self._client, index=index_name, actions=bulk_actions, raise_on_error=False)
        if errors:
            raise RuntimeError(errors)

    @staticmethod
    def _index_name_for_dataset(dataset):
        return f"rg.{dataset.id}"

    def _field_mapping_for_annotation(self, annotation_task: Annotation):
        if annotation_task.type == AnnotationType.rating:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/number.html
            return {"type": "integer"}
        elif annotation_task.type == AnnotationType.text:
            # See https://www.elastic.co/guide/en/elasticsearch/reference/current/text.html
            return {"type": "text", "index": False}
        else:
            raise ValueError(f"Annotation of type {annotation_task.type} cannot be processed")
