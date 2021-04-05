from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from rubrix.server.commons.models import BulkResponse, PaginationParams, TaskType
from rubrix.server.dataset_records import scan_data_response
from rubrix.server.dataset_records.model import (
    MultiTaskRecord,
    MultiTaskRecordSearchQuery,
    MultiTaskSortParam,
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
    base_endpoint + "/:search",
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
        records=[
            TokenClassificationRecord(
                **record.dict(by_alias=True),
                **record.task_info(task_meta.task).dict(by_alias=True),
            )
            for record in result.records
        ],
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
    base_endpoint + "/:bulk",
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


class TokenClassificationRecordsBulk(TokenClassificationBulkData):
    """A API backward compatibility data model for bulk records endpoint"""

    name: str


@router.post(
    "/token-classification/datasets/:bulk-records",
    deprecated=True,
    response_model=BulkResponse,
    response_model_exclude_none=True,
    operation_id="bulk_records_deprecated",
)
def bulk_records_deprecated(
    bulk: TokenClassificationRecordsBulk,
    datasets: DatasetsService = Depends(create_dataset_service),
    service: DatasetRecordsService = Depends(create_dataset_records_service),
    current_user: User = Depends(get_current_active_user),
) -> BulkResponse:
    """
    Deprecated endpoint for token classification bulk

    Parameters
    ----------
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
    return bulk_records(
        name=bulk.name,
        bulk=bulk,
        datasets=datasets,
        service=service,
        current_user=current_user,
    )


@router.post(
    "/token-classification/datasets/{name}/:search",
    operation_id="search_records_deprecated",
    deprecated=True,
    response_model=TokenClassificationSearchResults,
    response_model_exclude_none=True,
)
def search_records_deprecated(
    name: str,
    search: TokenClassificationSearchRequest = None,
    pagination: PaginationParams = Depends(),
    datasets: DatasetsService = Depends(create_dataset_service),
    service: DatasetRecordsService = Depends(create_dataset_records_service),
    current_user: User = Depends(get_current_active_user),
) -> TokenClassificationSearchResults:
    """Deprecated endpoint for token classification search"""
    return search_records(
        name=name,
        search=search,
        pagination=pagination,
        datasets=datasets,
        service=service,
        current_user=current_user,
    )


@router.get(
    base_endpoint + "/data",
    operation_id="get_dataset_data",
)
async def get_dataset_data(
    name: str,
    service: DatasetRecordsService = Depends(create_dataset_records_service),
    current_user: User = Depends(get_current_active_user),
) -> StreamingResponse:
    """
    Creates a data stream over dataset records

    Parameters
    ----------
    name
        The dataset name
    service:
        The dataset records service
    current_user:
        Request user

    """
    return scan_data_response(
        service,
        dataset=name,
        owner=current_user.current_group,
        tasks=[TokenClassificationTask],
    )
