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

from fastapi import APIRouter, Depends, Security

from .commons import TaskType
from .commons.service import TaskService
from .commons.task_factory import TaskFactory, _TaskConfig
from .text2text import Text2TextQuery, api as text2text
from .text_classification import TextClassificationQuery, api as text_classification
from .token_classification import TokenClassificationQuery, api as token_classification
from ..commons.api import TeamsQueryParams
from ..metrics.model import DatasetMetricResults
from ..security import auth
from ..security.model import User

router = APIRouter()


TaskFactory.register_task(
    task_type=TaskType.token_classification, query_request=TokenClassificationQuery
)

TaskFactory.register_task(
    task_type=TaskType.text_classification, query_request=TextClassificationQuery
)

TaskFactory.register_task(task_type=TaskType.text2text, query_request=Text2TextQuery)


def build_task_metrics_endpoint(task_router: APIRouter, cfg: _TaskConfig):
    @task_router.post(
        "/" + task_api.TASK_TYPE + "/{name}/metrics/{metric_id}",
        operation_id=f"{task_api.TASK_TYPE}_calculate_metric",
        name="calculate_metric",
        response_model=DatasetMetricResults,
    )
    def calculate_metrics(
        name: str,
        metric_id: str,
        request: cfg.query,
        teams_query: TeamsQueryParams = Depends(),
        current_user: User = Security(auth.get_user, scopes=[]),
        task_service: TaskService = Depends(TaskService.get_instance),
    ):
        return task_service.calculate_metrics(
            dataset=name,
            owner=current_user.check_team(teams_query.team),
            metric_id=metric_id,
            query=request,
        )


for task_api in [text_classification, token_classification, text2text]:
    task_cfg = TaskFactory.get_task_by_task_type(task_type=task_api.TASK_TYPE)
    if task_cfg:
        build_task_metrics_endpoint(task_api.router, cfg=task_cfg)
    router.include_router(task_api.router)
