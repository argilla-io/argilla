# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest.mock import Mock, patch

import pytest

from argilla.client import Argilla


class TestSpacesDeploymentMixin:
    @pytest.fixture
    def argilla_client_class(self):
        return Argilla

    @patch("argilla._helpers._deploy.HfApi")
    @patch("argilla._helpers._deploy.get_token")
    @patch("argilla.client.Argilla.__init__", return_value=None)
    def test_deploy_on_spaces(self, mock_argilla_init, mock_get_token, mock_hf_api, argilla_client_class):
        mock_get_token.return_value = "fake_token"
        mock_api = Mock(api_key="12345678")
        mock_hf_api.return_value = mock_api
        mock_api.whoami.return_value = {"name": "test_user"}
        mock_api.repo_exists.return_value = False
        mock_api.get_space_runtime.return_value = Mock(api_key="12345678", stage="RUNNING")

        result = argilla_client_class.deploy_on_spaces(
            username="test_user",
            password="test_pass",
            repo_name="test_repo",
            token="fake_token",
        )

        assert isinstance(result, Argilla)
        mock_api.duplicate_space.assert_called_once()
        mock_api.create_repo.assert_called_once()
        mock_argilla_init.assert_called_once()

        # Check the arguments passed to Argilla.__init__
        args, kwargs = mock_argilla_init.call_args
        assert kwargs["api_key"] == "12345678"
        assert kwargs["api_url"].startswith("https://")
        assert kwargs["api_url"].endswith(".hf.space/")
        assert "api_key" in kwargs
        assert "headers" in kwargs

    @patch("argilla._helpers._deploy.get_token")
    @patch("argilla._helpers._deploy.login")
    def test_acquire_hf_token(self, mock_login, mock_get_token, argilla_client_class):
        mock_get_token.side_effect = [None, "fake_token"]
        token = argilla_client_class._acquire_hf_token(None)
        assert token == "fake_token"
        mock_login.assert_called_once()

    @pytest.mark.parametrize(
        "stage,expected",
        [
            ("RUNNING", False),
            ("BUILDING", True),
            ("PAUSED", True),
            ("INVALID", pytest.raises(ValueError)),
        ],
    )
    def test_check_if_running(self, stage, expected, argilla_client_class):
        runtime = Mock(stage=stage)
        if isinstance(expected, bool):
            assert argilla_client_class._check_if_running(runtime) == expected
        else:
            with expected:
                argilla_client_class._check_if_running(runtime)

    @pytest.mark.parametrize(
        "stage,expected",
        [
            ("RUNNING", False),
            ("PAUSED", True),
            ("INVALID", pytest.raises(ValueError)),
        ],
    )
    def test_check_if_runtime_can_be_build(self, stage, expected, argilla_client_class):
        runtime = Mock(stage=stage)
        if isinstance(expected, bool):
            assert argilla_client_class._check_if_runtime_can_be_build(runtime) == expected
        else:
            with expected:
                argilla_client_class._check_if_runtime_can_be_build(runtime)

    @pytest.mark.parametrize(
        "component,expected",
        [
            ("Test-Repo", "test-repo"),
            ("Test_Repo_123", "test-repo-123"),
            ("Test Repo!@#", "test-repo"),
            ("-test-repo-", "test-repo"),
        ],
    )
    def test_sanitize_url_component(self, component, expected, argilla_client_class):
        assert argilla_client_class._sanitize_url_component(component) == expected
