from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field


class DatasetMetricCreation(BaseModel):
    id: str = Field(..., description="The metric id")
    name: str = Field(..., description="The metric name")
    description: str = Field(None, description="Descriptive text for dataset metric")
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

    class Config:
        allow_population_by_field_name = True


class DatasetMetric(DatasetMetricCreation):
    pass


class DatasetMetricResults(DatasetMetricCreation):
    kind: str
    results: Dict[str, Any] = Field(
        default_factory=dict, description="Whatever data the metric calculated"
    )
