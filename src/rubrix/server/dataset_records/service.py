import re
from typing import List, Optional

from fastapi import Depends
from rubrix.server.commons.helpers import detect_language
from rubrix.server.datasets.service import DatasetsService, create_dataset_service

from .dao import (
    DatasetRecordsDAO,
    LanguageWords,
    MultiTaskRecordDB,
    MultiTaskSearch,
    MultiTaskSearchResult,
    TaskSearch,
    create_dataset_records_dao,
)
from .es_helpers import filters, sort_list
from .model import (
    AddRecordsResponse,
    MultiTaskRecord,
    MultiTaskRecordSearchQuery,
    MultiTaskSortParam,
    MultitaskRecordSearchResults,
    RecordSearchAggregations,
    TaskMeta,
    WordCloudAggregations,
)


class DatasetRecordsService:
    """Dataset records operations service"""

    def __init__(
        self,
        datasets: DatasetsService,
        dao: DatasetRecordsDAO,
    ):
        self.__datasets__ = datasets
        self.__dao__ = dao

    def add_records(
        self,
        dataset: str,
        owner: Optional[str],
        records: List[MultiTaskRecord],
    ) -> AddRecordsResponse:
        """
        Adds a set of multitask records into a dataset

        Parameters
        ----------
        dataset:
            The dataset name
        owner:
            The dataset owner. Optional
        records:
            The multitask records batch

        Returns
        -------
            Response include processed and failed records
        """

        dataset = self.__datasets__.find_by_name(dataset, owner=owner)

        failed = self.__dao__.add_records(
            dataset=dataset,
            records=[
                _record_2_db_record(record, owner=dataset.owner) for record in records
            ],
        )
        return AddRecordsResponse(processed=len(records), failed=failed)

    def search(
        self,
        dataset: str,
        owner: Optional[str],
        search: MultiTaskRecordSearchQuery,
        record_from: int = 0,
        size: int = 100,
        sort: Optional[List[MultiTaskSortParam]] = None,
    ) -> MultitaskRecordSearchResults:
        """
        Run a search in a dataset

        Parameters
        ----------
        dataset:
            The dataset name
        owner:
            The dataset owner
        search:
            The search parameters
        record_from:
            The record from return results
        size:
            The max number of records to return
        sort:
            Sort order configuration

        Returns
        -------
            The matched records with aggregation info for specified task_meta.py

        """
        dataset = self.__datasets__.find_by_name(dataset, owner=owner)
        configured_tasks = [search.task_meta(t) for t in search.tasks]

        results = self.__dao__.search_records(
            dataset,
            search=_service_search_2_dao_search(search),
            size=size,
            record_from=record_from,
            sort=sort_list(sort),
        )
        return _dao_results_2_service_results(results, tasks=configured_tasks)


def _record_2_db_record(
    record: MultiTaskRecord, owner: Optional[str]
) -> MultiTaskRecordDB:
    """
    Converts a service multi task record into a dao multi task record

    Parameters
    ----------
    record:
        The input record
    owner:
        The dataset owner

    Returns
    -------

    A instance of `MultiTaskRecordDB`

    """

    record_lang = detect_language(record.relevant_text) or "en"

    return MultiTaskRecordDB(
        **record.dict(by_alias=True),
        language_words=LanguageWords(**{record_lang: record.relevant_text}),
        tasks={
            task.value: {**record.task_info(task).dict(), "owner": owner}
            for task in record.tasks
        },
    )


def _service_search_2_dao_search(
    search: MultiTaskRecordSearchQuery,
) -> MultiTaskSearch:
    """
    Builds a dao search data from service search definition

    Parameters
    ----------
    search:
        The service search definition

    Returns
    -------

    An instance of `MultiTaskSearch` ready for a search at dao level

    """
    _search = MultiTaskSearch(
        text_query=filters.text_query(search.text_query),
        metadata_filters=search.metadata,
    )

    for task in search.tasks:
        task_meta = search.task_meta(task)
        _search.tasks.append(
            TaskSearch(
                task=task_meta.task.value,
                filters=task_meta.filters.as_elasticsearch(),
                aggregations=task_meta.aggregations.elasticsearch_aggregations(),
            )
        )

    return _search


_DEFAULT_TOKENIZATION_PATTERN = re.compile(r"\s+")


def _record_db_2_record(
    db_record: MultiTaskRecordDB, _tasks: List[TaskMeta]
) -> MultiTaskRecord:
    """
    Builds a service record from a db record
    Parameters
    ----------
    db_record:
        The database record data
    _tasks:
        List of task to extract info from db record

    Returns
    -------
    A `MultiTaskRecord` instance
    """

    def _normalize_record_inputs(_record: MultiTaskRecord):
        """Normalize record inputs, filling missing inputs"""
        text = list(_record.text.values()) if _record.text else []
        if not _record.tokens:
            _record.tokens = _DEFAULT_TOKENIZATION_PATTERN.split("\n".join(text))
        if not _record.raw_text:
            _record.raw_text = (
                "".join(text) if len(text) == 1 else " ".join(_record.tokens)
            )
        if not _record.text:
            _record.text = {"text": _record.raw_text}

    record = MultiTaskRecord(
        **db_record.dict(),
    )

    for meta in _tasks:
        record.with_task_info(meta.task_info(**db_record.tasks.get(meta.task, {})))

    # Creates defaults inputs for handle multiple tasks
    _normalize_record_inputs(record)

    return record


def _dao_results_2_service_results(
    results: MultiTaskSearchResult, tasks: List[TaskMeta]
) -> MultitaskRecordSearchResults:
    """
    Build search results from dao response

    Parameters
    ----------
    results:
        The dao search response
    tasks:
        Tasks to extract information from the response

    Returns
    -------
        A instance of `MultitaskRecordSearchResults`

    """

    def _aggregations_from_dao_results(
        result: MultiTaskSearchResult, _tasks: List[TaskMeta]
    ) -> RecordSearchAggregations:
        """Build service aggregations from dao results"""

        aggregations = RecordSearchAggregations(
            words_cloud=result.language_word_clouds or WordCloudAggregations(),
            metadata_aggregations=result.metadata or {},
        )
        for meta in _tasks:
            task_aggregations_results = result.aggregations.get(meta.task, {})
            task_aggregations = meta.aggregations(**task_aggregations_results)
            aggregations.set_task_aggregations(
                meta.task,
                aggregations=task_aggregations,
            )

        return aggregations

    return MultitaskRecordSearchResults(
        total=results.total,
        records=[_record_db_2_record(r, _tasks=tasks) for r in results.records],
        aggregations=_aggregations_from_dao_results(results, _tasks=tasks),
    )


_instance = None


def create_dataset_records_service(
    datasets: DatasetsService = Depends(create_dataset_service),
    dao: DatasetRecordsDAO = Depends(create_dataset_records_dao),
) -> DatasetRecordsService:
    """
    Creates a dataset record service instance

    Parameters
    ----------
    datasets:
        The datasets service dependency
    dao:
        The dataset records dao dependency

    Returns
    -------
        A dataset records service instance
    """
    global _instance
    if not _instance:
        _instance = DatasetRecordsService(datasets=datasets, dao=dao)
    return _instance
