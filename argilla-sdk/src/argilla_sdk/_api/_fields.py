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
from argilla_sdk._models import FieldBaseModel, FieldModel, TextFieldModel

__all__ = ["FieldsAPI"]


class FieldsAPI(ResourceAPI[FieldBaseModel]):
    """Manage datasets via the API"""

    http_client: httpx.Client

    ################
    # CRUD methods #
    ################

    @api_error_handler
    def create(self, dataset_id: UUID, field: FieldModel) -> FieldModel:
        url = f"/api/v1/datasets/{dataset_id}/fields"
        response = self.http_client.post(url=url, json=field.model_dump())
        response.raise_for_status()
        response_json = response.json()
        field_model = self._model_from_json(response_json=response_json)
        self.log(message=f"Created field {field_model.name} in dataset {dataset_id}")
        return field_model

    @api_error_handler
    def update(self, field: FieldModel) -> FieldModel:
        # TODO: Implement update method for fields with server side ID
        raise NotImplementedError

    @api_error_handler
    def delete(self, dataset_id: UUID) -> None:
        # TODO: Implement delete method for fields with server side ID
        raise NotImplementedError

    ####################
    # Utility methods #
    ####################

    def create_many(self, dataset_id: UUID, fields: List[FieldModel]) -> List[FieldModel]:
        field_models = []
        for field in fields:
            field_model = self.create(dataset_id=dataset_id, field=field)
            field_models.append(field_model)
        return field_models

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
        response_json["inserted_at"] = self._date_from_iso_format(date=response_json["inserted_at"])
        response_json["updated_at"] = self._date_from_iso_format(date=response_json["updated_at"])
        return self._get_model_from_response(response_json=response_json)

    def _model_from_jsons(self, response_jsons: List[Dict]) -> List[FieldModel]:
        return list(map(self._model_from_json, response_jsons))

    def _get_model_from_response(self, response_json: Dict) -> FieldModel:
        try:
            field_type = response_json.get("settings", {}).get("type")
        except Exception as e:
            raise ValueError("Invalid response type: missing 'settings.type' in response") from e
        if field_type == "text":
            # TODO: Avoid apply validations here (check_fields=False?)
            return TextFieldModel(**response_json)
        else:
            # TODO: Add more field types
            raise ValueError(f"Invalid field type: {field_type}")
