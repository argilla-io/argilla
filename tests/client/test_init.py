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

from argilla import TextClassificationRecord
from argilla.client import api
from argilla.client.api import active_api


def test_resource_leaking_with_several_init(mocked_client):
    dataset = "test_resource_leaking_with_several_init"
    api.delete(dataset)

    # TODO: review performance in Windows. See https://github.com/recognai/argilla/pull/1702
    for i in range(0, 20):
        api.init()

    for i in range(0, 10):
        api.init()
        api.log(
            TextClassificationRecord(text="The text"),
            name=dataset,
            verbose=False,
        )

    assert len(api.load(dataset)) == 10


def test_init_with_extra_headers(mocked_client):
    expected_headers = {
        "X-Custom-Header": "Mocking rules!",
        "Other-header": "Header value",
    }
    api.init(extra_headers=expected_headers)
    active_api = api.active_api()

    for key, value in expected_headers.items():
        assert active_api.http_client.headers[key] == value, f"{key}:{value} not in client headers"


def test_init(mocked_client):
    the_api = active_api()
    user = the_api.http_client.get("/api/me")
    assert user["username"] == "argilla"

    api.init(api_key="argilla.apikey")
    the_api = active_api()
    user = the_api.http_client.get("/api/me")
    assert user["username"] == "argilla"
