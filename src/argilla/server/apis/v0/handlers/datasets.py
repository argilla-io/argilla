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
from datetime import datetime
from typing import List

from fastapi import APIRouter, Body, Depends, Security
from pydantic import parse_obj_as
from sqlalchemy.orm import Session

from argilla.server import database
from argilla.server.apis.v0.helpers import deprecate_endpoint
from argilla.server.apis.v0.models.commons.params import CommonTaskHandlerDependencies
from argilla.server.contexts import accounts
from argilla.server.daos.datasets import DatasetsDAO
from argilla.server.errors import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    ForbiddenOperationError,
)
from argilla.server.policies import DatasetPolicy, is_authorized
from argilla.server.schemas.datasets import (
    CopyDatasetRequest,
    CreateDatasetRequest,
    Dataset,
    UpdateDatasetRequest,
)
from argilla.server.security import auth
from argilla.server.security.model import User, Workspace

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
    workspace_params: CommonTaskHandlerDependencies = Depends(),
    datasets: DatasetsDAO = Depends(DatasetsDAO.get_instance),
    current_user: User = Security(auth.get_current_user, scopes=[]),
) -> List[Dataset]:
    if not is_authorized(current_user, DatasetPolicy.list):
        raise ForbiddenOperationError("You don't have the necessary permissions to list datasets.")

    workspaces = [workspace_params.workspace] if workspace_params.workspace is not None else None

    return parse_obj_as(List[Dataset], datasets.list_datasets(workspaces=workspaces))


@router.get("/{dataset_name}", response_model=Dataset, response_model_exclude_none=True, operation_id="get_dataset")
def get_dataset(
    dataset_name: str,
    workspace_params: CommonTaskHandlerDependencies = Depends(),
    datasets: DatasetsDAO = Depends(DatasetsDAO.get_instance),
    current_user: User = Security(auth.get_current_user, scopes=[]),
) -> Dataset:
    dataset = datasets.find_by_name_and_workspace(dataset_name, workspace_params.workspace)
    if not dataset:
        raise EntityNotFoundError(name=dataset, type=Dataset)

    if not is_authorized(current_user, DatasetPolicy.get):
        raise ForbiddenOperationError("You don't have the necessary permissions to get datasets.")

    return Dataset.from_orm(dataset)


@router.post(
    "",
    response_model=Dataset,
    response_model_exclude_none=True,
    operation_id="create_dataset",
    name="create_dataset",
    description="Create a new dataset",
)
async def create_dataset(
    db: Session = Depends(database.get_db),
    request: CreateDatasetRequest = Body(..., description="The request dataset info"),
    workspace_params: CommonTaskHandlerDependencies = Depends(),
    datasets: DatasetsDAO = Depends(DatasetsDAO.get_instance),
    current_user: User = Security(auth.get_current_user, scopes=[]),
) -> Dataset:
    request.workspace = request.workspace or workspace_params.workspace

    if not accounts.get_workspace_by_name(db, workspace_name=request.workspace):
        raise EntityNotFoundError(name=request.workspace, type=Workspace)

    if not is_authorized(current_user, DatasetPolicy.create):
        raise ForbiddenOperationError(
            "You don't have the necessary permissions to create datasets. Only administrators can create datasets"
        )

    dataset = datasets.create_dataset(user=current_user, dataset=request)

    return Dataset.from_orm(dataset)


@router.patch(
    "/{dataset_name}", operation_id="update_dataset", response_model=Dataset, response_model_exclude_none=True
)
def update_dataset(
    dataset_name: str,
    request: UpdateDatasetRequest,
    workspace_params: CommonTaskHandlerDependencies = Depends(),
    datasets: DatasetsDAO = Depends(DatasetsDAO.get_instance),
    current_user: User = Security(auth.get_current_user, scopes=[]),
) -> Dataset:
    dataset = datasets.find_by_name_and_workspace(name=dataset_name, workspace=workspace_params.workspace)
    if not dataset:
        raise EntityNotFoundError(name=dataset, type=Dataset)

    if not is_authorized(current_user, DatasetPolicy.update(dataset)):
        raise ForbiddenOperationError(
            "You don't have the necessary permissions to update this dataset. "
            "Only dataset creators or administrators can delete datasets"
        )

    dataset_update = dataset.copy(update={**request.dict(), "last_updated": datetime.utcnow()})
    updated_dataset = datasets.update_dataset(dataset_update)

    return Dataset.from_orm(updated_dataset)


