import dataclasses
import datetime
from typing import Any, Dict, List, Literal, NamedTuple, Optional
from uuid import UUID

import httpx

from argilla import sdk as sdk


@dataclasses.dataclass
class TextFieldSettings:
    type: Literal["text"] = "text"
    use_markdown: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "use_markdown": self.use_markdown,
        }


class Field(NamedTuple):
    id: UUID

    name: str
    title: str
    required: bool
    settings: TextFieldSettings

    inserted_at: datetime.datetime
    updated_at: datetime.datetime

    client: httpx.Client

    dataset_id: Optional[UUID] = None  # This can be None since the backend API entities are not aligned

    @classmethod
    def list(cls, dataset_id: UUID) -> List["Field"]:
        client = sdk.default_http_client

        response = client.get(f"/api/v1/datasets/{dataset_id}/fields")
        response.raise_for_status()

        json_response = response.json()
        return [cls._construct_field_from_server(field) for field in json_response["items"]]

    @classmethod
    def get(cls, field_id: UUID) -> "Field":
        client = sdk.default_http_client

        response = client.get(f"/api/v1/fields/{field_id}")
        response.raise_for_status()

        return cls._construct_field_from_server(response.json())

    @classmethod
    def by_name(cls, dataset_id: UUID, name: str) -> Optional["Field"]:
        # TODO: Maybe we should support an query parameter for this?
        fields = cls.list(dataset_id)
        for field in fields:
            if field.name == name:
                return field

    @classmethod
    def create(cls, dataset_id: UUID, name: str, title: str, required: bool, settings: TextFieldSettings) -> "Field":
        client = sdk.default_http_client

        response = client.post(
            f"/api/v1/datasets/{dataset_id}/fields",
            json={
                "name": name,
                "title": title,
                "required": required,
                "settings": settings.to_dict(),
            },
        )

        response.raise_for_status()
        return cls._construct_field_from_server(response.json())

    def update(self, title: Optional[str] = None, settings: Optional[TextFieldSettings] = None) -> "Field":
        client = self.client

        title = title or self.title
        settings = settings or self.settings

        response = client.patch(
            f"/api/v1/fields/{self.id}",
            json={
                "title": title,
                "settings": settings.to_dict(),
            },
        )

        response.raise_for_status()
        return self._construct_field_from_server(response.json())

    def delete(self) -> "Field":
        client = self.client

        response = client.delete(f"/api/v1/fields/{self.id}")
        response.raise_for_status()

        return self._construct_field_from_server(response.json())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "required": self.required,
            "settings": self.settings.to_dict(),
            "inserted_at": self.inserted_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def _construct_field_from_server(cls, data: Dict[str, Any]):
        client = sdk.default_http_client
        data["settings"] = TextFieldSettings(**data["settings"])

        return cls(**data, client=client)
