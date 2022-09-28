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

"""This file reflects the user facing API.
If you want to add something here, remember to add it as normal import in the _TYPE_CHECKING section (for IDEs),
as well as in the `_import_structure` dictionary.
"""

import sys as _sys
from typing import TYPE_CHECKING as _TYPE_CHECKING

from argilla.logging import configure_logging as _configure_logging

from . import _version
from .utils import LazyargillaModule as _LazyargillaModule

__version__ = _version.version

if _TYPE_CHECKING:
    from argilla.client.api import (
        copy,
        delete,
        delete_records,
        get_workspace,
        init,
        load,
        log,
        log_async,
        set_workspace,
    )
    from argilla.client.datasets import (
        DatasetForText2Text,
        DatasetForTextClassification,
        DatasetForTokenClassification,
        read_datasets,
        read_pandas,
    )
    from argilla.client.models import (
        Text2TextRecord,
        TextClassificationRecord,
        TokenAttributions,
        TokenClassificationRecord,
    )
    from argilla.datasets import (
        TextClassificationSettings,
        TokenClassificationSettings,
        configure_dataset,
    )
    from argilla.listeners import Metrics, RBListenerContext, Search, listener
    from argilla.monitoring.model_monitor import monitor
    from argilla.server.server import app

# TODO: remove me
_import_structure = {
    "client.api": [
        "copy",
        "delete",
        "get_workspace",
        "init",
        "load",
        "delete_records",
        "log",
        "log_async",
        "set_workspace",
    ],
    "client.models": [
        "Text2TextRecord",
        "TextClassificationRecord",
        "TokenClassificationRecord",
        "TokenAttributions",
    ],
    "client.datasets": [
        "DatasetForText2Text",
        "DatasetForTextClassification",
        "DatasetForTokenClassification",
        "read_datasets",
        "read_pandas",
    ],
    "monitoring.model_monitor": ["monitor"],
    "listeners.listener": ["listener", "RBListenerContext", "Search", "Metrics"],
    "datasets": [
        "configure_dataset",
        "TextClassificationSettings",
        "TokenClassificationSettings",
    ],
    "server.app": ["app"],
}

# can be removed in a future version
_deprecated_import_structure = {
    "client.models": ["Record", "BulkResponse"],
    "client.datasets": ["Dataset"],
    "_constants": ["DEFAULT_API_KEY"],
}

_sys.modules[__name__] = _LazyargillaModule(
    __name__,
    globals()["__file__"],
    _import_structure,
    deprecated_import_structure=_deprecated_import_structure,
    module_spec=__spec__,
    extra_objects={"__version__": __version__},
)

_configure_logging()
