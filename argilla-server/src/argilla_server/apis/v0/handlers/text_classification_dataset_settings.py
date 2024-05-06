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

from fastapi import APIRouter, Body, Depends, Security

from argilla_server.apis.v0.helpers import deprecate_endpoint
from argilla_server.apis.v0.models.commons.params import DATASET_NAME_PATH_PARAM, CommonTaskHandlerDependencies
from argilla_server.apis.v0.models.dataset_settings import TextClassificationSettings
from argilla_server.apis.v0.validators.text_classification import DatasetValidator
from argilla_server.commons.models import TaskType
from argilla_server.models import User
from argilla_server.security import auth
from argilla_server.services.datasets import DatasetsService


def configure_router(router: APIRouter):
    task_type = TaskType.text_classification
    base_endpoint = f"/{task_type.value}/{{name}}/settings"
    new_base_endpoint = f"/{{name}}/{task_type.value}/settings"

    @deprecate_endpoint(
        path=base_endpoint,
        new_path=new_base_endpoint,
        router_method=router.get,
        name=f"get_dataset_settings_for_{task_type.value}",
        operation_id=f"get_dataset_settings_for_{task_type.value}",
        description=f"Get the {task_type.value} dataset settings",
        response_model_exclude_none=True,
        response_model=TextClassificationSettings,
    )
    async def get_dataset_settings(
        name: str = DATASET_NAME_PATH_PARAM,
        ws_params: CommonTaskHandlerDependencies = Depends(),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        current_user: User = Security(auth.get_current_user),
    ) -> TextClassificationSettings:
        found_ds = await datasets.find_by_name(
            user=current_user,
            name=name,
            workspace=ws_params.workspace,
            task=task_type,
        )

        settings = await datasets.get_settings(
            user=current_user, dataset=found_ds, class_type=TextClassificationSettings
        )
        return settings

    @router.patch(
        path=new_base_endpoint,
        name=f"save_dataset_settings_for_{task_type.value}",
        operation_id=f"save_dataset_settings_for_{task_type.value}",
        description=f"Save the {task_type.value} dataset settings",
        response_model_exclude_none=True,
        response_model=TextClassificationSettings,
    )
    async def save_settings(
        request: TextClassificationSettings = Body(..., description=f"The {task_type.value} dataset settings"),
        name: str = DATASET_NAME_PATH_PARAM,
        ws_params: CommonTaskHandlerDependencies = Depends(),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        validator: DatasetValidator = Depends(DatasetValidator.get_instance),
        current_user: User = Security(auth.get_current_user),
    ) -> TextClassificationSettings:
        found_ds = await datasets.find_by_name(
            user=current_user,
            name=name,
            task=task_type,
            workspace=ws_params.workspace,
        )
        await validator.validate_dataset_settings(user=current_user, dataset=found_ds, settings=request)
        settings = await datasets.save_settings(
            user=current_user,
            dataset=found_ds,
            settings=TextClassificationSettings.parse_obj(request.dict()),
        )
        return settings

    # TODO: This will be remove in next iteration
    router.put(
        path=base_endpoint,
        name=f"old_save_dataset_settings_for_{task_type.value}",
        operation_id=f"old_save_dataset_settings_for_{task_type.value}",
        description=f"Save the {task_type.value} dataset settings",
        deprecated=True,
        response_model_exclude_none=True,
        response_model=TextClassificationSettings,
    )(save_settings)
    router.put(
        path=new_base_endpoint,
        name=f"new_save_dataset_settings_for_{task_type.value}_put",
        operation_id=f"new_save_dataset_settings_for_{task_type.value}_put",
        description=f"Save the {task_type.value} dataset settings",
        deprecated=True,
        response_model_exclude_none=True,
        response_model=TextClassificationSettings,
    )(save_settings)

    @deprecate_endpoint(
        path=base_endpoint,
        new_path=new_base_endpoint,
        router_method=router.delete,
        operation_id=f"delete_{task_type.value}_settings",
        name=f"delete_{task_type.value}_settings",
        description=f"Delete {task_type.value} dataset settings",
    )
    async def delete_settings(
        name: str = DATASET_NAME_PATH_PARAM,
        ws_params: CommonTaskHandlerDependencies = Depends(),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        user: User = Security(auth.get_current_user),
    ) -> None:
        found_ds = await datasets.find_by_name(
            user=user,
            name=name,
            task=task_type,
            workspace=ws_params.workspace,
        )

        await datasets.delete_settings(
            user=user,
            dataset=found_ds,
        )

    return router
