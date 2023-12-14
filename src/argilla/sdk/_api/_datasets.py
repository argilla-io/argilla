import datetime
from typing import List, Literal, NamedTuple, Optional
from uuid import UUID

import httpx

from argilla import sdk as sdk


class Dataset(NamedTuple):
    id: UUID

    name: str
    guidelines: str
    allow_extra_metadata: bool
    status: Literal["draft", "ready"]

    workspace_id: UUID

    inserted_at: datetime.datetime
    updated_at: datetime.datetime
    last_activity_at: datetime.datetime

    client: httpx.Client

    @classmethod
    def list(cls) -> List["Dataset"]:
        client = sdk.default_http_client

        response = client.get(f"/api/v1/me/datasets")
        response.raise_for_status()

        json_response = response.json()
        return [cls._construct_dataset_from_server(dataset) for dataset in json_response["items"]]

    @classmethod
    def _construct_dataset_from_server(cls, data: dict) -> "Dataset":
        client = sdk.default_http_client

        return cls(**data, client=client)

    @classmethod
    def get(cls, dataset_id: UUID) -> "Dataset":
        client = sdk.default_http_client

        response = client.get(f"/api/v1/datasets/{dataset_id}")

        response.raise_for_status()
        return cls._construct_dataset_from_server(response.json())

    @classmethod
    def create(
        cls,
        name: str,
        workspace_id: UUID,
        guidelines: str,
        allow_extra_metadata: bool,
    ) -> "Dataset":
        client: httpx.Client = sdk.default_http_client

        body = {
            "name": name,
            "workspace_id": str(workspace_id),
            "guidelines": guidelines,
        }

        if allow_extra_metadata is not None:
            body["allow_extra_metadata"] = allow_extra_metadata

        response = client.post("/api/v1/datasets", json=body)

        response.raise_for_status()
        return cls._construct_dataset_from_server(response.json())

    @classmethod
    def update(
        cls,
        dataset_id: Optional[UUID] = None,
        guidelines: Optional[str] = None,
        allow_extra_metadata: Optional[bool] = None,
    ) -> "Dataset":
        client = sdk.default_http_client

        response = client.patch(
            f"/api/v1/datasets/{dataset_id}",
            json={
                "guidelines": guidelines,
                "allow_extra_metadata": allow_extra_metadata,
            },
        )

        response.raise_for_status()
        return cls._construct_dataset_from_server(response.json())

    @classmethod
    def delete(cls, dataset_id: Optional[UUID] = None) -> "Dataset":
        client = sdk.default_http_client

        response = client.delete(f"/api/v1/datasets/{dataset_id}")

        response.raise_for_status()
        return cls._construct_dataset_from_server(response.json())

    @classmethod
    def publish(cls, dataset_id: UUID) -> "Dataset":
        client = sdk.default_http_client
        response = client.put(f"/api/v1/datasets/{dataset_id}/publish")

        response.raise_for_status()
        return cls._construct_dataset_from_server(response.json())
