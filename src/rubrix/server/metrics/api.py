import datetime
from typing import List

from fastapi import APIRouter, Depends

from rubrix.server.datasets.service import DatasetsService, create_dataset_service
from rubrix.server.metrics.model import (
    DatasetMetric,
    DatasetMetricCreation,
    DatasetMetricDB,
)
from rubrix.server.security import auth
from rubrix.server.security.model import User

BASE_ENDPOINT = "/{name}/metrics"

router = APIRouter(tags=["metrics"], prefix="/datasets")


@router.get(
    BASE_ENDPOINT,
    operation_id="get_dataset_metrics",
    response_model=List[DatasetMetric],
    response_model_exclude_none=True,
)
def get_dataset_metrics(
    name: str,
    datasets: DatasetsService = Depends(create_dataset_service),
    user: User = Depends(auth.get_user),
) -> List[DatasetMetric]:
    metrics = datasets.get_dataset_metrics(name, owner=user.current_group)
    return [DatasetMetric.parse_obj(m) for m in metrics]


@router.post(
    BASE_ENDPOINT,
    operation_id="create_dataset_metric",
    response_model=DatasetMetric,
    response_model_exclude_none=True,
)
def create_dataset_metric(
    name: str,
    request: DatasetMetricCreation,
    datasets: DatasetsService = Depends(create_dataset_service),
    user: User = Depends(auth.get_user),
) -> DatasetMetric:
    result = datasets.add_dataset_metric(
        name,
        owner=user.current_group,
        metric=DatasetMetricDB(
            **request.dict(),
            created_by=user.username,
            created_at=datetime.datetime.utcnow()
        ),
    )
    return DatasetMetric.parse_obj(result)


@router.delete(
    BASE_ENDPOINT + "/{metric}",
    operation_id="delete_dataset_metric",
    response_model_exclude_none=True,
)
def delete_dataset_metric(
    name: str,
    metric: str,
    datasets: DatasetsService = Depends(create_dataset_service),
    user: User = Depends(auth.get_user),
) -> None:
    return datasets.delete_dataset_metric(
        name, owner=user.current_group, metric_id=metric
    )
