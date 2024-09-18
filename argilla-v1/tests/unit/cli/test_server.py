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


class TestSuiteServerCli:
    @pytest.mark.skipif(reason="Argilla server is installed", condition=False)
    def test_server_cli_is_present(self, cli_runner: "CliRunner", cli: "Typer") -> None:
        result = cli_runner.invoke(cli, "server --help")

        assert result.exit_code == 0
        assert "Commands for Argilla server management" in result.stdout
