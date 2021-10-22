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

from fastapi import APIRouter

from rubrix.server.tasks.token_classification.metrics import TokenClassificationMetrics
from .commons import TaskType
from .commons.metrics.api import configure_metrics_endpoints
from .commons.task_factory import TaskFactory
from .text2text import Text2TextQuery, Text2TextRecord, api as text2text
from .text2text.metrics import Text2TextMetrics
from .text_classification import (
    TextClassificationQuery,
    TextClassificationRecord,
    api as text_classification,
)
from .text_classification.metrics import TextClassificationMetrics
from .token_classification import (
    TokenClassificationQuery,
    TokenClassificationRecord,
    api as token_classification,
)

router = APIRouter()

TaskFactory.register_task(
    task_type=TaskType.token_classification,
    query_request=TokenClassificationQuery,
    record_class=TokenClassificationRecord,
    metrics=TokenClassificationMetrics,
)

TaskFactory.register_task(
    task_type=TaskType.text_classification,
    query_request=TextClassificationQuery,
    record_class=TextClassificationRecord,
    metrics=TextClassificationMetrics,
)

TaskFactory.register_task(
    task_type=TaskType.text2text,
    query_request=Text2TextQuery,
    record_class=Text2TextRecord,
    metrics=Text2TextMetrics,
)


for task_api in [text_classification, token_classification, text2text]:
    cfg = TaskFactory.get_task_by_task_type(task_api.TASK_TYPE)
    if cfg:
        configure_metrics_endpoints(task_api.router, cfg)

    router.include_router(task_api.router)
