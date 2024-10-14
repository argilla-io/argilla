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
import warnings
from typing import TYPE_CHECKING, Literal, Optional, Union

from huggingface_hub import HfApi, SpaceStage, get_token, login, notebook_login
from huggingface_hub.hf_api import RepoUrl

from argilla._helpers._log import LoggingMixin

if TYPE_CHECKING:
    from huggingface_hub.hf_api import RepoUrl, SpaceHardware, SpaceStorage  # noqa

    from argilla.client import Argilla

_SLEEP_TIME = 10
_ARGILLA_SPACE_TEMPLATE_REPO = "argilla/argilla-template-space"


class SpacesDeploymentMixin(LoggingMixin):
    @classmethod
    def deploy_on_spaces(
        cls,
        api_key: str,
        repo_name: Optional[str] = "argilla",
        org_name: Optional[str] = None,
        hf_token: Optional[str] = None,
        space_storage: Optional[Union[str, "SpaceStorage", Literal["small", "medium", "large"]]] = None,
        space_hardware: Optional[Union[str, "SpaceHardware", Literal["cpu-basic", "cpu-upgrade"]]] = "cpu-basic",
        private: Optional[Union[bool, None]] = False,
        overwrite: Optional[Union[bool, None]] = False,
    ) -> "Argilla":
        """
                Deploys Argilla on Hugging Face Spaces.

                Args:
                    api_key (str): The Argilla API key to be defined for the owner user and creator of the Space.
                    repo_name (Optional[str]): The ID of the repository where Argilla will be deployed. Defaults to "argilla".
                    org_name (Optional[str]): The name of the organization where Argilla will be deployed. Defaults to None.
                    hf_token (Optional[Union[str, None]]): The Hugging Face authentication token. Defaults to None.
                    space_storage (Optional[Union[str, SpaceStorage]]): The persistant storage size for the space. Defaults to None without persistant storage.
                    space_hardware (Optional[Union[str, SpaceHardware]]): The hardware configuration for the space. Defaults to "cpu-basic" with downtime after 48 hours of inactivity.
                    private (Optional[Union[bool, None]]): Whether the space should be private. Defaults to False.
                    overwrite (Optional[Union[bool, None]]): Whether to overwrite the config of an existing space. Defaults to False.

                Returns:
                    Argilla: The Argilla client.

                Example:
                    ```Python
                    import argilla as rg
        api
                    client = rg.Argilla.deploy_on_spaces(api_key="12345678")
                    ```
        """
        hf_token = cls._acquire_hf_token(ht_token=hf_token)
        hf_api = HfApi(token=hf_token)

        # Get the org name from the repo name or default to the current user
        token_username = hf_api.whoami()["name"]
        org_name = org_name or token_username
        repo_id = f"{org_name}/{repo_name}"

        # Define the api_key for the space
        secrets = [
            {"key": "API_KEY", "value": api_key, "description": "The API key of the owner user."},
            {"key": "WORKSPACE", "value": "argilla", "description": "The workspace of the space."},
        ]

        # Check if the space already exists
        if hf_api.repo_exists(repo_id=repo_id, repo_type="space"):
            if cls._check_if_stage_can_be_build(hf_api.get_space_runtime(repo_id=repo_id).stage):
                hf_api.restart_space(repo_id=repo_id)

            if overwrite:
                for secret in secrets:
                    hf_api.add_space_secret(
                        repo_id=repo_id,
                        key=secret["key"],
                        value=secret["value"],
                        description=secret["description"],
                    )

                if space_hardware:
                    hf_api.request_space_hardware(repo_id=repo_id, hardware=space_hardware)

                if space_storage:
                    hf_api.request_space_storage(repo_id=repo_id, storage=space_storage)
                else:
                    cls._space_storage_warning()
        else:
            if space_storage is None:
                cls._space_storage_warning()

            hf_api.duplicate_space(
                from_id=_ARGILLA_SPACE_TEMPLATE_REPO,
                to_id=repo_id,
                private=private,
                exist_ok=True,
                hardware=space_hardware,
                storage=space_storage,
                secrets=secrets,
            )

        repo_url: RepoUrl = hf_api.create_repo(repo_id=repo_id, repo_type="space", exist_ok=True, space_sdk="docker")
        api_url: str = (
            f"https://{cls._sanitize_url_component(org_name)}-{cls._sanitize_url_component(repo_name)}.hf.space/"
        )
        cls._log_message(cls, message=f"Argilla is being deployed at: {repo_url}")
        while cls._check_if_running(hf_api.get_space_runtime(repo_id=repo_id).stage):
            time.sleep(_SLEEP_TIME)
            cls._log_message(cls, message=f"Deployment in progress. Waiting {_SLEEP_TIME} seconds.")

        headers = {}
        if private:
            headers["Authorization"] = f"Bearer {hf_token}"

        return cls(api_url=api_url, api_key=api_key, headers=headers)

    @staticmethod
    def _space_storage_warning() -> None:
        warnings.warn(
            "No storage provided. The space will not have persistant storage so every 48 hours your data will be reset."
        )

    @classmethod
    def _acquire_hf_token(cls, ht_token: Union[str, None]) -> str:
        """Obtain the Hugging Face authentication token to deploy a space and authenticate."""
        if ht_token is None:
            ht_token = get_token()
        if ht_token is None:
            if cls._is_interactive():
                notebook_login()
            else:
                login()
            ht_token = get_token()
        return ht_token

    @classmethod
    def _is_building(cls, stage: SpaceStage) -> bool:
        """Check the current stage of the space runtime. Simplified to return True when being built."""
        if stage in ["RUNNING_APP_STARTING", "RUNNING_BUILDING", "BUILDING", "APP_STARTING"]:
            return True
        elif stage in ["RUNNING", "PAUSED", "STOPPED"]:
            return False
        else:
            raise ValueError(f"Space configuration is wrong and in stage: {stage}")

    @classmethod
    def _is_space_stopped(cls, stage: SpaceStage) -> bool:
        """Check the current stage of the space runtime. Simplified to return True when it can be built."""
        if stage in ["RUNNING", "RUNNING_APP_STARTING", "RUNNING_BUILDING", "BUILDING", "APP_STARTING"]:
            return False
        elif stage in ["PAUSED", "STOPPED"]:
            return True
        else:
            raise ValueError(f"Space configuration is wrong and in stage: {stage}")

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
