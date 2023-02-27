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
import operator
import re
import sys
from typing import Optional

from packaging import version

# This file was adapted from Hugging Face's wonderful transformers module

# The package importlib_metadata is in a different place, depending on the python version.
if sys.version_info < (3, 8):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata

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
    func_name: Optional[str],
):
    if got_version is None or want_version is None:
        raise ValueError(
            f"Unable to compare versions for {requirement}: need={want_version} found={got_version}. This is unusual. Consider"
            f" reinstalling {package}."
        )
    if not ops[op](version.parse(got_version), version.parse(want_version)):
        raise ImportError(
            f"{requirement} must be installed{f' to use `{func_name}`' if func_name else ''}, but found {package}=={got_version}."
            f" You can install a supported version of '{package}' with this command: `pip install -U {requirement}`"
        )


def require_version(requirement: str, func_name: Optional[str] = None) -> None:
    """
    Perform a runtime check of the dependency versions, using the exact same syntax used by pip.
    The installed module version comes from the *site-packages* dir via *importlib_metadata*.

    Args:
        requirement (`str`): pip style definition, e.g.,  "tokenizers==0.9.4", "tqdm>=4.27", "numpy"
        func_name (`str`, *optional*): what suggestion to print in case of requirements not being met

    Example:
    ```python
    require_version("pandas>1.1.2")
    require_version("datasets>1.17.0", "from_datasets")
    ```
    """

    # non-versioned check
    if re.match(r"^[\w_\-\d]+$", requirement):
        package, op, want_version = requirement, None, None
    else:
        match = re.findall(r"^([^!=<>\s]+)([\s!=<>]{1,2}.+)", requirement)
        if not match:
            raise ValueError(
                "requirement needs to be in the pip package format, .e.g., package_a==1.23, or package_b>=1.23, but"
                f" got {requirement!r}."
            )
        package, want_full = match[0]
        want_range = want_full.split(",")  # there could be multiple requirements
        wanted = {}
        for w in want_range:
            match = re.findall(r"^([\s!=<>]{1,2})(.+)", w)
            if not match:
                raise ValueError(
                    "requirement needs to be in the pip package format, .e.g., package_a==1.23, or package_b>=1.23,"
                    f" but got {requirement!r}."
                )
            op, want_version = match[0]
            wanted[op] = want_version
            if op not in ops:
                raise ValueError(f"{requirement}: need one of {list(ops.keys())}, but got {op!r}.")

    # special case
    if package == "python":
        got_version = ".".join([str(x) for x in sys.version_info[:3]])
        for op, want_version in wanted.items():
            _compare_versions(op, got_version, want_version, requirement, package, func_name=func_name)
        return

    # check if any version is installed
    try:
        got_version = importlib_metadata.version(package)
    except importlib_metadata.PackageNotFoundError:
        raise ModuleNotFoundError(
            f"'{package}' must be installed{f' to use `{func_name}`' if func_name else ''}! You can"
            f" install '{package}' with this command: `pip install {requirement}`"
        )

    # check that the right version is installed if version number or a range was provided
    if want_version is not None:
        for op, want_version in wanted.items():
            _compare_versions(op, got_version, want_version, requirement, package, func_name=func_name)


def requires_decorator(requirement, func):
    @functools.wraps(func)
    def check_if_installed(*args, **kwargs):
        require_version(requirement, func.__name__)
        return func(*args, **kwargs)

    return check_if_installed


def requires_version(requirement):
    """Decorator variant of `require_version`.
    Perform a runtime check of the dependency versions, using the exact same syntax used by pip.
    The installed module version comes from the *site-packages* dir via *importlib_metadata*.

    Args:
        requirement (`str`): pip style definition, e.g.,  "tokenizers==0.9.4", "tqdm>=4.27", "numpy"

    Example:
    ```python
    @requires_version("datasets>1.17.0")
    def from_datasets(self, ...):
        ...
    ```
    """
    return functools.partial(requires_decorator, requirement)


__all__ = ["requires_version", "require_version"]
