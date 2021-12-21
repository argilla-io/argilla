from dataclasses import dataclass
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Security
from pydantic import BaseModel, Field

from rubrix.server.commons.api import CommonTaskQueryParams
from rubrix.server.datasets.service import DatasetsService
from rubrix.server.security import auth
from rubrix.server.security.model import User
from rubrix.server.tasks.commons.metrics.service import MetricsService
from rubrix.server.tasks.commons.task_factory import TaskConfig


class MetricInfo(BaseModel):
    """Metric info data model for retrieve dataset metrics information"""

    id: str = Field(description="The metric id")
    name: str = Field(description="The metric name")
    description: Optional[str] = Field(
        default=None, description="The metric description"
    )


@dataclass
class MetricSummaryParams:
    """
    For metrics summary calculation, common summary parameters.

    Attributes:
    -----------

    interval:
        For histogram summaries, the bucket interval

    size:
        For terminological metrics, the number of terms to retrieve

    """

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


def configure_metrics_endpoints(router: APIRouter, cfg: TaskConfig):
    """
    Configures an api router with the dataset task metrics endpoints.

    Parameters
    ----------
    router:
        The api router
    cfg:
        The task configuration model

    """
    base_metrics_endpoint = f"/{cfg.task}/{{name}}/metrics"

    @router.get(
        base_metrics_endpoint,
        operation_id=f"get_dataset_metrics",
        name="get_dataset_metrics",
    )
    def get_dataset_metrics(
        name: str,
        teams_query: CommonTaskQueryParams = Depends(),
        current_user: User = Security(auth.get_user, scopes=[]),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        metrics: MetricsService = Depends(MetricsService.get_instance),
    ) -> List[MetricInfo]:
        """
        List available metrics info for a given dataset

        Parameters
        ----------
        name:
            The dataset name
        teams_query:
            Team query param where dataset belongs to. Optional
        current_user:
            The current user
        datasets:
            The datasets service
        metrics:
            The metrics service

        Returns
        -------
            A list of metric info availables for given dataset

        """
        dataset = datasets.find_by_name(
            name, task=cfg.task, user=current_user, workspace=teams_query.workspace
        )
        metrics = metrics.get_dataset_metrics(dataset=dataset)
        return [MetricInfo.parse_obj(metric) for metric in metrics]

    @router.post(
        base_metrics_endpoint + "/{metric}:summary",
        operation_id=f"metric_summary",
        name="metric_summary",
    )
    def metric_summary(
        name: str,
        metric: str,
        query: cfg.query,
        metric_params: MetricSummaryParams = Depends(),
        teams_query: CommonTaskQueryParams = Depends(),
        current_user: User = Security(auth.get_user, scopes=[]),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        metrics: MetricsService = Depends(MetricsService.get_instance),
    ):
        """
        Summarizes a given metric for a given dataset.

        Parameters
        ----------
        name:
            The dataset name
        metric:
            The metric id
        query:
            A query for records filtering. Optional
        metric_params:
            Metric parameters for result calculation
        teams_query:
            Team query param where dataset belongs to. Optional
        current_user:
            The current user
        datasets:
            The datasets service
        metrics:
            The metrics service

        Returns
        -------
            The metric summary for a given dataset

        """
        dataset = datasets.find_by_name(
            name, task=cfg.task, user=current_user, workspace=teams_query.workspace
        )
        return metrics.summarize_metric(
            dataset=dataset,
            owner=current_user.check_workspace(teams_query.workspace),
            metric=metric,
            query=query,
            **vars(metric_params),
        )
