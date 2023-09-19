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
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query, Request, Security
from pydantic import BaseModel, Field

from argilla.server.apis.v0.helpers import deprecate_endpoint
from argilla.server.apis.v0.models.commons.params import CommonTaskHandlerDependencies
from argilla.server.commons.config import TaskConfig, TasksFactory
from argilla.server.models import User
from argilla.server.security import auth
from argilla.server.services.datasets import DatasetsService
from argilla.server.services.metrics import MetricsService


class MetricInfo(BaseModel):
    id: str = Field(description="The metric id")
    name: str = Field(description="The metric name")
    description: Optional[str] = Field(default=None, description="The metric description")


@dataclass
class MetricSummaryParams:
    request: Request

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

    @property
    def parameters(self) -> Dict[str, Any]:
        """Returns dynamic metric args found in the request query params"""
        return {
            "interval": self.interval,
            "size": self.size,
            **{k: v for k, v in self.request.query_params.items() if k not in ["interval", "size"]},
        }


def configure_router(router: APIRouter, cfg: TaskConfig):
    base_metrics_endpoint = f"/{cfg.task.value}/{{name}}/metrics"
    new_base_metrics_endpoint = f"/{{name}}/{cfg.task.value}/metrics"

    @deprecate_endpoint(
        path=base_metrics_endpoint,
        new_path=new_base_metrics_endpoint,
        router_method=router.get,
        operation_id="get_dataset_metrics",
        name="get_dataset_metrics",
    )
    async def get_dataset_metrics(
        name: str,
        request_deps: CommonTaskHandlerDependencies = Depends(),
        current_user: User = Security(auth.get_current_user),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
    ) -> List[MetricInfo]:
        dataset = await datasets.find_by_name(
            user=current_user,
            name=name,
            task=cfg.task,
            workspace=request_deps.workspace,
        )

        metrics = TasksFactory.get_task_metrics(dataset.task)
        metrics = metrics.metrics if metrics else []

        return [MetricInfo.parse_obj(metric) for metric in metrics]

    @deprecate_endpoint(
        path=base_metrics_endpoint + "/{metric}:summary",
        new_path=new_base_metrics_endpoint + "/{metric}:summary",
        router_method=router.post,
        operation_id="metric_summary",
        name="metric_summary",
    )
    async def metric_summary(
        name: str,
        metric: str,
        query: cfg.query,
        metric_params: MetricSummaryParams = Depends(),
        request_deps: CommonTaskHandlerDependencies = Depends(),
        current_user: User = Security(auth.get_current_user, scopes=[]),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        metrics: MetricsService = Depends(MetricsService.get_instance),
    ):
        dataset = await datasets.find_by_name(
            user=current_user,
            name=name,
            task=cfg.task,
            workspace=request_deps.workspace,
        )

        metric_ = TasksFactory.find_task_metric(task=cfg.task, metric_id=metric)
        record_class = TasksFactory.get_task_record(cfg.task)

        return metrics.summarize_metric(
            dataset=dataset,
            metric=metric_,
            record_class=record_class,
            query=query,
            **metric_params.parameters,
        )


router = APIRouter(tags=["Metrics"], prefix="/datasets")
for cfg in TasksFactory.get_all_configs():
    configure_router(router, cfg)
