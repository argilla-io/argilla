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

import random
from string import ascii_lowercase

import pytest

from argilla import Argilla, Dataset, Settings, Workspace, TextQuestion, TextField
from argilla._exceptions import SettingsError


def test_dataset_empty_settings(client: Argilla, workspace: Workspace):
    name = "".join(random.choices(ascii_lowercase, k=16))
    settings = Settings()
    dataset = Dataset(
        name=name,
        workspace=workspace.name,
        settings=settings,
        client=client,
    )
    with pytest.raises(expected_exception=SettingsError):
        dataset.create()


def test_dataset_no_fields(client: Argilla, workspace: Workspace) -> None:
    name = "".join(random.choices(ascii_lowercase, k=16))
    settings = Settings(
        questions=[
            TextQuestion(name="text_question"),
        ],
    )
    dataset = Dataset(
        name=name,
        workspace=workspace.name,
        settings=settings,
        client=client,
    )
    with pytest.raises(expected_exception=SettingsError):
        dataset.create()


def test_dataset_no_questions(client: Argilla, workspace: Workspace) -> Dataset:
    name = "".join(random.choices(ascii_lowercase, k=16))
    settings = Settings(
        fields=[
            TextField(name="text_field"),
        ],
    )
    dataset = Dataset(
        name=name,
        workspace=workspace.name,
        settings=settings,
        client=client,
    )
    with pytest.raises(expected_exception=SettingsError):
        dataset.create()
