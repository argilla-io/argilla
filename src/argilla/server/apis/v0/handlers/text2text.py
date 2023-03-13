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

import itertools
from typing import Iterable, Optional

from fastapi import APIRouter, Depends, Query, Security
from fastapi.responses import StreamingResponse

from argilla.server.apis.v0.handlers import metrics
from argilla.server.apis.v0.models.commons.model import BulkResponse
from argilla.server.apis.v0.models.commons.params import (
    CommonTaskHandlerDependencies,
    RequestPagination,
)
from argilla.server.apis.v0.models.text2text import (
    Text2TextBulkRequest,
    Text2TextMetrics,
    Text2TextQuery,
    Text2TextRecord,
    Text2TextSearchAggregations,
    Text2TextSearchRequest,
    Text2TextSearchResults,
)
from argilla.server.commons.config import TasksFactory
from argilla.server.commons.models import TaskType
from argilla.server.errors import EntityNotFoundError
from argilla.server.models import User
from argilla.server.schemas.datasets import CreateDatasetRequest
from argilla.server.security import auth
from argilla.server.services.datasets import DatasetsService, ServiceBaseDataset
from argilla.server.services.tasks.text2text import Text2TextService
from argilla.server.services.tasks.text2text.models import (
    ServiceText2TextQuery,
    ServiceText2TextRecord,
)


def configure_router():
    task_type = TaskType.text2text
    base_endpoint = "/{name}/" + task_type

    TasksFactory.register_task(
        task_type=TaskType.text2text,
        query_request=Text2TextQuery,
        record_class=ServiceText2TextRecord,
        metrics=Text2TextMetrics,
    )

    router = APIRouter(tags=[task_type], prefix="/datasets")

    @router.post(
        path=f"{base_endpoint}:bulk",
        operation_id="bulk_records",
        response_model=BulkResponse,
        response_model_exclude_none=True,
    )
    async def bulk_records(
        name: str,
        bulk: Text2TextBulkRequest,
        common_params: CommonTaskHandlerDependencies = Depends(),
        service: Text2TextService = Depends(Text2TextService.get_instance),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        current_user: User = Security(auth.get_current_user),
    ) -> BulkResponse:
        task = task_type
        workspace = common_params.workspace
        try:
            dataset = datasets.find_by_name(
                current_user,
                name=name,
                task=task,
                workspace=workspace,
            )
            datasets.update(
                user=current_user,
                dataset=dataset,
                tags=bulk.tags,
                metadata=bulk.metadata,
            )
        except EntityNotFoundError:
            dataset = CreateDatasetRequest(name=name, workspace=workspace, task=task, **bulk.dict())
            dataset = datasets.create_dataset(user=current_user, dataset=dataset)

        result = await service.add_records(
            dataset=dataset,
            records=[ServiceText2TextRecord.parse_obj(r) for r in bulk.records],
        )
        return BulkResponse(
            dataset=name,
            processed=result.processed,
            failed=result.failed,
        )

    @router.post(
        path=f"{base_endpoint}:search",
        response_model=Text2TextSearchResults,
        response_model_exclude_none=True,
        operation_id="search_records",
    )
    def search_records(
        name: str,
        search: Text2TextSearchRequest = None,
        common_params: CommonTaskHandlerDependencies = Depends(),
        include_metrics: bool = Query(False, description="If enabled, return related record metrics"),
        pagination: RequestPagination = Depends(),
        service: Text2TextService = Depends(Text2TextService.get_instance),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        current_user: User = Security(auth.get_current_user),
    ) -> Text2TextSearchResults:
        search = search or Text2TextSearchRequest()
        query = search.query or Text2TextQuery()
        dataset = datasets.find_by_name(
            user=current_user,
            name=name,
            task=task_type,
            workspace=common_params.workspace,
        )
        result = service.search(
            dataset=dataset,
            query=ServiceText2TextQuery.parse_obj(query),
            sort_by=search.sort,
            record_from=pagination.from_,
            size=pagination.limit,
            exclude_metrics=not include_metrics,
        )

        return Text2TextSearchResults(
            total=result.total,
            records=[Text2TextRecord.parse_obj(r) for r in result.records],
            aggregations=Text2TextSearchAggregations.parse_obj(result.metrics) if result.metrics else None,
        )

    metrics.configure_router(
        router,
        cfg=TasksFactory.get_task_by_task_type(task_type),
    )

    return router


router = configure_router()
