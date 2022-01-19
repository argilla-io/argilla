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

from rubrix.server.commons.api import CommonTaskQueryParams
from rubrix.server.datasets.model import CreationDatasetRequest, Dataset
from rubrix.server.datasets.service import DatasetsService
from rubrix.server.security import auth
from rubrix.server.security.model import User
from rubrix.server.tasks.commons.api import BulkResponse, PaginationParams, TaskType
from rubrix.server.tasks.commons.helpers import takeuntil
from rubrix.server.tasks.text2text.api.model import (
    Text2TextBulkData,
    Text2TextQuery,
    Text2TextRecord,
    Text2TextSearchRequest,
    Text2TextSearchResults,
)
from rubrix.server.tasks.text2text.service.service import (
    Text2TextService,
    text2text_service,
)

TASK_TYPE = TaskType.text2text
BASE_ENDPOINT = "/{name}/" + TASK_TYPE

router = APIRouter(tags=[TASK_TYPE], prefix="/datasets")


@router.post(
    BASE_ENDPOINT + ":bulk",
    operation_id="bulk_records",
    response_model=BulkResponse,
    response_model_exclude_none=True,
)
def bulk_records(
    name: str,
    bulk: Text2TextBulkData,
    common_params: CommonTaskQueryParams = Depends(),
    service: Text2TextService = Depends(text2text_service),
    datasets: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> BulkResponse:
    """
    Includes a chunk of record data with provided dataset bulk information

    Parameters
    ----------
    name:
        The dataset name
    bulk:
        The bulk data
    common_params:
        Common task query params
    service:
        the Service
    datasets:
        The dataset service
    current_user:
        Current request user

    Returns
    -------
        Bulk response data
    """

    task = TASK_TYPE
    dataset = datasets.upsert(
        CreationDatasetRequest(**{**bulk.dict(), "name": name}),
        task=task,
        user=current_user,
        workspace=common_params.workspace,
    )
    result = service.add_records(
        dataset=dataset,
        records=bulk.records,
    )
    return BulkResponse(
        dataset=name,
        processed=result.processed,
        failed=result.failed,
    )


@router.post(
    BASE_ENDPOINT + ":search",
    response_model=Text2TextSearchResults,
    response_model_exclude_none=True,
    operation_id="search_records",
)
def search_records(
    name: str,
    search: Text2TextSearchRequest = None,
    common_params: CommonTaskQueryParams = Depends(),
    include_metrics: bool = Query(
        False, description="If enabled, return related record metrics"
    ),
    pagination: PaginationParams = Depends(),
    service: Text2TextService = Depends(text2text_service),
    datasets: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> Text2TextSearchResults:
    """
    Searches data from dataset

    Parameters
    ----------
    name:
        The dataset name
    common_params:
        The task common query params
    include_metrics:
        Flag to include metrics in results
    search:
        THe search query request
    pagination:
        The pagination params
    service:
        The dataset records service
    datasets:
        The dataset service
    current_user:
        The current request user

    Returns
    -------
        The search results data

    """

    search = search or Text2TextSearchRequest()
    query = search.query or Text2TextQuery()
    dataset = datasets.find_by_name(
        name, task=TASK_TYPE, user=current_user, workspace=common_params.workspace
    )
    result = service.search(
        dataset=Dataset.parse_obj(dataset),
        query=query,
        sort_by=search.sort,
        record_from=pagination.from_,
        size=pagination.limit,
        exclude_metrics=not include_metrics,
    )

    return result


def scan_data_response(
    data_stream: Iterable[Text2TextRecord],
    chunk_size: int = 1000,
    limit: Optional[int] = None,
) -> StreamingResponse:
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
                    lambda r: r.json(by_alias=True, exclude_none=True), filtered_records
                )
            ) + "\n"

    return StreamingResponse(
        stream_generator(data_stream), media_type="application/json"
    )


@router.post(
    BASE_ENDPOINT + "/data",
    operation_id="stream_data",
)
async def stream_data(
    name: str,
    query: Optional[Text2TextQuery] = None,
    common_params: CommonTaskQueryParams = Depends(),
    limit: Optional[int] = Query(None, description="Limit loaded records", gt=0),
    service: Text2TextService = Depends(text2text_service),
    datasets: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
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

    """
    query = query or Text2TextQuery()
    dataset = datasets.find_by_name(
        name, task=TASK_TYPE, user=current_user, workspace=common_params.workspace
    )
    data_stream = service.read_dataset(Dataset.parse_obj(dataset), query=query)

    return scan_data_response(
        data_stream=data_stream,
        limit=limit,
    )
