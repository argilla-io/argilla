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

from rubrix.server.apis.v0.config.tasks_factory import TaskFactory
from rubrix.server.apis.v0.models.commons.workspace import CommonTaskQueryParams
from rubrix.server.apis.v0.models.datasets import (
    CopyDatasetRequest,
    Dataset,
    DatasetCreate,
    UpdateDatasetRequest,
)
from rubrix.server.errors import EntityNotFoundError
from rubrix.server.security import auth
from rubrix.server.security.model import User
from rubrix.server.services.datasets import DatasetsService

router = APIRouter(tags=["datasets"], prefix="/datasets")


@router.get(
    "/",
    response_model=List[Dataset],
    response_model_exclude_none=True,
    operation_id="list_datasets",
)
def list_datasets(
    ds_params: CommonTaskQueryParams = Depends(),
    service: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> List[Dataset]:
    """
    List accessible user datasets

    Parameters
    ----------
    ds_params:
        Common task query params
    service:
        The datasets service
    current_user:
        The request user

    Returns
    -------
        A list of datasets visible by current user
    """
    return service.list(
        user=current_user,
        workspaces=[ds_params.workspace] if ds_params.workspace is not None else None,
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
    request: DatasetCreate = Body(..., description=f"The request dataset info"),
    ws_params: CommonTaskQueryParams = Depends(),
    datasets: DatasetsService = Depends(DatasetsService.get_instance),
    user: User = Security(auth.get_user, scopes=["create:datasets"]),
) -> Dataset:

    owner = user.check_workspace(ws_params.workspace)

    dataset_class = TaskFactory.get_task_dataset(request.task)
    task_mappings = TaskFactory.get_task_mappings(request.task)

    dataset = dataset_class.parse_obj({**request.dict()})
    dataset.owner = owner

    response = datasets.create_dataset(
        user=user, dataset=dataset, mappings=task_mappings
    )

    return Dataset.parse_obj(response)


@router.get(
    "/{name}",
    response_model=Dataset,
    response_model_exclude_none=True,
    operation_id="get_dataset",
)
def get_dataset(
    name: str,
    ds_params: CommonTaskQueryParams = Depends(),
    service: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> Dataset:
    """
    Find a dataset by name visible for current user

    Parameters
    ----------
    name:
        The dataset name
    ds_params:
        Common dataset query params
    service:
        Datasets service
    current_user:
        The current user

    Returns
    -------
        - The found dataset if accessible or exists.
        - EntityNotFoundError if not found.
        - NotAuthorizedError if user cannot access the found dataset

    """
    return Dataset.parse_obj(
        service.find_by_name(
            user=current_user, name=name, workspace=ds_params.workspace
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
    update_request: UpdateDatasetRequest,
    ds_params: CommonTaskQueryParams = Depends(),
    service: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> Dataset:
    """
    Update a set of parameters for a dataset

    Parameters
    ----------
    name:
        The dataset name
    update_request:
        The fields to update
    ds_params:
        Common dataset query params
    service:
        The datasets service
    current_user:
        The current user

    Returns
    -------

    - The updated dataset if exists and user has access.
    - EntityNotFoundError if not found.
    - NotAuthorizedError if user cannot access the found dataset

    """

    found_ds = service.find_by_name(
        user=current_user, name=name, workspace=ds_params.workspace
    )

    return service.update(
        user=current_user,
        dataset=found_ds,
        tags=update_request.tags,
        metadata=update_request.metadata,
    )


@router.delete(
    "/{name}",
    operation_id="delete_dataset",
)
def delete_dataset(
    name: str,
    ds_params: CommonTaskQueryParams = Depends(),
    service: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
):
    """
    Deletes a dataset

    Parameters
    ----------
    name:
        The dataset name
    ds_params:
        Common dataset query params
    service:
        The datasets service
    current_user:
        The current user

    """
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
    ds_params: CommonTaskQueryParams = Depends(),
    service: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
):
    """
    Closes a dataset. This operation will releases backend resources

    Parameters
    ----------
    name:
        The dataset name
    ds_params:
        Common dataset query params
    service:
        The datasets service
    current_user:
        The current user

    """
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
    ds_params: CommonTaskQueryParams = Depends(),
    service: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
):
    """
    Closes a dataset. This operation will releases backend resources

    Parameters
    ----------
    name:
        The dataset name
    ds_params:
        Common dataset query params
    service:
        The datasets service
    current_user:
        The current user

    """
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
    ds_params: CommonTaskQueryParams = Depends(),
    service: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> Dataset:
    """
    Creates a dataset copy and its tags/metadata info

    Parameters
    ----------
    name:
        The dataset name
    copy_request:
        The copy request data
    ds_params:
        Common dataset query params
    service:
        The datasets service
    current_user:
        The current user

    """
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
