from rubrix import _client_instance as client
from rubrix.metrics import helpers
from rubrix.metrics.models import MetricSummary


def f1(name: str) -> MetricSummary:
    """Computes the single label f1 metric for a dataset

    Args:
        name:
            The dataset name.

    Returns:
        The f1 metric summary

    Examples:
        >>> from rubrix.metrics.text_classification import f1
        >>> summary = f1(name="example-dataset")
        >>> summary.visualize() # will plot a bar chart with results
        >>> summary.data # returns the raw result data
    """
    current_client = client()
    metric = current_client.calculate_metric(name, metric="F1")

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.bar(
            metric.results,
            title=metric.description,
        ),
    )


def f1_multilabel(name: str) -> MetricSummary:
    """Computes the multi-label label f1 metric for a dataset

    Args:
        name:
            The dataset name.

    Returns:
        The f1 metric summary

    Examples:
        >>> from rubrix.metrics.text_classification import f1_multilabel
        >>> summary = f1_multilabel(name="example-dataset")
        >>> summary.visualize() # will plot a bar chart with results
        >>> summary.data # returns the raw result data
    """
    current_client = client()
    metric = current_client.calculate_metric(name, metric="MultiLabelF1")

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.bar(
            {
                "micro": metric.results["micro"],
                "macro": metric.results["macro"],
                **metric.results["per_label"],
            }
            if metric.results
            else metric.results,
            title=metric.description,
        ),
    )
