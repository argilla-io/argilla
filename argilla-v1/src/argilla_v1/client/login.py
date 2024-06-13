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

import os
from pathlib import Path
from typing import Dict, Optional

from argilla_v1.client.sdk.commons.errors import HttpResponseError, UnauthorizedApiError
from argilla_v1.client.singleton import init
from argilla_v1.pydantic_v1 import AnyHttpUrl, BaseModel

cache_dir_env = os.environ.get("ARGILLA_CACHE_DIR")
if cache_dir_env:
    ARGILLA_CACHE_DIR = Path(cache_dir_env)
else:
    ARGILLA_CACHE_DIR = Path.home() / ".cache" / "argilla"

ARGILLA_CREDENTIALS_FILE = ARGILLA_CACHE_DIR / "credentials.json"


class ArgillaCredentials(BaseModel):
    api_url: AnyHttpUrl
    api_key: str
    workspace: Optional[str] = None
    extra_headers: Optional[Dict[str, str]] = None

    def save(self) -> None:
        with open(ARGILLA_CREDENTIALS_FILE, "w") as f:
            f.write(self.json())

    @classmethod
    def load(cls) -> "ArgillaCredentials":
        if not cls.exists():
            raise FileNotFoundError(f"'{ARGILLA_CREDENTIALS_FILE}' does not exist.")

        with open(ARGILLA_CREDENTIALS_FILE, "r") as f:
            return cls.parse_raw(f.read())

    @classmethod
    def remove(cls) -> None:
        if not cls.exists():
            raise FileNotFoundError(f"'{ARGILLA_CREDENTIALS_FILE}' does not exist.")

        ARGILLA_CREDENTIALS_FILE.unlink()

    @classmethod
    def exists(cls) -> bool:
        return ARGILLA_CREDENTIALS_FILE.exists()


def login(
    api_url: str, api_key: str, workspace: Optional[str] = None, extra_headers: Optional[Dict[str, str]] = None
) -> None:
    """Login to an Argilla server using the provided URL and API key. If the login is successful, the credentials will
    be stored in the Argilla cache directory (`~/.cache/argilla/credentials.json`).

    Args:
        api_url: The URL of the Argilla server.
        api_key: The API key to use when communicating with the Argilla server.
        workspace: The default workspace where the datasets will be created.
        extra_headers: A dictionary containing extra headers that will be sent to the Argilla server.

    Raises:
        ValueError: If the login fails.
    """
    # Try to login to the server
    try:
        init(api_url=api_url, api_key=api_key, workspace=workspace, extra_headers=extra_headers)
    except HttpResponseError as e:
        raise ValueError(
            f"Could not reach '{api_url}', make sure that the Argilla Server is running and working as expected"
        ) from e
    except UnauthorizedApiError as e:
        raise ValueError(f"Could not login in '{api_url}' using provided credentials") from e

    if not ARGILLA_CACHE_DIR.exists():
        ARGILLA_CACHE_DIR.mkdir(parents=True)

    ArgillaCredentials(api_url=api_url, api_key=api_key, workspace=workspace, extra_headers=extra_headers).save()
