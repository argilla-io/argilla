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

import asyncio
import sys
from functools import wraps
from typing import Any, Callable, Coroutine, TypeVar

import typer

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec


P = ParamSpec("P")
R = TypeVar("R")


# https://github.com/tiangolo/typer/issues/88#issuecomment-1613013597
class AsyncTyper(typer.Typer):
    def command(
        self, *args: Any, **kwargs: Any
    ) -> Callable[[Callable[P, Coroutine[Any, Any, R]]], Callable[P, Coroutine[Any, Any, R]]]:
        super_command = super().command(*args, **kwargs)

        def decorator(func: Callable[P, Coroutine[Any, Any, R]]) -> Callable[P, Coroutine[Any, Any, R]]:
            @wraps(func)
            def sync_func(*_args: P.args, **_kwargs: P.kwargs) -> R:
                return asyncio.run(func(*_args, **_kwargs))

            if asyncio.iscoroutinefunction(func):
                super_command(sync_func)
            else:
                super_command(func)

            return func

        return decorator


def run(function: Callable[..., Coroutine[Any, Any, Any]]) -> None:
    app = AsyncTyper(add_completion=False)
    app.command()(function)
    app()
