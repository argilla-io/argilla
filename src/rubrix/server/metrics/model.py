from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field


class DatasetMetricCreation(BaseModel):
    name: str = Field(..., description="The metric name")
    field: str = Field(
        None, description="The dataset field used for calculate the metric"
    )
    spec: Dict[str, Any] = Field(
        None,
        alias="_spec",
        description="""Metric spec used for calculate the metric. """
        """This field should be used only for advanced users""",
    )


class DatasetMetricDB(DatasetMetricCreation):
    created_by: str
    created_at: datetime = None


class DatasetMetric(DatasetMetricCreation):
    pass
