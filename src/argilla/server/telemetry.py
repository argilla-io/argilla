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
from typing import Any, Dict, Optional

from fastapi import Request

from argilla.server.commons.models import TaskType
from argilla.server.models import User
from argilla.server.settings import settings
from argilla.server.utils._telemetry import is_quickstart_server, is_running_on_docker_container

try:
    from analytics import Client  # This import works only for version 2.2.0
except (ImportError, ModuleNotFoundError):
    # TODO: show some warning info
    settings.enable_telemetry = False
    Client = None


_LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class TelemetryClient:
    enable_telemetry: dataclasses.InitVar[bool] = settings.enable_telemetry
    disable_send: dataclasses.InitVar[bool] = False
    api_key: dataclasses.InitVar[str] = settings.telemetry_key
    host: dataclasses.InitVar[str] = "https://api.segment.io"

    _server_id: Optional[uuid.UUID] = dataclasses.field(init=False, default=None)

    @property
    def server_id(self) -> uuid.UUID:
        return self._server_id

    def __post_init__(self, enable_telemetry: bool, disable_send: bool, api_key: str, host: str):
        from argilla import __version__

        self.client = None
        if enable_telemetry:
            try:
                self.client = Client(write_key=api_key, gzip=True, host=host, send=not disable_send, max_retries=10)
            except Exception as err:
                _LOGGER.warning(f"Cannot initialize telemetry. Error: {err}. Disabling...")

        self._server_id = uuid.UUID(int=uuid.getnode())
        self._system_info = {
            "system": platform.system(),
            "machine": platform.machine(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "sys_version": platform.version(),
            "deployment": "quickstart" if is_quickstart_server() else "server",
            "docker": is_running_on_docker_container(),
            "version": __version__,
        }

        _LOGGER.info("System Info:")
        _LOGGER.info(json.dumps(self._system_info, indent=2))

    def track_data(self, action: str, data: Dict[str, Any], include_system_info: bool = True):
        if not self.client:
            return

        event_data = data.copy()
        self.client.track(
            user_id=str(self._server_id),
            event=action,
            properties=event_data,
            context=self._system_info if include_system_info else {},
        )


_CLIENT = TelemetryClient()


def _process_request_info(request: Request):
    return {header: request.headers.get(header) for header in ["user-agent", "accept-language"]}


async def track_bulk(task: TaskType, records: int):
    _CLIENT.track_data(action="LogRecordsRequested", data={"task": task, "records": records})


async def track_login(request: Request, user: User):
    _CLIENT.track_data(
        action="UserInfoRequested",
        data={
            "is_default_user": user.username == "argilla",
            "user_id": str(user.id),
            "user_hash": str(uuid.uuid5(namespace=_CLIENT.server_id, name=user.username)),
            **_process_request_info(request),
        },
    )


def track_user_created(user: User, is_oauth: bool = False):
    _CLIENT.track_data(
        action="UserCreated",
        data={
            "user_id": str(user.id),
            "role": user.role,
            "is_default_user": user.username == "argilla",
            "is_oauth": is_oauth,
        },
    )


def get_telemetry_client() -> TelemetryClient:
    return _CLIENT
