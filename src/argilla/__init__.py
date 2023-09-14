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

try:
    from rich.traceback import install as _install_rich

    # Rely on `rich` for tracebacks
    _install_rich()
except ModuleNotFoundError:
    pass

__version__ = _version.version

if _TYPE_CHECKING:
    from argilla.client.api import (
        active_client,
        copy,
        delete,
        delete_records,
        get_workspace,
        init,
        list_datasets,
        list_workspaces,
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
        TextGenerationRecord,  # TODO Remove TextGenerationRecord
        TokenAttributions,
        TokenClassificationRecord,
    )
    from argilla.client.users import User
    from argilla.client.utils import server_info
    from argilla.client.workspaces import Workspace
    from argilla.datasets import (
        TextClassificationSettings,
        TokenClassificationSettings,
        configure_dataset,
        configure_dataset_settings,
        load_dataset_settings,
    )
    from argilla.feedback import (
        FeedbackDataset,
        FeedbackRecord,
        LabelQuestion,
        MultiLabelQuestion,
        RankingQuestion,
        RatingQuestion,
        ResponseSchema,
        TextField,
        TextQuestion,
        ValueSchema,
    )
    from argilla.listeners import Metrics, RGListenerContext, Search, listener
    from argilla.monitoring.model_monitor import monitor
    from argilla.server.server import app


# TODO: remove me
_import_structure = {
    "feedback": [
        "ArgillaTrainer",
        "LabelQuestionStrategy",
        "MultiLabelQuestionStrategy",
        "RatingQuestionStrategy",
        "FeedbackDataset",
        "FeedbackRecord",
        "LabelQuestion",
        "MultiLabelQuestion",
        "RatingQuestion",
        "RankingQuestion",
        "ResponseSchema",
        "TextField",
        "TextQuestion",
        "ValueSchema",
    ],
    "client.api": [
        "copy",
        "delete",
        "delete_records",
        "get_workspace",
        "init",
        "load",
        "log",
        "log_async",
        "set_workspace",
        "active_client",
        "list_datasets",
        "list_workspaces",
    ],
    "client.models": [
        "Text2TextRecord",
        "TextGenerationRecord",  # TODO Remove TextGenerationRecord
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
    "client.users": ["User"],
    "client.utils": ["server_info"],
    "client.workspaces": ["Workspace"],
    "monitoring.model_monitor": ["monitor"],
    "listeners.listener": [
        "listener",
        "RGListenerContext",
        "Search",
        "Metrics",
    ],
    "datasets": [
        "configure_dataset",
        "load_dataset_settings",
        "configure_dataset_settings",
        "TextClassificationSettings",
        "TokenClassificationSettings",
    ],
    "server.app": ["app"],
}

_sys.modules[__name__] = _LazyargillaModule(
    __name__,
    globals()["__file__"],
    _import_structure,
    module_spec=__spec__,
    extra_objects={"__version__": __version__},
)

_configure_logging()
