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


def test_complex_settings(monkeypatch):
    monkeypatch.setenv("ARGILLA_ELASTICSEARCH_EXTRA_ARGS", '{"a": 1, "b": 2}')
    monkeypatch.setenv("ARGILLA_OPENSEARCH_EXTRA_ARGS", '{"a": 1, "b": 2}')

    from argilla.server.settings import Settings

    settings = Settings()

    assert settings.elasticsearch_extra_args == {"a": 1, "b": 2}
    assert settings.opensearch_extra_args == {"a": 1, "b": 2}
