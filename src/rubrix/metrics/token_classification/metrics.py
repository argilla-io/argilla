from enum import Enum
from typing import Optional, Union

from rubrix import _client_instance as client
from rubrix.metrics import helpers
from rubrix.metrics.models import MetricSummary


def tokens_length(
    name: str, query: Optional[str] = None, interval: int = 1
) -> MetricSummary:
    """Computes the text length distribution measured in number of tokens.

    Args:
        name: The dataset name.
        query: An ElasticSearch query with the
            `query string syntax <https://rubrix.readthedocs.io/en/stable/reference/webapp/search_records.html>`_
        interval: The bins or bucket for result histogram

    Returns:
        The summary for token distribution

    Examples:
        >>> from rubrix.metrics.token_classification import tokens_length
        >>> summary = tokens_length(name="example-dataset", interval=5)
        >>> summary.visualize() # will plot a histogram with results
        >>> summary.data # the raw histogram data with bins of size 5
    """
    current_client = client()

    metric = current_client.compute_metric(
        name, metric="tokens_length", query=query, interval=interval
    )

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.histogram(
            metric.results,
            title=metric.description,
            x_legend="# tokens",
        ),
    )


def token_frequency(
    name: str, query: Optional[str] = None, tokens: int = 1000
) -> MetricSummary:
    """Computes the token frequency distribution for a numbe of tokens.

    Args:
        name: The dataset name.
        query: An ElasticSearch query with the
            `query string syntax <https://rubrix.readthedocs.io/en/stable/reference/webapp/search_records.html>`_
        tokens: The top-k number of tokens to retrieve

    Returns:
        The summary for token frequency distribution

    Examples:
        >>> from rubrix.metrics.token_classification import token_frequency
        >>> summary = token_frequency(name="example-dataset", token=50)
        >>> summary.visualize() # will plot a histogram with results
        >>> summary.data # the top-50 tokens frequency
    """
    current_client = client()

    metric = current_client.compute_metric(
        name, metric="token_frequency", query=query, size=tokens
    )

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.bar(
            metric.results,
            title=metric.description,
        ),
    )


def token_length(name: str, query: Optional[str] = None) -> MetricSummary:
    """Computes the token size distribution in terms of number of characters

    Args:
        name: The dataset name.
        query: An ElasticSearch query with the
            `query string syntax <https://rubrix.readthedocs.io/en/stable/reference/webapp/search_records.html>`_

    Returns:
        The summary for token length distribution

    Examples:
        >>> from rubrix.metrics.token_classification import token_length
        >>> summary = token_length(name="example-dataset")
        >>> summary.visualize() # will plot a histogram with results
        >>> summary.data # The token length distribution
    """
    current_client = client()

    metric = current_client.compute_metric(name, metric="token_length", query=query)

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.histogram(
            metric.results,
            title=metric.description,
            x_legend="# chars",
        ),
    )


def token_capitalness(name: str, query: Optional[str] = None) -> MetricSummary:
    """Computes the token capitalness distribution

    Args:
        name: The dataset name.
        query: An ElasticSearch query with the
            `query string syntax <https://rubrix.readthedocs.io/en/stable/reference/webapp/search_records.html>`_

    Returns:
        The summary for token length distribution

    Examples:
        >>> from rubrix.metrics.token_classification import token_capitalness
        >>> summary = token_capitalness(name="example-dataset")
        >>> summary.visualize() # will plot a histogram with results
        >>> summary.data # The token capitalness distribution
    """
    current_client = client()

    metric = current_client.compute_metric(
        name, metric="token_capitalness", query=query
    )

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.bar(
            metric.results,
            title=metric.description,
        ),
    )


class ComputeFor(Enum):
    ANNOTATIONS = "annotations"
    PREDICTIONS = "predictions"

    @classmethod
    def _missing_(cls, value):
        raise ValueError(
            f"{value} is not a valid {cls.__name__}, please select one of {list(cls._value2member_map_.keys())}"
        )


Annotations = ComputeFor.ANNOTATIONS
Predictions = ComputeFor.PREDICTIONS

_ACCEPTED_COMPUTE_FOR_VALUES = {
    Annotations: "annotated",
    Predictions: "predicted",
}


