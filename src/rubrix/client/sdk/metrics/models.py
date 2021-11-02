from typing import Optional

from pydantic import BaseModel, Field


class MetricInfo(BaseModel):
    """Metric info data model for retrieve dataset metrics information"""

    id: str = Field(description="The metric id")
    name: str = Field(description="The metric name")
    description: Optional[str] = Field(
        default=None, description="The metric description"
    )
