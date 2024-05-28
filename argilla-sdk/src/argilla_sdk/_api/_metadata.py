# Copyright 2024-present, Argilla, Inc.
# TODO: This license is not consistent with the license used in the project.
#       Delete the inconsistent license and above line and rerun pre-commit to insert a good license.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Dict, List
from uuid import UUID

import httpx

from argilla_sdk._api._base import ResourceAPI
from argilla_sdk._exceptions import api_error_handler
from argilla_sdk._models import MetadataFieldModel

__all__ = ["MetadataAPI"]


class MetadataAPI(ResourceAPI[MetadataFieldModel]):
    """Manage metadata via the API"""

    http_client: httpx.Client

    ################
    # CRUD methods #
    ################

    @api_error_handler
    def create(self, dataset_id: UUID, metadata_field: MetadataFieldModel) -> MetadataFieldModel:
        url = f"/api/v1/datasets/{dataset_id}/metadata-properties"
        response = self.http_client.post(url=url, json=metadata_field.model_dump())
        response.raise_for_status()
        response_json = response.json()
        metadata_field_model = self._model_from_json(response_json=response_json)
        self.log(message=f"Created metadata field {metadata_field_model.name} in dataset {dataset_id}")
        return metadata_field_model

    @api_error_handler
    def update(self, metadata_field: MetadataFieldModel) -> MetadataFieldModel:
        url = f"/api/v1/metadata-properties/{metadata_field.id}"
        response = self.http_client.patch(url=url, json=metadata_field.model_dump())
        response.raise_for_status()
        response_json = response.json()
        metadata_field_model = self._model_from_json(response_json=response_json)
        self.log(message=f"Updated field {metadata_field_model.name}")
        return metadata_field_model

    @api_error_handler
    def delete(self, id: UUID) -> None:
        url = f"/api/v1/metadata-properties/{id}"
        self.http_client.delete(url=url).raise_for_status()
        self.log(message=f"Deleted field {id}")

    @api_error_handler
    def get(self, id: UUID) -> MetadataFieldModel:
        raise NotImplementedError()

    ####################
    # Utility methods #
    ####################

    def create_many(self, dataset_id: UUID, metadata_fields: List[MetadataFieldModel]) -> List[MetadataFieldModel]:
        metadata_field_models = []
        for metadata_field in metadata_fields:
            metadata_field_model = self.create(dataset_id=dataset_id, metadata_field=metadata_field)
            metadata_field_models.append(metadata_field_model)
        return metadata_field_models

    @api_error_handler
    def list(self, dataset_id: UUID) -> List[MetadataFieldModel]:
        response = self.http_client.get(f"/api/v1/me/datasets/{dataset_id}/metadata-properties")
        response.raise_for_status()
        response_json = response.json()
        metadata_field_model = self._model_from_jsons(response_jsons=response_json["items"])
        return metadata_field_model

    ####################
    # Private methods #
    ####################

    def _model_from_json(self, response_json: Dict) -> MetadataFieldModel:
        response_json["inserted_at"] = self._date_from_iso_format(date=response_json["inserted_at"])
        response_json["updated_at"] = self._date_from_iso_format(date=response_json["updated_at"])
        return MetadataFieldModel(**response_json)

    def _model_from_jsons(self, response_jsons: List[Dict]) -> List[MetadataFieldModel]:
        return list(map(self._model_from_json, response_jsons))
