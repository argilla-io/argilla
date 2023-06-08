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
import warnings
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

# TODO: Remove this warning once https://github.com/argilla-io/argilla/issues/2902 is tackled
if _sys.version_info < (3, 8):
    warnings.warn(
        message="Python 3.7 is coming to its end-of-life and will be no longer supported in the upcoming release of Argilla. "
        "To ensure compatibility and uninterrupted service, we kindly request that you migrate to Argilla with"
        " Python 3.8 or higher.",
        category=DeprecationWarning,
    )

__version__ = _version.version

if _TYPE_CHECKING:
    from argilla.client.api import (
        active_client,
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
    from argilla.client.feedback.dataset import FeedbackDataset
    from argilla.client.feedback.schemas import (
        FeedbackRecord,
        LabelQuestion,
        LabelQuestionStrategy,
        MultiLabelQuestion,
        MultiLabelQuestionStrategy,
        RatingQuestion,
        RatingQuestionStrategy,
        TextField,
        TextQuestion,
        TrainingDataForTextClassification,
    )
    from argilla.client.models import (
        Text2TextRecord,
        TextClassificationRecord,
        TextGenerationRecord,  # TODO Remove TextGenerationRecord
        TokenAttributions,
        TokenClassificationRecord,
    )
    from argilla.client.workspaces import Workspace
    from argilla.datasets import (
        TextClassificationSettings,
        TokenClassificationSettings,
        configure_dataset,
        configure_dataset_settings,
        load_dataset_settings,
    )
    from argilla.listeners import Metrics, RGListenerContext, Search, listener
    from argilla.monitoring.model_monitor import monitor
    from argilla.server.server import app


# TODO: remove me
_import_structure = {
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
    "client.feedback.dataset": ["FeedbackDataset"],
    "client.feedback.schemas": [
        "FeedbackRecord",
        "LabelQuestion",
        "LabelQuestionStrategy",
        "MultiLabelQuestion",
        "MultiLabelQuestionStrategy",
        "RatingQuestion",
        "RatingQuestionStrategy",
        "TextField",
        "TextQuestion",
        "TrainingDataForTextClassification",
    ],
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
