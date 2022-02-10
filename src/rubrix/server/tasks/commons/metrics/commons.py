from rubrix.server.tasks.commons import EsRecordDataFieldNames, TaskStatus
from rubrix.server.tasks.commons.metrics.model.base import (
    HistogramAggregation,
    MetadataAggregations,
    TermsAggregation,
    WordCloudAggregation,
)


class CommonTasksMetrics:

    metrics = [
        HistogramAggregation(
            id="text_length",
            name="Text length distribution",
            description="Computes the input text length distribution",
            field=EsRecordDataFieldNames.words,
            # TODO(@frascuchon): This won't work once words is excluded from _source
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
            default_field="words",
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
