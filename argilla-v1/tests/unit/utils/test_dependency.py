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

import importlib
import sys
from typing import Any, List

import pytest
from argilla_v1.utils.dependency import is_package_with_extras_installed, require_dependencies, requires_dependencies


class TestDependencyRequirements:
    @pytest.mark.parametrize(
        ("decorator", "package_name", "import_name", "version"),
        [
            (requires_dependencies("datasets>1.17.0"), "datasets", "datasets", ">1.17.0"),
            (requires_dependencies("spacy"), "spacy", "spacy", ""),
            (requires_dependencies("scikit-learn"), "scikit-learn", "sklearn", ""),
            (requires_dependencies("faiss"), "faiss", "faiss", ""),
        ],
    )
    def test_missing_dependency_decorator(
        self, monkeypatch: pytest.MonkeyPatch, decorator, package_name: str, import_name: str, version: str
    ):
        monkeypatch.setitem(sys.modules, import_name, None)
        monkeypatch.setattr(sys, "meta_path", [], raising=False)

        # Ensure that the package indeed cannot be imported due to the monkeypatch
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(import_name)

        @decorator
        def test_inner():
            pass

        requirement = package_name + version
        # Verify that the decorator does its work and shows the desired output with `pip install ...`
        with pytest.raises(
            ModuleNotFoundError,
            match=f"'{package_name}' must be installed to use `test_inner`!.*?`pip install {requirement}`",
        ):
            test_inner()

    @pytest.mark.parametrize(
        ("decorator"),
        [
            requires_dependencies("datasets>1.17.0"),
            requires_dependencies("spacy"),
            requires_dependencies("scikit-learn"),
            requires_dependencies(["datasets>1.17.0", "spacy", "scikit-learn"]),
        ],
    )
    def test_installed_dependency_decorator(self, decorator):
        # Ensure that the decorated function can be called just fine if the dependencies are installed,
        # which they should be for these tests

        @decorator
        def test_inner():
            return True

        assert test_inner()

    def test_installed_dependency_but_incorrect_version(self):
        def test_inner():
            require_dependencies("datasets<1.0.0")
            return True

        # This method should fail, as our dependencies require a higher version of datasets
        with pytest.raises(
            ImportError,
            match="but found datasets==.*?You can install a supported version of 'datasets' with this command: `pip install -U datasets<1.0.0`",
        ):
            test_inner()

    def test_require_version_failures(self):
        # This operation is not supported
        with pytest.raises(ValueError):
            require_dependencies("datasets~=1.0.0")

        # Add some unsupported tokens, e.g. " "
        with pytest.raises(ValueError):
            require_dependencies(" datasets")

        # Add unsupported operation in second requirement version
        with pytest.raises(ValueError):
            require_dependencies("datasets>1.0.0,~1.17.0")

    def test_special_python_case(self):
        require_dependencies("python>3.6")

    def test_multiple_version_requirements(self):
        # This is equivalent to just datasets>1.17.0, but we expect it to work still
        require_dependencies("datasets>1.0.0,>1.8.0,>1.17.0")
        # A more common example (designed not to break eventually):
        require_dependencies("datasets>1.17.0,<1000.0.0")

    def test_list_of_dependencies(self):
        require_dependencies(["datasets>1.17.0", "spacy", "scikit-learn"])

    def test_list_without_dependencies(self):
        with pytest.raises(ValueError, match="requirements cannot be an empty list."):
            require_dependencies([])


@pytest.mark.parametrize(
    "args, expected", [(["argilla_v1", ["server"]], True), (["invented_package", ["invented"]], False)]
)
def test_is_package_with_extras_installed(args: List[Any], expected: bool) -> None:
    assert is_package_with_extras_installed(*args) == expected


def test_is_package_with_extras_installed_raises_key_error() -> None:
    with pytest.raises(KeyError, match="'argilla_v1' package does not provide 'invented' extra"):
        is_package_with_extras_installed("argilla_v1", ["invented"])
