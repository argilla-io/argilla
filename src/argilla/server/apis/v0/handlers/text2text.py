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
    Text2TextDataset,
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
from argilla.server.helpers import takeuntil
from argilla.server.responses import StreamingResponseWithErrorHandling
from argilla.server.security import auth
from argilla.server.security.model import User
from argilla.server.services.datasets import DatasetsService
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
        dataset_class=Text2TextDataset,
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
        current_user: User = Security(auth.get_user, scopes=[]),
    ) -> BulkResponse:

        task = task_type
        owner = current_user.check_workspace(common_params.workspace)
        try:
            dataset = datasets.find_by_name(
                current_user,
                name=name,
                task=task,
                workspace=owner,
                as_dataset_class=TasksFactory.get_task_dataset(task_type),
            )
            datasets.update(
                user=current_user,
                dataset=dataset,
                tags=bulk.tags,
                metadata=bulk.metadata,
            )
        except EntityNotFoundError:
            dataset_class = TasksFactory.get_task_dataset(task)
            dataset = dataset_class.parse_obj({**bulk.dict(), "name": name})
            dataset.owner = owner
            datasets.create_dataset(user=current_user, dataset=dataset)

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
        include_metrics: bool = Query(
            False, description="If enabled, return related record metrics"
        ),
        pagination: RequestPagination = Depends(),
        service: Text2TextService = Depends(Text2TextService.get_instance),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        current_user: User = Security(auth.get_user, scopes=[]),
    ) -> Text2TextSearchResults:

        search = search or Text2TextSearchRequest()
        query = search.query or Text2TextQuery()
        dataset = datasets.find_by_name(
            user=current_user,
            name=name,
            task=task_type,
            workspace=common_params.workspace,
            as_dataset_class=TasksFactory.get_task_dataset(task_type),
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
            aggregations=Text2TextSearchAggregations.parse_obj(result.metrics)
            if result.metrics
            else None,
        )

    def scan_data_response(
        data_stream: Iterable[Text2TextRecord],
        chunk_size: int = 1000,
        limit: Optional[int] = None,
    ) -> StreamingResponseWithErrorHandling:
        """Generate an textual stream data response for a dataset scan"""

        async def stream_generator(stream):
            """Converts dataset scan into a text stream"""

            def grouper(n, iterable, fillvalue=None):
                args = [iter(iterable)] * n
                return itertools.zip_longest(fillvalue=fillvalue, *args)

            if limit:
                stream = takeuntil(stream, limit=limit)

            for batch in grouper(
                n=chunk_size,
                iterable=stream,
            ):
                filtered_records = filter(lambda r: r is not None, batch)
                yield "\n".join(
                    map(
                        lambda r: r.json(by_alias=True, exclude_none=True),
                        filtered_records,
                    )
                ) + "\n"

        return StreamingResponseWithErrorHandling(
            stream_generator(data_stream), media_type="application/json"
        )

    @router.post(
        path=f"{base_endpoint}/data",
        operation_id="stream_data",
    )
    async def stream_data(
        name: str,
        query: Optional[Text2TextQuery] = None,
        common_params: CommonTaskHandlerDependencies = Depends(),
        limit: Optional[int] = Query(None, description="Limit loaded records", gt=0),
        service: Text2TextService = Depends(Text2TextService.get_instance),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        current_user: User = Security(auth.get_user, scopes=[]),
        id_from: Optional[str] = None,
    ) -> StreamingResponse:
        """
            Creates a data stream over dataset records

        Parameters
        ----------
        name
            The dataset name
        query:
            The stream data query
        common_params:
            The task common query params
        limit:
            The load number of records limit. Optional
        service:
            The dataset records service
        datasets:
            The datasets service
        current_user:
            Request user
        id_from:
            If provided, read the samples after this record ID

        """
        query = query or Text2TextQuery()
        dataset = datasets.find_by_name(
            user=current_user,
            name=name,
            task=task_type,
            workspace=common_params.workspace,
            as_dataset_class=TasksFactory.get_task_dataset(task_type),
        )
        data_stream = map(
            Text2TextRecord.parse_obj,
            service.read_dataset(
                dataset,
                query=ServiceText2TextQuery.parse_obj(query),
                id_from=id_from,
                limit=limit,
            ),
        )
        return scan_data_response(
            data_stream=data_stream,
            limit=limit,
        )

    metrics.configure_router(
        router,
        cfg=TasksFactory.get_task_by_task_type(task_type),
    )

    return router


router = configure_router()
