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

from datetime import datetime
from typing import TYPE_CHECKING, Union
from uuid import UUID

from pydantic import BaseModel

from argilla import Dataset, Record, UserResponse, Workspace
from argilla._exceptions import ArgillaAPIError
from argilla._models import RecordModel, UserResponseModel, WorkspaceModel, EventType

if TYPE_CHECKING:
    from argilla import Argilla

__all__ = ["RecordEvent", "DatasetEvent", "UserResponseEvent", "WebhookEvent"]


class RecordEvent(BaseModel):
    """
    A parsed record event.

    Attributes:
        type (EventType): The type of the event.
        timestamp (datetime): The timestamp of the event.
        record (Record): The record of the event.
    """

    type: EventType
    timestamp: datetime
    record: Record


class DatasetEvent(BaseModel):
    """
    A parsed dataset event.

    Attributes:
        type (EventType): The type of the event.
        timestamp (datetime): The timestamp of the event.
        dataset (Dataset): The dataset of the event.
    """

    type: EventType
    timestamp: datetime
    dataset: Dataset


class UserResponseEvent(BaseModel):
    """
    A parsed user response event.

    Attributes:
        type (EventType): The type of the event.
        timestamp (datetime): The timestamp of the event.
        response (UserResponse): The user response of the event.
    """

    type: EventType
    timestamp: datetime
    response: UserResponse


class WebhookEvent(BaseModel):
    """
    A webhook event.

    Attributes:
        type (EventType): The type of the event.
        timestamp (datetime): The timestamp of the event.
        data (dict): The data of the event.
    """

    type: EventType
    timestamp: datetime
    data: dict

    def parsed(self, client: "Argilla") -> Union[RecordEvent, DatasetEvent, UserResponseEvent, "WebhookEvent"]:
        """
        Parse the webhook event.

        Args:
            client: The Argilla client.

        Returns:
            Event: The parsed event.

        """
        resource = self.type.resource
        data = self.data or {}

        if resource == "dataset":
            dataset = self._parse_dataset_from_webhook_data(data, client)
            return DatasetEvent(
                type=self.type,
                timestamp=self.timestamp,
                dataset=dataset,
            )

        elif resource == "record":
            record = self._parse_record_from_webhook_data(data, client)
            return RecordEvent(
                type=self.type,
                timestamp=self.timestamp,
                record=record,
            )

        elif resource == "response":
            user_response = self._parse_response_from_webhook_data(data, client)
            return UserResponseEvent(
                type=self.type,
                timestamp=self.timestamp,
                response=user_response,
            )

        return self

    @classmethod
    def _parse_dataset_from_webhook_data(cls, data: dict, client: "Argilla") -> Dataset:
        workspace = Workspace.from_model(WorkspaceModel.model_validate(data["workspace"]), client=client)
        # TODO: Parse settings from the data
        # settings = Settings._from_dict(data)

        dataset = Dataset(name=data["name"], workspace=workspace, client=client)
        dataset.id = UUID(data["id"])

        try:
            dataset.get()
        except ArgillaAPIError as _:
            # TODO: Show notification
            pass
        finally:
            return dataset

    @classmethod
    def _parse_record_from_webhook_data(cls, data: dict, client: "Argilla") -> Record:
        dataset = cls._parse_dataset_from_webhook_data(data["dataset"], client)

        record = Record.from_model(RecordModel.model_validate(data), dataset=dataset)
        try:
            record.get()
        except ArgillaAPIError as _:
            # TODO: Show notification
            pass
        finally:
            return record

    @classmethod
    def _parse_response_from_webhook_data(cls, data: dict, client: "Argilla") -> UserResponse:
        record = cls._parse_record_from_webhook_data(data["record"], client)

        # TODO: Link the user resource to the response
        user_response = UserResponse.from_model(
            model=UserResponseModel(**data, user_id=data["user"]["id"]),
            record=record,
        )

        return user_response


Event = Union[RecordEvent, DatasetEvent, UserResponseEvent, WebhookEvent]
