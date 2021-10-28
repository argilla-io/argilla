import warnings
from typing import Any, Callable, Dict

from pydantic import BaseModel, PrivateAttr


class MetricSummary(BaseModel):
    """THe metric summary result data model"""

    data: Dict[str, Any]
    _build_visualization: Callable = PrivateAttr()

    def visualize(self):
        try:
            return self._build_visualization()
        except ModuleNotFoundError:
            warnings.warn(
                "Please, install plotly in order to use this feature\n"
                "%>pip install plotly"
            )

    @classmethod
    def new_summary(
        cls, data: Dict[str, Any], visualization: Callable
    ) -> "MetricSummary":
        summary = cls(data=data)
        summary._build_visualization = visualization
        return summary
