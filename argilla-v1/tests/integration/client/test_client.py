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

import pytest
from argilla_v1.client.sdk.client import Client
from argilla_v1.client.singleton import active_api


@pytest.mark.parametrize(
    ("url", "raises_error"),
    [
        ("https://wrong_hostname", True),
        ("http://wrong_hostname_but_http", False),
        ("https://good-hostname", False),
        ("https://good-hostname/with_undescore_path", False),
        ("https://space.orchestapp.io/pbp-service-argilla_6900", False),
    ],
)
def test_wrong_hostname_values(
    url: str,
    raises_error: bool,
):
    if raises_error:
        with pytest.raises(Exception):
            Client(base_url=url)
    else:
        client = Client(base_url=url)
        assert client


def test_http_calls(mocked_client):
    rb_api = active_api()
    data = rb_api.http_client.get("/api/_info")
    assert data.get("version"), data
