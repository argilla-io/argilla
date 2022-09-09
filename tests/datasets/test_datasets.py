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

import rubrix as rb
from rubrix import TextClassificationSettings, TokenClassificationSettings
from rubrix.client import api


@pytest.mark.parametrize(
    ("settings_", "wrong_settings"),
    [
        (
            TextClassificationSettings(label_schema={"A", "B"}),
            TokenClassificationSettings(label_schema={"PER", "ORG"}),
        ),
        (
            TokenClassificationSettings(label_schema={"PER", "ORG"}),
            TextClassificationSettings(label_schema={"A", "B"}),
        ),
    ],
)
def test_settings_workflow(mocked_client, settings_, wrong_settings):
    dataset = "test-dataset"
    rb.delete(dataset)
    rb.configure_dataset(dataset, settings=settings_)

    current_api = api.active_api()
    datasets_api = current_api.datasets

    found_settings = datasets_api.load_settings(dataset)
    assert found_settings == settings_

    settings_.label_schema = {"LALALA"}
    rb.configure_dataset(dataset, settings_)

    found_settings = datasets_api.load_settings(dataset)
    assert found_settings == settings_

    with pytest.raises(ValueError, match="Task type mismatch"):
        rb.configure_dataset(dataset, wrong_settings)
