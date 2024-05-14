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
from typing import Optional

from argilla.client.sdk.client import AuthenticatedClient


class AbstractApi(object):
    def __init__(self, client: AuthenticatedClient):
        self.__client__ = client

    @property
    def http_client(self):
        return self.__client__

    @staticmethod
    def _parse_query(*, query: Optional[dict]):
        query_request = query or {}
        return {k: v for k, v in query_request.items() if v is not None}
