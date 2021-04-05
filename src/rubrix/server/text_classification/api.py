import itertools

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
from rubrix.server.text_classification.model.task_meta import (
    TaskSearchFilters,
)
from rubrix.server.users.model import User

from .model import (
    CreationTextClassificationRecord,
    TaskSearchAggregations,
    TextClassificationAggregations,
    TextClassificationBulkData,
    TextClassificationQuery,
    TextClassificationRecord,
    TextClassificationSearchRequest,
    TextClassificationSearchResults,
    TextClassificationTask,
)

router = APIRouter(tags=[TaskType.text_classification])

base_endpoint = "/datasets/{name}/" + TaskType.text_classification


@router.post(
    base_endpoint + "/:bulk",
    operation_id="bulk_records",
    response_model=BulkResponse,
    response_model_exclude_none=True,
)
def bulk_records(
    name: str,
    bulk: TextClassificationBulkData,
    datasets: DatasetsService = Depends(create_dataset_service),
    service: DatasetRecordsService = Depends(create_dataset_records_service),
    current_user: User = Depends(get_current_active_user),
) -> BulkResponse:
    """
    Includes a chunk of record data with provided dataset bulk information

    Parameters
    ----------
    name:
        The dataset name
    bulk:
        The bulk data
    datasets:
        The dataset service
    service:
        The dataset records service
    current_user:
        Current request user

    Returns
    -------

        Bulk response data

    """

    task = TaskType.text_classification

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
                CreationTextClassificationRecord.parse_obj(record)
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
    base_endpoint + "/:search",
    response_model=TextClassificationSearchResults,
    response_model_exclude_none=True,
    operation_id="search_records",
)
def search_records(
    name: str,
    search: TextClassificationSearchRequest = None,
    pagination: PaginationParams = Depends(),
    service: DatasetRecordsService = Depends(create_dataset_records_service),
    datasets: DatasetsService = Depends(create_dataset_service),
    current_user: User = Depends(get_current_active_user),
) -> TextClassificationSearchResults:
    """
    Searches data from dataset

    Parameters
    ----------
    name:
        The dataset name
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

    datasets.find_by_name(name, owner=current_user.current_group)
    search = search or TextClassificationSearchRequest()
    query = search.query or TextClassificationQuery()
    sort = search.sort or []

    task_meta = TaskMeta(
        filters=TaskSearchFilters.parse_obj(query),
        aggregations=TaskSearchAggregations,
        task_info=TextClassificationTask,
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

    return TextClassificationSearchResults(
        total=result.total,
        records=[
            TextClassificationRecord(
                **record.dict(by_alias=True),
                **record.task_info(task_meta.task).dict(by_alias=True),
                inputs=record.text,
            )
            for record in result.records
        ],
        aggregations=TextClassificationAggregations(
            **result.aggregations.task_aggregations(task=task_meta.task).dict(
                by_alias=True
            ),
            metadata=result.aggregations.metadata_aggregations,
            words=result.aggregations.words_cloud,
        )
        if result.aggregations
        else None,
    )


class TextClassificationRecordsBulk(TextClassificationBulkData):
    """
    API backward compatibility data model for bulk record old endpoint

    Attributes:
    -----------

    name:str
        The dataset name

    """

    name: str


@router.post(
    "/classification/datasets/:bulk-records",
    deprecated=True,
    response_model=BulkResponse,
    response_model_exclude_none=True,
    operation_id="bulk_records_deprecated",
)
def bulk_records_deprecated(
    bulk: TextClassificationRecordsBulk,
    datasets: DatasetsService = Depends(create_dataset_service),
    service: DatasetRecordsService = Depends(create_dataset_records_service),
    current_user: User = Depends(get_current_active_user),
) -> BulkResponse:
    """
    Old search endpoint

    Parameters
    ----------
    bulk:
        The bulk data
    datasets:
        The datasets service
    service:
        The dataset records service
    current_user:
        Current request user

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
    "/classification/datasets/{name}/:search",
    operation_id="search_records_deprecated",
    deprecated=True,
    response_model=TextClassificationSearchResults,
    response_model_exclude_none=True,
)
def search_records_deprecated(
    name: str,
    search: TextClassificationSearchRequest = None,
    pagination: PaginationParams = Depends(),
    service: DatasetRecordsService = Depends(create_dataset_records_service),
    datasets: DatasetsService = Depends(create_dataset_service),
    current_user: User = Depends(get_current_active_user),
) -> TextClassificationSearchResults:
    """Deprecated endpoint for text classification search"""
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
        tasks=[TextClassificationTask],
    )
