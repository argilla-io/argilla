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

from pydantic import BaseModel

from argilla import Argilla, Dataset, Record, UserResponse
from argilla._models import DatasetModel, RecordModel, UserResponseModel


class WebhookEvent(BaseModel):
    type: str
    timestamp: datetime
    data: dict

    def normalize(self, client: Argilla) -> dict:
        instance_type = self.type.split(".")[0]
        data = self.data or {}

        arguments = {
            "type": self.type,
            "timestamp": self.timestamp,
        }

        if instance_type == "dataset":
            dataset = Dataset.from_model(DatasetModel.model_validate(data), client=client).get()
            arguments.update({"dataset": dataset})

        elif instance_type == "record":
            dataset = Dataset.from_model(DatasetModel.model_validate(data["dataset"]), client=client).get()
            record = Record.from_model(RecordModel.model_validate(data), dataset=dataset).get()

            arguments.update({"record": record, "dataset": dataset})

        elif instance_type == "response":
            dataset = Dataset.from_model(DatasetModel.model_validate(data["record"]["dataset"]), client=client)
            record = Record.from_dict(data["record"], dataset=dataset)
            user_response = UserResponse.from_model(
                UserResponseModel(**data, user_id=data["user"]["id"]), dataset=dataset
            )
            arguments.update({"response": user_response, "record": record, "dataset": dataset})

        else:
            arguments.update({"data": data})

        return arguments
