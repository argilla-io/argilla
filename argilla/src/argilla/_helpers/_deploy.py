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

import os
import time
from typing import TYPE_CHECKING, Optional, Union

from huggingface_hub import HfApi, SpaceRuntime, get_token, login, notebook_login

if TYPE_CHECKING:
    from huggingface_hub.hf_api import RepoUrl, SpaceHardware, SpaceStorage  # noqa

SLEEP_TIME = 10
FROM_REPO_ID = "argilla/argilla-template-space"
FROM_REPO_ID_OAUTH = "argilla/argilla-template-space-with-oauth"


class DeploymentMixin:
    def _is_interactive(self):
        raise NotImplementedError("Should be implemented within LoggingMixin")

    def _log_message(self):
        raise NotImplementedError("Should be implemented within LoggingMixin")

    def _acquire_hf_token(self, token: Union[str, None]) -> str:
        """Obtain the Hugging Face authentication token to deploy a space and authenticate."""
        if token is None:
            token = get_token()
        if token is None:
            token = os.getenv("HF_TOKEN")
        if token is None:
            if self._is_interactive():
                notebook_login()
            else:
                login()
            token = get_token()
        return token

    def _check_if_runtime_can_be_build(runtime: SpaceRuntime):
        """Check the current stage of the space runtime. Simplified to return True when being build."""
        if runtime.stage.value in ["RUNNING"]:
            return False
        elif runtime.stage.value in ["RUNNING_BUILDING", "BUILDING", "PAUSED", "STOPPED"]:
            return True
        else:
            raise ValueError(f"Space configuration is wrong and in state: {runtime.stage.value}")

    @classmethod
    def deploy_on_spaces(
        cls,
        repo_id: str,
        token: str = None,
        space_storage: Optional[Union[str, SpaceStorage, None]] = None,
        space_hardware: Optional[Union[str, SpaceHardware]] = "cpu-basic",
        private: Optional[Union[bool, None]] = False,
        admin_username: Optional[Union[str, None]] = "admin",
        admin_password: Optional[Union[str, None]] = "12345678",
        admin_apikey: Optional[Union[str, None]] = "admin.apikey",
        owner_username: Optional[Union[str, None]] = "owner",
        owner_password: Optional[Union[str, None]] = "12345678",
        owner_apikey: Optional[Union[str, None]] = "owener.apikey",
        annotator_username: Optional[Union[str, None]] = "annotator",
        annotator_password: Optional[Union[str, None]] = "12345678",
        argilla_workspace: Optional[Union[str, None]] = None,
        oauth_huggingface_client_id: Optional[Union[str, None]] = None,
        oauth_huggingface_client_secret: Optional[Union[str, None]] = None,
    ) -> "RepoUrl":
        """
        Deploys Argilla on Hugging Face Spaces.
        For a full guide check our docs.

        Args:
            repo_id (str): The ID of the repository where Argilla will be deployed.
            token (Optional[Union[str, SpaceStorage, None]]): The Hugging Face authentication token. Defaults to None.
            space_storage (Optional[Union[str, SpaceStorage, None]]): The storage size for the space. Defaults to None without persistant storage.
            space_hardware (Optional[Union[str, SpaceStorage, None]]): The hardware configuration for the space. Defaults to "cpu-basic" with downtime after 48 hours of inactivity.
            private (Optional[Union[bool, None]]): Whether the space should be private. Defaults to False.
            admin_username (Optional[Union[str, None]]): The admin username for the space. Defaults to "admin".
            admin_password (Optional[Union[str, None]]): The admin password for the space. Defaults to "12345678".
            admin_apikey (Optional[Union[str, None]]): The admin API key for the space. Defaults to "admin.apikey".
            owner_username (Optional[Union[str, None]]): The owner username for the space. Defaults to "owner".
            owner_password (Optional[Union[str, None]]): The owner password for the space. Defaults to "12345678".
            owner_apikey (Optional[Union[str, None]]): The owner API key for the space. Defaults to "owner.apikey".
            annotator_username (Optional[Union[str, None]]): The annotator username for the space. Defaults to "annotator".
            annotator_password (Optional[Union[str, None]]): The annotator password for the space. Defaults to "12345678".
            argilla_workspace (Optional[Union[str, None]]): The Argilla workspace for the space. Defaults to None.
            oauth_huggingface_client_id (Optional[Union[str, None]]): The OAuth client ID for Hugging Face. Defaults to None.
            oauth_huggingface_client_secret (Optional[Union[str, None]]): The OAuth client secret for Hugging Face. Defaults to None.

        Returns:
            RepoUrl: The URL of the created space.

        Example:
            import argilla as rg
            url = rg.Argilla.deploy_on_spaces(
                repo_id="my-org/my-space",
                token="hf_ABC123",
                space_storage="10GB",
                space_hardware="gpu",
                private=True,
                admin_username="admin",
                admin_password="password123",
                owner_username="owner",
                owner_password="ownerpass",
                annotator_username="annotator",
                annotator_password="annotatorpass",
                argilla_workspace="workspace",
                oauth_huggingface_client_id="client_id",
                oauth_huggingface_client_secret="client_secret"
            )
        """
        token = cls._acquire_hf_token(token=token)
        api = HfApi(token=token)

        from_id = (
            FROM_REPO_ID_OAUTH if (oauth_huggingface_client_id and oauth_huggingface_client_secret) else FROM_REPO_ID
        )
        secrets = [
            {"ADMIN_USERNAME": admin_username},
            {"ADMIN_PASSWORD": admin_password},
            {"ADMIN_API_KEY": admin_apikey},
            {"OWNER_USERNAME": owner_username},
            {"OWNER_PASSWORD": owner_password},
            {"OWNER_API_KEY": owner_apikey},
            {"ANNOTATOR_USERNAME": annotator_username},
            {"ANNOTATOR_PASSWORD": annotator_password},
            {"ARGILLA_WORKSPACE": argilla_workspace},
            {"OAUTH2_HUGGINGFACE_CLIENT_ID": oauth_huggingface_client_id},
            {"OAUTH2_HUGGINGFACE_CLIENT_SECRET": oauth_huggingface_client_secret},
        ]
        secrets = [secret for secret in secrets if list(secret.values())[0] is not None]
        # restart space if needed and potentially update secrets
        if api.repo_exists(repo_id=repo_id, repo_type="space", token=token):
            if cls._check_if_runtime_can_be_build(api.get_space_runtime(repo_id=repo_id, token=token)):
                api.restart_space(repo_id=repo_id, token=token)
            for key, value in secrets.items():
                api.add_space_secret(repo_id=repo_id, key=key, value=value, token=token)

        repo_url: RepoUrl = api.duplicate_space(
            from_id=from_id,
            to_id=repo_id,
            private=private,
            token=token,
            exist_ok=True,
            hardware=space_hardware,
            storage=space_storage,
            secrets=secrets,
        )

        api_url = repo_url.url
        cls._log_message(message=f"Argilla is being deployed at: {api_url}")
        while cls._check_if_runtime_can_be_build(api.get_space_runtime(repo_id=repo_id)):
            time.sleep(SLEEP_TIME)
            cls._log_message(message=f"Waiting {SLEEP_TIME} seconds.")

        headers = {}
        if private:
            headers["Authorization"] = f"Bearer {token}"

        return cls(api_url=api_url, api_key=owner_apikey, headers=headers)
