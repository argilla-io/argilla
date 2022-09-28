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

from typing import List

from fastapi import APIRouter, Body, Depends, Security

from argilla.server.apis.v0.models.commons.params import CommonTaskHandlerDependencies
from argilla.server.apis.v0.models.datasets import (
    CopyDatasetRequest,
    CreateDatasetRequest,
    Dataset,
    UpdateDatasetRequest,
)
from argilla.server.commons.config import TasksFactory
from argilla.server.errors import EntityNotFoundError
from argilla.server.security import auth
from argilla.server.security.model import User
from argilla.server.services.datasets import DatasetsService

router = APIRouter(tags=["datasets"], prefix="/datasets")


@router.get(
    "/",
    response_model=List[Dataset],
    response_model_exclude_none=True,
    operation_id="list_datasets",
)
async def list_datasets(
    request_deps: CommonTaskHandlerDependencies = Depends(),
    service: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> List[Dataset]:
    return service.list(
        user=current_user,
        workspaces=[request_deps.workspace]
        if request_deps.workspace is not None
        else None,
    )


@router.post(
    "",
    response_model=Dataset,
    response_model_exclude_none=True,
    operation_id="create_dataset",
    name="create_dataset",
    description="Create a new dataset",
)
async def create_dataset(
    request: CreateDatasetRequest = Body(..., description=f"The request dataset info"),
    ws_params: CommonTaskHandlerDependencies = Depends(),
    datasets: DatasetsService = Depends(DatasetsService.get_instance),
    user: User = Security(auth.get_user, scopes=["create:datasets"]),
) -> Dataset:

    owner = user.check_workspace(ws_params.workspace)

    dataset_class = TasksFactory.get_task_dataset(request.task)
    dataset = dataset_class.parse_obj({**request.dict()})
    dataset.owner = owner

    response = datasets.create_dataset(user=user, dataset=dataset)
    return Dataset.parse_obj(response)


@router.get(
    "/{name}",
    response_model=Dataset,
    response_model_exclude_none=True,
    operation_id="get_dataset",
)
def get_dataset(
    name: str,
    ds_params: CommonTaskHandlerDependencies = Depends(),
    service: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> Dataset:
    return Dataset.parse_obj(
        service.find_by_name(
            user=current_user,
            name=name,
            workspace=ds_params.workspace,
        )
    )


@router.patch(
    "/{name}",
    operation_id="update_dataset",
    response_model=Dataset,
    response_model_exclude_none=True,
)
def update_dataset(
    name: str,
    request: UpdateDatasetRequest,
    ds_params: CommonTaskHandlerDependencies = Depends(),
    service: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> Dataset:

    found_ds = service.find_by_name(
        user=current_user, name=name, workspace=ds_params.workspace
    )

    return service.update(
        user=current_user,
        dataset=found_ds,
        tags=request.tags,
        metadata=request.metadata,
    )


@router.delete(
    "/{name}",
    operation_id="delete_dataset",
)
def delete_dataset(
    name: str,
    ds_params: CommonTaskHandlerDependencies = Depends(),
    service: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
):
    try:
        found_ds = service.find_by_name(
            user=current_user, name=name, workspace=ds_params.workspace
        )
        service.delete(user=current_user, dataset=found_ds)
    except EntityNotFoundError:
        pass


@router.put(
    "/{name}:close",
    operation_id="close_dataset",
)
def close_dataset(
    name: str,
    ds_params: CommonTaskHandlerDependencies = Depends(),
    service: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
):
    found_ds = service.find_by_name(
        user=current_user, name=name, workspace=ds_params.workspace
    )
    service.close(user=current_user, dataset=found_ds)


@router.put(
    "/{name}:open",
    operation_id="open_dataset",
)
def open_dataset(
    name: str,
    ds_params: CommonTaskHandlerDependencies = Depends(),
    service: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
):
    found_ds = service.find_by_name(
        user=current_user, name=name, workspace=ds_params.workspace
    )
    service.open(user=current_user, dataset=found_ds)


@router.put(
    "/{name}:copy",
    operation_id="copy_dataset",
    response_model=Dataset,
    response_model_exclude_none=True,
)
def copy_dataset(
    name: str,
    copy_request: CopyDatasetRequest,
    ds_params: CommonTaskHandlerDependencies = Depends(),
    service: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> Dataset:
    found = service.find_by_name(
        user=current_user, name=name, workspace=ds_params.workspace
    )
    return service.copy_dataset(
        user=current_user,
        dataset=found,
        copy_name=copy_request.name,
        copy_workspace=copy_request.target_workspace,
        copy_tags=copy_request.tags,
        copy_metadata=copy_request.metadata,
    )
