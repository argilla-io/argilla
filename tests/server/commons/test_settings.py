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
from argilla.server.settings import Settings
from pydantic import ValidationError


@pytest.mark.parametrize("bad_namespace", ["Badns", "bad-ns", "12-bad-ns", "@bad"])
def test_wrong_settings_namespace(monkeypatch, bad_namespace):
    monkeypatch.setenv("ARGILLA_NAMESPACE", bad_namespace)
    with pytest.raises(ValidationError):
        Settings()


def test_settings_namespace(monkeypatch):
    monkeypatch.setenv("ARGILLA_NAMESPACE", "namespace")
    settings = Settings()

    assert settings.namespace == "namespace"
    assert settings.dataset_index_name == "namespace.ar.datasets"
    assert settings.dataset_records_index_name == "namespace.ar.dataset.{}"


def test_settings_index_replicas_with_shards_defined(monkeypatch):
    monkeypatch.setenv("ARGILLA_ES_RECORDS_INDEX_SHARDS", "100")
    monkeypatch.setenv("ARGILLA_ES_RECORDS_INDEX_REPLICAS", "2")

    settings = Settings()
    assert settings.es_records_index_replicas == 2


def test_settings_default_index_replicas_with_shards_defined(monkeypatch):
    monkeypatch.setenv("ARGILLA_ES_RECORDS_INDEX_SHARDS", "100")
    settings = Settings()

    assert settings.es_records_index_shards == 100
    assert settings.es_records_index_replicas == 0
