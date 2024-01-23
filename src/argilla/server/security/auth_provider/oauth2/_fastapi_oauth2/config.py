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

import os
from typing import List, Union

from .client import OAuth2Client


class OAuth2Config:
    """Configuration class of the authentication middleware."""

    enable_ssr: bool
    allow_http: bool
    jwt_secret: str
    jwt_expires: int
    jwt_algorithm: str
    clients: List[OAuth2Client]

    def __init__(
        self,
        *,
        enable_ssr: bool = True,
        allow_http: bool = False,
        jwt_secret: str = "",
        jwt_expires: Union[int, str] = 900,
        jwt_algorithm: str = "HS256",
        clients: List[OAuth2Client] = None,
    ) -> None:
        if allow_http:
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        self.enable_ssr = enable_ssr
        self.allow_http = allow_http
        self.jwt_secret = jwt_secret
        self.jwt_expires = int(jwt_expires)
        self.jwt_algorithm = jwt_algorithm
        self.clients = clients or []
