#  coding=utf-8
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
import pytest
from argilla_v1.utils import LazyargillaModule


def test_lazy_argilla_module(monkeypatch):
    def mock_import_module(name, package):
        return name

    monkeypatch.setattr("importlib.import_module", mock_import_module)

    lazy_module = LazyargillaModule(
        name="rb_mock",
        module_file="rb_mock_file",
        import_structure={"mock_module": ["title"]},
        extra_objects={"string": str},
        deprecated_import_structure={"dep_mock_module": ["upper"]},
    )
    assert all(attr in dir(lazy_module) for attr in ["mock_module", "title"])
    assert lazy_module.mock_module == ".mock_module"
    assert lazy_module.title() == ".mock_module".title()
    assert lazy_module.string == str

    with pytest.warns(FutureWarning, match="Importing 'dep_mock_module' from the argilla namespace"):
        assert lazy_module.dep_mock_module == ".dep_mock_module"

    with pytest.warns(FutureWarning, match="Importing 'upper' from the argilla namespace"):
        assert lazy_module.upper() == ".dep_mock_module".upper()

    with pytest.raises(AttributeError):
        lazy_module.not_available_mock

    assert lazy_module.__reduce__()


def test_lazy_argilla_module_import_error(monkeypatch):
    def mock_import_module(*args, **kwargs):
        raise Exception

    monkeypatch.setattr("importlib.import_module", mock_import_module)

    lazy_module = LazyargillaModule(
        name="rb_mock",
        module_file=__file__,
        import_structure={"mock_module": ["title"]},
    )

    with pytest.raises(RuntimeError, match="Failed to import rb_mock.mock_module"):
        lazy_module.mock_module
