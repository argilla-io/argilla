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
from argilla._models import FieldModel

__all__ = ["FieldsAPI"]


class FieldsAPI(ResourceAPI[FieldModel]):
    """Manage datasets via the API"""

    http_client: httpx.Client

    ################
    # CRUD methods #
    ################

    @api_error_handler
    def get(self, id: UUID) -> FieldModel:
        raise NotImplementedError()

    @api_error_handler
    def create(self, field: FieldModel) -> FieldModel:
        url = f"/api/v1/datasets/{field.dataset_id}/fields"
        response = self.http_client.post(url=url, json=field.model_dump())
        response.raise_for_status()
        response_json = response.json()
        created_field = self._model_from_json(response_json=response_json)
        self._log_message(message=f"Created field {created_field.name} in dataset {field.dataset_id}")
        return created_field

    @api_error_handler
    def update(self, field: FieldModel) -> FieldModel:
        url = f"/api/v1/fields/{field.id}"
        response = self.http_client.patch(url, json=field.model_dump())
        response.raise_for_status()
        response_json = response.json()
        updated_field = self._model_from_json(response_json)
        self._log_message(message=f"Update field {updated_field.name} with id {field.id}")
        return updated_field

    @api_error_handler
    def delete(self, field_id: UUID) -> None:
        url = f"/api/v1/fields/{field_id}"
        self.http_client.delete(url).raise_for_status()
        self._log_message(message=f"Deleted field {field_id}")

    ####################
    # Utility methods #
    ####################

    @api_error_handler
    def list(self, dataset_id: UUID) -> List[FieldModel]:
        response = self.http_client.get(f"/api/v1/datasets/{dataset_id}/fields")
        response.raise_for_status()
        response_json = response.json()
        field_models = self._model_from_jsons(response_jsons=response_json["items"])
        return field_models

    ####################
    # Private methods #
    ####################

    def _model_from_json(self, response_json: Dict) -> FieldModel:
        return FieldModel(**response_json)

    def _model_from_jsons(self, response_jsons: List[Dict]) -> List[FieldModel]:
        return list(map(self._model_from_json, response_jsons))
