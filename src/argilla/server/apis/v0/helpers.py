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

from typing import Callable


def deprecate_endpoint(
    path: str, new_path: str, router_method: Callable, *args, **kwargs
):
    """
    Helper decorator to deprecate a `path` endpoint adding the `new_path` endpoint.

    Both `path` and `new_path` shares the same router method (get, post, patch,...) `router_method`
    """

    def decorator(func: Callable):
        kwargs.pop("path", None)
        kwargs.pop("deprecated", None)
        router_method(path=path, *args, deprecated=True, **kwargs)(func)
        router_method(path=new_path, *args, deprecated=False, **kwargs)(func)

    return decorator
