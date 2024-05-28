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
from argilla_sdk._api._base import ResourceAPI
from argilla_sdk._exceptions import api_error_handler
from argilla_sdk._models import VectorFieldModel

__all__ = ["VectorsAPI"]


class VectorsAPI(ResourceAPI[VectorFieldModel]):
    """Manage vectors via the API"""

    http_client: httpx.Client

    ################
    # CRUD methods #
    ################

    @api_error_handler
    def create(self, dataset_id: UUID, vector: VectorFieldModel) -> VectorFieldModel:
        url = f"/api/v1/datasets/{dataset_id}/vectors-settings"
        response = self.http_client.post(url=url, json=vector.model_dump())
        response.raise_for_status()
        response_json = response.json()
        vector_model = self._model_from_json(response_json=response_json)
        self.log(message=f"Created vector {vector_model.name} in dataset {dataset_id}")
        return vector_model

    @api_error_handler
    def update(self, vector: VectorFieldModel) -> VectorFieldModel:
        # TODO: Implement update method for vectors with server side ID
        raise NotImplementedError

    @api_error_handler
    def delete(self, vector_id: UUID) -> None:
        # TODO: Implement delete method for vectors with server side ID
        raise NotImplementedError

    ####################
    # Utility methods #
    ####################

    def create_many(self, dataset_id: UUID, vectors: List[VectorFieldModel]) -> List[VectorFieldModel]:
        vector_models = []
        for vector in vectors:
            vector_model = self.create(dataset_id=dataset_id, vector=vector)
            vector_models.append(vector_model)
        return vector_models

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
        response_json["inserted_at"] = self._date_from_iso_format(date=response_json["inserted_at"])
        response_json["updated_at"] = self._date_from_iso_format(date=response_json["updated_at"])
        return VectorFieldModel(**response_json)

    def _model_from_jsons(self, response_jsons: List[Dict]) -> List[VectorFieldModel]:
        return list(map(self._model_from_json, response_jsons))
