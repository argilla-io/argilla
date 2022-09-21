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

import httpx

from rubrix.client.sdk.client import AuthenticatedClient
from rubrix.client.sdk.commons.errors_handler import handle_response_error
from rubrix.client.sdk.users.models import User


def whoami(client: AuthenticatedClient) -> User:
    response = client.get("/api/me")
    return User(**response)
