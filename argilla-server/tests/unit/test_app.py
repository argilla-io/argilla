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

import pytest
from argilla_server._app import create_server_app
from argilla_server.settings import Settings, settings
from starlette.routing import Mount
from starlette.testclient import TestClient


@pytest.fixture
def test_settings():
    yield settings

    settings.base_url = "/"


class TestApp:
    def test_create_app_with_base_url(self, test_settings: Settings):
        base_url = "/base/url"
        settings.base_url = base_url

        app = create_server_app()
        client = TestClient(app)

        response = client.get("/api/docs")
        assert response.status_code == 404

        response = client.get(f"{base_url}/api/docs")
        assert response.status_code == 200

        response = client.get("/api/_info")
        assert response.status_code == 404

        response = client.get(f"{base_url}/api/_info")
        assert response.status_code == 200

        assert len(app.routes) == 1
        assert cast(Mount, app.routes[0]).path == base_url
