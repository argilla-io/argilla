from typing import Any, Callable, Dict

from pydantic import BaseModel


class MetricSummary(BaseModel):

    data: Dict[str, Any]
    build_visualization: Callable

    def visualize(self):
        try:
            return self.build_visualization()
        except ModuleNotFoundError:
            raise RuntimeError(
                "Please, install plotly in order to use this feature\n"
                "%>pip install plotly"
            )
