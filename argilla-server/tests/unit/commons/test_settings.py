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

from argilla_server.settings import Settings


def test_settings_index_replicas_with_shards_defined(monkeypatch):
    monkeypatch.setenv("ARGILLA_ES_RECORDS_INDEX_SHARDS", "100")
    monkeypatch.setenv("ARGILLA_ES_RECORDS_INDEX_REPLICAS", "2")

    assert Settings().es_records_index_replicas == 2


def test_settings_default_index_replicas_with_shards_defined(monkeypatch):
    monkeypatch.setenv("ARGILLA_ES_RECORDS_INDEX_SHARDS", "100")

    settings = Settings()

    assert settings.es_records_index_shards == 100
    assert settings.es_records_index_replicas == 0


def test_settings_default_database_url(monkeypatch):
    monkeypatch.setenv("ARGILLA_DATABASE_URL", "")

    settings = Settings()

    assert settings.database_url == f"sqlite+aiosqlite:///{settings.home_path}/argilla.db?check_same_thread=False"


@pytest.mark.parametrize(
    "url, expected_url",
    [
        ("sqlite:///test.db", "sqlite+aiosqlite:///test.db"),
        ("sqlite:///:memory:", "sqlite+aiosqlite:///:memory:"),
        ("postgresql://user:pass@localhost:5432/db", "postgresql+asyncpg://user:pass@localhost:5432/db"),
        ("postgresql+psycopg2://user:pass@localhost:5432/db", "postgresql+asyncpg://user:pass@localhost:5432/db"),
    ],
)
def test_settings_database_url(url: str, expected_url: str, monkeypatch):
    monkeypatch.setenv("ARGILLA_DATABASE_URL", url)

    assert Settings().database_url == expected_url


def test_settings_default_database_sqlite_timeout():
    assert Settings().database_sqlite_timeout == 5


def test_settings_database_sqlite_timeout(monkeypatch):
    monkeypatch.setenv("ARGILLA_DATABASE_SQLITE_TIMEOUT", "3")

    assert Settings().database_sqlite_timeout == 3


def test_settings_default_database_postgresql_pool_size():
    assert Settings().database_postgresql_pool_size == 15


def test_settings_database_postgresql_pool_size(monkeypatch):
    monkeypatch.setenv("ARGILLA_DATABASE_POSTGRESQL_POOL_SIZE", "42")

    assert Settings().database_postgresql_pool_size == 42


def test_settings_default_database_postgresql_max_overflow():
    assert Settings().database_postgresql_max_overflow == 10


def test_settings_database_postgresql_max_overflow(monkeypatch):
    monkeypatch.setenv("ARGILLA_DATABASE_POSTGRESQL_MAX_OVERFLOW", "12")

    assert Settings().database_postgresql_max_overflow == 12


def test_enable_share_your_progress(monkeypatch):
    monkeypatch.setenv("ARGILLA_ENABLE_SHARE_YOUR_PROGRESS", "true")

    assert Settings().enable_share_your_progress is True


def test_disable_enable_share_your_progress(monkeypatch):
    monkeypatch.setenv("ARGILLA_ENABLE_SHARE_YOUR_PROGRESS", "false")

    assert Settings().enable_share_your_progress is False
