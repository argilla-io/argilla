from typing import Type

from fastapi import APIRouter, Body, Depends, Security

from rubrix.server.apis.v1.config.factory import TaskFactory
from rubrix.server.apis.v1.config.factory import __all__ as all_tasks
from rubrix.server.apis.v1.models.commons.params import (
    DATASET_NAME_PATH_PARAM,
    WorkspaceParams,
)
from rubrix.server.apis.v1.models.commons.task import TaskType
from rubrix.server.apis.v1.models.dataset_settings import DatasetSettings
from rubrix.server.models.dataset_settings import SVCDatasetSettings
from rubrix.server.security import auth
from rubrix.server.security.model import User
from rubrix.server.services.datasets import DatasetsService


def __extended_settings_class__(
    task: TaskType, settings_class: Type[DatasetSettings]
) -> Type[SVCDatasetSettings]:
    return type(f"{task}_DatasetSettings", (SVCDatasetSettings, settings_class), {})


def configure_router():

    router: APIRouter = APIRouter(tags=["Dataset settings"])

    def configure_task_endpoints(router_: APIRouter, cfg: TaskFactory):
        task = cfg.task
        svc_settings_class = __extended_settings_class__(task, cfg.settings_class)

        async def get_settings(
            name: str = DATASET_NAME_PATH_PARAM,
            ws_params: WorkspaceParams = Depends(),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            user: User = Security(auth.get_user, scopes=["ReadDatasetSettings"]),
        ) -> DatasetSettings:

            found_ds = datasets.find_by_name(
                user=user,
                name=name,
                task=cfg.task.as_old_task_type(),
                workspace=ws_params.workspace,
            )

            settings: SVCDatasetSettings = await datasets.get_settings(
                user=user, dataset=found_ds, class_type=svc_settings_class
            )
            return cfg.settings_class.parse_obj(settings)

        async def save_settings(
            request: cfg.settings_class = Body(
                ..., description=f"The {task} dataset setting"
            ),
            name: str = DATASET_NAME_PATH_PARAM,
            ws_params: WorkspaceParams = Depends(),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            validator: cfg.settings_validator = Depends(
                cfg.settings_validator.get_instance
            ),
            user: User = Security(auth.get_user, scopes=["SaveDatasetSettings"]),
        ) -> DatasetSettings:
            found_ds = datasets.find_by_name(
                user=user,
                name=name,
                task=cfg.task.as_old_task_type(),
                workspace=ws_params.workspace,
            )

            validator.validate(found_ds, settings=request)
            settings = await datasets.save_settings(
                user=user,
                dataset=found_ds,
                settings=svc_settings_class.parse_obj(request.dict()),
            )
            return cfg.settings_class.parse_obj(settings)

        async def delete_settings(
            name: str = DATASET_NAME_PATH_PARAM,
            ws_params: WorkspaceParams = Depends(),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            user: User = Security(auth.get_user, scopes=["DeleteDatasetSettings"]),
        ):
            found_ds = datasets.find_by_name(
                user=user,
                name=name,
                task=cfg.task.as_old_task_type(),
                workspace=ws_params.workspace,
            )
            await datasets.delete_settings(
                user=user,
                dataset=found_ds,
            )

        for _task in [cfg.task, cfg.task.as_old_task_type()]:
            router_.get(
                f"/{_task}/{{name}}/settings",
                name=f"{_task}/get_settings",
                operation_id=f"{_task}/get_settings",
                response_model=cfg.settings_class,
            )(get_settings)

            router_.put(
                f"/{_task}/{{name}}/settings",
                name=f"{_task}/save_settings",
                operation_id=f"{_task}/get_settings",
                response_model=cfg.settings_class,
            )(save_settings)

            router_.delete(
                f"/{_task}/{{name}}/settings",
                name=f"{_task}/delete_settings",
                operation_id=f"{_task}/delete_settings",
            )(delete_settings)

    for cfg in all_tasks:
        if cfg.settings_class and cfg.settings_validator:
            configure_task_endpoints(router, cfg)

    return router


__router__ = configure_router()
