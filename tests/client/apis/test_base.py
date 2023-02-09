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
from argilla.client import api
from argilla.client.apis import AbstractApi, api_compatibility
from argilla.client.sdk._helpers import handle_response_error
from argilla.client.sdk.commons.errors import ApiCompatibilityError


def test_api_compatibility(mocked_client):
    client = api.active_api().http_client
    dummy_api = AbstractApi(client)
    with pytest.raises(ApiCompatibilityError):
        with api_compatibility(api=dummy_api, min_version="999.1.0"):
            handle_response_error(mocked_client.post("/api/datasets"))
