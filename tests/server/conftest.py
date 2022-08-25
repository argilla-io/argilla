import pytest

from rubrix.server.commons import telemetry


@pytest.fixture
def telemetry_track_data(mocker):
    client = telemetry._TelemetryClient.get()
    spy = mocker.spy(client, "track_data")

    return spy
