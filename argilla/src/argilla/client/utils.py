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

import functools
import warnings
from dataclasses import dataclass
from typing import Callable, List, TypeVar

try:
    from typing import ParamSpec
except ImportError:
    from typing_extensions import ParamSpec

from argilla.client.apis.status import Status
from argilla.client.sdk.users import api as users_api
from argilla.client.sdk.users.models import UserRole
from argilla.client.singleton import active_client

_P = ParamSpec("_P")
_R = TypeVar("_R")


def allowed_for_roles(roles: List[UserRole]) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    """Decorator function to check the role of the user calling the function, to restrict
    access to certain Argilla functions for users with certain roles. Note that the method
    inside the class to be decorated must contain the `_client` attribute with the active
    client at the class initialization time; otherwise, the current active client will be
    used instead, which in most of the cases won't match the client used during the class
    initialization.

    Args:
        roles: List of roles that are allowed to call the function.

    Example:
        >>> @allowed_for_roles(["owner"])
        >>> def delete_user(user_id: UUID) -> None:
        >>>     ...
    """

    def decorator(func: Callable[_P, _R]) -> Callable[_P, _R]:
        @functools.wraps(func)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            client = args[0]._client if hasattr(args[0], "_client") else active_client().http_client.httpx
            user = users_api.whoami_httpx(client).parsed
            if user.role not in roles:
                raise PermissionError(
                    f"User with role={user.role} is not allowed to call `{func.__name__}`."
                    f" Only users with role={roles} are allowed to call this function."
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator


@dataclass
class ServerInfo:
    url: str
    version: str
    elasticsearch_version: str


def server_info() -> ServerInfo:
    """Returns the information about the Argilla server that is currently active.

    Note that the connections to Argilla are established via `rg.init`, `argilla login` or
    setting the `ARGILLA_API_URL` and `ARGILLA_API_KEY` env variables.

    Returns:
        A `dataclass` with the following fields: `url`, `version` and `elasticsearch_version`.
    """
    # Filtering the warnings to avoid some redundant and unrelated warnings
    warnings.filterwarnings("ignore", category=UserWarning)

    try:
        client = active_client().client
        info = Status(client).get_status()
    except Exception as e:
        raise RuntimeError(
            "You must be logged in to Argilla to use this function."
            " Please call `rg.init`, run `argilla login` or set the `ARGILLA_API_URL` and `ARGILLA_API_KEY` env variables."
            " If you already did it, please check that the Argilla server is up and running."
        ) from e

    return ServerInfo(
        url=client.base_url,
        version=info.version,
        elasticsearch_version=(
            f"{info.elasticsearch.version.number} ({info.elasticsearch.version.distribution})"
            if info.elasticsearch.version.distribution
            else info.elasticsearch.version.number
        ),
    )
