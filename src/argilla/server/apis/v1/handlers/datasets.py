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

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from argilla.server.contexts import datasets
from argilla.server.database import get_db
from argilla.server.errors import EntityAlreadyExistsError
from argilla.server.policies import DatasetPolicyV1, authorize
from argilla.server.schemas.v1.datasets import Dataset, DatasetCreate
from argilla.server.security import auth
from argilla.server.security.model import User

router = APIRouter(tags=["datasets"])


@router.get("/datasets", response_model=List[Dataset])
def list_datasets(*, db: Session = Depends(get_db), current_user: User = Security(auth.get_current_user)):
    authorize(current_user, DatasetPolicyV1.list)

    if current_user.is_admin:
        return datasets.list_datasets(db)
    else:
        return current_user.datasets


@router.post("/datasets", response_model=Dataset)
def create_dataset(
    *,
    db: Session = Depends(get_db),
    dataset_create: DatasetCreate,
    current_user: User = Security(auth.get_current_user),
):
    authorize(current_user, DatasetPolicyV1.create)

    if datasets.get_dataset_by_name_and_workspace_id(db, dataset_create.name, dataset_create.workspace_id):
        raise EntityAlreadyExistsError(name=dataset_create.name, type=Dataset)

    return datasets.create_dataset(db, dataset_create)
