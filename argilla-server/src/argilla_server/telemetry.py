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
    FloatMetadataPropertySettings,
    IntegerMetadataPropertySettings,
    MetadataProperty,
    MetadataPropertySettings,
    Question,
    Record,
    TermsMetadataPropertySettings,
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

    _server_id: Optional[uuid.UUID] = dataclasses.field(init=False, default=None)

    @property
    def server_id(self) -> uuid.UUID:
        return self._server_id

    def __post_init__(self, enable_telemetry: bool):
        self._server_id = uuid.UUID(int=uuid.getnode())
        self._system_info = {
            "server_id": str(self._server_id),
            "system": platform.system(),
            "machine": platform.machine(),
            "platform": platform.platform(),
            "sys_version": platform.version(),
            "deployment": server_deployment_type(),
            "docker": is_running_on_docker_container(),
        }

        _LOGGER.info("System Info:")
        _LOGGER.info(f"Server id: {self.server_id}")
        _LOGGER.info(f"Context: {json.dumps(self._system_info, indent=2)}")
        self.enable_telemetry = enable_telemetry

    @staticmethod
    def _process_request_info(request: Request):
        return {header: request.headers.get(header) for header in ["user-agent", "accept-language"]}

    @staticmethod
    def _process_user_model(user: User):
        return {"user_id": str(user.id), "role": user.role, "is_default_user": user.username == DEFAULT_USERNAME}

    @staticmethod
    def _process_workspace_model(workspace: Workspace):
        return {"workspace_id": str(workspace.id)}

    @staticmethod
    def _process_dataset_model(dataset: Dataset):
        return {
            "dataset_id": str(dataset.id),
            "workspace_id": str(dataset.workspace_id),
        }

    @staticmethod
    def _process_record_model(record: Record):
        return {
            "dataset_id": str(record.dataset_id),
            "record_id": str(record.id),
        }

    @staticmethod
    def _process_dataset_settings(dataset: Dataset):
        user_data = {}
        if dataset.is_relationship_loaded("guidelines"):
            user_data["guidelines"] = True if getattr(dataset, "guidelines") else False
        if dataset.is_relationship_loaded("guidelines"):
            user_data["allow_extra_metadata"] = getattr(dataset, "allow_extra_metadata")
        if dataset.is_relationship_loaded("distribution"):
            distribution = getattr(dataset, "distribution")
            user_data["distribution_strategy"] = distribution["strategy"]
            if "min_submitted" in distribution:
                user_data["distribution_min_submitted"] = distribution["min_submitted"]

        attributes = [
            "fields",
            "questions",
            "vectors_settings",
            "metadata_properties",
        ]
        for attr in attributes:
            if dataset.is_relationship_loaded(attr):
                user_data[f"count_{attr}"] = len(getattr(dataset, attr))

        return user_data

    @staticmethod
    def _process_dataset_setting_settings(
        setting: Union[
            Field,
            VectorSettings,
            Question,
            FloatMetadataPropertySettings,
            TermsMetadataPropertySettings,
            IntegerMetadataPropertySettings,
        ],
    ):
        user_data = {"dataset_id": str(setting.dataset_id)}
        if isinstance(setting, (Field, Question)):
            user_data["required"] = setting.required
            user_data["type"] = setting.settings["type"]
        elif isinstance(
            setting,
            (
                FloatMetadataPropertySettings,
                TermsMetadataPropertySettings,
                IntegerMetadataPropertySettings,
                MetadataProperty,
            ),
        ):
            user_data["type"] = setting.type.value
        elif isinstance(setting, VectorSettings):
            user_data["dimensions"] = setting.dimensions
            user_data["type"] = "default"
        else:
            raise NotImplementedError("Expected a setting to be processed.")

        return user_data

    async def track_data(self, topic: str, user_agent: dict, include_system_info: bool = True, count: int = 1):
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
        await self.track_data(topic=topic, user_agent=user_agent)

    async def track_crud_user(
        self,
        action: str,
        user: Union[User, None] = None,
        is_oauth: Union[bool, None] = None,
        is_login: Union[bool, None] = None,
        count: Union[int, None] = None,
    ):
        topic = f"user/{action}"
        user_agent = {}
        if user:
            user_agent.update(self._process_user_model(user=user))
        if is_oauth is not None:
            user_agent["is_oauth"] = is_oauth
        if is_login is not None:
            user_agent["is_login"] = is_login
        await self.track_data(topic=topic, user_agent=user_agent, count=count)

    async def track_crud_workspace(
        self, action: str, workspace: Union[Workspace, None] = None, count: Union[int, None] = None
    ):
        topic: str = f"workspace/{action}"
        user_agent = {}
        if workspace:
            user_agent.update(self._process_workspace_model(workspace=workspace))
        await self.track_data(topic=topic, user_agent=user_agent, count=count)

    async def track_crud_dataset(
        self, action: str, dataset: Union[Dataset, None] = None, count: Union[int, None] = None
    ):
        topic = f"dataset/{action}"
        user_agent = {}
        if dataset:
            user_agent.update(self._process_dataset_model(dataset=dataset))
            user_agent.update(self._process_dataset_settings(dataset=dataset))
        await self.track_data(topic=topic, user_agent=user_agent, count=count)

        attributes: list[str] = ["fields", "questions", "vectors_settings", "metadata_properties"]
        if dataset:
            for attr in attributes:
                if dataset.is_relationship_loaded(attr):
                    obtained_attr_list = getattr(dataset, attr)
                    await self.track_crud_dataset_setting(
                        action=action, setting_name=attr, dataset=dataset, setting=None, count=len(obtained_attr_list)
                    )
                    for obtained_attr in obtained_attr_list:
                        await self.track_crud_dataset_setting(
                            action=action, setting_name=attr, dataset=dataset, setting=obtained_attr
                        )

    async def track_crud_dataset_setting(
        self,
        action: str,
        setting_name: str,
        dataset: Dataset,
        setting: Union[Field, VectorSettings, Question, MetadataPropertySettings, None] = None,
        count: Union[int, None] = None,
    ):
        topic = f"dataset/{setting_name}/{action}"
        user_agent = self._process_dataset_model(dataset=dataset)
        if setting:
            user_agent.update(self._process_dataset_setting_settings(setting=setting))
        await self.track_data(topic=topic, user_agent=user_agent, count=count)

    async def track_crud_records(
        self, action: str, record_or_dataset: Union[Record, Dataset, None] = None, count: Union[int, None] = None
    ):
        topic = f"dataset/records/{action}"
        if isinstance(record_or_dataset, Record):
            user_agent = self._process_record_model(record=record_or_dataset)
        elif isinstance(record_or_dataset, Dataset):
            user_agent = self._process_dataset_model(dataset=record_or_dataset)
        else:
            raise NotImplementedError("Expected element of `Dataset` or `Record`")
        await self.track_data(topic=topic, user_agent=user_agent, count=count)

    async def track_crud_records_subtopic(
        self,
        action: str,
        sub_topic: str,
        record_id: str,
        count: Union[int, None] = None,
    ):
        topic = f"dataset/records/{sub_topic}/{action}"
        user_agent = {"record_id": record_id}
        await self.track_data(topic=topic, user_agent=user_agent, count=count)


_TELEMETRY_CLIENT = TelemetryClient()


def get_telemetry_client() -> TelemetryClient:
    return _TELEMETRY_CLIENT