def _check_compute_for(compute_for: Union[str, ComputeFor]) -> str:
    if not compute_for:
        compute_for = Predictions
    if isinstance(compute_for, str):
        compute_for = compute_for.lower().strip()
        compute_for = ComputeFor(compute_for)
    return _ACCEPTED_COMPUTE_FOR_VALUES[compute_for]


def mention_length(
    name: str,
    query: Optional[str] = None,
    level: str = "token",
    compute_for: Union[str, ComputeFor] = Predictions,
    interval: int = 1,
) -> MetricSummary:
    """Computes mentions length distribution (in number of tokens).

    Args:
        name: The dataset name.
        query: An ElasticSearch query with the
            `query string syntax <https://rubrix.readthedocs.io/en/stable/reference/webapp/search_records.html>`_
        level: The mention length level. Accepted values are "token" and "char"
        compute_for: Metric can be computed for annotations or predictions. Accepted values are
            ``Annotations`` and ``Predictions``. Defaults to ``Predictions``.
        interval: The bins or bucket for result histogram

    Returns:
        The summary for mention token distribution

    Examples:
        >>> from rubrix.metrics.token_classification import mention_length
        >>> summary = mention_length(name="example-dataset", interval=2)
        >>> summary.visualize() # will plot a histogram chart with results
        >>> summary.data # the raw histogram data with bins of size 2
    """
    current_client = client()
    level = (level or "token").lower().strip()
    accepted_levels = ["token", "char"]
    assert (
        level in accepted_levels
    ), f"Unexpected value for level. Accepted values are {accepted_levels}"

    metric = current_client.compute_metric(
        name,
        metric=f"{_check_compute_for(compute_for)}_mention_{level}_length",
        query=query,
        interval=interval,
    )

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.histogram(
            metric.results,
            title=metric.description,
            x_legend=f"# {level}",
        ),
    )


def entity_labels(
    name: str,
    query: Optional[str] = None,
    compute_for: Union[str, ComputeFor] = Predictions,
    labels: int = 50,
) -> MetricSummary:
    """Computes the entity labels distribution

    Args:
        name: The dataset name.
        query: An ElasticSearch query with the
            `query string syntax <https://rubrix.readthedocs.io/en/stable/reference/webapp/search_records.html>`_
        compute_for: Metric can be computed for annotations or predictions. Accepted values are
            ``Annotations`` and ``Predictions``. Default to ``Predictions``
        labels: The number of top entities to retrieve. Lower numbers will be better performants

    Returns:
        The summary for entity tags distribution

    Examples:
        >>> from rubrix.metrics.token_classification import entity_labels
        >>> summary = entity_labels(name="example-dataset", labels=20)
        >>> summary.visualize() # will plot a bar chart with results
        >>> summary.data # The top-20 entity tags
    """
    current_client = client()

    metric = current_client.compute_metric(
        name,
        metric=f"{_check_compute_for(compute_for)}_entity_labels",
        query=query,
        size=labels,
    )

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.bar(
            metric.results,
            title=metric.description,
        ),
    )


def entity_density(
    name: str,
    query: Optional[str] = None,
    compute_for: Union[str, ComputeFor] = Predictions,
    interval: float = 0.005,
) -> MetricSummary:
    """Computes the entity density distribution. Then entity density is calculated at
    record level for each mention as ``mention_length/tokens_length``

    Args:
        name: The dataset name.
        query: An ElasticSearch query with the
            `query string syntax <https://rubrix.readthedocs.io/en/stable/reference/webapp/search_records.html>`_
        compute_for: Metric can be computed for annotations or predictions. Accepted values are
            ``Annotations`` and ``Predictions``. Default to ``Predictions``.
        interval: The interval for histogram. The entity density is defined in the range 0-1.

    Returns:
        The summary entity density distribution

    Examples:
        >>> from rubrix.metrics.token_classification import entity_density
        >>> summary = entity_density(name="example-dataset")
        >>> summary.visualize()
    """
    current_client = client()
    metric = current_client.compute_metric(
        name,
        metric=f"{_check_compute_for(compute_for)}_entity_density",
        query=query,
        interval=interval,
    )

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.histogram(
            metric.results,
            title=metric.description,
        ),
    )