@router.delete("/{dataset_name}", operation_id="delete_dataset")
def delete_dataset(
    dataset_name: str,
    workspace_params: CommonTaskHandlerDependencies = Depends(),
    datasets: DatasetsDAO = Depends(DatasetsDAO.get_instance),
    current_user: User = Security(auth.get_current_user, scopes=[]),
):
    dataset = datasets.find_by_name_and_workspace(name=dataset_name, workspace=workspace_params.workspace)
    if not dataset:
        # We are not raising an EntityNotFoundError because this endpoint
        # was not doing it originally so we want to continue doing the same.
        return

    if not is_authorized(current_user, DatasetPolicy.delete(dataset)):
        raise ForbiddenOperationError(
            "You don't have the necessary permissions to delete this dataset. "
            "Only dataset creators or administrators can delete datasets"
        )

    datasets.delete_dataset(dataset)


@router.put("/{dataset_name}:open", operation_id="open_dataset")
def open_dataset(
    dataset_name: str,
    workspace_params: CommonTaskHandlerDependencies = Depends(),
    datasets: DatasetsDAO = Depends(DatasetsDAO.get_instance),
    current_user: User = Security(auth.get_current_user, scopes=[]),
):
    dataset = datasets.find_by_name_and_workspace(dataset_name, workspace_params.workspace)
    if not dataset:
        raise EntityNotFoundError(name=dataset_name, type=Dataset)

    if not is_authorized(current_user, DatasetPolicy.open(dataset)):
        raise ForbiddenOperationError(
            "You don't have the necessary permissions to open this dataset. "
            "Only dataset creators or administrators can open datasets"
        )

    datasets.open(dataset)


@router.put("/{dataset_name}:close", operation_id="close_dataset")
def close_dataset(
    dataset_name: str,
    workspace_params: CommonTaskHandlerDependencies = Depends(),
    datasets: DatasetsDAO = Depends(DatasetsDAO.get_instance),
    current_user: User = Security(auth.get_current_user, scopes=[]),
):
    dataset = datasets.find_by_name_and_workspace(dataset_name, workspace_params.workspace)
    if not dataset:
        raise EntityNotFoundError(name=dataset_name, type=Dataset)

    if not is_authorized(current_user, DatasetPolicy.close(dataset)):
        raise ForbiddenOperationError(
            "You don't have the necessary permissions to close this dataset. "
            "Only dataset creators or administrators can close datasets"
        )

    datasets.close(dataset)


@router.put(
    "/{dataset_name}:copy", operation_id="copy_dataset", response_model=Dataset, response_model_exclude_none=True
)
def copy_dataset(
    *,
    db: Session = Depends(database.get_db),
    dataset_name: str,
    workspace_params: CommonTaskHandlerDependencies = Depends(),
    copy_request: CopyDatasetRequest,
    datasets: DatasetsDAO = Depends(DatasetsDAO.get_instance),
    current_user: User = Security(auth.get_current_user, scopes=[]),
) -> Dataset:
    source_dataset_name = dataset_name
    source_workspace_name = workspace_params.workspace

    target_dataset_name = copy_request.name
    target_workspace_name = copy_request.target_workspace or source_workspace_name

    source_dataset = datasets.find_by_name_and_workspace(source_dataset_name, source_workspace_name)
    if not source_dataset:
        raise EntityNotFoundError(name=source_dataset_name, type=Dataset)

    target_workspace = accounts.get_workspace_by_name(db, target_workspace_name)
    if not target_workspace:
        raise EntityNotFoundError(name=target_workspace_name, type=Workspace)

    if datasets.find_by_name_and_workspace(target_dataset_name, target_workspace_name):
        raise EntityAlreadyExistsError(name=target_dataset_name, workspace=target_workspace_name, type=Dataset)

    if not is_authorized(current_user, DatasetPolicy.copy(source_dataset)):
        raise ForbiddenOperationError(
            "You don't have the necessary permissions to copy this dataset. "
            "Only dataset creators or administrators can copy datasets"
        )

    target_dataset = source_dataset.copy()
    target_dataset.name = target_dataset_name
    target_dataset.workspace = target_workspace_name
    target_dataset.created_at = target_dataset.last_updated = datetime.utcnow()
    target_dataset.tags = {**target_dataset.tags, **(copy_request.tags or {})}
    target_dataset.metadata = {
        **target_dataset.metadata,
        **(copy_request.metadata or {}),
        "source_workspace": source_workspace_name,
        "copied_from": source_dataset_name,
    }

    datasets.copy(source_dataset, target_dataset)

    return Dataset.from_orm(target_dataset)
