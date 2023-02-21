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

import pytest
from argilla.utils.dependency import (
    require_version,
    requires_datasets,
    requires_sklearn,
    requires_spacy,
    requires_version,
)


class TestDependencyRequirements:
    @pytest.mark.parametrize(
        ("decorator", "package_name", "import_name", "version"),
        [
            (requires_datasets, "datasets", "datasets", ">1.17.0"),
            (requires_spacy, "spacy", "spacy", ""),
            (requires_sklearn, "scikit-learn", "sklearn", ""),
            (requires_version("faiss"), "faiss", "faiss", ""),
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
            requires_datasets,
            requires_spacy,
            requires_sklearn,
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
            require_version("datasets<1.0.0")
            return True

        # This method should fail, as our dependencies require a higher version of datasets
        with pytest.raises(
            ImportError,
            match=f"but found datasets==.*?You can install a supported version of 'datasets' with this command: `pip install -U datasets<1.0.0`",
        ):
            test_inner()

    def test_require_version_failures(self):
        # This operation is not supported
        with pytest.raises(ValueError):
            require_version("datasets~=1.0.0")

        # Add some unsupported tokens, e.g. " "
        with pytest.raises(ValueError):
            require_version(" datasets")

        # Add unsupported operation in second requirement version
        with pytest.raises(ValueError):
            require_version("datasets>1.0.0,~1.17.0")

    def test_special_python_case(self):
        require_version("python>3.6")

    def test_multiple_version_requirements(self):
        # This is equivalent to just datasets>1.17.0, but we expect it to work still
        require_version("datasets>1.0.0,>1.8.0,>1.17.0")
        # A more common example (designed not to break eventually):
        require_version("datasets>1.17.0,<1000.0.0")
