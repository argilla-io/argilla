from rubrix.server.commons.models import TaskStatus
from rubrix.server.elasticseach.metrics.base import (
    HistogramAggregation,
    MetadataAggregations,
    TermsAggregation,
    WordCloudAggregation,
)

METRICS = {
    "text_length": HistogramAggregation(
        id="text_length",
        field="metrics.text_length",
        script="params._source.text.length()",
        fixed_interval=1,
    ),
    "error_distribution": TermsAggregation(
        id="error_distribution",
        field="predicted",
        missing="unknown",
        fixed_size=3,
    ),
    "status_distribution": TermsAggregation(
        id="status_distribution",
        field="status",
        fixed_size=len(TaskStatus),
    ),
    "words_cloud": WordCloudAggregation(
        id="words_cloud",
        default_field="text.wordcloud",
    ),
    "metadata": MetadataAggregations(
        id="metadata",
    ),
    "predicted_by": TermsAggregation(
        id="predicted_by",
        field="predicted_by",
    ),
    "annotated_by": TermsAggregation(
        id="annotated_by",
        field="annotated_by",
    ),
    "score": HistogramAggregation(
        id="score",
        field="score",
        fixed_interval=0.001,
    ),
}
