import enum
from http import HTTPStatus

from fastapi import APIRouter, Body, Depends, Path, Security

from rubrix.server.api.v1.config.factory import __all__ as all_tasks
from rubrix.server.api.v1.constants import (
    API_VERSION,
    DATASET_NAME_PATTERN,
    TASK_DATASET_ENDPOINT,
    TASKS_PATTERN,
)
from rubrix.server.api.v1.models.commons.params import (
    CommonTaskQueryParams,
    PaginationParams,
    TaskNameEndpointHandlerParams,
)
from rubrix.server.api.v1.models.commons.task import TaskType
from rubrix.server.api.v1.models.datasets import Dataset, DatasetCopy, DatasetsList
from rubrix.server.datasets.model import DatasetDB
from rubrix.server.datasets.service import DatasetsService
from rubrix.server.security import auth
from rubrix.server.security.model import User


class OpenCloseAction(str, enum.Enum):
    open = "open"
    close = "close"


def configure_router() -> APIRouter:
    """Configure path routes to router"""
    router = APIRouter(tags=[f"{API_VERSION} / Datasets"])

    @router.get(
        "/",
        name="Get all datasets",
        status_code=HTTPStatus.OK,
        response_model_exclude_none=True,
        response_model=DatasetsList,
        operation_id="get_all_datasets",
    )
    async def get_all_datasets(
        params: CommonTaskQueryParams = Depends(),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        user: User = Security(auth.get_user, scopes=["read"]),
    ) -> DatasetsList:
        all_datasets = datasets.list(
            user=user,
            workspaces=[params.workspace] if params.workspace is not None else None,
        )

        return DatasetsList(total=len(all_datasets), data=all_datasets)

    @router.get(
        path="/{tasks}",
        name="Get tasks datasets",
        status_code=HTTPStatus.OK,
        response_model_exclude_none=True,
        response_model=DatasetsList,
        operation_id="get_datasets_by_tasks",
    )
    async def get_datasets_by_tasks(
        tasks: str = Path(..., regex=TASKS_PATTERN),
        params: CommonTaskQueryParams = Depends(),
        pagination: PaginationParams = Depends(),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        user: User = Security(auth.get_user, scopes=["read"]),
    ):
        tasks = set([t.strip() for t in tasks.split(",")]) if tasks else {}
        workspaces = [params.workspace] if params.workspace is not None else None

        all_datasets = [
            dataset
            for task in tasks
            for dataset in datasets.list(
                user=user,
                workspaces=workspaces,
                task=TaskType(task),
            )
        ]

        return DatasetsList(total=len(all_datasets), data=all_datasets)

    @router.post(
        TASK_DATASET_ENDPOINT + ":copy",
        response_model=Dataset,
        response_model_exclude_none=True,
        operation_id="copy_dataset",
    )
    async def copy_dataset(
        params: TaskNameEndpointHandlerParams = Depends(),
        request: DatasetCopy = Body(...),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        user: User = Security(auth.get_user, scopes=["read", "write"]),
    ) -> Dataset:
        found = datasets.find_by_name(
            user=user,
            name=params.name,
            workspace=params.common.workspace,
            task=params.task,
        )
        return datasets.copy_dataset(
            user=user,
            dataset=found,
            copy_name=request.name,
            copy_workspace=request.target_workspace,
            copy_tags=request.tags,
            copy_metadata=request.metadata,
        )

    @router.post(
        TASK_DATASET_ENDPOINT + ":{action}", operation_id="open_and_close_dataset"
    )
    async def open_and_close_dataset(
        action: OpenCloseAction = Path(...),
        params: TaskNameEndpointHandlerParams = Depends(),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        user: User = Security(auth.get_user, scopes=["read", "write"]),
    ):
        found_ds = datasets.find_by_name(
            user=user,
            name=params.name,
            workspace=params.common.workspace,
            task=params.task,
        )
        method = datasets.open if action == OpenCloseAction.open else datasets.close
        return method(user=user, dataset=found_ds)

    @router.delete(
        path=TASK_DATASET_ENDPOINT,
        name="Delete a dataset",
        status_code=HTTPStatus.OK,
        operation_id="delete_dataset",
    )
    async def delete_dataset(
        params: TaskNameEndpointHandlerParams = Depends(),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        user: User = Security(auth.get_user, scopes=["read", "write"]),
    ):
        found = datasets.find_by_name(
            user=user,
            name=params.name,
            task=TaskType(params.task),
            workspace=params.common.workspace,
        )
        datasets.delete(user=user, dataset=found)

    for cfg in all_tasks:

        @router.post(
            path=f"/{cfg.task}",
            name=f"Create a new {cfg.task} dataset",
            status_code=HTTPStatus.OK,
            response_model=cfg.output_dataset_class,
            response_model_exclude_none=True,
            operation_id=f"{cfg.task}/create_new_dataset",
        )
        async def create_new_dataset(
            request: cfg.create_dataset_class,
            name: str = Path(..., regex=DATASET_NAME_PATTERN),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            user: User = Security(auth.get_user, scopes=["read", "write"]),
        ) -> cfg.output_dataset_class:

            dataset = datasets.create_dataset(
                user=user,
                dataset=DatasetDB(
                    name=name,
                    task=cfg.task,
                    **request.dict(),
                ),
            )
            return Dataset.parse_obj(dataset)

        base_endpoint = f"/{cfg.task}/{{name}}"

        @router.get(
            path=base_endpoint,
            name=f"Get a {cfg.task} dataset",
            response_model=cfg.output_dataset_class,
            response_model_exclude_none=True,
            operation_id=f"{cfg.task}/get_dataset",
        )
        async def get_dataset(
            name: str = Path(..., regex=DATASET_NAME_PATTERN),
            common: CommonTaskQueryParams = Depends(),
            service: DatasetsService = Depends(DatasetsService.get_instance),
            user: User = Security(auth.get_user, scopes=["read"]),
        ):
            found = service.find_by_name(
                user=user,
                name=name,
                workspace=common.workspace,
                task=cfg.task,
            )

            return cfg.output_dataset_class.parse_obj(found)

        @router.patch(
            base_endpoint,
            name=f"Update a {cfg.task} dataset",
            operation_id=f"{cfg.task}/update_dataset",
            response_model=cfg.output_dataset_class,
            response_model_exclude_none=True,
        )
        def update_dataset(
            request: cfg.update_dataset_class,
            name: str = Path(..., regex=DATASET_NAME_PATTERN),
            common: CommonTaskQueryParams = Depends(),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            user: User = Security(auth.get_user, scopes=["read", "write"]),
        ) -> Dataset:
            found_ds = datasets.find_by_name(
                user=user,
                name=name,
                workspace=common.workspace,
                task=cfg.task,
            )

            updated = datasets.update(
                user=user,
                dataset=found_ds,
                tags=request.tags,
                metadata=request.metadata,
            )

            return cfg.output_dataset_class.parse_obj(updated)

    return router


__router__ = configure_router()
