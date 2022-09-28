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
import logging
import platform
import uuid
from typing import Any, Dict, Optional

import httpx
from fastapi import Request

from argilla.server.commons.models import TaskType
from argilla.server.errors.base_errors import ServerError
from argilla.server.settings import settings

try:
    from analytics import Client
except ModuleNotFoundError:
    # TODO: show some warning info
    settings.enable_telemetry = False
    Client = None


def _configure_analytics(disable_send: bool = False) -> Client:
    API_KEY = settings.telemetry_key or "C6FkcaoCbt78rACAgvyBxGBcMB3dM3nn"
    TELEMETRY_HOST = "https://api.segment.io"

    # Check host connection
    httpx.options(TELEMETRY_HOST, timeout=1, verify=False)

    return Client(
        write_key=API_KEY,
        gzip=True,
        host=TELEMETRY_HOST,
        send=not disable_send,
        max_retries=5,
    )


@dataclasses.dataclass
class _TelemetryClient:

    client: Client

    __INSTANCE__: "_TelemetryClient" = None
    __server_id__: Optional[uuid.UUID] = dataclasses.field(init=False, default=None)

    @property
    def server_id(self) -> uuid.UUID:
        return self.__server_id__

    @classmethod
    def get(cls):
        if settings.enable_telemetry:
            if cls.__INSTANCE__ is None:
                try:
                    cls.__INSTANCE__ = cls(client=_configure_analytics())
                except Exception as err:
                    logging.getLogger(__name__).warning(
                        f"Cannot initialize telemetry. Error: {err}. Disabling..."
                    )
                    settings.enable_telemetry = False
                    return None
            return cls.__INSTANCE__

    def __post_init__(self):

        from argilla import __version__

        self.__server_id__ = uuid.UUID(int=uuid.getnode())
        self.__server_id_str__ = str(self.__server_id__)
        self.__system_info__ = {
            "system": platform.system(),
            "machine": platform.machine(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "sys_version": platform.version(),
            "version": __version__,
        }

    def track_data(
        self, action: str, data: Dict[str, Any], include_system_info: bool = True
    ):
        event_data = data.copy()
        self.client.track(
            user_id=self.__server_id_str__,
            event=action,
            properties=event_data,
            context=self.__system_info__ if include_system_info else {},
        )


def _process_request_info(request: Request):
    return {
        header: request.headers.get(header)
        for header in ["user-agent", "accept-language"]
    }


async def track_error(error: ServerError, request: Request):
    client = _TelemetryClient.get()
    if client:
        client.track_data(
            "ServerErrorFound", {"code": error.code, **_process_request_info(request)}
        )


async def track_bulk(task: TaskType, records: int):
    client = _TelemetryClient.get()
    if client:
        client.track_data("LogRecordsRequested", {"task": task, "records": records})


async def track_login(request: Request, username: str):
    client = _TelemetryClient.get()
    if client:
        client.track_data(
            "UserInfoRequested",
            {
                "is_default_user": username == "argilla",
                "user_hash": str(uuid.uuid5(namespace=client.server_id, name=username)),
                **_process_request_info(request),
            },
        )
