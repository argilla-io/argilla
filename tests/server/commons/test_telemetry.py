import pytest

from rubrix.server.commons import telemetry
from rubrix.server.commons.models import TaskType
from rubrix.server.errors import RubrixServerError


@pytest.mark.asyncio
async def test_track_login(mocker):
    client = telemetry._TelemetryClient.get()
    spy = mocker.spy(client, "track_data")

    await telemetry.track_login()
    spy.assert_called_once_with("UserLogged", {})


@pytest.mark.asyncio
async def test_track_bulk(mocker):
    client = telemetry._TelemetryClient.get()
    spy = mocker.spy(client, "track_data")

    task, records = TaskType.token_classification, 100
    await telemetry.track_bulk(task=task, records=records)
    spy.assert_called_once_with("BulkData", {"task": task, "records": records})


@pytest.mark.asyncio
async def test_track_error(mocker):
    client = telemetry._TelemetryClient.get()
    spy = mocker.spy(client, "track_data")

    error = RubrixServerError()
    await telemetry.track_error(error)
    spy.assert_called_once_with("ServerError", {"code": error.get_error_code()})
