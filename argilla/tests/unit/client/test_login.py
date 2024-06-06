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

import importlib
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from argilla_v1.client import login

if TYPE_CHECKING:
    from pytest_mock import MockFixture


def test_argilla_credentials_save(mocker: "MockFixture"):
    mocker.patch("builtins.open", new_callable=mocker.mock_open)

    login.ArgillaCredentials(
        api_url="http://unit-test.com:6900",
        api_key="unit.test",
        workspace="unit-tests",
        extra_headers={"X-Unit-Test": "true"},
    ).save()

    open.assert_called_once_with(login.ARGILLA_CREDENTIALS_FILE, "w")
    open().write.assert_called_once_with(
        '{"api_url": "http://unit-test.com:6900", "api_key": "unit.test", "workspace": "unit-tests", "extra_headers": {"X-Unit-Test": "true"}}'
    )


def test_argilla_credentials_load(mocker: "MockFixture"):
    mocker.patch(
        "builtins.open",
        mocker.mock_open(
            read_data='{"api_url": "http://unit-test.com:6900", "api_key": "unit.test", "workspace": "unit-tests", "extra_headers": {"X-Unit-Test": "true"}}'
        ),
    )
    path_mock = mocker.patch.object(Path, "exists")
    path_mock.return_value = True

    credentials = login.ArgillaCredentials.load()

    open.assert_called_once_with(login.ARGILLA_CREDENTIALS_FILE, "r")
    assert credentials.api_url == "http://unit-test.com:6900"
    assert credentials.api_key == "unit.test"
    assert credentials.workspace == "unit-tests"
    assert credentials.extra_headers == {"X-Unit-Test": "true"}


def test_argilla_credentials_remove(mocker: "MockFixture"):
    path_mock = mocker.patch.object(Path, "exists")
    path_mock.return_value = True
    unlink_mock = mocker.patch.object(Path, "unlink")

    login.ArgillaCredentials.remove()

    path_mock.assert_called_once()
    unlink_mock.assert_called_once()


def test_argilla_credentials_remove_raises_error(mocker: "MockFixture"):
    path_mock = mocker.patch.object(Path, "exists")
    path_mock.return_value = False

    with pytest.raises(FileNotFoundError):
        login.ArgillaCredentials.remove()


def test_argilla_credentials_load_raises_error():
    with pytest.raises(FileNotFoundError):
        login.ArgillaCredentials.load()


def test_login(mocker: "MockFixture"):
    mocker.patch("builtins.open", new_callable=mocker.mock_open)
    init_mock = mocker.patch("argilla_v1.client.login.init")

    login.login(
        api_url="http://unit-test.com:6900",
        api_key="unit.test",
        workspace="unit-tests",
        extra_headers={"X-Unit-Test": "true"},
    )

    init_mock.assert_called_once_with(
        api_url="http://unit-test.com:6900",
        api_key="unit.test",
        workspace="unit-tests",
        extra_headers={"X-Unit-Test": "true"},
    )


def test_argilla_cache_dir_environment_variable():
    import os

    assert login.ARGILLA_CACHE_DIR == Path().home() / ".cache" / "argilla"

    os.environ["ARGILLA_CACHE_DIR"] = "/tmp/unit-test"

    importlib.reload(login)

    assert login.ARGILLA_CACHE_DIR == Path("/tmp/unit-test")
