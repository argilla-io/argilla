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

from typing import TYPE_CHECKING

from argilla._version import version

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_api_status(client: "TestClient"):
    response = client.get("/api/_status")

    assert response.status_code == 200
    output = response.json()
    assert "version" in output and output["version"] == str(version)
    assert "elasticsearch" in output and isinstance(output["elasticsearch"], dict)
    assert "mem_info" in output and isinstance(output["mem_info"], dict)


def test_api_info(client: "TestClient"):
    response = client.get("/api/_info")

    assert response.status_code == 200
    output = response.json()
    assert output["version"] == str(version)
