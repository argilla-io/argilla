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
from typing import Optional

from fastapi import Request
from huggingface_hub.utils import send_telemetry

from argilla_server._version import __version__
from argilla_server.constants import DEFAULT_USERNAME
from argilla_server.models import User, Workspace
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

    def track_data(
        self, topic: str, user_agent: dict, include_system_info: bool = True, count: int = 1, type: str = None
    ):
        library_name = "argilla"
        topic = f"{library_name}/{topic}"

        if include_system_info:
            user_agent.update(self._system_info)
        user_agent["count"] = count

        send_telemetry(topic=topic, library_name=library_name, library_version=__version__, user_agent=user_agent)

    @staticmethod
    def _process_request_info(request: Request):
        return {header: request.headers.get(header) for header in ["user-agent", "accept-language"]}

    @staticmethod
    def _process_workspace_model(workspace: Workspace):
        return {
            "workspace_id": str(workspace.id),
            "workspace": str(uuid.uuid5(namespace=_TELEMETRY_CLIENT.server_id, name=workspace.name)),
        }

    @staticmethod
    def _process_user_model(user: User):
        return {
            "user_id": str(user.id),
            "role": user.role,
            "is_default_user": user.username == DEFAULT_USERNAME,
            "user_hash": str(uuid.uuid5(namespace=_TELEMETRY_CLIENT.server_id, name=user.username)),
        }

    async def track_user_login(self, request: Request, user: User):
        topic = "user/login"
        user_agent = self._process_user_model(user=user)
        user_agent.update(**self._process_request_info(request))
        self.track_data(topic=topic, user_agent=user_agent)

    async def track_crud_user(self, action: str, user: User, is_oauth: bool = None):
        topic = f"user/{action}"
        user_agent = self._process_user_model(user=user)
        if is_oauth is not None:
            user_agent["is_oauth"] = is_oauth
        self.track_data(topic=topic, user_agent=user_agent)

    async def track_crud_workspace(self, action: str, workspace: Workspace):
        topic: str = f"workspace/{action}"
        user_agent = self._process_workspace_model(workspace)
        self.track_data(topic=topic, user_agent=user_agent)


def get_telemetry_client() -> TelemetryClient:
    return _TELEMETRY_CLIENT


_TELEMETRY_CLIENT = TelemetryClient()
