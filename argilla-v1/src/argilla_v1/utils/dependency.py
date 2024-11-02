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
import importlib.metadata
import importlib.util
import operator
import re
import sys
from typing import Callable, Dict, List, Optional, TypeVar, Union

from packaging import version

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

ops = {
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
    ">=": operator.ge,
    ">": operator.gt,
}


def _compare_versions(
    op: str,
    got_version: Optional[str],
    want_version: Optional[str],
    requirement: str,
    package: str,
    fn_name: Optional[str],
):
    if got_version is None or want_version is None:
        raise ValueError(
            f"Unable to compare versions for {requirement}: need={want_version} found={got_version}. This is unusual. Consider"
            f" reinstalling {package}."
        )
    if not ops[op](version.parse(got_version), version.parse(want_version)):
        raise ImportError(
            f"{requirement} must be installed{f' to use `{fn_name}`' if fn_name else ''}, but found {package}=={got_version}."
            f" You can install a supported version of '{package}' with this command: `pip install -U {requirement}`"
        )


def require_dependencies(requirements: Union[str, List[str]], fn_name: Optional[str] = None) -> None:
    """
    Perform a runtime check of the dependency versions, using the exact same syntax used by pip.
    The installed module version comes from the *site-packages* dir via *importlib.metadata*.

    Args:
        requirements: pip style definition of dependencies, e.g. "tokenizers==0.9.4", "tqdm>=4.27", "numpy". Can either be a single dependency or a list of dependencies.
        fn_name: what suggestion to print in case of requirements not being met

    Example:
    ```python
    require_dependencies("pandas>1.1.2")
    require_dependencies("datasets>1.17.0", "from_datasets")
    require_dependencies(["pandas>1.1.2", "datasets>1.17.0"])
    ```
    """

    if isinstance(requirements, list):
        if len(requirements) == 0:
            raise ValueError("requirements cannot be an empty list.")
        for requirement in requirements:
            require_dependencies(requirement, fn_name=fn_name)
        return

    # non-versioned check
    if re.match(r"^[\w_\-\d]+$", requirements):
        package, op, want_version = requirements, None, None
    else:
        match = re.findall(r"^([^!=<>\s]+)([\s!=<>]{1,2}.+)", requirements)
        if not match:
            raise ValueError(
                "requirement needs to be in the pip package format, .e.g., package_a==1.23, or package_b>=1.23, but"
                f" got {requirements!r}."
            )
        package, want_full = match[0]
        want_range = want_full.split(",")  # there could be multiple requirements
        wanted = {}
        for w in want_range:
            match = re.findall(r"^([\s!=<>]{1,2})(.+)", w)
            if not match:
                raise ValueError(
                    "requirement needs to be in the pip package format, .e.g., package_a==1.23, or package_b>=1.23,"
                    f" but got {requirements!r}."
                )
            op, want_version = match[0]
            wanted[op] = want_version
            if op not in ops:
                raise ValueError(f"{requirements}: need one of {list(ops.keys())}, but got {op!r}.")

    # special case
    if package == "python":
        got_version = ".".join([str(x) for x in sys.version_info[:3]])
        for op, want_version in wanted.items():
            _compare_versions(op, got_version, want_version, requirements, package, fn_name=fn_name)
        return

    # check if any version is installed
    try:
        got_version = importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        raise ModuleNotFoundError(
            f"'{package}' must be installed{f' to use `{fn_name}`' if fn_name else ''}! You can"
            f" install '{package}' with this command: `pip install {requirements}`"
        )

    # check that the right version is installed if version number or a range was provided
    if want_version is not None:
        for op, want_version in wanted.items():
            _compare_versions(op, got_version, want_version, requirements, package, fn_name=fn_name)


_P = ParamSpec("_P")
_R = TypeVar("_R")


def requires_dependencies(requirements: Union[str, List[str]]) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    """Decorator variant of `require_dependencies`.
    Perform a runtime check of the dependency versions, using the exact same syntax used by pip.
    The installed module version comes from the *site-packages* dir via *importlib.metadata*.

    Args:
        requirements: pip style definition, e.g.,  "tokenizers==0.9.4", "tqdm>=4.27", "numpy"

    Example:
    ```python
    @requires_dependencies("datasets>1.17.0")
    def from_datasets(self, ...):
        ...
    ```
    """

    def decorator(func: Callable[_P, _R]) -> Callable[_P, _R]:
        @functools.wraps(func)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            require_dependencies(requirements, func.__name__)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def _group_by_extra(dependencies: List[str]) -> Dict[str, List[str]]:
    grouped = {"base": []}

    for dep in dependencies:
        # Extract the name of the dependency by splitting at the first space or '['
        dep_name = dep.split()[0].split("[")[0]

        if "; extra ==" in dep:
            # Split the dependency and the extra value
            _, extra_value = dep.split(" ; extra ==")
            extra_value = extra_value.strip().strip("'")

            # Append the dependency name to the right extra group
            if extra_value not in grouped:
                grouped[extra_value] = []
            grouped[extra_value].append(dep_name)
        else:
            grouped["base"].append(dep_name)

    return grouped


def is_package_with_extras_installed(name: str, extras: List[str]) -> bool:
    """Checks the given extras of a package are installed.

    Args:
        name: the name of the package to check.
        extras: the extras to check.

    Returns:
        `True`, if the extras are installed, `False` otherwise.
    """
    try:
        requirements = importlib.metadata.requires(name)
    except importlib.metadata.PackageNotFoundError:
        return False

    grouped_requirements = _group_by_extra(requirements)
    available_extras = list(grouped_requirements.keys())
    for extra in extras:
        if extra not in available_extras:
            raise KeyError(f"'{name}' package does not provide '{extra}' extra")
        for requirement in grouped_requirements[extra]:
            try:
                importlib.metadata.version(requirement)
            except importlib.metadata.PackageNotFoundError:
                return False

    return True


__all__ = ["requires_dependencies", "require_dependencies", "is_package_with_extras_installed"]
