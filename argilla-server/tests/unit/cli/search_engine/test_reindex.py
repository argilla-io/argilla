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

from uuid import uuid4

from typer import Typer
from typer.testing import CliRunner


class TestCliServerSearchEngineReindex:
    # TODO: This test should create multiple datasets and records so they are reindexed.
    # In order to do that right now we need to duplicate all async test factories to be synchronous.
    # Instead of do that we can (once we move away from asynchronous requests) use regular factories here and improve
    # the test.
    def test_reindex(self, cli_runner: CliRunner, cli: Typer):
        result = cli_runner.invoke(cli, "search-engine reindex")

        assert result.exit_code == 0, result.output

    def test_reindex_with_nonexistent_dataset_id(self, cli_runner: CliRunner, cli: Typer):
        result = cli_runner.invoke(cli, f"search-engine reindex --dataset-id {uuid4()}")

        assert result.exit_code == 1
