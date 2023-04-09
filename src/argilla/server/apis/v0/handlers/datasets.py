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
from pydantic import parse_obj_as

from argilla.server.apis.v0.helpers import deprecate_endpoint
from argilla.server.apis.v0.models.commons.params import (
    CommonTaskHandlerDependencies,
    OptionalWorkspaceRequestDependency,
)
from argilla.server.errors import EntityNotFoundError
from argilla.server.models import User
from argilla.server.schemas.datasets import (
    CopyDatasetRequest,
    CreateDatasetRequest,
    Dataset,
    UpdateDatasetRequest,
)
from argilla.server.security import auth
from argilla.server.services.datasets import DatasetsService

router = APIRouter(tags=["datasets"], prefix="/datasets")


@deprecate_endpoint(
    "/",
    new_path="",
    router_method=router.get,
    response_model=List[Dataset],
    response_model_exclude_none=True,
    operation_id="list_datasets",
)
async def list_datasets(
    workspace_request: OptionalWorkspaceRequestDependency = Depends(),
    service: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_current_user),
) -> List[Dataset]:
    datasets = service.list(
        user=current_user,
        workspaces=[workspace_request.workspace] if workspace_request.workspace is not None else None,
    )

    return parse_obj_as(List[Dataset], datasets)


@router.post(
    "",
    response_model=Dataset,
    response_model_exclude_none=True,
    operation_id="create_dataset",
    name="create_dataset",
    description="Create a new dataset",
)
async def create_dataset(
    request: CreateDatasetRequest = Body(..., description="The request dataset info"),
    ws_params: CommonTaskHandlerDependencies = Depends(),
    datasets: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_current_user),
) -> Dataset:
    request.workspace = request.workspace or ws_params.workspace
    dataset = datasets.create_dataset(user=current_user, dataset=request)

    return Dataset.from_orm(dataset)


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
    current_user: User = Security(auth.get_current_user),
) -> Dataset:
    return Dataset.from_orm(
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
    current_user: User = Security(auth.get_current_user),
) -> Dataset:
    found_ds = service.find_by_name(user=current_user, name=name, workspace=ds_params.workspace)

    dataset = service.update(
        user=current_user,
        dataset=found_ds,
        tags=request.tags,
        metadata=request.metadata,
    )

    return Dataset.from_orm(dataset)


@router.delete(
    "/{name}",
    operation_id="delete_dataset",
)
def delete_dataset(
    name: str,
    ds_params: CommonTaskHandlerDependencies = Depends(),
    service: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_current_user),
):
    try:
        found_ds = service.find_by_name(
            user=current_user,
            name=name,
            workspace=ds_params.workspace,
        )
        service.delete(
            user=current_user,
            dataset=found_ds,
        )
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
    current_user: User = Security(auth.get_current_user),
):
    found_ds = service.find_by_name(user=current_user, name=name, workspace=ds_params.workspace)
    service.close(user=current_user, dataset=found_ds)


@router.put(
    "/{name}:open",
    operation_id="open_dataset",
)
def open_dataset(
    name: str,
    ds_params: CommonTaskHandlerDependencies = Depends(),
    service: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_current_user),
):
    found_ds = service.find_by_name(user=current_user, name=name, workspace=ds_params.workspace)
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
    current_user: User = Security(auth.get_current_user),
) -> Dataset:
    found = service.find_by_name(user=current_user, name=name, workspace=ds_params.workspace)
    dataset = service.copy_dataset(
        user=current_user,
        dataset=found,
        copy_name=copy_request.name,
        copy_workspace=copy_request.target_workspace,
        copy_tags=copy_request.tags,
        copy_metadata=copy_request.metadata,
    )

    return Dataset.from_orm(dataset)
