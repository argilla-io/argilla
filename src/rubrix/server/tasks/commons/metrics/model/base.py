from typing import Any, ClassVar, Dict, Generic, Iterable, List, Optional, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

from rubrix.server.commons.es_helpers import aggregations
from rubrix.server.tasks.commons import BaseRecord


GenericRecord = TypeVar("GenericRecord", bound=BaseRecord)


class BaseMetric(BaseModel):
    """
    Base model for rubrix dataset metrics summaries
    """

    id: str
    name: str
    description: str = None


class PythonMetric(BaseMetric, Generic[GenericRecord]):
    """
    A metric definition which will be calculated using raw queried data
    """

    def apply(self, records: Iterable[GenericRecord]) -> Dict[str, Any]:
        """
        Metric calculation method.

        Parameters
        ----------
        records:
            The matched records

        Returns
        -------
            The metric result
        """
        raise NotImplementedError()


class ElasticsearchMetric(BaseMetric):
    """
    A metric summarized by using one or several elasticsearch aggregations
    """

    def aggregation_request(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Configures the summary es aggregation definition
        """
        raise NotImplementedError()

    def aggregation_result(self, aggregation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the es aggregation result. Override this method
        for result customization

        Parameters
        ----------
        aggregation_result:
            Retrieved es aggregation result

        """
        return aggregation_result


class NestedPathElasticsearchMetric(ElasticsearchMetric):
    """
    A ``ElasticsearchMetric`` which need nested fields for summary calculation.

    Aggregations for nested fields need some extra configuration and this class
    encapsulate these common logic.

    Attributes:
    -----------
    nested_path:
        The nested
    """

    nested_path: str

    def inner_aggregation(self, *args, **kwargs) -> Dict[str, Any]:
        """The specific aggregation definition"""
        raise NotImplementedError()

    def aggregation_request(self, *args, **kwargs) -> Dict[str, Any]:
        """Implements the common mechanism to define aggregations with nested fields"""
        return aggregations.nested_aggregation(
            nested_path=self.nested_path,
            inner_aggregation=self.inner_aggregation(*args, **kwargs),
        )


class BaseTaskMetrics(GenericModel, Generic[GenericRecord]):
    """
    Base class encapsulating related task metrics

    Attributes:
    -----------

    metrics:
        A list of configured metrics for task
    """

    metrics: ClassVar[List[BaseMetric]]

    @classmethod
    def configure_es_index(cls):
        """
        If some metrics require specific es field mapping definitions,
        include them here.

        """
        pass

    @classmethod
    def find_metric(cls, id: str) -> Optional[BaseMetric]:
        """
        Finds a metric by id

        Parameters
        ----------
        id:
            The metric id

        Returns
        -------
            Found metric if any, ``None`` otherwise

        """
        for metric in cls.metrics:
            if metric.id == id:
                return metric

    @classmethod
    def record_metrics(cls, record: GenericRecord) -> Dict[str, Any]:
        """
        Use this method is some configured metric requires additional
        records fields.

        Generated records will be persisted under ``metrics`` record path.
        For example, if you define a field called ``sentence_length`` like

        >>> def record_metrics(cls, record)-> Dict[str, Any]:
        ...     return { "sentence_length" : len(record.text) }

        The new field will be stored in elasticsearch in ``metrics.sentence_length``

        Parameters
        ----------
        record:
            The record used for calculate metrics fields

        Returns
        -------
            A dict with calculated metrics fields
        """
        return {}
