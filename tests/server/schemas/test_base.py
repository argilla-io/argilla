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

import pytest
from argilla.server.schemas.base import UpdateSchema


def test_update_schema():
    class UnitTestUpdateSchema(UpdateSchema):
        unit: Optional[str]
        test: Optional[bool]

        __non_nullable_fields__ = {"unit", "test"}

    with pytest.raises(ValueError):
        UnitTestUpdateSchema(unit=None, test=None)
