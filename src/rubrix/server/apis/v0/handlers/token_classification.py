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

from rubrix.server.apis.v0.config.tasks_factory import TaskFactory
from rubrix.server.apis.v0.handlers import token_classification_dataset_settings
from rubrix.server.apis.v0.models.commons.model import BulkResponse, PaginationParams
from rubrix.server.apis.v0.models.commons.workspace import CommonTaskQueryParams
from rubrix.server.apis.v0.models.token_classification import (
    TokenClassificationAggregations,
    TokenClassificationBulkData,
    TokenClassificationQuery,
    TokenClassificationRecord,
    TokenClassificationSearchRequest,
    TokenClassificationSearchResults,
)
from rubrix.server.apis.v0.validators.token_classification import DatasetValidator
from rubrix.server.commons.models import TaskType
from rubrix.server.errors import EntityNotFoundError
from rubrix.server.helpers import takeuntil
from rubrix.server.responses import StreamingResponseWithErrorHandling
from rubrix.server.security import auth
from rubrix.server.security.model import User
from rubrix.server.services.datasets import DatasetsService
from rubrix.server.services.tasks.token_classification import TokenClassificationService
from rubrix.server.services.tasks.token_classification.model import (
    ServiceTokenClassificationQuery,
    ServiceTokenClassificationRecord,
)

TASK_TYPE = TaskType.token_classification
BASE_ENDPOINT = "/{name}/" + TASK_TYPE

router = APIRouter(tags=[TASK_TYPE], prefix="/datasets")


@router.post(
    BASE_ENDPOINT + ":bulk",
    operation_id="bulk_records",
    response_model=BulkResponse,
    response_model_exclude_none=True,
)
async def bulk_records(
    name: str,
    bulk: TokenClassificationBulkData,
    common_params: CommonTaskQueryParams = Depends(),
    service: TokenClassificationService = Depends(
        TokenClassificationService.get_instance
    ),
    datasets: DatasetsService = Depends(DatasetsService.get_instance),
    validator: DatasetValidator = Depends(DatasetValidator.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> BulkResponse:

    task = TASK_TYPE
    owner = current_user.check_workspace(common_params.workspace)
    try:
        dataset = datasets.find_by_name(
            current_user,
            name=name,
            task=task,
            workspace=owner,
            as_dataset_class=TaskFactory.get_task_dataset(TASK_TYPE),
        )
        datasets.update(
            user=current_user,
            dataset=dataset,
            tags=bulk.tags,
            metadata=bulk.metadata,
        )
    except EntityNotFoundError:
        dataset_class = TaskFactory.get_task_dataset(task)
        dataset = dataset_class.parse_obj({**bulk.dict(), "name": name})
        dataset.owner = owner
        datasets.create_dataset(user=current_user, dataset=dataset)

    await validator.validate_dataset_records(
        user=current_user,
        dataset=dataset,
        records=bulk.records,
    )

    result = service.add_records(
        dataset=dataset,
        records=[ServiceTokenClassificationRecord.parse_obj(r) for r in bulk.records],
        metrics=TaskFactory.get_task_metrics(TASK_TYPE),
    )
    return BulkResponse(
        dataset=name,
        processed=result.processed,
        failed=result.failed,
    )


@router.post(
    BASE_ENDPOINT + ":search",
    response_model=TokenClassificationSearchResults,
    response_model_exclude_none=True,
    operation_id="search_records",
)
def search_records(
    name: str,
    search: TokenClassificationSearchRequest = None,
    common_params: CommonTaskQueryParams = Depends(),
    include_metrics: bool = Query(
        False, description="If enabled, return related record metrics"
    ),
    pagination: PaginationParams = Depends(),
    service: TokenClassificationService = Depends(
        TokenClassificationService.get_instance
    ),
    datasets: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> TokenClassificationSearchResults:

    search = search or TokenClassificationSearchRequest()
    query = search.query or TokenClassificationQuery()

    dataset = datasets.find_by_name(
        user=current_user,
        name=name,
        task=TASK_TYPE,
        workspace=common_params.workspace,
        as_dataset_class=TaskFactory.get_task_dataset(TASK_TYPE),
    )
    results = service.search(
        dataset=dataset,
        query=ServiceTokenClassificationQuery.parse_obj(query),
        sort_by=search.sort,
        record_from=pagination.from_,
        size=pagination.limit,
        exclude_metrics=not include_metrics,
        metrics=TaskFactory.find_task_metrics(
            TASK_TYPE,
            # TODO(@frascuchon): Move out from HERE!
            metric_ids={
                "words_cloud",
                "predicted_by",
                "predicted_as",
                "annotated_by",
                "annotated_as",
                "error_distribution",
                "predicted_mentions_distribution",
                "annotated_mentions_distribution",
                "status_distribution",
                "metadata",
                "score",
            },
        ),
    )

    return TokenClassificationSearchResults(
        total=results.total,
        records=[TokenClassificationRecord.parse_obj(r) for r in results.records],
        aggregations=TokenClassificationAggregations.parse_obj(results.metrics)
        if results.metrics
        else None,
    )


def scan_data_response(
    data_stream: Iterable[TokenClassificationRecord],
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
                    lambda r: r.json(by_alias=True, exclude_none=True), filtered_records
                )
            ) + "\n"

    return StreamingResponseWithErrorHandling(
        stream_generator(data_stream), media_type="application/json"
    )


@router.post(
    BASE_ENDPOINT + "/data",
    operation_id="stream_data",
)
async def stream_data(
    name: str,
    query: Optional[TokenClassificationQuery] = None,
    common_params: CommonTaskQueryParams = Depends(),
    limit: Optional[int] = Query(None, description="Limit loaded records", gt=0),
    service: TokenClassificationService = Depends(
        TokenClassificationService.get_instance
    ),
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
        Common query params
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
    query = query or TokenClassificationQuery()
    dataset = datasets.find_by_name(
        user=current_user,
        name=name,
        task=TASK_TYPE,
        workspace=common_params.workspace,
        as_dataset_class=TaskFactory.get_task_dataset(TASK_TYPE),
    )
    data_stream = map(
        TokenClassificationRecord.parse_obj,
        service.read_dataset(
            dataset=dataset, query=ServiceTokenClassificationQuery.parse_obj(query), id_from=id_from, limit=limit
        ),
    )

    return scan_data_response(
        data_stream=data_stream,
        limit=limit,
    )


token_classification_dataset_settings.configure_router(router)
