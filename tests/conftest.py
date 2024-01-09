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

from pathlib import Path

from tests.pydantic_v1 import PYDANTIC_MAJOR_VERSION


def pytest_ignore_collect(path: Path, **kwargs) -> bool:
    """
    This function ignore server and integration related tests when pydantic v2 is detected since
    the server side is not pydantic v2 compatible
    """
    for ignore_pattern in ["**/unit/server/**", "**/integration/**"]:
        if Path(path).match(ignore_pattern):
            return PYDANTIC_MAJOR_VERSION == 2
    return False
