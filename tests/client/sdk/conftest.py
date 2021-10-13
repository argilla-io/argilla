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

from rubrix._constants import DEFAULT_API_KEY
from rubrix.client.sdk.client import AuthenticatedClient


class Helpers:
    def remove_description(self, schema: dict):
        """Removes the 'description' key from a model schema. We do not care about the doc strings."""
        if "description" in schema:
            del schema["description"]
        for value in schema.values():
            if isinstance(value, dict):
                self.remove_description(value)
        return schema


@pytest.fixture(scope="session")
def helpers():
    return Helpers()


@pytest.fixture(scope="session")
def sdk_client():
    return AuthenticatedClient(base_url="http://localhost:6900", token=DEFAULT_API_KEY)
