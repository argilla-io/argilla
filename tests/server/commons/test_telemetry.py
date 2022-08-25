import pytest

from rubrix.server.commons import telemetry
from rubrix.server.commons.models import TaskType
from rubrix.server.errors import RubrixServerError


@pytest.mark.asyncio
async def test_track_login(telemetry_track_data):

    await telemetry.track_login()
    telemetry_track_data.assert_called_once_with("UserLogged", {})


@pytest.mark.asyncio
async def test_track_bulk(telemetry_track_data):
    task, records = TaskType.token_classification, 100

    await telemetry.track_bulk(task=task, records=records)
    telemetry_track_data.assert_called_once_with(
        "DataLogged", {"task": task, "records": records}
    )


@pytest.mark.asyncio
async def test_track_error(telemetry_track_data):
    error = RubrixServerError()

    await telemetry.track_error(error)
    telemetry_track_data.assert_called_once_with(
        "ErrorRaised", {"code": error.get_error_code()}
    )
