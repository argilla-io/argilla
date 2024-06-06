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
from unittest.mock import ANY, call

import pytest
from argilla_v1.client.enums import DatasetType
from rich.table import Table

if TYPE_CHECKING:
    from argilla_v1.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
    from argilla_v1.client.sdk.datasets.models import Dataset
    from click.testing import CliRunner
    from pytest_mock import MockerFixture
    from typer import Typer


@pytest.mark.usefixtures("login_mock")
class TestSuiteListDatasetsCommand:
    def test_list_datasets(
        self,
        cli_runner: "CliRunner",
        cli: "Typer",
        mocker: "MockerFixture",
        remote_feedback_dataset: "RemoteFeedbackDataset",
        dataset: "Dataset",
    ) -> None:
        add_row_spy = mocker.spy(Table, "add_row")
        list_datasets_mock = mocker.patch(
            "argilla_v1.client.api.list_datasets", return_value=[remote_feedback_dataset, dataset]
        )

        result = cli_runner.invoke(cli, "datasets list")

        assert result.exit_code == 0
        list_datasets_mock.assert_called_once_with(None, None)
        add_row_spy.assert_has_calls(
            [
                call(
                    ANY,
                    str(remote_feedback_dataset.id),
                    remote_feedback_dataset.name,
                    remote_feedback_dataset.workspace.name,
                    "Feedback",
                    None,
                    remote_feedback_dataset.created_at.isoformat(sep=" "),
                    remote_feedback_dataset.updated_at.isoformat(sep=" "),
                ),
                call(
                    ANY,
                    str(dataset.id),
                    dataset.name,
                    "unit-test",
                    "TextClassification",
                    ANY,
                    dataset.created_at.isoformat(sep=" "),
                    dataset.last_updated.isoformat(sep=" "),
                ),
            ]
        )

    def test_list_datasets_with_workspace(self, cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture") -> None:
        workspace_from_name_mock = mocker.patch("argilla_v1.client.workspaces.Workspace.from_name")
        list_datasets_mock = mocker.patch("argilla_v1.client.api.list_datasets")

        result = cli_runner.invoke(cli, "datasets list --workspace unit-test")

        assert result.exit_code == 0
        workspace_from_name_mock.assert_called_once_with("unit-test")
        list_datasets_mock.assert_called_once_with("unit-test", None)

    def test_list_datasets_with_non_existing_workspace(
        self, cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture"
    ) -> None:
        workspace_from_name_mock = mocker.patch(
            "argilla_v1.client.workspaces.Workspace.from_name", side_effect=ValueError
        )

        result = cli_runner.invoke(cli, "datasets list --workspace unit-test")

        assert result.exit_code == 1
        assert "Workspace with name=unit-test does not exist" in result.stdout
        workspace_from_name_mock.assert_called_once_with("unit-test")

    def test_list_datasets_using_type_feedback_filter(
        self, cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture"
    ) -> None:
        list_datasets_mock = mocker.patch("argilla_v1.client.api.list_datasets")

        result = cli_runner.invoke(cli, "datasets list --type feedback")

        assert result.exit_code == 0
        list_datasets_mock.assert_called_once_with(None, DatasetType.feedback)

    def test_list_datasets_using_type_other_filter(
        self, cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture"
    ) -> None:
        list_datasets_mock = mocker.patch("argilla_v1.client.api.list_datasets")

        result = cli_runner.invoke(cli, "datasets list --type other")

        assert result.exit_code == 0
        list_datasets_mock.assert_called_once_with(None, DatasetType.other)


@pytest.mark.usefixtures("not_logged_mock")
def test_cli_datasets_list_needs_login(cli_runner: "CliRunner", cli: "Typer") -> None:
    result = cli_runner.invoke(cli, "datasets list")

    assert "You are not logged in. Please run 'argilla login' to login" in result.stdout
    assert result.exit_code == 1
