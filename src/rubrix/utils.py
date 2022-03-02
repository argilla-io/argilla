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
import importlib
import os
import warnings
from itertools import chain
from types import ModuleType
from typing import Any, Optional


class _LazyRubrixModule(ModuleType):
    """Module class that surfaces all objects but only performs associated imports when the objects are requested.

    Shamelessly copied and adapted from the Hugging Face transformers implementation.
    """

    def __init__(
        self,
        name,
        module_file,
        import_structure,
        deprecated_import_structure=None,
        module_spec=None,
        extra_objects=None,
    ):
        super().__init__(name)
        self._modules = set(import_structure.keys())
        self._class_to_module = {}
        for key, values in import_structure.items():
            for value in values:
                self._class_to_module[value] = key
        # Needed for autocompletion in an IDE
        self.__all__ = list(import_structure.keys()) + list(
            chain(*import_structure.values())
        )
        self.__file__ = module_file
        self.__spec__ = module_spec
        self.__path__ = [os.path.dirname(module_file)]
        self._objects = {} if extra_objects is None else extra_objects
        self._name = name
        self._import_structure = import_structure

        # deprecated stuff
        deprecated_import_structure = deprecated_import_structure or {}
        self._deprecated_modules = set(deprecated_import_structure.keys())
        self._deprecated_class_to_module = {}
        for key, values in deprecated_import_structure.items():
            for value in values:
                self._deprecated_class_to_module[value] = key

    # Needed for autocompletion in an IDE
    def __dir__(self):
        result = super().__dir__()
        # The elements of self.__all__ that are submodules may or may not be in the dir already, depending on whether
        # they have been accessed or not. So we only add the elements of self.__all__ that are not already in the dir.
        for attr in self.__all__:
            if attr not in result:
                result.append(attr)
        return result

    def __getattr__(self, name: str) -> Any:
        if name in self._objects:
            return self._objects[name]
        if name in self._modules:
            value = self._get_module(name)
        elif name in self._class_to_module.keys():
            module = self._get_module(self._class_to_module[name])
            value = getattr(module, name)
        elif name in self._deprecated_modules:
            value = self._get_module(name, deprecated=True)
        elif name in self._deprecated_class_to_module.keys():
            module = self._get_module(
                self._deprecated_class_to_module[name], deprecated=True, class_name=name
            )
            value = getattr(module, name)
        else:
            raise AttributeError(f"module {self.__name__} has no attribute {name}")

        setattr(self, name, value)
        return value

    def _get_module(
        self,
        module_name: str,
        deprecated: bool = False,
        class_name: Optional[str] = None,
    ):
        if deprecated:
            warnings.warn(
                f"Importing '{class_name or module_name}' from the rubrix namespace (that is "
                f"`rubrix.{class_name or module_name}`) is deprecated and will not work in a future version. "
                f"Make sure you update your code accordingly.",
                category=FutureWarning,
            )

        try:
            return importlib.import_module("." + module_name, self.__name__)
        except Exception as e:
            raise RuntimeError(
                f"Failed to import {self.__name__}.{module_name} because of the following error "
                f"(look up to see its traceback):\n{e}"
            ) from e

    def __reduce__(self):
        return self.__class__, (self._name, self.__file__, self._import_structure)
