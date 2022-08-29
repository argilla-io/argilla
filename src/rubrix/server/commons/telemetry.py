import dataclasses
import platform
import uuid
from typing import Any, Dict

from fastapi import Request

from rubrix.server.commons.models import TaskType
from rubrix.server.errors.base_errors import RubrixServerError
from rubrix.server.settings import settings

try:
    from analytics import Client
except ModuleNotFoundError:
    # TODO: show some warning info
    settings.enable_telemetry = False
    Client = None


def _configure_analytics(disable_send: bool = False) -> Client:
    API_KEY = settings.telemetry_key or "C6FkcaoCbt78rACAgvyBxGBcMB3dM3nn"

    return Client(write_key=API_KEY, gzip=True, send=not disable_send)


@dataclasses.dataclass
class _TelemetryClient:

    __INSTANCE__: "_TelemetryClient" = None

    __server_id__: str = dataclasses.field(init=False, default=None)
    _client: Client = dataclasses.field(
        init=False, default_factory=_configure_analytics
    )

    @classmethod
    def get(cls):
        if settings.enable_telemetry:
            if cls.__INSTANCE__ is None:
                cls.__INSTANCE__ = cls()
            return cls.__INSTANCE__

    def __post_init__(self):

        from rubrix import __version__

        self.__server_id__ = str(uuid.UUID(int=uuid.getnode()))
        self.__system_info__ = {
            "system": platform.system(),
            "machine": platform.machine(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "sys_version": platform.version(),
            "rubrix_version": __version__,
        }

    def track_data(
        self, action: str, data: Dict[str, Any], include_system_info: bool = True
    ):
        event_data = data.copy()
        if include_system_info:
            event_data.update(self.__system_info__)
        self._client.track(self.__server_id__, action, event_data)


def _process_request_info(request: Request):
    return {
        header: request.headers.get(header)
        for header in ["user-agent", "accept-language"]
    }


async def track_error(error: RubrixServerError, request: Request):
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
            {"is_default_user": username == "rubrix", **_process_request_info(request)},
        )
