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

from fastapi import Request, Response
from huggingface_hub.utils import send_telemetry

from argilla_server._version import __version__
from argilla_server.api.errors.v1.exception_handlers import get_request_error
from argilla_server.integrations.huggingface.spaces import HUGGINGFACE_SETTINGS
from argilla_server.security.authentication.provider import get_request_user
from argilla_server.utils._fastapi import resolve_endpoint_path_for_request
from argilla_server.telemetry._helpers import (
    is_running_on_docker_container,
    server_deployment_type,
    get_server_id,
)

_LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class TelemetryClient:
    _server_id: uuid.UUID = dataclasses.field(init=False)

    def __post_init__(self):
        self._server_id = get_server_id()
        self._system_info = {
            "server_id": self._server_id.urn,
            "system": platform.system(),
            "machine": platform.machine(),
            "platform": platform.platform(),
            "sys_version": platform.version(),
            "deployment": server_deployment_type(),
            "docker": is_running_on_docker_container(),
            "persistent_storage_enabled": HUGGINGFACE_SETTINGS.space_persistent_storage_enabled,
        }

        _LOGGER.info("System Info:")
        _LOGGER.info(f"Context: {json.dumps(self._system_info, indent=2)}")

    def track_data(self, topic: str, data: Optional[dict] = None):
        library_name = "argilla-server"
        topic = f"argilla/server/{topic}"

        user_agent = {**(data or {}), **self._system_info}
        send_telemetry(topic=topic, library_name=library_name, library_version=__version__, user_agent=user_agent)

    async def track_api_request(self, request: Request, response: Response) -> None:
        """
        Track the endpoint usage. This method is called after the endpoint is processed.
        The method will track the endpoint usage, the user-agent, and the response status code. If an error is raised
        during the endpoint processing, the error will be tracked as well.

        Parameters:
            request (Request): The incoming request
            response (Response): The outgoing response

        """

        endpoint_path = resolve_endpoint_path_for_request(request)
        if endpoint_path is None:
            return

        data = {
            "endpoint": f"{request.method} {endpoint_path}",
            "request.user-agent": request.headers.get("user-agent"),
            "request.method": request.method,
            "request.accept-language": request.headers.get("accept-language"),
            "response.status": str(response.status_code),
        }

        if server_timing := response.headers.get("Server-Timing"):
            duration_in_ms = server_timing.removeprefix("total;dur=")
            data["duration_in_milliseconds"] = duration_in_ms

        if user := get_request_user(request=request):
            data["user.id"] = user.id.urn
            data["user.role"] = user.role

        if response.status_code >= 400:
            if argilla_error := get_request_error(request=request):
                data["response.error_code"] = argilla_error.code  # noqa

        self.track_data(topic="endpoints", data=data)

    def track_server_startup(self) -> None:
        """
        This method is used to track the launch of the server.

        Returns:
            None
        """
        self.track_data(topic="startup")


_TELEMETRY_CLIENT = TelemetryClient()


def get_telemetry_client() -> TelemetryClient:
    return _TELEMETRY_CLIENT
