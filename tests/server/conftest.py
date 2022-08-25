import pytest

from rubrix.server.commons import telemetry


@pytest.fixture
def telemetry_track_data(mocker):

    client = telemetry._TelemetryClient.get()
    # Disable sending data for tests
    client._client = telemetry._configure_analytics(disable_send=False)
    spy = mocker.spy(client, "track_data")

    return spy
