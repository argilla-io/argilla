from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from rubrix.server.commons.models import BulkResponse, PaginationParams, TaskType
from rubrix.server.dataset_records import scan_data_response
from rubrix.server.dataset_records.model import (
    MultiTaskRecord,
    MultiTaskRecordSearchQuery,
    MultiTaskSortParam,
    StreamDataRequest,
    TaskMeta,
)
from rubrix.server.dataset_records.service import (
    DatasetRecordsService,
    create_dataset_records_service,
)
from rubrix.server.datasets.model import CreationDatasetRequest
from rubrix.server.datasets.service import DatasetsService, create_dataset_service
from rubrix.server.security.api import get_current_active_user
from rubrix.server.users.model import User

from .model import (
    CreationTokenClassificationRecord,
    DefaultTaskSearchFilters,
    TokenClassificationAggregations,
    TokenClassificationBulkData,
    TokenClassificationQuery,
    TokenClassificationRecord,
    TokenClassificationSearchRequest,
    TokenClassificationSearchResults,
    TokenClassificationTask,
)

router = APIRouter(tags=[TaskType.token_classification])

base_endpoint = "/datasets/{name}/" + TaskType.token_classification


@router.post(
    base_endpoint + ":search",
    response_model=TokenClassificationSearchResults,
    response_model_exclude_none=True,
    operation_id="search_records",
)
def search_records(
    name: str,
    search: TokenClassificationSearchRequest = None,
    pagination: PaginationParams = Depends(),
    datasets: DatasetsService = Depends(create_dataset_service),
    service: DatasetRecordsService = Depends(create_dataset_records_service),
    current_user: User = Depends(get_current_active_user),
) -> TokenClassificationSearchResults:
    """

    Parameters
    ----------
    name:
        The dataset name
    search:
        The query search data
    pagination:
        The search pagination info
    datasets:
        The datasets service
    service:
        The dataset records service
    current_user:
        The current request user

    Returns
    -------
        The search results
    """

    datasets.find_by_name(name, owner=current_user.current_group)
    search = search or TokenClassificationSearchRequest()
    query = search.query or TokenClassificationQuery()
    sort = search.sort or []

    task_meta = TaskMeta(
        filters=DefaultTaskSearchFilters.parse_obj(query),
        task_info=TokenClassificationTask,
    )

    result = service.search(
        name,
        owner=current_user.current_group,
        search=MultiTaskRecordSearchQuery(
            text_query=query.text_query,
            metadata=query.metadata or {},
        ).with_task(task_meta),
        record_from=pagination.from_,
        size=pagination.limit,
        sort=[
            MultiTaskSortParam(
                **s.dict(), task=None if s.by.startswith("metadata") else task_meta.task
            )
            for s in sort
        ],
    )

    return TokenClassificationSearchResults(
        records=list(map(_multi_task_record_2_token_classification, result.records)),
        total=result.total,
        aggregations=TokenClassificationAggregations(
            **result.aggregations.task_aggregations(task=task_meta.task).dict(
                by_alias=True
            ),
            metadata=result.aggregations.metadata_aggregations,
            words=result.aggregations.words_cloud,
        )
        if result.aggregations
        else None,
    )


@router.post(
    base_endpoint + ":bulk",
    operation_id="bulk_records",
    response_model=BulkResponse,
    response_model_exclude_none=True,
)
def bulk_records(
    name: str,
    bulk: TokenClassificationBulkData,
    datasets: DatasetsService = Depends(create_dataset_service),
    service: DatasetRecordsService = Depends(create_dataset_records_service),
    current_user: User = Depends(get_current_active_user),
) -> BulkResponse:
    """
    Set a chunk of records data with provided dataset bulk information.

    If dataset does not exists, this bulk will create a new one with provided info.

    Parameters
    ----------
    name:
        The dataset name
    bulk:
        The bulk data
    datasets:
        The datasets service
    service:
        The dataset records service
    current_user:
        The current request user

    Returns
    -------
        The bulk response
    """

    task = TaskType.token_classification

    datasets.upsert(
        CreationDatasetRequest(**{**bulk.dict(), "name": name}),
        owner=current_user.current_group,
        task=task,
    )
    result = service.add_records(
        dataset=name,
        owner=current_user.current_group,
        records=[
            MultiTaskRecord(**record.dict()).with_task_info(
                CreationTokenClassificationRecord.parse_obj(record)
            )
            for record in bulk.records
        ],
    )
    return BulkResponse(
        dataset=name,
        processed=result.processed,
        failed=result.failed,
    )


@router.post(
    base_endpoint + "/data",
    operation_id="stream_data",
)
async def stream_data(
    name: str,
    request: Optional[StreamDataRequest] = None,
    limit: int = Query(default=None, description="Limit loaded records", gt=0),
    service: DatasetRecordsService = Depends(create_dataset_records_service),
    datasets: DatasetsService = Depends(create_dataset_service),
    current_user: User = Depends(get_current_active_user),
) -> StreamingResponse:
    """
    Creates a data stream over dataset records

    Parameters
    ----------
    name
        The dataset name
    request:
        The stream data request
    limit:
        The number of records limit. Optional
    service:
        The dataset records service
    datasets:
        The datasets service
    current_user:
        Request user

    """
    datasets.find_by_name(name, owner=current_user.current_group)

    request = request or StreamDataRequest()
    return scan_data_response(
        service,
        dataset=name,
        owner=current_user.current_group,
        tasks=[TokenClassificationTask],
        record_transform=_multi_task_record_2_token_classification,
        limit=limit,
        ids=request.ids,
    )


def _multi_task_record_2_token_classification(
    record: MultiTaskRecord,
) -> TokenClassificationRecord:
    return TokenClassificationRecord(
        **record.dict(by_alias=True),
        **record.task_info(TokenClassificationRecord.task()).dict(by_alias=True),
    )
