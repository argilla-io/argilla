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

if TYPE_CHECKING:
    from argilla_v1.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
    from click.testing import CliRunner
    from pytest_mock import MockerFixture
    from typer import Typer


@pytest.mark.usefixtures("login_mock")
class TestSuiteDeleteDataset:
    def test_delete_dataset(
        self,
        cli_runner: "CliRunner",
        cli: "Typer",
        mocker: "MockerFixture",
        remote_feedback_dataset: "RemoteFeedbackDataset",
    ) -> None:
        dataset_from_argilla_mock = mocker.patch(
            "argilla_v1.client.feedback.dataset.local.dataset.FeedbackDataset.from_argilla",
            return_value=remote_feedback_dataset,
        )
        remote_feedback_dataset_delete_mock = mocker.patch(
            "argilla_v1.client.feedback.dataset.remote.dataset.RemoteFeedbackDataset.delete"
        )

        result = cli_runner.invoke(cli, "datasets --name unit-test --workspace unit-test delete")

        assert result.exit_code == 0
        assert "`FeedbackDataset` with name=unit-test and workspace=unit-test deleted" in result.stdout
        dataset_from_argilla_mock.assert_called_once_with(name="unit-test", workspace="unit-test")
        remote_feedback_dataset_delete_mock.assert_called_once()

    def test_delete_dataset_runtime_error(
        self,
        cli_runner: "CliRunner",
        cli: "Typer",
        mocker: "MockerFixture",
        remote_feedback_dataset: "RemoteFeedbackDataset",
    ) -> None:
        dataset_from_argilla_mock = mocker.patch(
            "argilla_v1.client.feedback.dataset.local.dataset.FeedbackDataset.from_argilla",
            return_value=remote_feedback_dataset,
        )
        remote_feedback_dataset_delete_mock = mocker.patch(
            "argilla_v1.client.feedback.dataset.remote.dataset.RemoteFeedbackDataset.delete", side_effect=RuntimeError
        )

        result = cli_runner.invoke(cli, "datasets --name unit-test --workspace unit-test delete")

        assert result.exit_code == 1
        assert "An unexpected error occurred when trying to delete the `FeedbackDataset`" in result.stdout
        dataset_from_argilla_mock.assert_called_once_with(name="unit-test", workspace="unit-test")
        remote_feedback_dataset_delete_mock.assert_called_once()


@pytest.mark.usefixtures("not_logged_mock")
def test_cli_datasets_delete_needs_login(cli_runner: "CliRunner", cli: "Typer") -> None:
    result = cli_runner.invoke(cli, "datasets --name my-dataset --workspace my-workspace delete")

    assert "You are not logged in. Please run 'argilla login' to login" in result.stdout
    assert result.exit_code == 1
