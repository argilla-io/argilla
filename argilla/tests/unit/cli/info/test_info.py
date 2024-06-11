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

from typing import TYPE_CHECKING

import pytest
from argilla_v1._version import version
from argilla_v1.client.apis.status import ApiStatus

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock import MockerFixture
    from typer import Typer


@pytest.mark.usefixtures("login_mock")
def test_info_command(cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture") -> None:
    status_get_status_mock = mocker.patch(
        "argilla_v1.client.apis.status.Status.get_status",
        return_value=ApiStatus(
            **{
                "version": "1.2.3",
                "elasticsearch": {
                    "name": "elasticsearch",
                    "cluster_name": "es-argilla-local",
                    "cluster_uuid": "p7gBcG5OTlG7e-RHg28-Qg",
                    "version": {
                        "number": "1.2.3",
                        "build_flavor": "default",
                        "build_type": "docker",
                        "build_hash": "4ed5ee9afac63de92ec98f404ccbed7d3ba9584e",
                        "build_date": "2022-12-05T18:22:22.226119656Z",
                        "build_snapshot": False,
                        "lucene_version": "9.4.2",
                        "minimum_wire_compatibility_version": "7.17.0",
                        "minimum_index_compatibility_version": "7.0.0",
                    },
                    "tagline": "You Know, for Search",
                },
                "mem_info": {"rss": "210M", "vms": "391G", "pfaults": "18K", "pageins": "26B"},
            }
        ),
    )

    result = cli_runner.invoke(cli, "info")

    assert result.exit_code == 0
    assert f"Client version: {version}" in result.stdout
    assert "Server version: 1.2.3" in result.stdout
    assert "ElasticSearch version: 1.2.3" in result.stdout
    status_get_status_mock.assert_called_once()


@pytest.mark.usefixtures("not_logged_mock")
def test_info_needs_login(cli_runner: "CliRunner", cli: "Typer") -> None:
    result = cli_runner.invoke(cli, "info")

    assert result.exit_code == 1
    assert "You are not logged in. Please run 'argilla login' to login" in result.stdout
