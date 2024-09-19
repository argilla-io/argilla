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
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel

from argilla import Dataset, Record, UserResponse, Workspace
from argilla._exceptions import ArgillaAPIError
from argilla._models import RecordModel, UserResponseModel, WorkspaceModel

if TYPE_CHECKING:
    from argilla import Argilla


def _parse_dataset_from_webhook_data(data: dict, client: "Argilla") -> Dataset:
    workspace = Workspace.from_model(WorkspaceModel.model_validate(data["workspace"]), client=client)
    # TODO: Parse settings from the data
    # settings = Settings._from_dict(data)

    dataset = Dataset(name=data["name"], workspace=workspace, client=client)
    dataset.id = UUID(data["id"])

    return dataset.get()


def _parse_record_from_webhook_data(data: dict, client: "Argilla") -> Record:
    dataset = _parse_dataset_from_webhook_data(data["dataset"], client)

    record = Record.from_model(RecordModel.model_validate(data), dataset=dataset)
    try:
        record.get()
    except ArgillaAPIError as _:
        # TODO: Show notification
        pass
    finally:
        return record


def _parse_response_from_webhook_data(data: dict, client: "Argilla") -> UserResponse:
    record = _parse_record_from_webhook_data(data["record"], client)

    # TODO: Link the user resource to the response
    user_response = UserResponse.from_model(
        model=UserResponseModel(**data, user_id=data["user"]["id"]),
        record=record,
    )

    return user_response


class WebhookEvent(BaseModel):
    type: str
    timestamp: datetime
    data: dict

    def normalize(self, client: "Argilla") -> dict:
        instance_type, action_type = self.type.split(".")
        data = self.data or {}

        arguments = {"type": self.type, "timestamp": self.timestamp}

        if action_type == "deleted":
            return {**arguments, "data": data}

        if instance_type == "dataset":
            dataset = _parse_dataset_from_webhook_data(data, client)
            arguments["dataset"] = dataset

        elif instance_type == "record":
            record = _parse_record_from_webhook_data(data, client)
            arguments["record"] = record

        elif instance_type == "response":
            user_response = _parse_response_from_webhook_data(data, client)
            arguments["response"] = user_response

        else:
            arguments["data"] = data

        return arguments
