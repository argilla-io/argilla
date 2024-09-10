# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from unittest import mock
from argilla.settings._templates import DefaultSettingsMixin


class TestDefaultSettingsMixin:
    def test_for_document_classification(self):
        mock_labels = ["positive", "negative"]
        settings = DefaultSettingsMixin.for_classification(labels=mock_labels)
        assert settings.guidelines == "Select a label for the document."
        assert len(settings.fields) == 1
        assert settings.fields[0].name == "text"
        assert len(settings.questions) == 1
        assert settings.questions[0].name == "label"
        assert settings.questions[0].labels == mock_labels

    def test_for_response_ranking(self):
        settings = DefaultSettingsMixin.for_ranking()
        assert settings.guidelines == "Rank the responses."
        assert len(settings.fields) == 3
        assert settings.fields[0].name == "instruction"
        assert settings.fields[1].name == "response1"
        assert settings.fields[2].name == "response2"
        assert len(settings.questions) == 1
        assert settings.questions[0].name == "ranking"
        assert settings.questions[0].values == ["response1", "response2"]

    def test_for_response_rating(self):
        settings = DefaultSettingsMixin.for_rating()
        assert settings.guidelines == "Rate the response."
        assert len(settings.fields) == 2
        assert settings.fields[0].name == "instruction"
        assert settings.fields[1].name == "response"
        assert len(settings.questions) == 1
        assert settings.questions[0].name == "rating"
        assert settings.questions[0].values == [1, 2, 3, 4, 5]
