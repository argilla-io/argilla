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

from argilla.server.apis.v0.models.commons.model import BaseUpdateLabelingRule


@pytest.mark.parametrize(
    "name",
    [
        "Bad name",
        "bad??name",
        "bad    name",
        "bad\nname",
        "what?",
        "Yeah!",
        "**clever**",
    ],
)
def test_wrong_name_for_labeling_rule(name):
    with pytest.raises(ValidationError):
        BaseUpdateLabelingRule(name=name)


@pytest.mark.parametrize(
    "name",
    [
        "cool.name",
        "cool_name",
        "CoolName",
        "cool_name.here",
        "oh-yeah",
        "33-23",
    ],
)
def test_good_name_for_labeling_rule(name):
    rule = BaseUpdateLabelingRule(name=name)
    assert rule.name == name
