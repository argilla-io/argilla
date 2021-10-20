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

from .commons import TaskType
from .commons.task_factory import TaskFactory
from .text2text import Text2TextQuery, api as text2text
from .text_classification import TextClassificationQuery, api as text_classification
from .token_classification import TokenClassificationQuery, api as token_classification

router = APIRouter()


TaskFactory.register_task(
    task_type=TaskType.token_classification, query_request=TokenClassificationQuery
)

TaskFactory.register_task(
    task_type=TaskType.text_classification, query_request=TextClassificationQuery
)

TaskFactory.register_task(task_type=TaskType.text2text, query_request=Text2TextQuery)


for task_api in [text_classification, token_classification, text2text]:
    router.include_router(task_api.router)
