from typing import Type

from fastapi import APIRouter, Body, Depends, Security

from rubrix.server.apis.v0.models.commons.model import TaskType
from rubrix.server.apis.v0.models.commons.params import DATASET_NAME_PATH_PARAM
from rubrix.server.apis.v0.models.commons.workspace import CommonTaskQueryParams
from rubrix.server.apis.v0.models.dataset_settings import TokenClassificationSettings
from rubrix.server.apis.v0.validators.token_classification import DatasetValidator
from rubrix.server.security import auth
from rubrix.server.security.model import User
from rubrix.server.services.datasets import DatasetsService, SVCDatasetSettings

__svc_settings_class__: Type[SVCDatasetSettings] = type(
    f"{TaskType.token_classification}_DatasetSettings",
    (SVCDatasetSettings, TokenClassificationSettings),
    {},
)


def configure_router(router: APIRouter):
    task = TaskType.token_classification
    base_endpoint = f"/{task}/{{name}}/settings"

    @router.get(
        path=base_endpoint,
        name=f"get_dataset_settings_for_{task}",
        operation_id=f"get_dataset_settings_for_{task}",
        description=f"Get the {task} dataset settings",
        response_model_exclude_none=True,
        response_model=TokenClassificationSettings,
    )
    async def get_dataset_settings(
        name: str = DATASET_NAME_PATH_PARAM,
        ws_params: CommonTaskQueryParams = Depends(),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        user: User = Security(auth.get_user, scopes=["read:dataset.settings"]),
    ) -> TokenClassificationSettings:

        found_ds = datasets.find_by_name(
            user=user,
            name=name,
            workspace=ws_params.workspace,
            task=task,
        )

        settings = await datasets.get_settings(
            user=user, dataset=found_ds, class_type=__svc_settings_class__
        )
        return TokenClassificationSettings.parse_obj(settings)

    @router.put(
        path=base_endpoint,
        name=f"save_dataset_settings_for_{task}",
        operation_id=f"save_dataset_settings_for_{task}",
        description=f"Save the {task} dataset settings",
        response_model_exclude_none=True,
        response_model=TokenClassificationSettings,
    )
    async def save_settings(
        request: TokenClassificationSettings = Body(
            ..., description=f"The {task} dataset settings"
        ),
        name: str = DATASET_NAME_PATH_PARAM,
        ws_params: CommonTaskQueryParams = Depends(),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        validator: DatasetValidator = Depends(DatasetValidator.get_instance),
        user: User = Security(auth.get_user, scopes=["write:dataset.settings"]),
    ) -> TokenClassificationSettings:

        found_ds = datasets.find_by_name(
            user=user,
            name=name,
            task=task,
            workspace=ws_params.workspace,
        )
        await validator.validate_dataset_settings(
            user=user, dataset=found_ds, settings=request
        )
        settings = await datasets.save_settings(
            user=user,
            dataset=found_ds,
            settings=__svc_settings_class__.parse_obj(request.dict()),
        )
        return TokenClassificationSettings.parse_obj(settings)

    @router.delete(
        path=base_endpoint,
        operation_id=f"delete_{task}_settings",
        name=f"delete_{task}_settings",
        description=f"Delete {task} dataset settings",
    )
    async def delete_settings(
        name: str = DATASET_NAME_PATH_PARAM,
        ws_params: CommonTaskQueryParams = Depends(),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        user: User = Security(auth.get_user, scopes=["delete:dataset.settings"]),
    ) -> None:
        found_ds = datasets.find_by_name(
            user=user,
            name=name,
            task=task,
            workspace=ws_params.workspace,
        )
        await datasets.delete_settings(
            user=user,
            dataset=found_ds,
        )

    return router
