from rubrix.server.tasks.commons import EsRecordDataFieldNames, TaskStatus
from rubrix.server.tasks.commons.metrics.model.base import (
    HistogramAggregation,
    TermsAggregation,
)


class CommonTasksMetrics:

    metrics = [
        HistogramAggregation(
            id="text_length",
            name="Text length distribution",
            description="Computes the input text length distribution",
            field=EsRecordDataFieldNames.words,
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
    ]
