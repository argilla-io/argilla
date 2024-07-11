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
from argilla_v1._version import version
from argilla_v1.client import singleton
from argilla_v1.client.utils import ServerInfo, server_info

if TYPE_CHECKING:
    from argilla_server.models import User as ServerUser


def test_server_info_no_auth() -> None:
    with pytest.raises(RuntimeError, match="You must be logged in to Argilla to use this function."):
        server_info()


@pytest.mark.skip(reason="No sense to test this in CI")
def test_server_info(owner: "ServerUser") -> None:
    singleton.init(api_key=owner.api_key)
    info = server_info()
    assert isinstance(info, ServerInfo)
    assert info.version == version
