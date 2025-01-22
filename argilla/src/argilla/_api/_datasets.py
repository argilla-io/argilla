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

from typing import List, Optional, Dict
from uuid import UUID

import httpx
from argilla._api._base import ResourceAPI
from argilla._exceptions._api import api_error_handler
from argilla._models import DatasetModel

__all__ = ["DatasetsAPI"]

from argilla._models._dataset_progress import UserProgressModel, DatasetProgressModel


class DatasetsAPI(ResourceAPI[DatasetModel]):
    """Manage datasets via the API"""

    http_client: httpx.Client
    url_stub = "/api/v1/datasets"

    ################
    # CRUD methods #
    ################

    @api_error_handler
    def create(self, dataset: "DatasetModel") -> "DatasetModel":
        json_body = dataset.model_dump(exclude_unset=True)
        response = self.http_client.post(
            url=self.url_stub,
            json=json_body,
        )
        response.raise_for_status()
        response_json = response.json()
        dataset = self._model_from_json(response_json=response_json)
        self._log_message(message=f"Created dataset {dataset.name}")
        return dataset

    @api_error_handler
    def update(self, dataset: "DatasetModel") -> "DatasetModel":
        json_body = dataset.model_dump(exclude_unset=True)
        dataset_id = json_body["id"]  # type: ignore
        response = self.http_client.patch(f"{self.url_stub}/{dataset_id}", json=json_body)
        response.raise_for_status()
        response_json = response.json()
        dataset = self._model_from_json(response_json=response_json)
        self._log_message(message=f"Updated dataset {dataset.id}")
        return dataset

    @api_error_handler
    def get(self, dataset_id: UUID) -> "DatasetModel":
        response = self.http_client.get(url=f"{self.url_stub}/{dataset_id}")
        response.raise_for_status()
        response_json = response.json()
        dataset = self._model_from_json(response_json=response_json)
        self._log_message(message=f"Got dataset {dataset.id}")
        return dataset

    @api_error_handler
    def delete(self, dataset_id: UUID) -> None:
        response = self.http_client.delete(f"{self.url_stub}/{dataset_id}")
        response.raise_for_status()
        self._log_message(message=f"Deleted dataset {dataset_id}")

    def exists(self, dataset_id: UUID) -> bool:
        response = self.http_client.get(f"{self.url_stub}/{dataset_id}")
        return response.status_code == 200

    ####################
    # Utility methods #
    ####################

    @api_error_handler
    def get_progress(self, dataset_id: UUID) -> DatasetProgressModel:
        response = self.http_client.get(f"{self.url_stub}/{dataset_id}/progress")
        response.raise_for_status()
        response_json = response.json()

        self._log_message(message=f"Got progress for dataset {dataset_id}")
        return DatasetProgressModel.model_validate(response_json)

    @api_error_handler
    def list_users_progress(self, dataset_id: UUID) -> List[UserProgressModel]:
        response = self.http_client.get(f"{self.url_stub}/{dataset_id}/users/progress")
        response.raise_for_status()
        response_json = response.json()

        self._log_message(message=f"Got users progress for dataset {dataset_id}")
        return [UserProgressModel.model_validate(data) for data in response_json["users"]]

    @api_error_handler
    def publish(self, dataset_id: UUID) -> "DatasetModel":
        response = self.http_client.put(url=f"{self.url_stub}/{dataset_id}/publish")
        response.raise_for_status()
        response_json = response.json()
        self._log_message(message=f"Published dataset {dataset_id}")
        return self._model_from_json(response_json=response_json)

    @api_error_handler
    def list(self, workspace_id: Optional[UUID] = None) -> List["DatasetModel"]:
        response = self.http_client.get("/api/v1/me/datasets")
        response.raise_for_status()
        response_json = response.json()
        datasets = self._model_from_jsons(response_jsons=response_json["items"])
        if workspace_id:
            datasets = [dataset for dataset in datasets if dataset.workspace_id == workspace_id]
        self._log_message(message=f"Listed {len(datasets)} datasets")
        return datasets

    def get_by_name_and_workspace_id(self, name: str, workspace_id: UUID) -> Optional["DatasetModel"]:
        datasets = self.list(workspace_id=workspace_id)
        for dataset in datasets:
            if dataset.name == name:
                self._log_message(message=f"Got dataset {dataset.name}")
                return dataset

    def name_exists(self, name: str, workspace_id: UUID) -> bool:
        return bool(self.get_by_name_and_workspace_id(name=name, workspace_id=workspace_id))

    ####################
    # Private methods #
    ####################

    def _model_from_json(self, response_json: Dict) -> "DatasetModel":
        return DatasetModel(**response_json)

    def _model_from_jsons(self, response_jsons: List[Dict]) -> List["DatasetModel"]:
        return list(map(self._model_from_json, response_jsons))
