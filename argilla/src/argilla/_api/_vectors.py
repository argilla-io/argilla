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
from argilla._models import VectorFieldModel

__all__ = ["VectorsAPI"]


class VectorsAPI(ResourceAPI[VectorFieldModel]):
    """Manage vectors via the API"""

    http_client: httpx.Client

    ################
    # CRUD methods #
    ################

    @api_error_handler
    def create(self, vector: VectorFieldModel) -> VectorFieldModel:
        url = f"/api/v1/datasets/{vector.dataset_id}/vectors-settings"
        response = self.http_client.post(url=url, json=vector.model_dump())
        response.raise_for_status()
        response_json = response.json()
        created_vector = self._model_from_json(response_json=response_json)
        self._log_message(message=f"Created vector {created_vector.name} in dataset {created_vector.dataset_id}")
        return created_vector

    @api_error_handler
    def update(self, vector: VectorFieldModel) -> VectorFieldModel:
        url = f"/api/v1/vectors-settings/{vector.id}"
        response = self.http_client.patch(url, json=vector.model_dump())
        response.raise_for_status()
        response_json = response.json()
        updated_vector = self._model_from_json(response_json)
        self._log_message(message=f"Updated vector {updated_vector.name} with id {updated_vector.id}")
        return updated_vector

    @api_error_handler
    def delete(self, vector_id: UUID) -> None:
        url = f"/api/v1/vectors-settings/{vector_id}"
        response = self.http_client.delete(url)
        response.raise_for_status()
        self._log_message(message=f"Deleted vector with id {vector_id}")

    ####################
    # Utility methods #
    ####################

    @api_error_handler
    def list(self, dataset_id: UUID) -> List[VectorFieldModel]:
        response = self.http_client.get(f"/api/v1/datasets/{dataset_id}/vectors-settings")
        response.raise_for_status()
        response_json = response.json()
        vector_models = self._model_from_jsons(response_jsons=response_json["items"])
        return vector_models

    ####################
    # Private methods #
    ####################

    def _model_from_json(self, response_json: Dict) -> VectorFieldModel:
        return VectorFieldModel(**response_json)

    def _model_from_jsons(self, response_jsons: List[Dict]) -> List[VectorFieldModel]:
        return list(map(self._model_from_json, response_jsons))
