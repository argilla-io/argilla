from typing import (
    Any,
    ClassVar,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    TypeVar,
    Union,
)

from pydantic import BaseModel

from rubrix.server.services.tasks.commons import ServiceRecord


class ServiceBaseMetric(BaseModel):
    """
    Base model for rubrix dataset metrics summaries
    """

    id: str
    name: str
    description: str = None


class ServicePythonMetric(ServiceBaseMetric, Generic[ServiceRecord]):
    """
    A metric definition which will be calculated using raw queried data
    """

    def apply(self, records: Iterable[ServiceRecord]) -> Dict[str, Any]:
        """
        ServiceBaseMetric calculation method.

        Parameters
        ----------
        records:
            The matched records

        Returns
        -------
            The metric result
        """
        raise NotImplementedError()


ServiceMetric = TypeVar("ServiceMetric", bound=ServiceBaseMetric)


class ServiceBaseTaskMetrics(BaseModel):
    """
    Base class encapsulating related task metrics

    Attributes:
    -----------

    metrics:
        A list of configured metrics for task
    """

    metrics: ClassVar[List[Union[ServicePythonMetric, str]]]

    @classmethod
    def find_metric(cls, id: str) -> Optional[Union[ServicePythonMetric, str]]:
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
    def record_metrics(cls, record: ServiceRecord) -> Dict[str, Any]:
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


class CommonTasksMetrics(ServiceBaseTaskMetrics, Generic[ServiceRecord]):
    """Common task metrics"""

    @classmethod
    def record_metrics(cls, record: ServiceRecord) -> Dict[str, Any]:
        """Record metrics will persist the text_length"""
        return {"text_length": len(record.all_text())}

    metrics: ClassVar[List[ServiceBaseMetric]] = [
        ServiceBaseMetric(
            id="text_length",
            name="Text length distribution",
            description="Computes the input text length distribution",
        ),
        ServiceBaseMetric(
            id="error_distribution",
            name="Error distribution",
            description="Computes the dataset error distribution. It's mean, records "
            "with correct predictions vs records with incorrect prediction "
            "vs records with unknown prediction result",
        ),
        ServiceBaseMetric(
            id="status_distribution",
            name="Record status distribution",
            description="The dataset record status distribution",
        ),
        ServiceBaseMetric(
            id="words_cloud",
            name="Inputs words cloud",
            description="The words cloud for dataset inputs",
        ),
        ServiceBaseMetric(id="metadata", name="Metadata fields stats"),
        ServiceBaseMetric(
            id="predicted_by",
            name="Predicted by distribution",
        ),
        ServiceBaseMetric(
            id="annotated_by",
            name="Annotated by distribution",
        ),
        ServiceBaseMetric(
            id="score",
            name="Score record distribution",
        ),
    ]
