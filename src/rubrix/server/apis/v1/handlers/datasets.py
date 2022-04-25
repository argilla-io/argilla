import datetime
from http import HTTPStatus
from typing import Type, Union

from fastapi import APIRouter, Body, Depends, Security

from rubrix.server.apis.v0.models.commons.model import TaskType as TaskTypeV0
from rubrix.server.apis.v1.config.factory import TaskFactory
from rubrix.server.apis.v1.config.factory import __all__ as all_tasks
from rubrix.server.apis.v1.config.factory import find_config_by_task
from rubrix.server.apis.v1.models.commons.params import (
    TASK_TYPE_PATH_PARAM,
    WorkspaceParams,
)
from rubrix.server.apis.v1.models.commons.task import TaskType
from rubrix.server.apis.v1.models.datasets import Dataset, DatasetCreate
from rubrix.server.security import auth
from rubrix.server.security.model import User
from rubrix.server.services.datasets import Dataset as ServiceDataset
from rubrix.server.services.datasets import DatasetDB, DatasetsService


def __extended_dataset_class__(cfg: TaskFactory) -> Type[ServiceDataset]:
    return type(
        f"{cfg.task}_Dataset", (DatasetDB, cfg.output_dataset_class), {}
    )  # Mixing api dataset with service storage dataset


def configure_router() -> APIRouter:
    """Configure path routes to router"""
    router = APIRouter(tags=[f"Datasets"])

    DEFAULT_TASK_DATASET_MAP = {
        cfg.task: __extended_dataset_class__(cfg) for cfg in all_tasks
    }

    @router.post(
        path="/{task}",
        name=f"create_new_dataset",
        operation_id=f"create_new_dataset",
        description=f"Create a new dataset",
        status_code=HTTPStatus.OK,
        response_model=Dataset,
        response_model_exclude_none=True,
    )
    async def create_new_dataset(
        task: Union[TaskType, TaskTypeV0] = TASK_TYPE_PATH_PARAM,
        request: DatasetCreate = Body(..., description=f"The dataset"),
        ws_params: WorkspaceParams = Depends(),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        user: User = Security(auth.get_user, scopes=["CreateDataset"]),
    ) -> Dataset:
        if isinstance(task, TaskTypeV0):
            task = TaskType.from_old_task_type(task)

        old_fashion_task = task.as_old_task_type()
        dataset_class = DEFAULT_TASK_DATASET_MAP.get(task)
        dataset = datasets.create_dataset(
            user=user,
            dataset=dataset_class(
                **request.dict(),
                task=old_fashion_task,
                owner=user.check_workspace(ws_params.workspace),
                created_by=user.username,
                created_at=datetime.datetime.utcnow(),
            ),
            mappings=find_config_by_task(task).es_mapping,
        )
        response = Dataset.parse_obj({**dataset.dict(), "task": task})
        return response

    return router


__router__ = configure_router()
