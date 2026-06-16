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
from pytest_mock import MockerFixture

import argilla as rg


class TestSettingsUpdateCallsEachGroupOnce:
    """Settings.update() must call _update() exactly once per property group.

    Bug: the method contained a duplicate ``self.__questions._update()`` call at
    the end, causing every question to be sent to the API twice and the
    ``_delete()`` step for removed questions to run twice.
    """

    def test_update_calls_each_property_group_exactly_once(self, mocker: "MockerFixture"):
        """Each of fields/questions/vectors/metadata must be updated exactly once."""
        settings = rg.Settings(
            fields=[rg.TextField(name="text")],
            questions=[rg.LabelQuestion(name="label", labels=["pos", "neg"])],
        )

        mocker.patch.object(settings, "_update_dataset_related_attributes")
        mocker.patch.object(settings, "_update_last_api_call")
        mocker.patch.object(settings, "validate")

        # Access the name-mangled private attributes
        fields_update = mocker.patch.object(settings._Settings__fields, "_update")
        questions_update = mocker.patch.object(settings._Settings__questions, "_update")
        vectors_update = mocker.patch.object(settings._Settings__vectors, "_update")
        metadata_update = mocker.patch.object(settings._Settings__metadata, "_update")

        settings.update()

        fields_update.assert_called_once()
        questions_update.assert_called_once()
        vectors_update.assert_called_once()
        metadata_update.assert_called_once()
