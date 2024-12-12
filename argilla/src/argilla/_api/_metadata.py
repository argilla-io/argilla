# Copyright 2024-present, Argilla, Inc.
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

from typing import List, Dict
from uuid import UUID

import httpx

from argilla._api._base import ResourceAPI
from argilla._exceptions import api_error_handler
from argilla._models import MetadataFieldModel

__all__ = ["MetadataAPI"]


class MetadataAPI(ResourceAPI[MetadataFieldModel]):
    """Manage metadata via the API"""

    http_client: httpx.Client

    ################
    # CRUD methods #
    ################

    @api_error_handler
    def get(self, metadata_id: UUID) -> MetadataFieldModel:
        raise NotImplementedError()

    @api_error_handler
    def create(self, metadata: MetadataFieldModel) -> MetadataFieldModel:
        url = f"/api/v1/datasets/{metadata.dataset_id}/metadata-properties"
        response = self.http_client.post(url=url, json=metadata.model_dump())
        response.raise_for_status()
        response_json = response.json()
        created_metadata = self._model_from_json(response_json=response_json)
        self._log_message(message=f"Created metadata field {created_metadata.name} in dataset {metadata.dataset_id}")
        return created_metadata

    @api_error_handler
    def update(self, metadata: MetadataFieldModel) -> MetadataFieldModel:
        url = f"/api/v1/metadata-properties/{metadata.id}"
        response = self.http_client.patch(url=url, json=metadata.model_dump())
        response.raise_for_status()
        response_json = response.json()
        updated_metadata = self._model_from_json(response_json=response_json)
        self._log_message(message=f"Updated metadata field {updated_metadata.name}")
        return updated_metadata

    def delete(self, metadata_id: UUID) -> None:
        url = f"/api/v1/metadata-properties/{metadata_id}"
        self.http_client.delete(url=url).raise_for_status()
        self._log_message(message=f"Deleted metadata field {metadata_id}")

    ####################
    # Utility methods #
    ####################

    @api_error_handler
    def list(self, dataset_id: UUID) -> List[MetadataFieldModel]:
        response = self.http_client.get(f"/api/v1/me/datasets/{dataset_id}/metadata-properties")
        response.raise_for_status()
        response_json = response.json()
        return self._model_from_jsons(response_jsons=response_json["items"])

    ####################
    # Private methods #
    ####################

    def _model_from_json(self, response_json: Dict) -> MetadataFieldModel:
        return MetadataFieldModel(**response_json)

    def _model_from_jsons(self, response_jsons: List[Dict]) -> List[MetadataFieldModel]:
        return list(map(self._model_from_json, response_jsons))
