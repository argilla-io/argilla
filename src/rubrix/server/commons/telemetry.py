import dataclasses
import uuid
from typing import Any, Dict, Optional

from rubrix.server.errors import RubrixServerError
from rubrix.server.services.tasks.commons import TaskType
from rubrix.server.settings import settings


@dataclasses.dataclass
class _TelemetryClient:

    __API_KEY__ = "C6FkcaoCbt78rACAgvyBxGBcMB3dM3nn"

    __server_id__: Optional[uuid.UUID] = dataclasses.field(init=False, default=None)

    __INSTANCE__: "_TelemetryClient" = None

    @classmethod
    def get(cls):
        if settings.enable_telemetry:
            if cls.__INSTANCE__ is None:
                cls.__INSTANCE__ = cls()
            return cls.__INSTANCE__

    def __post_init__(self):
        import platform
        import sys

        import analytics

        from rubrix import __version__

        analytics.write_key = self.__API_KEY__
        self.__server_id__ = uuid.UUID(int=uuid.getnode())
        self.__system_info__ = {
            "system": platform.system(),
            "machine": platform.machine(),
            "platform": platform.platform(),
            "python_version": sys.version,
            "sys_version": platform.version(),
            "rubrix_version": __version__,
        }

    def track_data(self, action: str, data: Dict[str, Any]):
        import analytics

        analytics.track(self.__server_id__, action, {**data, **self.__system_info__})


async def track_error(error: RubrixServerError):
    client = _TelemetryClient.get()
    if client:
        client.track_data("ServerError", {"code": error.code})


async def track_bulk(task: TaskType, records: int):
    client = _TelemetryClient.get()
    if client:
        client.track_data("BulkData", {"task": task, records: records})


async def track_login():
    client = _TelemetryClient.get()
    if client:
        client.track_data("UserLogged", {})
