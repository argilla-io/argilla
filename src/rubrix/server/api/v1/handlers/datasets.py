import enum
from http import HTTPStatus

from fastapi import APIRouter, Body, Depends, Path, Security

from rubrix.server.api.v1.config.factory import __all__ as all_tasks
from rubrix.server.api.v1.constants import (
    API_VERSION,
    TASK_DATASET_ENDPOINT,
    TASKS_PATTERN,
)
from rubrix.server.api.v1.models.commons.params import (
    DATASET_NAME_PATH_PARAM,
    TASK_TYPE_PATH_PARAM,
    WorkspaceParams,
)
from rubrix.server.api.v1.models.commons.task import TaskType
from rubrix.server.api.v1.models.datasets import (
    Dataset,
    DatasetCopy,
    DatasetsList,
    PaginationParams,
)
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
        path="/",
        name="get_datasets",
        operation_id="get_datasets",
        description="Get all datasets",
        status_code=HTTPStatus.OK,
        response_model=DatasetsList,
        response_model_exclude_none=True,
    )
    async def get_datasets(
        ws_params: WorkspaceParams = Depends(),
        pagination: PaginationParams = Depends(),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        user: User = Security(auth.get_user, scopes=["ReadDataset"]),
    ) -> DatasetsList:
        all_datasets = datasets.list(
            user=user,
            workspaces=[ws_params.workspace]
            if ws_params.workspace is not None
            else None,
        )

        return DatasetsList(total=len(all_datasets), data=all_datasets)

    @router.get(
        path="/{tasks}",
        name="get_datasets_by_tasks",
        operation_id="get_datasets_by_tasks",
        description="Get datasets by tasks",
        status_code=HTTPStatus.OK,
        response_model=DatasetsList,
        response_model_exclude_none=True,
    )
    async def get_datasets_by_tasks(
        tasks: str = Path(
            ..., regex=TASKS_PATTERN, description="Comma separated task types"
        ),
        ws_params: WorkspaceParams = Depends(),
        pagination: PaginationParams = Depends(),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        user: User = Security(auth.get_user, scopes=["ReadDataset"]),
    ):
        tasks = set([t.strip() for t in tasks.split(",")]) if tasks else {}
        workspaces = [ws_params.workspace] if ws_params.workspace is not None else None

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
        path=TASK_DATASET_ENDPOINT + ":copy",
        name="copy_dataset",
        operation_id="copy_dataset",
        description="Copy a dataset. Target dataset can be created in the same or another workspace",
        status_code=HTTPStatus.OK,
        response_model=Dataset,
        response_model_exclude_none=True,
    )
    async def copy_dataset(
        task: TaskType = TASK_TYPE_PATH_PARAM,
        name: str = DATASET_NAME_PATH_PARAM,
        ws_params: WorkspaceParams = Depends(),
        request: DatasetCopy = Body(..., description="Copy dataset info"),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        user: User = Security(auth.get_user, scopes=["CopyDataset"]),
    ) -> Dataset:
        found = datasets.find_by_name(
            user=user,
            task=task,
            name=name,
            workspace=ws_params.workspace,
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
        path=TASK_DATASET_ENDPOINT + ":{action}",
        name="open_or_close_dataset",
        operation_id="open_or_close_dataset",
        description="Open/close a dataset",
        status_code=HTTPStatus.OK,
        response_model_exclude_none=True,
    )
    async def open_or_close_dataset(
        task: TaskType = TASK_TYPE_PATH_PARAM,
        name: str = DATASET_NAME_PATH_PARAM,
        action: OpenCloseAction = Path(..., description="The action to apply"),
        ws_params: WorkspaceParams = Depends(),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        user: User = Security(auth.get_user, scopes=["read", "write"]),
    ):
        found_ds = datasets.find_by_name(
            user=user,
            task=task,
            name=name,
            workspace=ws_params.workspace,
        )
        method = datasets.open if action == OpenCloseAction.open else datasets.close
        return method(user=user, dataset=found_ds)

    @router.delete(
        path=TASK_DATASET_ENDPOINT,
        name="delete_dataset",
        operation_id="delete_dataset",
        description="Delete a dataset",
        status_code=HTTPStatus.OK,
        response_model=Dataset,
        response_model_exclude_none=True,
    )
    async def delete_dataset(
        task: TaskType = TASK_TYPE_PATH_PARAM,
        name: str = DATASET_NAME_PATH_PARAM,
        ws_params: WorkspaceParams = Depends(),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        user: User = Security(auth.get_user, scopes=["DeleteDatasets"]),
    ) -> Dataset:
        found = datasets.find_by_name(
            user=user,
            task=task,
            name=name,
            workspace=ws_params.workspace,
        )
        datasets.delete(user=user, dataset=found)
        return found

    for cfg in all_tasks:

        @router.post(
            path=f"/{cfg.task}",
            name=f"{cfg.task}/create_new_dataset",
            operation_id=f"{cfg.task}/create_new_dataset",
            description=f"Create a new {cfg.task} dataset",
            status_code=HTTPStatus.OK,
            response_model=cfg.output_dataset_class,
            response_model_exclude_none=True,
        )
        async def create_new_dataset(
            name: str = DATASET_NAME_PATH_PARAM,
            request: cfg.create_dataset_class = Body(
                ..., description=f"The {cfg.task} dataset"
            ),
            ws_params: WorkspaceParams = Depends(),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            user: User = Security(auth.get_user, scopes=["CreateDatasets"]),
        ) -> cfg.output_dataset_class:

            dataset = datasets.create_dataset(
                user=user,
                dataset=DatasetDB(
                    name=name,
                    task=cfg.task,
                    owner=user.check_workspace(ws_params.workspace),
                    **request.dict(),
                ),
            )
            return cfg.output_dataset_class.parse_obj(dataset)

        base_endpoint = f"/{cfg.task}/{{name}}"

        @router.get(
            path=base_endpoint,
            name=f"{cfg.task}/get_dataset",
            operation_id=f"{cfg.task}/get_dataset",
            description=f"Get a {cfg.task} dataset",
            status_code=HTTPStatus.OK,
            response_model=cfg.output_dataset_class,
            response_model_exclude_none=True,
        )
        async def get_dataset(
            name: str = DATASET_NAME_PATH_PARAM,
            ws_params: WorkspaceParams = Depends(),
            service: DatasetsService = Depends(DatasetsService.get_instance),
            user: User = Security(auth.get_user, scopes=["ReadDataset"]),
        ) -> cfg.output_dataset_class:
            found = service.find_by_name(
                user=user,
                name=name,
                workspace=ws_params.workspace,
                task=cfg.task,
            )

            return cfg.output_dataset_class.parse_obj(found)

        @router.patch(
            base_endpoint,
            name=f"{cfg.task}/update_dataset",
            operation_id=f"{cfg.task}/update_dataset",
            description=f"Update a {cfg.task} dataset",
            status_code=HTTPStatus.OK,
            response_model=cfg.output_dataset_class,
            response_model_exclude_none=True,
        )
        def update_dataset(
            name: str = DATASET_NAME_PATH_PARAM,
            request: cfg.update_dataset_class = Body(
                ..., description="Accepted fields for dataset update"
            ),
            ws_params: WorkspaceParams = Depends(),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            user: User = Security(auth.get_user, scopes=["UpdateDatasetBasic"]),
        ) -> Dataset:
            found_ds = datasets.find_by_name(
                user=user,
                name=name,
                workspace=ws_params.workspace,
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
