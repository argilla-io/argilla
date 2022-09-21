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

import os

import pytest
from pydantic import ValidationError

from rubrix.server.settings import ApiSettings


@pytest.mark.parametrize("bad_namespace", ["Badns", "bad-ns", "12-bad-ns", "@bad"])
def test_wrong_settings_namespace(bad_namespace):
    os.environ["RUBRIX_NAMESPACE"] = bad_namespace
    with pytest.raises(ValidationError):
        ApiSettings()


def test_settings_namespace():
    os.environ["RUBRIX_NAMESPACE"] = "namespace"
    settings = ApiSettings()

    assert settings.namespace == "namespace"
    assert settings.dataset_index_name == ".rubrix.namespace.datasets-v0"
    assert (
        settings.dataset_records_index_name == ".rubrix.namespace.dataset.{}.records-v0"
    )
