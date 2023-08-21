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

from pathlib import Path
from typing import Dict, Optional

from argilla.client.api import init
from argilla.client.sdk.commons.errors import HttpResponseError, UnauthorizedApiError
from argilla.client.login import ArgillaCredentials

ARGILLA_CACHE_DIR = Path.home() / ".cache" / "argilla"
ARGILLA_CREDENTIALS_FILE = ARGILLA_CACHE_DIR / "credentials.json"


def logout(
    api_url: str, api_key: str, workspace: Optional[str] = None, extra_headers: Optional[Dict[str, str]] = None
) -> None:
    """Logout from Argilla server using the provided URL and API key. If the logout is successful, the credentials will
    be removed from the Argilla cache directory (`~/.cache/argilla/credentials.json`).

    Args:
        api_url: The URL of the Argilla server.
        api_key: The API key to use when communicating with the Argilla server.
        workspace: The default workspace where the datasets will be created.
        extra_headers: A dictionary containing extra headers that will be sent to the Argilla server.

    Raises:
        ValueError: If the logout fails.
    """
    # Try to logout from the server
    try:
        init(api_url=api_url, api_key=api_key,
             workspace=workspace, extra_headers=extra_headers)
        ArgillaCredentials(api_url=api_url, api_key=api_key,
                           workspace=workspace, extra_headers=extra_headers).remove()
    except HttpResponseError as e:
        raise ValueError(
            f"Could not reach '{api_url}', make sure that the Argilla Server is running and working as expected"
        ) from e
    except UnauthorizedApiError as e:
        raise ValueError(
            f"Could not logout from '{api_url}' using provided credentials") from e
    except FileNotFoundError as e:
        raise ValueError(
            f"User is not logged in on Argilla Server at '{api_url}' ") from e
