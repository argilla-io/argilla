#  coding=utf-8
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
from pydantic import ValidationError
from rubrix.server.datasets.model import CreationDatasetRequest


@pytest.mark.parametrize(
    "name",
    ["fine", "fine33", "fine_33", "fine-3-3"],
)
def test_dataset_naming_ok(name):
    request = CreationDatasetRequest(name=name)
    assert request.name == name


@pytest.mark.parametrize(
    "name",
    [
        "WrongName",
        "-wrong_name",
        "_wrong_name",
        "wrong_name-??",
        "wrong name",
        "wrong:name",
        "wrong=?name",
    ],
)
def test_dataset_naming_ko(name):
    with pytest.raises(ValidationError, match="string does not match regex"):
        CreationDatasetRequest(name=name)
