from typing import Optional

from rubrix import _client_instance as client
from rubrix.metrics import helpers
from rubrix.metrics.models import MetricSummary


def text_length(name: str, query: Optional[str] = None) -> MetricSummary:
    """Computes the input text length metrics for a dataset

    Args:
        name:
            The dataset name.
        query:
            An ElasticSearch query with the [query string syntax](https://rubrix.readthedocs.io/en/stable/reference/webapp/search_records.html)

    Returns:
        The text length metric summary

    Examples:
        >>> from rubrix.metrics.commons import text_length
        >>> summary = text_length(name="example-dataset")
        >>> summary.visualize() # will plot an histogram with results
        >>> summary.data # returns the raw result data
    """
    current_client = client()
    metric = current_client.compute_metric(name, metric="text_length", query=query)

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.histogram(
            data=metric.results, title=metric.description
        ),
    )


def records_status(name: str, query: Optional[str] = None) -> MetricSummary:
    """Computes the records status distribution for a dataset

    Args:
        name:
            The dataset name.
        query:
            An ElasticSearch query with the [query string syntax](https://rubrix.readthedocs.io/en/stable/reference/webapp/search_records.html)

    Returns:
        The status distribution  metric summary

    Examples:
        >>> from rubrix.metrics.commons import records_status
        >>> summary = records_status(name="example-dataset")
        >>> summary.visualize() # will plot an histogram with results
        >>> summary.data # returns the raw result data
    """
    current_client = client()
    metric = current_client.compute_metric(
        name, metric="status_distribution", query=query
    )

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.bar(
            data=metric.results, title=metric.description
        ),
    )
