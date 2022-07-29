from typing import Any, Dict, Generic, Iterable, TypeVar

from pydantic import BaseModel

from rubrix.server.services.tasks.commons import BaseRecordDB

GenericRecord = TypeVar("GenericRecord", bound=BaseRecordDB)


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