def entity_capitalness(
    name: str,
    query: Optional[str] = None,
    compute_for: Union[str, ComputeFor] = Predictions,
) -> MetricSummary:
    """Computes the entity capitalness. The entity capitalness splits the entity mention shape in 4 groups:

        ``UPPER``: All charactes in entity mention are upper case

        ``LOWER``: All charactes in entity mention are lower case

        ``FIRST``: The mention is capitalized

        ``MIDDLE``: Some character in mention between first and last is capitalized

    Args:
        name: The dataset name.
        query: An ElasticSearch query with the
            `query string syntax <https://rubrix.readthedocs.io/en/stable/reference/webapp/search_records.html>`_
        compute_for: Metric can be computed for annotations or predictions. Accepted values are
            ``Annotations`` and ``Predictions``. Default to ``Predictions``.
    Returns:
        The summary entity capitalness distribution

    Examples:
        >>> from rubrix.metrics.token_classification import entity_capitalness
        >>> summary = entity_capitalness(name="example-dataset")
        >>> summary.visualize()
    """
    current_client = client()
    metric = current_client.compute_metric(
        name,
        metric=f"{_check_compute_for(compute_for)}_entity_capitalness",
        query=query,
    )

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.bar(
            metric.results,
            title=metric.description,
        ),
    )


def entity_consistency(
    name: str,
    query: Optional[str] = None,
    compute_for: Union[str, ComputeFor] = Predictions,
    mentions: int = 10,
    threshold: int = 2,
):
    """Computes the consistency for top entity mentions in the dataset.

    Entity consistency defines the label variability for a given mention. For example, a mention `first` identified
    in the whole dataset as `Cardinal`, `Person` and `Time` is less consistent than a mention `Peter` identified as
    `Person` in the dataset.

    Args:
        name: The dataset name.
        query: An ElasticSearch query with the
            `query string syntax <https://rubrix.readthedocs.io/en/stable/reference/webapp/search_records.html>`_
        compute_for: Metric can be computed for annotations or predictions. Accepted values are
            ``Annotations`` and ``Predictions``. Default to ``Predictions``
        mentions: The number of top mentions to retrieve.
        threshold: The entity variability threshold (must be greater or equal to 2).

    Returns:
        The summary entity capitalness distribution

    Examples:
        >>> from rubrix.metrics.token_classification import entity_consistency
        >>> summary = entity_consistency(name="example-dataset")
        >>> summary.visualize()
    """
    if threshold < 2:
        # TODO: Warning???
        threshold = 2

    current_client = client()
    metric = current_client.compute_metric(
        name,
        metric=f"{_check_compute_for(compute_for)}_entity_consistency",
        query=query,
        size=mentions,
        interval=threshold,
    )
    mentions = [mention["mention"] for mention in metric.results["mentions"]]
    entities = {}

    for mention in metric.results["mentions"]:
        for entity in mention["entities"]:
            mentions_for_label = entities.get(entity["label"], [0] * len(mentions))
            mentions_for_label[mentions.index(mention["mention"])] = entity["count"]
            entities[entity["label"]] = mentions_for_label

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.stacked_bar(
            x=mentions, y_s=entities, title=metric.description
        ),
    )


def f1(name: str, query: Optional[str] = None) -> MetricSummary:
    """Computes F1 metrics for a dataset based on entity-level.

    Args:
        name: The dataset name.
        query: An ElasticSearch query with the
            `query string syntax <https://rubrix.readthedocs.io/en/stable/reference/webapp/search_records.html>`_

    Returns:
        The F1 metric summary containing precision, recall and the F1 score (averaged and per label).

    Examples:
        >>> from rubrix.metrics.token_classification import f1
        >>> summary = f1(name="example-dataset")
        >>> summary.visualize() # will plot three bar charts with the results
        >>> summary.data # returns the raw result data

        To display the results as a table:

        >>> import pandas as pd
        >>> pd.DataFrame(summary.data.values(), index=summary.data.keys())
    """
    current_client = client()
    metric = current_client.compute_metric(name, metric="F1", query=query)

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.f1(metric.results, metric.description),
    )
