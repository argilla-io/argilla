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

import pytest
from argilla._version import version
from argilla.client import api
from argilla.client.utils import server_version

if TYPE_CHECKING:
    from argilla.server.models import User as ServerUser


def test_server_version_no_auth() -> None:
    with pytest.raises(RuntimeError, match="You must be logged in to Argilla to use this function."):
        server_version()


def test_server_version(owner: "ServerUser") -> None:
    api.init(api_key=owner.api_key)
    assert isinstance(server_version(), str)
    assert server_version() == version
