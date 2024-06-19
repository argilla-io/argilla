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
    from argilla_v1.client.feedback.dataset.local.dataset import FeedbackDataset
    from argilla_v1.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
    from click.testing import CliRunner
    from pytest_mock import MockerFixture
    from typer import Typer


@pytest.mark.usefixtures("login_mock")
class TestSuiteDatasetsPushCommand:
    def test_push_to_huggingface(
        self,
        cli_runner: "CliRunner",
        cli: "Typer",
        mocker: "MockerFixture",
        feedback_dataset: "FeedbackDataset",
        remote_feedback_dataset: "RemoteFeedbackDataset",
    ) -> None:
        dataset_from_argilla_mock = mocker.patch(
            "argilla_v1.client.feedback.dataset.local.dataset.FeedbackDataset.from_argilla",
            return_value=remote_feedback_dataset,
        )
        dataset_pull_mock = mocker.patch(
            "argilla_v1.client.feedback.dataset.remote.dataset.RemoteFeedbackDataset.pull",
            return_value=feedback_dataset,
        )
        push_to_huggingface_mock = mocker.patch(
            "argilla_v1.client.feedback.integrations.huggingface.dataset.HuggingFaceDatasetMixin.push_to_huggingface",
            return_value=None,
        )

        result = cli_runner.invoke(
            cli,
            "datasets --name my-dataset --workspace my-workspace push-to-huggingface --repo-id argilla/my-dataset --private",
        )

        assert result.exit_code == 0
        dataset_from_argilla_mock.assert_called_once_with(name="my-dataset", workspace="my-workspace")
        push_to_huggingface_mock.assert_called_once_with(
            repo_id="argilla/my-dataset", generate_card=True, private=True, token=None
        )
        dataset_pull_mock.assert_called_once_with()

    def test_push_to_huggingface_missing_repo_id_arg(
        self,
        cli_runner: "CliRunner",
        cli: "Typer",
        mocker: "MockerFixture",
        remote_feedback_dataset: "RemoteFeedbackDataset",
    ) -> None:
        mocker.patch(
            "argilla_v1.client.feedback.dataset.local.dataset.FeedbackDataset.from_argilla",
            return_value=remote_feedback_dataset,
        )

        result = cli_runner.invoke(cli, "datasets --name my-dataset push-to-huggingface")

        assert "Missing option" in result.stdout
        assert result.exit_code == 2


@pytest.mark.usefixtures("not_logged_mock")
def test_cli_datasets_push_to_huggingface_needs_login(cli_runner: "CliRunner", cli: "Typer") -> None:
    result = cli_runner.invoke(
        cli, "datasets --name my-dataset --workspace my-workspace push-to-huggingface --repo-id argilla/my-dataset"
    )

    assert "You are not logged in. Please run 'argilla login' to login" in result.stdout
    assert result.exit_code == 1
