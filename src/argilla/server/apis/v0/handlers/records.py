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

from typing import Optional, Union

from fastapi import APIRouter, Depends, Query, Security
from pydantic import BaseModel

from argilla.client.sdk.token_classification.models import TokenClassificationQuery
from argilla.server.apis.v0.models.commons.params import CommonTaskHandlerDependencies
from argilla.server.apis.v0.models.text2text import Text2TextQuery, Text2TextRecord
from argilla.server.apis.v0.models.text_classification import (
    TextClassificationQuery,
    TextClassificationRecord,
)
from argilla.server.apis.v0.models.token_classification import TokenClassificationRecord
from argilla.server.commons.config import TasksFactory
from argilla.server.models import User
from argilla.server.security import auth
from argilla.server.services.datasets import DatasetsService
from argilla.server.services.search.service import SearchRecordsService
from argilla.server.services.storage.service import RecordsStorageService


def configure_router(router: APIRouter):
    QueryType = Union[TextClassificationQuery, TokenClassificationQuery, Text2TextQuery]

    class DeleteRecordsResponse(BaseModel):
        matched: int
        processed: int

    RecordType = Union[
        TextClassificationRecord,
        TokenClassificationRecord,
        Text2TextRecord,
    ]

    @router.get("/{name}/records/{id}", response_model=RecordType)
    async def get_dataset_record(
        name: str,
        id: str,
        request_deps: CommonTaskHandlerDependencies = Depends(),
        service: DatasetsService = Depends(DatasetsService.get_instance),
        search: SearchRecordsService = Depends(SearchRecordsService.get_instance),
        current_user: User = Security(auth.get_current_user),
    ) -> RecordType:
        found = service.find_by_name(
            user=current_user,
            name=name,
            workspace=request_deps.workspace,
        )

        record_class = TasksFactory.get_task_record(found.task)

        return await search.find_record_by_id(
            dataset=found,
            id=id,
            record_type=record_class,
        )

    @router.delete(
        "/{name}/data",
        operation_id="delete_dataset_records",
        response_model=DeleteRecordsResponse,
    )
    async def delete_dataset_records(
        name: str,
        query: Optional[QueryType] = None,
        mark_as_discarded: bool = Query(
            default=False,
            title="If True, matched records won't be deleted."
            " Instead of that, the record status will be changed to `Discarded`",
        ),
        request_deps: CommonTaskHandlerDependencies = Depends(),
        service: DatasetsService = Depends(DatasetsService.get_instance),
        storage: RecordsStorageService = Depends(RecordsStorageService.get_instance),
        current_user: User = Security(auth.get_current_user),
    ):
        found = service.find_by_name(
            user=current_user,
            name=name,
            workspace=request_deps.workspace,
        )

        result = await storage.delete_records(
            user=current_user,
            dataset=found,
            query=query,
            mark_as_discarded=mark_as_discarded,
        )

        return DeleteRecordsResponse(
            matched=result.processed,
            processed=result.deleted or result.discarded,
        )


router = APIRouter(tags=["datasets"], prefix="/datasets")
configure_router(router)
