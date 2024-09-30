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

import time
import uuid
from typing import TYPE_CHECKING, Optional, Union

from huggingface_hub import HfApi, SpaceRuntime, get_token, login, notebook_login
from huggingface_hub.hf_api import RepoUrl
from huggingface_hub.utils import is_google_colab, is_notebook

from argilla._helpers._log import LoggingMixin

if TYPE_CHECKING:
    from huggingface_hub.hf_api import RepoUrl, SpaceHardware, SpaceStorage  # noqa

    from argilla.client import Argilla

_SLEEP_TIME = 10
_FROM_REPO_ID = "argilla/argilla-template-space"


class SpacesDeploymentMixin(LoggingMixin):
    @classmethod
    def deploy_on_spaces(
        cls,
        username: Optional[Union[str, None]] = None,
        password: Optional[Union[str, None]] = "12345678",
        api_key: Optional[Union[str, None]] = None,
        repo_name: Optional[str] = "argilla",
        org_name: Optional[str] = None,
        token: Optional[str] = None,
        space_storage: Optional[Union[str, "SpaceStorage", None]] = None,
        space_hardware: Optional[Union[str, "SpaceHardware"]] = "cpu-basic",
        private: Optional[Union[bool, None]] = False,
        overwrite: Optional[Union[bool, None]] = False,
    ) -> "Argilla":
        """
        Deploys Argilla on Hugging Face Spaces.
        For a full guide check our docs.

        Args:
            username (Optional[Union[str, None]]): The username of the admin user.
                Defaults to None and is set to the current user of the Hugging Face Hub token.
            password (Optional[Union[str, None]]): The password of the admin user. Defaults to "12345678".
            api_key (Optional[Union[str, None]]): The API key of the admin user. Defaults to None.
                When None, a random API key will be generated using a `uuid.uuid4().hex`.
            repo_name (Optional[str]): The ID of the repository where Argilla will be deployed. Defaults to "argilla".
            org_name (Optional[str]): The name of the organization where Argilla will be deployed. Defaults to None.
            token (Optional[Union[str, SpaceStorage, None]]): The Hugging Face authentication token. Defaults to None.
            space_storage (Optional[Union[str, SpaceStorage, None]]): The persistant storage size for the space. Defaults to None without persistant storage.
            space_hardware (Optional[Union[str, SpaceStorage, None]]): The hardware configuration for the space. Defaults to "cpu-basic" with downtime after 48 hours of inactivity.
            private (Optional[Union[bool, None]]): Whether the space should be private. Defaults to False.
            overwrite (Optional[Union[bool, None]]): Whether to overwrite the existing space. Defaults to False.

        Returns:
            RepoUrl: The URL of the created space.

        Example:
            import argilla as rg

            client = rg.Argilla.deploy_on_spaces(
                username="admin",
                password="12345678",
                api_key=None,
                repo_name="my-space",
                org_name="my-org",
                token="hf_ABC123",
                space_storage="10GB",
                space_hardware="cpu-basic",
                private=True,
                overwrite=False,
            )
        """
        token = cls._acquire_hf_token(cls, token=token)
        api = HfApi(token=token)

        # Get the org name from the repo name or default to the current user
        token_username = api.whoami(token=token)["name"]
        username = username or token_username
        org_name = org_name or token_username
        repo_id = f"{org_name}/{repo_name}"

        # Define the secrets for the space
        api_key = api_key or uuid.uuid4().hex
        secrets = [
            {"key": "USERNAME", "value": username, "description": "The username of the admin user"},
            {"key": "PASSWORD", "value": password, "description": "The password of the admin user"},
            {"key": "API_KEY", "value": api_key, "description": "The API key of the admin user"},
        ]

        # Check if the space already exists
        if api.repo_exists(repo_id=repo_id, repo_type="space", token=token):
            if cls._check_if_runtime_can_be_build(api.get_space_runtime(repo_id=repo_id, token=token)):
                api.restart_space(repo_id=repo_id, token=token)
            if overwrite:
                for secret in secrets:
                    api.add_space_secret(
                        repo_id=repo_id,
                        key=secret["key"],
                        value=secret["value"],
                        description=secret["description"],
                        token=token,
                    )
                if space_hardware:
                    api.request_space_hardware(hardware=space_hardware, token=token)
                if space_storage:
                    api.request_space_storage(storage=space_storage, token=token)
        else:
            api.duplicate_space(
                from_id=_FROM_REPO_ID,
                to_id=repo_id,
                private=private,
                token=token,
                exist_ok=True,
                hardware=space_hardware,
                storage=space_storage,
                secrets=secrets,
            )

        repo_url: RepoUrl = api.create_repo(
            repo_id=repo_id, repo_type="space", token=token, exist_ok=True, space_sdk="docker"
        )
        api_url: str = (
            f"https://{cls._sanitize_url_component(org_name)}-{cls._sanitize_url_component(repo_name)}.hf.space/"
        )
        cls._log_message(cls, message=f"Argilla is being deployed at: {repo_url}")
        while cls._check_if_running(api.get_space_runtime(repo_id=repo_id, token=token)):
            time.sleep(_SLEEP_TIME)
            cls._log_message(cls, message=f"Deploying. Waiting {_SLEEP_TIME} seconds.")

        headers = {}
        if private:
            headers["Authorization"] = f"Bearer {token}"

        return cls(api_url=api_url, api_key=api_key, headers=headers)

    def _acquire_hf_token(self, token: Union[str, None]) -> str:
        """Obtain the Hugging Face authentication token to deploy a space and authenticate."""
        if token is None:
            token = get_token()
        if token is None:
            if self._is_interactive():
                notebook_login()
            else:
                login()
            token = get_token()
        return token

    def _check_if_running(runtime: SpaceRuntime):
        """Check the current stage of the space runtime. Simplified to return True when being build."""
        if runtime.stage in ["RUNNING"]:
            return False
        elif runtime.stage in [
            "RUNNING_APP_STARTING",
            "RUNNING_BUILDING",
            "BUILDING",
            "PAUSED",
            "STOPPED",
            "APP_STARTING",
        ]:
            return True
        else:
            raise ValueError(f"Space configuration is wrong and in state: {runtime.stage}")

    def _check_if_runtime_can_be_build(runtime: SpaceRuntime):
        """Check the current stage of the space runtime. Simplified to return True when being build."""
        if runtime.stage in ["RUNNING", "RUNNING_APP_STARTING", "RUNNING_BUILDING", "BUILDING", "APP_STARTING"]:
            return False
        elif runtime.stage in ["PAUSED", "STOPPED"]:
            return True
        else:
            raise ValueError(f"Space configuration is wrong and in state: {runtime.stage}")

    def __repr__(self) -> str:
        if is_notebook() or is_google_colab():
            from IPython.display import IFrame, display

            display(IFrame(src=self.api_url, frameborder=0, width=850, height=600))
            return f"Argilla is being deployed at: {self.api_url}"
        else:
            return f"Argilla is being deployed at: {self.api_url}"

    @staticmethod
    def _sanitize_url_component(component: str) -> str:
        """Sanitize a component of a URL by replacing non-URL compatible characters."""
        import re

        # Replace any character that's not alphanumeric or hyphen with a hyphen
        sanitized = re.sub(r"[^a-zA-Z0-9-]", "-", component)
        # Convert to lowercase
        sanitized = sanitized.lower()
        # Remove any leading or trailing hyphens
        sanitized = sanitized.strip("-")
        return sanitized
