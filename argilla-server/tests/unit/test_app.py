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
from typing import cast
from unittest import mock
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server._app import (
    create_server_app,
    configure_database,
    _create_oauth_allowed_workspaces,
    track_server_startup,
)
from argilla_server.models import Workspace
from argilla_server.security.authentication.oauth2 import OAuth2Settings
from argilla_server.security.authentication.oauth2.settings import AllowedWorkspace
from argilla_server.settings import Settings, settings
from starlette.routing import Mount
from starlette.testclient import TestClient

from argilla_server.telemetry import TelemetryClient
from tests.factories import WorkspaceFactory


@pytest.fixture
def test_settings():
    yield settings

    settings.base_url = "/"


@pytest.mark.asyncio
class TestApp:
    def test_create_app_with_base_url(self, test_settings: Settings):
        base_url = "/base/url"
        settings.base_url = base_url

        app = create_server_app()
        client = TestClient(app)

        response = client.get("/api/v1/docs")
        assert response.status_code == 404

        response = client.get(f"{base_url}/api/v1/docs")
        assert response.status_code == 200

        response = client.get("/api/v1/version")
        assert response.status_code == 404

        response = client.get(f"{base_url}/api/v1/version")
        assert response.status_code == 200

        assert len(app.routes) == 1
        assert cast(Mount, app.routes[0]).path == base_url

    def test_server_timing_header(self):
        client = TestClient(create_server_app())

        response = client.get("/api/v1/version")

        assert response.headers["Server-Timing"]

    async def test_create_allowed_workspaces(self, db: AsyncSession):
        with mock.patch(
            "argilla_server.security.settings.Settings.oauth",
            new_callable=lambda: OAuth2Settings.from_dict(
                {
                    "allowed_workspaces": [{"name": "ws1"}, {"name": "ws2"}],
                }
            ),
        ):
            await _create_oauth_allowed_workspaces(db)

            workspaces = (await db.scalars(select(Workspace))).all()
            assert len(workspaces) == 2
            assert set([ws.name for ws in workspaces]) == {"ws1", "ws2"}

    async def test_create_workspaces_with_empty_workspaces_list(self, db: AsyncSession):
        with mock.patch("argilla_server.security.settings.Settings.oauth", new_callable=OAuth2Settings):
            await _create_oauth_allowed_workspaces(db)

            workspaces = (await db.scalars(select(Workspace))).all()
            assert len(workspaces) == 0

    async def test_create_workspaces_with_existing_workspaces(self, db: AsyncSession):
        ws = await WorkspaceFactory.create(name="test")

        with mock.patch(
            "argilla_server.security.settings.Settings.oauth",
            new_callable=lambda: OAuth2Settings(allowed_workspaces=[AllowedWorkspace(name=ws.name)]),
        ):
            await _create_oauth_allowed_workspaces(db)

            workspaces = (await db.scalars(select(Workspace))).all()
            assert len(workspaces) == 1

    def test_track_telemetry_on_startup(self, test_settings: Settings, test_telemetry: TelemetryClient):
        settings.enable_telemetry = True

        track_server_startup()
        test_telemetry.track_server_startup.assert_called_once()

    def test_track_telemetry_on_startup_disabled(self, test_settings: Settings, test_telemetry: TelemetryClient):
        settings.enable_telemetry = False

        track_server_startup()
        test_telemetry.track_server_startup.assert_not_called()
