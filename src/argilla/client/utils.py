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
from typing import Callable, List, TypeVar

try:
    from typing import ParamSpec
except ImportError:
    from typing_extensions import ParamSpec

from argilla.client.api import active_client
from argilla.client.sdk.users import api as users_api
from argilla.client.sdk.users.models import UserRole

_P = ParamSpec("_P")
_R = TypeVar("_R")


def allowed_for_roles(roles: List[UserRole]) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    """Decorator function to check the role of the user calling the function, to restrict
    access to certain Argilla functions for users with certain roles.

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
            client = args[0].__client if hasattr(args[0], "__client") else active_client().http_client.httpx
            user = users_api.whoami_httpx(client).parsed
            if user.role not in roles:
                raise PermissionError(
                    f"User with role={user.role} is not allowed to call `{func.__name__}`."
                    f" Only users with role={roles} are allowed to call this function."
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator
