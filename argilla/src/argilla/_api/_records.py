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

from typing import List, Dict, Tuple, Union, Optional
from uuid import UUID

import httpx
from typing_extensions import deprecated

from argilla._api._base import ResourceAPI
from argilla._exceptions import api_error_handler
from argilla._models import RecordModel, UserResponseModel, SearchQueryModel

__all__ = ["RecordsAPI"]


class RecordsAPI(ResourceAPI[RecordModel]):
    """Manage datasets via the API"""

    MAX_RECORDS_PER_CREATE_BULK = 500
    MAX_RECORDS_PER_UPSERT_BULK = 500
    MAX_RECORDS_PER_DELETE_BULK = 100

    http_client: httpx.Client

    ################
    # CRUD methods #
    ################
    @api_error_handler
    def get(self, record_id: UUID) -> RecordModel:
        response = self.http_client.get(f"/api/v1/records/{record_id}")
        response.raise_for_status()
        response_json = response.json()
        return self._model_from_json(response_json=response_json)

    @api_error_handler
    def update(self, record: RecordModel) -> RecordModel:
        response = self.http_client.patch(
            url=f"/api/v1/records/{record.id}",
            json=record.model_dump(),
        )
        response.raise_for_status()
        response_json = response.json()
        return self._model_from_json(response_json=response_json)

    @api_error_handler
    def delete(self, record_id: UUID) -> None:
        response = self.http_client.delete(f"/api/v1/records/{record_id}")
        response.raise_for_status()
        self._log_message(message=f"Deleted record {record_id}")

    ####################
    # Utility methods #
    ####################
    @api_error_handler
    def list(
        self,
        dataset_id: UUID,
        offset: int = 0,
        limit: int = 100,
        with_suggestions: bool = True,
        with_responses: bool = True,
        with_vectors: Optional[Union[List, bool]] = None,
    ) -> List[RecordModel]:
        """List records in a dataset
        Args:
            dataset_id: The ID of the dataset
            offset: The offset to start from
            limit: The number of records to return
            with_vectors: The name of vectors to include
            with_suggestions: Whether to include suggestions
            with_responses: Whether to include responses
        """
        include = []
        if with_suggestions:
            include.append("suggestions")
        if with_responses:
            include.append("responses")
        if with_vectors:
            include.append(self._represent_vectors_to_include(with_vectors))

        params = {
            "offset": offset,
            "limit": limit,
            "include": include,
        }

        response = self.http_client.get(f"/api/v1/datasets/{dataset_id}/records", params=params)
        response.raise_for_status()
        response_json = response.json()
        json_records = response_json["items"]
        return self._model_from_jsons(json_records)

    @api_error_handler
    def search(
        self,
        dataset_id: UUID,
        query: SearchQueryModel,
        offset: int = 0,
        limit: int = 100,
        with_suggestions: bool = True,
        with_responses: bool = True,
        with_vectors: Optional[Union[List, bool]] = None,
    ) -> Tuple[List[Tuple[RecordModel, float]], int]:
        include = []
        if with_suggestions:
            include.append("suggestions")
        if with_responses:
            include.append("responses")
        if with_vectors:
            include.append(self._represent_vectors_to_include(with_vectors))
        params = {
            "offset": offset,
            "limit": limit,
            "include": include,
        }

        response = self.http_client.post(
            f"/api/v1/datasets/{dataset_id}/records/search",
            json=query.model_dump(by_alias=True),
            params=params,
        )
        response.raise_for_status()
        response_json = response.json()
        json_items = response_json["items"]
        total = response_json["total"]
        return [(self._model_from_json(item["record"]), item["query_score"]) for item in json_items], total

    @api_error_handler
    @deprecated("Use `bulk_create` or `bulk_upsert` instead")
    def create_many(self, dataset_id: UUID, records: List[RecordModel]) -> None:
        record_dicts = [record.model_dump() for record in records]
        response = self.http_client.post(
            url=f"/api/v1/datasets/{dataset_id}/records",
            json={"items": record_dicts},
        )
        response.raise_for_status()
        self._log_message(message=f"Created {len(records)} records in dataset {dataset_id}")
        # TODO: Once server returns the records, return them here

    @api_error_handler
    @deprecated("Use `bulk_create` or `bulk_upsert` instead")
    def update_many(self, dataset_id: UUID, records: List[RecordModel]) -> None:
        record_dicts = [record.model_dump() for record in records]
        response = self.http_client.patch(
            url=f"/api/v1/datasets/{dataset_id}/records",
            json={"items": record_dicts},
        )
        response.raise_for_status()
        self._log_message(message=f"Updated {len(records)} records in dataset {dataset_id}")

    @api_error_handler
    def delete_many(self, dataset_id: UUID, records: List[RecordModel]) -> None:
        record_ids = [str(record.id) for record in records]
        record_ids_str = ",".join(record_ids)
        response = self.http_client.delete(url=f"/api/v1/datasets/{dataset_id}/records", params={"ids": record_ids_str})
        response.raise_for_status()
        self._log_message(message=f"Deleted {len(records)} records in dataset {dataset_id}")

    @api_error_handler
    def bulk_create(
        self, dataset_id: UUID, records: List[RecordModel]
    ) -> Union[List[RecordModel], Tuple[List[RecordModel], int]]:
        if len(records) > self.MAX_RECORDS_PER_CREATE_BULK:
            raise ValueError(f"Cannot create more than {self.MAX_RECORDS_PER_CREATE_BULK} records at once")
        record_dicts = [record.model_dump() for record in records]
        response = self.http_client.post(
            url=f"/api/v1/datasets/{dataset_id}/records/bulk",
            json={"items": record_dicts},
        )
        response.raise_for_status()
        response_json = response.json()
        self._log_message(message=f"Created {len(records)} in dataset {dataset_id}")
        return self._model_from_jsons(response_jsons=response_json["items"])

    @api_error_handler
    def bulk_upsert(self, dataset_id: UUID, records: List[RecordModel]) -> Tuple[List[RecordModel], int]:
        if len(records) > self.MAX_RECORDS_PER_UPSERT_BULK:
            raise ValueError(f"Cannot upsert more than {self.MAX_RECORDS_PER_UPSERT_BULK} records at once")
        record_dicts = [record.model_dump() for record in records]
        response = self.http_client.put(
            url=f"/api/v1/datasets/{dataset_id}/records/bulk",
            json={"items": record_dicts},
        )
        response.raise_for_status()
        response_json = response.json()
        updated = len(response_json.get("updated_item_ids", []))
        self._log_message(
            message=f"Updated {updated} records and create {len(records) - updated} records in dataset {dataset_id}"
        )
        return self._model_from_jsons(response_jsons=response_json["items"]), updated

    ####################
    # Response methods #
    ####################

    @api_error_handler
    def create_record_response(self, record_id: UUID, user_response: UserResponseModel) -> None:
        self.http_client.post(
            url=f"/api/v1/records/{record_id}/responses",
            json=user_response.model_dump(),
        ).raise_for_status()

    def create_record_responses(self, record: RecordModel) -> None:
        if not record.responses:
            return
        if not record.id:
            raise ValueError("Record must have an ID to create responses")
        for record_response in record.responses:
            self.create_record_response(record_id=record.id, user_response=record_response)

    ####################
    # Private methods #
    ####################

    def _model_from_json(self, response_json: Dict) -> RecordModel:
        if "vectors" in response_json:
            response_json["vectors"] = [
                {"name": key, "vector_values": value} for key, value in response_json["vectors"].items()
            ]
        return RecordModel(**response_json)

    def _model_from_jsons(self, response_jsons: List[Dict]) -> List[RecordModel]:
        return list(map(self._model_from_json, response_jsons))

    def _represent_vectors_to_include(self, with_vectors: Union[List, str, bool]) -> Union[str, None]:
        """Represent the vectors to include in the API request"""
        vector_stub = "vectors"
        if with_vectors is True:
            return vector_stub
        elif not with_vectors:
            return None
        elif isinstance(with_vectors, str):
            return f"{vector_stub}:{with_vectors}"
        elif isinstance(with_vectors, list):
            return f"{vector_stub}:{','.join(with_vectors)}"
        else:
            raise ValueError(f"Invalid value for with_vectors: {with_vectors}")
