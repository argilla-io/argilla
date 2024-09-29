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

import logging
from typing import Optional

import httpx
from argilla._exceptions._api import UnauthorizedError
from argilla._exceptions._client import ArgillaCredentialsError

from argilla._api import HTTPClientConfig, create_http_client
from argilla._api._datasets import DatasetsAPI
from argilla._api._fields import FieldsAPI
from argilla._api._metadata import MetadataAPI
from argilla._api._questions import QuestionsAPI
from argilla._api._records import RecordsAPI
from argilla._api._users import UsersAPI
from argilla._api._vectors import VectorsAPI
from argilla._api._workspaces import WorkspacesAPI
from argilla._exceptions import ArgillaError
from argilla._api._token import get_token

__all__ = ["APIClient"]


ARGILLA_API_URL = get_secret("ARGILLA_API_URL") or _DEFAULT_API_URL
ARGILLA_API_KEY = get_secret("ARGILLA_API_KEY")

DEFAULT_HTTP_CONFIG = HTTPClientConfig(api_url=ARGILLA_API_URL, api_key=ARGILLA_API_KEY)


class ArgillaAPI:
    """Argilla API access object."""

    def __init__(self, http_client: httpx.Client):
        self.http_client = http_client

        self.__workspaces = WorkspacesAPI(http_client=self.http_client)
        self.__datasets = DatasetsAPI(http_client=self.http_client)
        self.__users = UsersAPI(http_client=self.http_client)
        self.__fields = FieldsAPI(http_client=self.http_client)
        self.__questions = QuestionsAPI(http_client=self.http_client)
        self.__records = RecordsAPI(http_client=self.http_client)
        self.__vectors = VectorsAPI(http_client=self.http_client)
        self.__metadata = MetadataAPI(http_client=self.http_client)

    @property
    def workspaces(self) -> "WorkspacesAPI":
        return self.__workspaces

    @property
    def users(self) -> "UsersAPI":
        return self.__users

    @property
    def datasets(self) -> "DatasetsAPI":
        return self.__datasets

    @property
    def fields(self) -> "FieldsAPI":
        return self.__fields

    @property
    def questions(self) -> "QuestionsAPI":
        return self.__questions

    @property
    def records(self) -> "RecordsAPI":
        return self.__records

    @property
    def vectors(self) -> "VectorsAPI":
        return self.__vectors

    @property
    def metadata(self) -> "MetadataAPI":
        return self.__metadata


class APIClient:
    """Initialize the SDK with the given API URL and API key.
    This class is used to create an instance of the Argilla API client.

    Args:
        api_url (str, optional): The URL of the Argilla API. Defaults to the value of
            the `ARGILLA_API_URL` environment variable.
        api_key (str, optional): The API key to authenticate with the Argilla API. Defaults to
            the value of the `ARGILLA_API_KEY` environment variable.
        timeout (int, optional): The timeout in seconds for the HTTP requests. Defaults to 60.
        **http_client_args: Additional keyword arguments to pass to the httpx.Client instance.
            See https://www.python-httpx.org/api/#client for more information.
    """

    def __init__(
        self,
        api_url: Optional[str] = DEFAULT_HTTP_CONFIG.api_url,
        api_key: Optional[str] = DEFAULT_HTTP_CONFIG.api_key,
        timeout: int = DEFAULT_HTTP_CONFIG.timeout,
        retries: int = DEFAULT_HTTP_CONFIG.retries,
        **http_client_args,
    ):
        if not api_url:
            raise ArgillaError("Missing api_url. You must provide a valid API url")

        if not api_key:
            raise ArgillaError("Missing api_key. You must provide a valid API key.")

        self.api_url = api_url
        self.api_key = api_key

        http_client_args = http_client_args or {}
        http_client_args["timeout"] = timeout
        http_client_args["retries"] = retries

        self.http_client = create_http_client(
            api_url=self.api_url,  # type: ignore
            api_key=self.api_key,  # type: ignore
            **http_client_args,
        )

        self.api = ArgillaAPI(self.http_client)

        try:
            self._validate_connection()
        except UnauthorizedError as e:
            raise ArgillaCredentialsError() from e

    ##############################
    # Utility methods
    ##############################

    def log(self, message: str, level: int = logging.INFO) -> None:
        class_name = self.__class__.__name__
        message = f"{class_name}: {message}"
        logging.log(level=level, msg=message)

    def _validate_connection(self) -> None:
        user = self.api.users.get_me()
        message = f"Logged in as {user.username} with the role {user.role}"
        self.log(message=message, level=logging.INFO)
