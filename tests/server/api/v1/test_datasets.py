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

from fastapi.testclient import TestClient

from tests.factories import DatasetFactory


def test_list_datasets(client: TestClient, admin_auth_header: dict):
    DatasetFactory.create(name="dataset-a")
    DatasetFactory.create(name="dataset-b")
    DatasetFactory.create(name="dataset-c")

    response = client.get("/api/v1/datasets", headers=admin_auth_header)

    assert response.status_code == 200

    response_body = response.json()
    assert [dataset["name"] for dataset in response_body] == ["dataset-a", "dataset-b", "dataset-c"]
