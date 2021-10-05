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

from fastapi import APIRouter, Depends, Security
from rubrix.server.security import auth
from rubrix.server.security.model import User
from typing import List

from .model import CopyDatasetRequest, Dataset, UpdateDatasetRequest
from .service import DatasetsService, create_dataset_service

router = APIRouter(tags=["datasets"], prefix="/datasets")


@router.get(
    "/",
    response_model=List[Dataset],
    response_model_exclude_none=True,
    operation_id="list_datasets",
)
def list_datasets(
    service: DatasetsService = Depends(create_dataset_service),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> List[Dataset]:
    """
    List accessible user datasets

    Parameters
    ----------
    service:
        The datasets service
    current_user:
        The request user

    Returns
    -------
        A list of datasets visibles by current user
    """
    return service.list(owners=current_user.user_groups)


@router.get(
    "/{name}",
    response_model=Dataset,
    response_model_exclude_none=True,
    operation_id="get_dataset",
)
def get_dataset(
    name: str,
    service: DatasetsService = Depends(create_dataset_service),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> Dataset:
    """
    Find a dataset by name visible for current user

    Parameters
    ----------
    name:
        The dataset name
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
        service.find_by_name(name, owner=current_user.current_group)
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
    service: DatasetsService = Depends(create_dataset_service),
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
    return service.update(name, data=update_request, owner=current_user.current_group)


@router.delete(
    "/{name}",
    operation_id="delete_dataset",
)
def delete_dataset(
    name: str,
    service: DatasetsService = Depends(create_dataset_service),
    current_user: User = Security(auth.get_user, scopes=[]),
):
    """
    Deletes a dataset

    Parameters
    ----------
    name:
        The dataset name
    service:
        The datasets service
    current_user:
        The current user

    """
    service.delete(name, owner=current_user.current_group)


@router.put(
    "/{name}:close",
    operation_id="close_dataset",
)
def close_dataset(
    name: str,
    service: DatasetsService = Depends(create_dataset_service),
    current_user: User = Security(auth.get_user, scopes=[]),
):
    """
    Closes a dataset. This operation will releases backend resources

    Parameters
    ----------
    name:
        The dataset name
    service:
        The datasets service
    current_user:
        The current user

    """
    service.close_dataset(name, owner=current_user.current_group)


@router.put(
    "/{name}:open",
    operation_id="open_dataset",
)
def open_dataset(
    name: str,
    service: DatasetsService = Depends(create_dataset_service),
    current_user: User = Security(auth.get_user, scopes=[]),
):
    """
    Closes a dataset. This operation will releases backend resources

    Parameters
    ----------
    name:
        The dataset name
    service:
        The datasets service
    current_user:
        The current user

    """
    service.open_dataset(name, owner=current_user.current_group)


@router.put(
    "/{name}:copy",
    operation_id="copy_dataset",
    response_model=Dataset,
    response_model_exclude_none=True,
)
def copy_dataset(
    name: str,
    copy_request: CopyDatasetRequest,
    service: DatasetsService = Depends(create_dataset_service),
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
    service:
        The datasets service
    current_user:
        The current user

    """

    return service.copy_dataset(
        name=name, owner=current_user.current_group, data=copy_request
    )
