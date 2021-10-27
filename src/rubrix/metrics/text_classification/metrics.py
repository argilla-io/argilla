from rubrix import _client_instance as client
from rubrix.metrics import helpers
from rubrix.metrics.models import MetricSummary


def f1(name: str) -> MetricSummary:
    current_client = client()
    metric = current_client.calculate_metric(name, metric="F1")

    return MetricSummary(
        data=metric.results,
        build_visualization=lambda: helpers.bar(
            metric.results,
            title=metric.description,
        ),
    )


def f1_multilabel(name: str) -> MetricSummary:
    current_client = client()
    metric = current_client.calculate_metric(name, metric="MultiLabelF1")

    return MetricSummary(
        data=metric.results,
        build_visualization=lambda: helpers.bar(
            metric.results,
            title=metric.description,
        ),
    )
