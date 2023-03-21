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

from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, Depends, Security
from pydantic import BaseModel

from argilla.server.apis.v0.models.commons.params import CommonTaskHandlerDependencies
from argilla.server.apis.v0.models.text2text import Text2TextRecord
from argilla.server.apis.v0.models.text_classification import TextClassificationRecord
from argilla.server.apis.v0.models.token_classification import TokenClassificationRecord
from argilla.server.commons.config import TasksFactory
from argilla.server.commons.models import TaskStatus, TaskType
from argilla.server.daos.backend import GenericElasticEngineBackend
from argilla.server.errors import EntityNotFoundError
from argilla.server.schemas.datasets import Dataset
from argilla.server.security import auth
from argilla.server.security.model import User
from argilla.server.services.datasets import DatasetsService
from argilla.server.services.search.service import SearchRecordsService
from argilla.server.services.storage.service import RecordsStorageService
from argilla.server.services.tasks.text2text.models import ServiceText2TextRecord
from argilla.server.services.tasks.text_classification.model import (
    ServiceTextClassificationRecord,
)
from argilla.server.services.tasks.token_classification.model import (
    ServiceTokenClassificationRecord,
)


def configure_router(router: APIRouter):
    RecordType = Union[
        TextClassificationRecord,
        TokenClassificationRecord,
        Text2TextRecord,
    ]

    class PartialUpdateRequest(BaseModel):
        metadata: Optional[Dict[str, Any]] = None
        status: Optional[TaskStatus] = None

    @router.patch(
        "/{name}/records/{record_id}",
        response_model=RecordType,
    )
    async def partial_update_dataset_record(
        name: str,
        record_id: str,
        request: PartialUpdateRequest,
        request_deps: CommonTaskHandlerDependencies = Depends(),
        service: DatasetsService = Depends(DatasetsService.get_instance),
        search: SearchRecordsService = Depends(SearchRecordsService.get_instance),
        storage: RecordsStorageService = Depends(RecordsStorageService.get_instance),
        current_user: User = Security(auth.get_user, scopes=[]),
    ) -> RecordType:
        dataset = service.find_by_name(
            user=current_user,
            name=name,
            workspace=request_deps.workspace,
        )

        record_class = TasksFactory.get_task_record(dataset.task)
        record = await search.find_record_by_id(
            dataset=dataset,
            id=record_id,
            record_type=record_class,
        )

        return await storage.update_record(
            dataset=dataset,
            record=record,
            metadata=request.metadata,
            status=request.status,
        )

    class PartialRecord(BaseModel):
        id: str
        data: dict

    class BatchUpdateRecords(BaseModel):
        records: List[PartialRecord]

    class BatchUpdateResult(BaseModel):
        updated: int
        not_found_ids: List[str]

    @router.post("/{dataset_id}/records/:batch-update")
    async def batch_update_dataset_records(
        dataset_id: str,
        request: BatchUpdateRecords,
        engine: GenericElasticEngineBackend = Depends(GenericElasticEngineBackend.get_instance),
        storage: RecordsStorageService = Depends(RecordsStorageService.get_instance),
    ) -> BatchUpdateResult:
        dataset = engine.find_dataset(id=dataset_id)
        if not dataset:
            raise EntityNotFoundError(name=dataset_id, type="Dataset")

        dataset = Dataset.parse_obj(dataset)
        if dataset.task == TaskType.text_classification:
            record_class = ServiceTextClassificationRecord
        elif dataset.task == TaskType.token_classification:
            record_class = ServiceTokenClassificationRecord
        elif dataset.task == TaskType.text2text:
            record_class = ServiceText2TextRecord
        else:
            raise ValueError(f"Task {dataset.task} not supported")

        stored_records = engine.find_record_by_ids(dataset_id, [record.id for record in request.records])

        records_update = []
        records_not_found = []

        for stored_record, partial_record in zip(stored_records, request.records):
            record_id, record = stored_record

            if record is None:
                records_not_found.append(record_id)
                continue

            record = record_class.parse_obj({**record, **partial_record.data})
            records_update.append(record)

        await storage.store_records(dataset=dataset, records=records_update, record_type=record_class)

        return BatchUpdateResult(updated=len(records_update), not_found_ids=records_not_found)


router = APIRouter(tags=["records"], prefix="/datasets")
configure_router(router)
