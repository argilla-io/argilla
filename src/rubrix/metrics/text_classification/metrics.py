from typing import Optional

import pandas as pd

from rubrix import _client_instance as client
from rubrix.metrics import helpers
from rubrix.metrics.models import MetricSummary


def cautious_classification_report(
    y_true,
    y_pred,
    labels=None,
    model_labels=None,
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

    def report_to_str(report, metrics):
        for metric in metrics:
            report.update(
                {
                    metric: {
                        "precision": None,
                        "recall": None,
                        "f1-score": report[metric],
                        "support": report["macro avg"]["support"],
                    }
                }
            )
        report["accuracy"] = {
            "precision": None,
            "recall": None,
            "f1-score": report["accuracy"],
            "support": report["macro avg"]["support"],
        }

        df = pd.DataFrame(report).transpose()

        df = df.astype(float).applymap(lambda x: "{:,.2f}".format(x))
        df["support"] = df["support"].astype(float).apply(lambda x: "{:,g}".format(x))

        df["bool_field"] = df["precision"].apply(lambda x: x == "nan")
        df = df.sort_values(by=["bool_field"], ascending=True)
        df = df.drop("bool_field", axis=1)

        df = df.reset_index()
        boundary = df.index[(df["precision"] == "nan").argmax()] + 1
        df = df.set_index("index")
        df.index.name = None
        df = df.replace(["nan", "None"], "")

        output = df.to_string().split("\n")
        try:
            output = output[:boundary] + ["\n"] + output[boundary:]
        except:
            raise Exception(str(boundary))
        output = "\n".join(output)

        return output

    if not is_tie.any():
        y_true_partial = y_true
        y_pred_partial = y_pred
    else:
        y_true_partial = y_true[~is_tie]
        y_pred_partial = y_pred[~is_tie]

    if y_true_partial.any() and target_names is None:
        target_names = model_labels[: y_true_partial.max() + 1]

    coverage = len(y_true_partial) / len(y_true)

    report_final = {}

    if y_true_partial.any():
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

        accuracy = report_partial["accuracy"]

        report_final = {
            "efficacy": (accuracy + coverage) / 2,
            "fscore_cautious": 2 * (accuracy * coverage) / (accuracy + coverage),
            "coverage": coverage,
        }

        report_final.update(report_partial)

        if not output_dict:
            report_final = report_to_str(
                report_final, ["efficacy", "fscore_cautious", "coverage"]
            )

    elif output_dict:
        report_final = {
            "accuracy": 0,
            "efficacy": 0,
            "fscore_cautious": 0,
            "coverage": 0,
        }
    else:
        report_final = """
            accuracy            0.0
            efficacy            0.0
            fscore_cautious     0.0
            coverage            0.0
        """

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
