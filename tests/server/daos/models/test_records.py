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

import warnings

import pytest

from argilla.server.daos.models.records import BaseRecordInDB
from argilla.server.settings import settings


def test_metadata_limit():

    long_value = "a" * (settings.metadata_field_length + 1)
    short_value = "a" * (settings.metadata_field_length - 1)

    with pytest.warns(expected_warning=UserWarning):
        BaseRecordInDB(metadata=dict(a=long_value))

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        BaseRecordInDB(metadata=dict(a=short_value))
