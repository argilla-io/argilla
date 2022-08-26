import dataclasses
import platform
import sys
import uuid
from typing import Any, Dict

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
            "python_version": "{major}.{minor}.{patch}".format(
                major=sys.version_info.major,
                minor=sys.version_info.minor,
                patch=sys.version_info.micro,
            ),
            "sys_version": platform.version(),
            "rubrix_version": __version__,
        }

    def track_data(self, action: str, data: Dict[str, Any]):
        self._client.track(self.__server_id__, action, {**data, **self.__system_info__})


async def track_error(error: RubrixServerError):
    client = _TelemetryClient.get()
    if client:
        client.track_data("ServerErrorFound", {"code": error.code})


async def track_bulk(task: TaskType, records: int):
    client = _TelemetryClient.get()
    if client:
        client.track_data("LogRecordsRequested", {"task": task, "records": records})


async def track_login():
    client = _TelemetryClient.get()
    if client:
        client.track_data("UserInfoRequested", {})
