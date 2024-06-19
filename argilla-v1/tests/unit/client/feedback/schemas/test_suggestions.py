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
from argilla_v1.feedback import TextQuestion


def test_create_suggestion():
    question = TextQuestion(name="text")

    suggestion = question.suggestion("Value for text", agent="mock")

    assert suggestion.question_name == question.name
    assert suggestion.agent == "mock"


def test_create_suggestion_with_wrong_value():
    with pytest.raises(ValueError, match="Value 10 is not valid for question type text. Expected <class 'str'>."):
        TextQuestion(name="text").suggestion(value=10, agent="Mock")
