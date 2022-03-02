from typing import Optional

from rubrix import _client_instance as client
from rubrix.metrics import helpers
from rubrix.metrics.models import MetricSummary


def cautious_classification_report(
    y_true,
    y_pred,
    labels=None,
    target_names=None,
    sample_weight=None,
    digits=2,
    output_dict=False,
    zero_division="warn",
    is_tie=None,
):
    try:
        import sklearn
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            "'sklearn' must be installed to compute the metrics! "
            "You can install 'sklearn' with the command: `pip install scikit-learn`"
        )
    from sklearn.metrics import classification_report

    if not output_dict:
        raise NotImplementedError(
            "Formatted string output is not implemented for cautious_classification_report."
        )

    y_true_partial = y_true[~is_tie]
    y_pred_partial = y_pred[~is_tie]

    coverage = len(y_true_partial) / len(y_true)

    report_partial = classification_report(
        y_true_partial,
        y_pred_partial,
        labels=labels,
        target_names=target_names,
        sample_weight=sample_weight,
        digits=digits,
        output_dict=True,
        zero_division=zero_division,
    )

    report_final = {}

    accuracy = report_partial["accuracy"]

    report_final["efficacy"] = (accuracy + coverage) / 2

    report_final["fscore_cautious"] = 2 * (accuracy * coverage) / (accuracy + coverage)

    report_final.update(report_partial)

    return report_final


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
