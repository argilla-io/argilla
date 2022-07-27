from typing import Callable, Optional, Type, TypeVar, Union

from fastapi import Depends

from rubrix.server.apis.v0.models.metrics.base import (
    ElasticsearchMetric,
    NestedPathElasticsearchMetric,
    PythonMetric,
)
from rubrix.server.apis.v0.models.metrics.commons import *
from rubrix.server.daos.models.records import RecordSearch
from rubrix.server.daos.records import DatasetRecordsDAO, dataset_records_dao
from rubrix.server.elasticseach.search.query_builder import EsQueryBuilder
from rubrix.server.errors import WrongInputParamError
from rubrix.server.services.datasets import Dataset
from rubrix.server.services.tasks.commons.record import BaseRecordDB

GenericQuery = TypeVar("GenericQuery")


class MetricsService:
    """The dataset metrics service singleton"""

    _INSTANCE = None

    @classmethod
    def get_instance(
        cls,
        dao: DatasetRecordsDAO = Depends(DatasetRecordsDAO.get_instance),
    ) -> "MetricsService":
        """
        Creates the service instance.

        Parameters
        ----------
        dao:
            The dataset records dao

        Returns
        -------
            The metrics service instance

        """
        if not cls._INSTANCE:
            cls._INSTANCE = cls(dao)
        return cls._INSTANCE

    def __init__(self, dao: DatasetRecordsDAO):
        """
        Creates a service instance

        Parameters
        ----------
        dao:
            The dataset records dao
        """
        self.__dao__ = dao

    def summarize_metric(
        self,
        dataset: Dataset,
        metric: BaseMetric,
        record_class: Optional[Type[BaseRecordDB]] = None,
        query: Optional[GenericQuery] = None,
        **metric_params,
    ) -> Dict[str, Any]:
        """
        Applies a metric summarization.

        Parameters
        ----------
        dataset:
            The records dataset
        metric:
            The selected metric
        query:
            An optional query passed for records filtering
        metric_params:
            Related metrics parameters

        Returns
        -------
            The metric summarization info
        """

        if isinstance(metric, ElasticsearchMetric):
            return self._handle_elasticsearch_metric(
                metric, metric_params, dataset=dataset, query=query
            )
        elif isinstance(metric, PythonMetric):
            records = self.__dao__.scan_dataset(
                dataset, search=RecordSearch(query=query)
            )
            return metric.apply(map(record_class.parse_obj, records))

        raise WrongInputParamError(f"Cannot process {metric} of type {type(metric)}")

    def _handle_elasticsearch_metric(
        self,
        metric: ElasticsearchMetric,
        metric_params: Dict[str, Any],
        dataset: Dataset,
        query: GenericQuery,
    ) -> Dict[str, Any]:
        """
        Parameters
        ----------
        metric:
            The elasticsearch metric summary
        metric_params:
            The summary params
        dataset:
            The records dataset
        query:
            The filter to apply to dataset

        Returns
        -------
            The metric summary result

        """
        params = self.__compute_metric_params__(
            dataset=dataset, metric=metric, query=query, provided_params=metric_params
        )
        results = self.__metric_results__(
            dataset=dataset,
            query=query,
            metric_aggregation=metric.aggregation_request(**params),
        )
        return metric.aggregation_result(
            aggregation_result=results.get(metric.id, results)
        )

    def __compute_metric_params__(
        self,
        dataset: Dataset,
        metric: ElasticsearchMetric,
        query: Optional[GenericQuery],
        provided_params: Dict[str, Any],
    ) -> Dict[str, Any]:

        return self._filter_metric_params(
            metric=metric,
            function=metric.aggregation_request,
            metric_params={
                **provided_params,  # in case of param conflict, provided metric params will be preserved
                "dataset": dataset,
                "dao": self.__dao__,
            },
        )

    def __metric_results__(
        self,
        dataset: Dataset,
        query: Optional[GenericQuery],
        metric_aggregation: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> Dict[str, Any]:

        if not metric_aggregation:
            return {}

        if not isinstance(metric_aggregation, list):
            metric_aggregation = [metric_aggregation]

        results = {}
        for agg in metric_aggregation:
            results_ = self.__dao__.search_records(
                dataset,
                size=0,  # No records at all
                search=RecordSearch(
                    query=query,
                    aggregations=agg,
                ),
            )
            results.update(results_.aggregations)
        return results

    @staticmethod
    def _filter_metric_params(
        metric: ElasticsearchMetric, function: Callable, metric_params: Dict[str, Any]
    ):
        """
        Select from provided metric parameter those who can be applied to given metric

        Parameters
        ----------
        metric:
            The target metric
        metric_params:
            A dict of metric parameters

        """

        if isinstance(metric, NestedPathElasticsearchMetric):
            function = metric.inner_aggregation

        return {
            argument: metric_params[argument]
            for argument in function.__code__.co_varnames
            if argument in metric_params
        }
