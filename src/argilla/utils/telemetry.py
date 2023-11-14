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
from typing import TYPE_CHECKING, Any, Dict, Optional

from argilla.server.commons.models import TaskType
from argilla.server.settings import settings

if TYPE_CHECKING:
    from fastapi import Request

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
            "version": __version__,
        }

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


def _process_request_info(request: "Request"):
    return {header: request.headers.get(header) for header in ["user-agent", "accept-language"]}


async def track_bulk(task: TaskType, records: int):
    _CLIENT.track_data(action="LogRecordsRequested", data={"task": task, "records": records})


async def track_login(request: "Request", username: str):
    _CLIENT.track_data(
        action="UserInfoRequested",
        data={
            "is_default_user": username == "argilla",
            "user_hash": str(uuid.uuid5(namespace=_CLIENT.server_id, name=username)),
            **_process_request_info(request),
        },
    )


def get_current_filename() -> Optional[str]:
    """Returns the filename of the current file.

    It will try to get the filename from the following sources:
    - __file__ variable (only works when running from python)
    - __vsc_ipynb_file__ variable (only works when running from vscode)
    - ipynbname.name() (only works when running from a notebook/gooble colab)
    - None if it can't be determined
    """
    from pathlib import Path

    try:
        try:
            # Should work if we are running from python
            return Path(__file__).stem
        except NameError as e:
            # This should work if we are running a notebook from vscode
            globals_ = globals()
            return Path(globals_["__vsc_ipynb_file__"]).stem
    except KeyError as e:
        # This should work for notebooks running locally or using google colab
        import urllib.parse

        import ipynbname

        return Path(urllib.parse.unquote_plus(ipynbname.name())).stem


def tutorial_running() -> None:
    """Can be called when a tutorial is executed so that the tutorial_id is used to identify the tutorial and send an event."""
    if tutorial_id := get_current_filename():
        _CLIENT.track_data(action="TutorialRunning", data={"tutorial_id": tutorial_id})


def get_telemetry_client() -> TelemetryClient:
    return _CLIENT
