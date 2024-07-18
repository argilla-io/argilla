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

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock import MockerFixture
    from typer import Typer


def test_start_command(cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture") -> None:
    uvicorn_run_mock = mocker.patch("uvicorn.run")
    result = cli_runner.invoke(cli, "start --host 1.1.1.1 --port 6899 --no-access-log")

    assert result.exit_code == 0
    uvicorn_run_mock.assert_called_once_with("argilla_server:app", host="1.1.1.1", port=6899, access_log=False)
