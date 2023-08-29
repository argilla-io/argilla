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

from datetime import datetime
from typing import TYPE_CHECKING
from unittest.mock import ANY, call
from uuid import uuid4

import httpx
import pytest
from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
from argilla.client.feedback.schemas.fields import TextField
from argilla.client.feedback.schemas.questions import TextQuestion
from argilla.client.sdk.datasets.models import Dataset
from argilla.client.workspaces import Workspace
from rich.table import Table

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock import MockerFixture
    from typer import Typer


@pytest.fixture
def remote_feedback_dataset() -> "RemoteFeedbackDataset":
    workspace = Workspace.__new__(Workspace)
    workspace.__dict__.update(
        {
            "id": uuid4(),
            "name": "unit-test",
            "inserted_at": datetime.now(),
            "updated_at": datetime.now(),
        }
    )
    return RemoteFeedbackDataset(
        client=httpx.Client(),
        id=uuid4(),
        name="unit-test",
        workspace=workspace,
        fields=[TextField(name="prompt")],
        questions=[TextQuestion(name="corrected")],
    )


@pytest.fixture
def dataset() -> Dataset:
    return Dataset(
        name="unit-test",
        id="rg.unit-test",
        task="TextClassification",
        owner="unit-test",
        workspace="unit-test",
        created_at=datetime.now(),
        last_updated=datetime.now(),
    )


@pytest.mark.usefixtures("login_mock")
class TestSuiteListDatasetsCommand:
    def test_list_datasets(
        self,
        cli_runner: "CliRunner",
        cli: "Typer",
        mocker: "MockerFixture",
        remote_feedback_dataset: RemoteFeedbackDataset,
        dataset: Dataset,
    ) -> None:
        add_row_spy = mocker.spy(Table, "add_row")
        feedback_dataset_list_mock = mocker.patch(
            "argilla.client.feedback.dataset.local.FeedbackDataset.list", return_value=[remote_feedback_dataset]
        )
        list_datasets_mock = mocker.patch("argilla.client.api.list_datasets", return_value=[dataset])

        result = cli_runner.invoke(cli, "datasets list")

        assert result.exit_code == 0
        feedback_dataset_list_mock.assert_called_once_with(None)
        list_datasets_mock.assert_called_once_with(None)
        add_row_spy.assert_has_calls(
            [
                call(
                    ANY,
                    str(remote_feedback_dataset.id),
                    remote_feedback_dataset.name,
                    remote_feedback_dataset.workspace.name,
                    "Feedback",
                    None,
                    None,
                    None,
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
        feedback_dataset_list_mock = mocker.patch("argilla.client.feedback.dataset.local.FeedbackDataset.list")
        list_datasets_mock = mocker.patch("argilla.client.api.list_datasets")

        result = cli_runner.invoke(cli, "datasets list --workspace unit-test")

        assert result.exit_code == 0
        feedback_dataset_list_mock.assert_called_once_with("unit-test")
        list_datasets_mock.assert_called_once_with("unit-test")

    def test_list_datasets_using_kind_feedback_filter(
        self, cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture"
    ) -> None:
        feedback_dataset_list_mock = mocker.patch("argilla.client.feedback.dataset.local.FeedbackDataset.list")
        list_datasets_mock = mocker.patch("argilla.client.api.list_datasets")

        result = cli_runner.invoke(cli, "datasets list --kind feedback")

        assert result.exit_code == 0
        feedback_dataset_list_mock.assert_called_once_with(None)
        list_datasets_mock.assert_not_called()

    def test_list_datasets_using_kind_other_filter(
        self, cli_runner: "CliRunner", cli: "Typer", mocker: "MockerFixture"
    ) -> None:
        feedback_dataset_list_mock = mocker.patch("argilla.client.feedback.dataset.local.FeedbackDataset.list")
        list_datasets_mock = mocker.patch("argilla.client.api.list_datasets")

        result = cli_runner.invoke(cli, "datasets list --kind other")

        assert result.exit_code == 0
        feedback_dataset_list_mock.assert_not_called()
        list_datasets_mock.assert_called_once_with(None)


@pytest.mark.usefixtures("not_logged_mock")
def test_cli_datasets_list_needs_login(cli_runner: "CliRunner", cli: "Typer") -> None:
    result = cli_runner.invoke(cli, "datasets list")

    assert "You are not logged in. Please run `argilla login` to login to an Argilla server." in result.stdout
    assert result.exit_code == 1
