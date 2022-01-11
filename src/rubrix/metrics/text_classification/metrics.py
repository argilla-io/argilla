from typing import Optional

from rubrix import _client_instance as client
from rubrix.metrics import helpers
from rubrix.metrics.models import MetricSummary


def f1(name: str, query: Optional[str] = None) -> MetricSummary:
    """Computes the single label f1 metric for a dataset

    Args:
        name:
            The dataset name.
        query:
            An ElasticSearch query with the [query string syntax](https://rubrix.readthedocs.io/en/stable/reference/webapp/search_records.html)

    Returns:
        The f1 metric summary

    Examples:
        >>> from rubrix.metrics.text_classification import f1
        >>> summary = f1(name="example-dataset")
        >>> summary.visualize() # will plot a bar chart with results
        >>> summary.data # returns the raw result data
    """
    current_client = client()
    metric = current_client.compute_metric(name, metric="F1", query=query)

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.f1(data=metric.results, title=metric.description),
    )


def f1_multilabel(name: str, query: Optional[str] = None) -> MetricSummary:
    """Computes the multi-label label f1 metric for a dataset

    Args:
        name:
            The dataset name.
        query:
            An ElasticSearch query with the [query string syntax](https://rubrix.readthedocs.io/en/stable/reference/webapp/search_records.html)

    Returns:
        The f1 metric summary

    Examples:
        >>> from rubrix.metrics.text_classification import f1_multilabel
        >>> summary = f1_multilabel(name="example-dataset")
        >>> summary.visualize() # will plot a bar chart with results
        >>> summary.data # returns the raw result data
    """
    current_client = client()
    metric = current_client.compute_metric(name, metric="MultiLabelF1", query=query)

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.f1(data=metric.results, title=metric.description),
    )
