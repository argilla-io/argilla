from typing import Any, ClassVar, Dict, Generic, List, Optional, Union

from pydantic import BaseModel

from rubrix.server.services.metrics import BaseMetric as _BaseMetric
from rubrix.server.services.metrics import PythonMetric as _PythonMetric
from rubrix.server.services.tasks.commons import ServiceRecord as GenericRecord


class Metric(_BaseMetric):
    pass


class PythonMetric(Metric, _PythonMetric, Generic[GenericRecord]):
    pass


class BaseTaskMetrics(BaseModel):
    """
    Base class encapsulating related task metrics

    Attributes:
    -----------

    metrics:
        A list of configured metrics for task
    """

    metrics: ClassVar[List[Union[PythonMetric, str]]]

    @classmethod
    def find_metric(cls, id: str) -> Optional[Union[PythonMetric, str]]:
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
            if isinstance(metric, str) and metric == id:
                return metric
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
