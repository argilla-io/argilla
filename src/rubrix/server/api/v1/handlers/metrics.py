from http import HTTPStatus
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, Path, Security

from rubrix.server.api.v1 import API_VERSION
from rubrix.server.api.v1.config.factory import __all__ as all_tasks
from rubrix.server.api.v1.models.commons.params import (
    DATASET_NAME_PATH_PARAM,
    WorkspaceParams,
)
from rubrix.server.api.v1.models.metrics import (
    DatasetMetrics,
    MetricInfo,
    MetricSummaryParams,
    PaginationParams,
)
from rubrix.server.datasets.service import DatasetsService
from rubrix.server.security import auth
from rubrix.server.security.model import User
from rubrix.server.tasks.commons.metrics.service import MetricsService


def configure_router() -> APIRouter:

    router = APIRouter(tags=[f"{API_VERSION} / Metrics"])

    METRICS_PATH_PARAM = Path(..., description="The metric id")

    for cfg in all_tasks:
        base_metrics_endpoint = f"/{cfg.task}/{{name}}/metrics"

        @router.get(
            base_metrics_endpoint,
            name=f"{cfg.task}/get_dataset_metrics",
            operation_id=f"{cfg.task}/get_dataset_metrics",
            description=f"Get defined metrics for a {cfg.task} dataset",
            status_code=HTTPStatus.OK,
            response_model=DatasetMetrics,
            response_model_exclude_none=True,
        )
        def get_dataset_metrics(
            name: str = DATASET_NAME_PATH_PARAM,
            ws_params: WorkspaceParams = Depends(),
            pagination: PaginationParams = Depends(),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            metrics: MetricsService = Depends(MetricsService.get_instance),
            user: User = Security(auth.get_user, scopes=["read"]),
        ) -> DatasetMetrics:
            dataset = datasets.find_by_name(
                user=user,
                name=name,
                task=cfg.task,
                workspace=ws_params.workspace,
            )
            metrics = metrics.get_dataset_metrics(dataset=dataset)
            return DatasetMetrics(
                total=len(metrics),
                metrics=[MetricInfo.parse_obj(metric) for metric in metrics],
            )

        @router.get(
            base_metrics_endpoint + "/{metric}",
            name=f"{cfg.task}/get_dataset_metric",
            operation_id=f"{cfg.task}/get_dataset_metric",
            description=f"Get a {cfg.task} dataset metric by id",
            status_code=HTTPStatus.OK,
            response_model=MetricInfo,
            response_model_exclude_none=True,
        )
        def get_dataset_metric(
            name: str = DATASET_NAME_PATH_PARAM,
            metric: str = METRICS_PATH_PARAM,
            ws_params: WorkspaceParams = Depends(),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            metrics: MetricsService = Depends(MetricsService.get_instance),
            user: User = Security(auth.get_user, scopes=["read"]),
        ) -> MetricInfo:
            datasets.find_by_name(
                user=user,
                name=name,
                task=cfg.task,
                workspace=ws_params.workspace,
            )
            metric = metrics.find_metric_by_id(metric=metric, task=cfg.task)
            return MetricInfo.parse_obj(metric)

        @router.post(
            base_metrics_endpoint + "/{metric}:summary",
            name="metric_summary",
            operation_id=f"metric_summary",
            description="Compute the metric over the dataset",
            status_code=HTTPStatus.OK,
            response_model=Dict[str, Any],
            response_model_exclude_none=True,
        )
        def metric_summary(
            name: str = DATASET_NAME_PATH_PARAM,
            metric: str = METRICS_PATH_PARAM,
            query: Optional[cfg.query_class] = Body(
                default=None,
                description="The optional query applied to compute the metric",
            ),
            ws_params: WorkspaceParams = Depends(),
            params_metrics: MetricSummaryParams = Depends(),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            metrics: MetricsService = Depends(MetricsService.get_instance),
            user: User = Security(auth.get_user, scopes=["read", "compute"]),
        ) -> Dict[str, Any]:
            dataset = datasets.find_by_name(
                user=user,
                name=name,
                task=cfg.task,
                workspace=ws_params.workspace,
            )
            return metrics.summarize_metric(
                dataset=dataset,
                owner=user.check_workspace(ws_params.workspace),
                metric=metric,
                query=query,
                **vars(params_metrics),
            )

    return router


__router__ = configure_router()
