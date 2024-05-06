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

from typing import Any, Dict, Optional

from argilla.client.client import Argilla


class ArgillaSingleton:
    """The active argilla singleton instance"""

    _INSTANCE: Optional[Argilla] = None

    @classmethod
    def get(cls) -> Argilla:
        if cls._INSTANCE is None:
            return cls.init()
        return cls._INSTANCE

    @classmethod
    def clear(cls) -> None:
        cls._INSTANCE = None

    @classmethod
    def init(
        cls,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        workspace: Optional[str] = None,
        timeout: int = 60,
        extra_headers: Optional[Dict[str, str]] = None,
        httpx_extra_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Argilla:
        cls._INSTANCE = None

        cls._INSTANCE = Argilla(
            api_url=api_url,
            api_key=api_key,
            timeout=timeout,
            workspace=workspace,
            extra_headers=extra_headers,
            httpx_extra_kwargs=httpx_extra_kwargs,
        )

        return cls._INSTANCE


def init(
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
    workspace: Optional[str] = None,
    timeout: int = 60,
    extra_headers: Optional[Dict[str, str]] = None,
    httpx_extra_kwargs: Optional[Dict[str, Any]] = None,
) -> None:
    """Init the Python client.

    If this function is called with `api_url=None` and `api_key=None` and no values have been set for the environment
    variables `ARGILLA_API_URL` and `ARGILLA_API_KEY`, then the local credentials stored by a previous call to `argilla
    login` command will be used. If local credentials are not found, then `api_url` and `api_key` will fallback to the
    default values.

    Args:
        api_url: Address of the REST API. If `None` (default) and the env variable ``ARGILLA_API_URL`` is not set,
            it will default to `http://localhost:6900`.
        api_key: Authentication key for the REST API. If `None` (default) and the env variable ``ARGILLA_API_KEY``
            is not set, it will default to `argilla.apikey`.
        workspace: The workspace to which records will be logged/loaded. If `None` (default) and the
            env variable ``ARGILLA_WORKSPACE`` is not set, it will default to the private user workspace.
        timeout: Wait `timeout` seconds for the connection to timeout. Default: 60.
        extra_headers: Extra HTTP headers sent to the server. You can use this to customize
            the headers of argilla client requests, like additional security restrictions. Default: `None`.
        httpx_extra_kwargs: Extra kwargs passed to the `httpx.Client` constructor. For more information about the
            available arguments, see https://www.python-httpx.org/api/#client. Defaults to `None`.

    Examples:
        >>> import argilla as rg
        >>>
        >>> rg.init(api_url="http://localhost:9090", api_key="4AkeAPIk3Y")
        >>> # Customizing request headers
        >>> headers = {"X-Client-id":"id","X-Secret":"secret"}
        >>> rg.init(api_url="http://localhost:9090", api_key="4AkeAPIk3Y", extra_headers=headers)
    """
    ArgillaSingleton.init(
        api_url=api_url,
        api_key=api_key,
        workspace=workspace,
        timeout=timeout,
        extra_headers=extra_headers,
        httpx_extra_kwargs=httpx_extra_kwargs,
    )


def active_client() -> Argilla:
    """Returns the active argilla client.

    If Active client is None, initialize a default one.
    """
    return ArgillaSingleton.get()


active_api = active_client  # backward compatibility
