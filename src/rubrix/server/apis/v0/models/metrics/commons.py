from typing import Any, ClassVar, Dict, Generic, List

from rubrix.server.apis.v0.models.metrics.base import (
    BaseTaskMetrics,
    GenericRecord,
    Metric,
)


class CommonTasksMetrics(BaseTaskMetrics, Generic[GenericRecord]):
    """Common task metrics"""

    @classmethod
    def record_metrics(cls, record: GenericRecord) -> Dict[str, Any]:
        """Record metrics will persist the text_length"""
        return {"text_length": len(record.all_text())}

    metrics: ClassVar[List[Metric]] = [
        Metric(
            id="text_length",
            name="Text length distribution",
            description="Computes the input text length distribution",
        ),
        Metric(
            id="error_distribution",
            name="Error distribution",
            description="Computes the dataset error distribution. It's mean, records "
            "with correct predictions vs records with incorrect prediction "
            "vs records with unknown prediction result",
        ),
        Metric(
            id="status_distribution",
            name="Record status distribution",
            description="The dataset record status distribution",
        ),
        Metric(
            id="words_cloud",
            name="Inputs words cloud",
            description="The words cloud for dataset inputs",
        ),
        Metric(id="metadata", name="Metadata fields stats"),
        Metric(
            id="predicted_by",
            name="Predicted by distribution",
        ),
        Metric(
            id="annotated_by",
            name="Annotated by distribution",
        ),
        Metric(
            id="score",
            name="Score record distribution",
        ),
    ]
