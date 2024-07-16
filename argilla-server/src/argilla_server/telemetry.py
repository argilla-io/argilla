#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import dataclasses
import json
import logging
import platform
import uuid
from typing import Optional, Union

from fastapi import Request
from huggingface_hub.utils import send_telemetry

from argilla_server._version import __version__
from argilla_server.constants import DEFAULT_USERNAME
from argilla_server.models import (
    Dataset,
    Field,
    MetadataPropertySettings,
    Question,
    Record,
    User,
    VectorSettings,
    Workspace,
)
from argilla_server.settings import settings
from argilla_server.utils._telemetry import (
    is_running_on_docker_container,
    server_deployment_type,
)

_LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class TelemetryClient:
    enable_telemetry: dataclasses.InitVar[bool] = settings.enable_telemetry
    disable_send: dataclasses.InitVar[bool] = False

    _server_id: Optional[uuid.UUID] = dataclasses.field(init=False, default=None)

    @property
    def server_id(self) -> uuid.UUID:
        return self._server_id

    def __post_init__(self):
        self._server_id = uuid.UUID(int=uuid.getnode())
        self._system_info = {
            "server_id": self._server_id,
            "system": platform.system(),
            "machine": platform.machine(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "sys_version": platform.version(),
            "deployment": server_deployment_type(),
            "docker": is_running_on_docker_container(),
        }

        _LOGGER.info("System Info:")
        _LOGGER.info(f"Server id: {self.server_id}")
        _LOGGER.info(f"Context: {json.dumps(self._system_info, indent=2)}")

    @staticmethod
    def _process_request_info(request: Request):
        return {header: request.headers.get(header) for header in ["user-agent", "accept-language"]}

    @staticmethod
    def _process_workspace_model(workspace: Workspace):
        return {
            "workspace_id": str(workspace.id),
            "workspace_hash": str(uuid.uuid5(namespace=_TELEMETRY_CLIENT.server_id, name=workspace.name)),
        }

    @staticmethod
    def _process_dataset_model(dataset: Dataset):
        return {
            "dataset_id": str(dataset.id),
            "dataset_hash": str(uuid.uuid5(namespace=_TELEMETRY_CLIENT.server_id, name=dataset.name)),
        }

    @staticmethod
    def _process_record_model(record: Record):
        return {
            "dataset_id": str(record.dataset_id),
            "record_id": str(record.id),
        }

    @staticmethod
    def _process_dataset_settings(dataset: Dataset):
        return {
            "count_fields": len(dataset.fields),
            "count_questions": len(dataset.questions),
            "count_vector_settings": len(dataset.vectors_settings),
            "count_metadata_properties": len(dataset.metadata_properties),
            "allow_extra_metadata": dataset.allow_extra_metadata,
            "guidelines": True if dataset.guidelines else False,
        }

    @staticmethod
    def _process_dataset_setting_settings(setting: Union[Field, VectorSettings, Question, MetadataPropertySettings]):
        user_data = {"dataset_id": str(setting.dataset_id)}
        if isinstance(setting, (Field, Question)):
            user_data["required"] = setting.required
            user_data.update(setting.settings)
        elif isinstance(setting, MetadataPropertySettings):
            user_data["type"] = setting.type
        elif isinstance(setting, VectorSettings):
            user_data["dimensions"] = setting.dimensions

        return user_data

    @staticmethod
    def _process_user_model(user: User):
        return {
            "user_id": str(user.id),
            "role": user.role,
            "is_default_user": user.username == DEFAULT_USERNAME,
            "user_hash": str(uuid.uuid5(namespace=_TELEMETRY_CLIENT.server_id, name=user.username)),
        }

    def track_data(self, topic: str, user_agent: dict, include_system_info: bool = True, count: int = 1):
        if not self.enable_telemetry:
            return

        library_name = "argilla"
        topic = f"{library_name}/{topic}"

        if include_system_info:
            user_agent.update(self._system_info)
        if count is not None:
            user_agent["count"] = count

        send_telemetry(topic=topic, library_name=library_name, library_version=__version__, user_agent=user_agent)

    async def track_user_login(self, request: Request, user: User):
        topic = "user/login"
        user_agent = self._process_user_model(user=user)
        user_agent.update(**self._process_request_info(request))
        self.track_data(topic=topic, user_agent=user_agent)

    async def track_crud_user(
        self,
        action: str,
        user: Union[User, None] = None,
        is_oauth: Union[bool, None] = None,
        count: Union[int, None] = None,
    ):
        topic = f"user/{action}"
        if user:
            user_agent = self._process_user_model(user=user)
        if is_oauth is not None:
            user_agent["is_oauth"] = is_oauth
        self.track_data(topic=topic, user_agent=user_agent, count=count)

    async def track_crud_workspace(
        self, action: str, workspace: Union[Workspace, None] = None, count: Union[int, None] = None
    ):
        topic: str = f"workspace/{action}"
        if workspace:
            user_agent = self._process_workspace_model(workspace=workspace)
        self.track_data(topic=topic, user_agent=user_agent, count=count)

    async def track_crud_dataset(
        self, action: str, dataset: Union[Dataset, None] = None, count: Union[int, None] = None
    ):
        topic = f"dataset/{action}"
        if dataset:
            user_agent = self._process_dataset_model(dataset=dataset)
            user_agent.update(self._process_dataset_settings(dataset=dataset))
        self.track_data(topic=topic, user_agent=user_agent, count=count)

        for field in dataset.fields:
            self.track_crud_dataset_setting(action=action, setting_name="fields", dataset=dataset, setting=field)
        for question in dataset.questions:
            self.track_crud_dataset_setting(action=action, setting_name="questions", dataset=dataset, setting=question)
        for vector in dataset.vectors_settings:
            self.track_crud_dataset_setting(
                action=action, setting_name="vectors_settings", dataset=dataset, setting=vector
            )
        for meta_data in dataset.metadata_properties:
            self.track_crud_dataset_setting(
                action=action, setting_name="metadata_properties", dataset=dataset, setting=meta_data
            )

    async def track_crud_dataset_setting(
        self,
        action: str,
        setting_name: str,
        dataset: Dataset,
        setting: Union[Field, VectorSettings, Question, MetadataPropertySettings],
        count: Union[int, None] = None,
    ):
        topic = f"dataset/{setting_name}/{setting.settings.type}/{action}"
        user_agent = self._process_dataset_model(dataset=dataset)
        user_agent.update(self._process_dataset_setting_settings(setting=setting))
        self.track_data(topic=topic, user_agent=user_agent, count=count)

    async def track_crud_records(self, action: str, record: Union[Record, None] = None, count: Union[int, None] = None):
        topic = f"dataset/records/{action}"
        user_agent = self._process_record_model(record=record)
        self.track_data(topic=topic, user_agent=user_agent, count=count)

    async def track_crud_records_subtopic(
        self,
        action: str,
        sub_topic: str,
        record_id: str,
        count: Union[int, None] = None,
    ):
        topic = f"dataset/records/{sub_topic}/{action}"
        user_agent = {"record_id": record_id}
        self.track_data(topic=topic, user_agent=user_agent, count=count)


def get_telemetry_client() -> TelemetryClient:
    return _TELEMETRY_CLIENT


_TELEMETRY_CLIENT = TelemetryClient()
