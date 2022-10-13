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

from dataclasses import dataclass
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Security
from pydantic import BaseModel, Field

from argilla.server.apis.v0.helpers import deprecate_endpoint
from argilla.server.apis.v0.models.commons.params import CommonTaskHandlerDependencies
from argilla.server.commons.config import TaskConfig, TasksFactory
from argilla.server.security import auth
from argilla.server.security.model import User
from argilla.server.services.datasets import DatasetsService
from argilla.server.services.metrics import MetricsService


class MetricInfo(BaseModel):

    id: str = Field(description="The metric id")
    name: str = Field(description="The metric name")
    description: Optional[str] = Field(
        default=None, description="The metric description"
    )


@dataclass
class MetricSummaryParams:

    interval: Optional[float] = Query(
        default=None,
        gt=0.0,
        description="The histogram interval for histogram summaries",
    )
    size: Optional[int] = Query(
        default=None,
        ge=1,
        description="The number of terms for terminological summaries",
    )


def configure_router(router: APIRouter, cfg: TaskConfig):

    base_metrics_endpoint = f"/{cfg.task}/{{name}}/metrics"
    new_base_metrics_endpoint = f"/{{name}}/{cfg.task}/metrics"

    @deprecate_endpoint(
        path=base_metrics_endpoint,
        new_path=new_base_metrics_endpoint,
        router_method=router.get,
        operation_id=f"get_dataset_metrics",
        name="get_dataset_metrics",
    )
    def get_dataset_metrics(
        name: str,
        request_deps: CommonTaskHandlerDependencies = Depends(),
        current_user: User = Security(auth.get_user, scopes=[]),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
    ) -> List[MetricInfo]:
        dataset = datasets.find_by_name(
            user=current_user,
            name=name,
            task=cfg.task,
            workspace=request_deps.workspace,
            as_dataset_class=TasksFactory.get_task_dataset(cfg.task),
        )

        metrics = TasksFactory.get_task_metrics(dataset.task)
        metrics = metrics.metrics if metrics else []

        return [MetricInfo.parse_obj(metric) for metric in metrics]

    @deprecate_endpoint(
        path=base_metrics_endpoint + "/{metric}:summary",
        new_path=new_base_metrics_endpoint + "/{metric}:summary",
        router_method=router.post,
        operation_id=f"metric_summary",
        name="metric_summary",
    )
    def metric_summary(
        name: str,
        metric: str,
        query: cfg.query,
        metric_params: MetricSummaryParams = Depends(),
        request_deps: CommonTaskHandlerDependencies = Depends(),
        current_user: User = Security(auth.get_user, scopes=[]),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        metrics: MetricsService = Depends(MetricsService.get_instance),
    ):
        dataset = datasets.find_by_name(
            user=current_user,
            name=name,
            task=cfg.task,
            workspace=request_deps.workspace,
            as_dataset_class=TasksFactory.get_task_dataset(cfg.task),
        )

        metric_ = TasksFactory.find_task_metric(task=cfg.task, metric_id=metric)
        record_class = TasksFactory.get_task_record(cfg.task)

        return metrics.summarize_metric(
            dataset=dataset,
            owner=current_user.check_workspace(request_deps.workspace),
            metric=metric_,
            record_class=record_class,
            query=query,
            **vars(metric_params),
        )


router = APIRouter(tags=["Metrics"], prefix="/datasets")
for cfg in TasksFactory.get_all_configs():
    configure_router(router, cfg)
