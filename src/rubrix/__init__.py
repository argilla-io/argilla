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

"""This file reflects the user facing API."""

from typing import TYPE_CHECKING

from rubrix.logging import configure_logging

from . import _version

__version__ = _version.version

if TYPE_CHECKING:
    from rubrix.client.api import (
        copy,
        delete,
        get_workspace,
        init,
        load,
        log,
        set_workspace,
    )
    from rubrix.client.datasets import (
        DatasetForText2Text,
        DatasetForTextClassification,
        DatasetForTokenClassification,
        read_datasets,
        read_pandas,
    )
    from rubrix.client.models import (
        Text2TextRecord,
        TextClassificationRecord,
        TokenAttributions,
        TokenClassificationRecord,
    )
    from rubrix.monitoring.model_monitor import monitor
    from rubrix.server.server import app

# try:
#     from rubrix.server.server import app
# except ModuleNotFoundError as ex:
#     _module_name = ex.name
#
#     def fallback_app(*args, **kwargs):
#         raise RuntimeError(
#             "\n"
#             f"Cannot start rubrix server. Some dependencies was not found:[{_module_name}].\n"
#             "Please, install missing modules or reinstall rubrix with server extra deps:\n"
#             "pip install rubrix[server]"
#         )
#
#     app = fallback_app

_import_structure = {
    "client.models": ["TextClassificationRecord"],
    "server.server": ["app"],
}
_deprecated_import_structure = {"client.models": ["Record"]}

import sys as _sys

from .utils import _LazyRubrixModule

_sys.modules[__name__] = _LazyRubrixModule(
    __name__,
    globals()["__file__"],
    _import_structure,
    deprecated_import_structure=_deprecated_import_structure,
    module_spec=__spec__,
    extra_objects={"__version__": __version__},
)

configure_logging()