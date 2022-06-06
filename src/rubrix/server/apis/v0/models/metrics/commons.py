from typing import Any, ClassVar, Dict, Generic, List

from rubrix.server.apis.v0.models.commons.model import (
    EsRecordDataFieldNames,
    TaskStatus,
)
from rubrix.server.apis.v0.models.metrics.base import (
    BaseMetric,
    BaseTaskMetrics,
    GenericRecord,
    HistogramAggregation,
    MetadataAggregations,
    TermsAggregation,
    WordCloudAggregation,
)


class CommonTasksMetrics(BaseTaskMetrics, Generic[GenericRecord]):
    """Common task metrics"""

    @classmethod
    def record_metrics(cls, record: GenericRecord) -> Dict[str, Any]:
        """Record metrics will persist the text_length"""
        return {"text_length": len(record.all_text())}

    metrics: ClassVar[List[BaseMetric]] = [
        HistogramAggregation(
            id="text_length",
            name="Text length distribution",
            description="Computes the input text length distribution",
            field="metrics.text_length",
            # TODO(@frascuchon): This won't work once words is excluded from _source
            # TODO: Implement changes with backward compatibility
            script="params._source.words.length()",
            fixed_interval=1,
        ),
        TermsAggregation(
            id="error_distribution",
            name="Error distribution",
            description="Computes the dataset error distribution. It's mean, records "
            "with correct predictions vs records with incorrect prediction "
            "vs records with unknown prediction result",
            field=EsRecordDataFieldNames.predicted,
            missing="unknown",
            fixed_size=3,
        ),
        TermsAggregation(
            id="status_distribution",
            name="Record status distribution",
            description="The dataset record status distribution",
            field=EsRecordDataFieldNames.status,
            fixed_size=len(TaskStatus),
        ),
        WordCloudAggregation(
            id="words_cloud",
            name="Inputs words cloud",
            description="The words cloud for dataset inputs",
            # TODO(@frascuchon): This won't work once words is excluded from _source
            # TODO: Implement changes with backward compatibility
            default_field=EsRecordDataFieldNames.words,
        ),
        MetadataAggregations(id="metadata", name="Metadata fields stats"),
        TermsAggregation(
            id="predicted_by",
            name="Predicted by distribution",
            field="predicted_by",
        ),
        TermsAggregation(
            id="annotated_by",
            name="Annotated by distribution",
            field="annotated_by",
        ),
        HistogramAggregation(
            id="score",
            name="Score record distribution",
            field="score",
            fixed_interval=0.001,
        ),
    ]
