#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import warnings
from enum import Enum
from typing import Optional, Set, Union

import deprecated

from argilla_v1.client import singleton
from argilla_v1.metrics import helpers
from argilla_v1.metrics.models import MetricSummary

_UNUSED_METRIC_WARNING_MESSAGE = (
    "This metric won't be computed anymore and this function will disappear in a next release!!\n"
    "The metric could return empty results for new Argilla servers"
)


def tokens_length(name: str, query: Optional[str] = None, interval: int = 1) -> MetricSummary:
    """Computes the text length distribution measured in number of tokens.

    Args:
        name: The dataset name.
        query: An ElasticSearch query with the
            `query string syntax <https://docs.v1.argilla.io/en/latest/practical_guides/filter_dataset.html>`_
        interval: The bins or bucket for result histogram

    Returns:
        The summary for token distribution

    Examples:
        >>> from argilla_v1.metrics.token_classification import tokens_length
        >>> summary = tokens_length(name="example-dataset", interval=5)
        >>> summary.visualize() # will plot a histogram with results
        >>> summary.data # the raw histogram data with bins of size 5
    """
    warnings.warn(message=_UNUSED_METRIC_WARNING_MESSAGE, category=DeprecationWarning)

    metric = singleton.active_api().compute_metric(name, metric="tokens_length", query=query, interval=interval)

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.histogram(
            metric.results,
            title=metric.description,
            x_legend="# tokens",
        ),
    )


def token_frequency(name: str, query: Optional[str] = None, tokens: int = 1000) -> MetricSummary:
    """Computes the token frequency distribution for a number of tokens.

    Args:
        name: The dataset name.
        query: An ElasticSearch query with the
            `query string syntax <https://docs.v1.argilla.io/en/latest/practical_guides/filter_dataset.html>`_
        tokens: The top-k number of tokens to retrieve

    Returns:
        The summary for token frequency distribution

    Examples:
        >>> from argilla_v1.metrics.token_classification import token_frequency
        >>> summary = token_frequency(name="example-dataset", token=50)
        >>> summary.visualize() # will plot a histogram with results
        >>> summary.data # the top-50 tokens frequency
    """
    metric = singleton.active_api().compute_metric(name, metric="token_frequency", query=query, size=tokens)

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
            `query string syntax <https://docs.v1.argilla.io/en/latest/practical_guides/filter_dataset.html>`_

    Returns:
        The summary for token length distribution

    Examples:
        >>> from argilla_v1.metrics.token_classification import token_length
        >>> summary = token_length(name="example-dataset")
        >>> summary.visualize() # will plot a histogram with results
        >>> summary.data # The token length distribution
    """
    warnings.warn(message=_UNUSED_METRIC_WARNING_MESSAGE, category=DeprecationWarning)

    metric = singleton.active_api().compute_metric(name, metric="token_length", query=query)

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

        ``UPPER``: All characters in the token are upper case.

        ``LOWER``: All characters in the token are lower case.

        ``FIRST``: The first character in the token is upper case.

        ``MIDDLE``: First character in the token is lower case and at least one other character is upper case.

    Args:
        name: The dataset name.
        query: An ElasticSearch query with the
            `query string syntax <https://docs.v1.argilla.io/en/latest/practical_guides/filter_dataset.html>`_

    Returns:
        The summary for token length distribution

    Examples:
        >>> from argilla_v1.metrics.token_classification import token_capitalness
        >>> summary = token_capitalness(name="example-dataset")
        >>> summary.visualize() # will plot a histogram with results
        >>> summary.data # The token capitalness distribution
    """
    metric = singleton.active_api().compute_metric(name, metric="token_capitalness", query=query)

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
            `query string syntax <https://docs.v1.argilla.io/en/latest/practical_guides/filter_dataset.html>`_
        level: The mention length level. Accepted values are "token" and "char"
        compute_for: Metric can be computed for annotations or predictions. Accepted values are
            ``Annotations`` and ``Predictions``. Defaults to ``Predictions``.
        interval: The bins or bucket for result histogram

    Returns:
        The summary for mention token distribution

    Examples:
        >>> from argilla_v1.metrics.token_classification import mention_length
        >>> summary = mention_length(name="example-dataset", interval=2)
        >>> summary.visualize() # will plot a histogram chart with results
        >>> summary.data # the raw histogram data with bins of size 2
    """
    warnings.warn(message=_UNUSED_METRIC_WARNING_MESSAGE, category=DeprecationWarning)

    level = (level or "token").lower().strip()
    accepted_levels = ["token", "char"]
    assert level in accepted_levels, f"Unexpected value for level. Accepted values are {accepted_levels}"

    metric = singleton.active_api().compute_metric(
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
    name: str, query: Optional[str] = None, compute_for: Union[str, ComputeFor] = Predictions, labels: int = 50
) -> MetricSummary:
    """Computes the entity labels distribution

    Args:
        name: The dataset name.
        query: An ElasticSearch query with the
            `query string syntax <https://docs.v1.argilla.io/en/latest/practical_guides/filter_dataset.html>`_
        compute_for: Metric can be computed for annotations or predictions. Accepted values are
            ``Annotations`` and ``Predictions``. Default to ``Predictions``
        labels: The number of top entities to retrieve. Lower numbers will be better performants

    Returns:
        The summary for entity tags distribution

    Examples:
        >>> from argilla_v1.metrics.token_classification import entity_labels
        >>> summary = entity_labels(name="example-dataset", labels=20)
        >>> summary.visualize() # will plot a bar chart with results
        >>> summary.data # The top-20 entity tags
    """
    metric = singleton.active_api().compute_metric(
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
    name: str, query: Optional[str] = None, compute_for: Union[str, ComputeFor] = Predictions, interval: float = 0.005
) -> MetricSummary:
    """Computes the entity density distribution. Then entity density is calculated at
    record level for each mention as ``mention_length/tokens_length``

    Args:
        name: The dataset name.
        query: An ElasticSearch query with the
            `query string syntax <https://docs.v1.argilla.io/en/latest/practical_guides/filter_dataset.html>`_
        compute_for: Metric can be computed for annotations or predictions. Accepted values are
            ``Annotations`` and ``Predictions``. Default to ``Predictions``.
        interval: The interval for histogram. The entity density is defined in the range 0-1.

    Returns:
        The summary entity density distribution

    Examples:
        >>> from argilla_v1.metrics.token_classification import entity_density
        >>> summary = entity_density(name="example-dataset")
        >>> summary.visualize()
    """

    warnings.warn(message=_UNUSED_METRIC_WARNING_MESSAGE, category=DeprecationWarning)

    metric = singleton.active_api().compute_metric(
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
    name: str, query: Optional[str] = None, compute_for: Union[str, ComputeFor] = Predictions
) -> MetricSummary:
    """Computes the entity capitalness. The entity capitalness splits the entity mention shape in 4 groups:

        ``UPPER``: All characters in entity mention are upper case.

        ``LOWER``: All characters in entity mention are lower case.

        ``FIRST``: The first character in the mention is upper case.

        ``MIDDLE``: First character in the mention is lower case and at least one other character is upper case.

    Args:
        name: The dataset name.
        query: An ElasticSearch query with the
            `query string syntax <https://docs.v1.argilla.io/en/latest/practical_guides/filter_dataset.html>`_
        compute_for: Metric can be computed for annotations or predictions. Accepted values are
            ``Annotations`` and ``Predictions``. Default to ``Predictions``.
    Returns:
        The summary entity capitalness distribution

    Examples:
        >>> from argilla_v1.metrics.token_classification import entity_capitalness
        >>> summary = entity_capitalness(name="example-dataset")
        >>> summary.visualize()
    """
    metric = singleton.active_api().compute_metric(
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


@deprecated.deprecated(reason="Use `top_k_mentions` instead")
def entity_consistency(*args, **kwargs):
    message = "This function is not used anymore.\nYou should use the top_k_mentions function instead"
    warnings.warn(
        message=message,
        category=DeprecationWarning,
    )
    return MetricSummary.new_summary(
        data={},
        visualization=lambda: helpers.empty_visualization(),
    )


def top_k_mentions(
    name: str,
    query: Optional[str] = None,
    compute_for: Union[str, ComputeFor] = Predictions,
    k: int = 100,
    threshold: int = 2,
    post_label_filter: Optional[Set[str]] = None,
):
    """Computes the consistency for top k mentions in the dataset.

    Entity consistency defines the label variability for a given mention. For example, a mention `first` identified
    in the whole dataset as `Cardinal`, `Person` and `Time` is less consistent than a mention `Peter` identified as
    `Person` in the dataset.

    Args:
        name: The dataset name.
        query: An ElasticSearch query with the
            `query string syntax <https://docs.v1.argilla.io/en/latest/practical_guides/filter_dataset.html>`_
        compute_for: Metric can be computed for annotations or predictions. Accepted values are
            ``Annotations`` and ``Predictions``. Default to ``Predictions``
        k: The number of mentions to retrieve.
        threshold: The entity variability threshold (must be greater or equal to 1).
        post_label_filter: A set of labels used for filtering the results. This filter may affect to the expected
        number of mentions

    Returns:
        The summary top k mentions distribution

    Examples:
        >>> from argilla_v1.metrics.token_classification import top_k_mentions
        >>> summary = top_k_mentions(name="example-dataset")
        >>> summary.visualize()
    """

    threshold = max(1, threshold)
    metric = singleton.active_api().compute_metric(
        name,
        metric=f"{_check_compute_for(compute_for)}_top_k_mentions_consistency",
        query=query,
        size=k,
        interval=threshold,
    )

    filtered_mentions, mention_values = [], []
    for mention in metric.results["mentions"]:
        entities = mention["entities"]
        if post_label_filter:
            entities = [entity for entity in entities if entity["label"] in post_label_filter]
        if entities:
            mention["entities"] = entities
            filtered_mentions.append(mention)
            mention_values.append(mention["mention"])

    entities = {}
    for mention in filtered_mentions:
        for entity in mention["entities"]:
            label = entity["label"]
            mentions_for_label = entities.get(label, [0] * len(filtered_mentions))
            mentions_for_label[mention_values.index(mention["mention"])] = entity["count"]
            entities[label] = mentions_for_label

    return MetricSummary.new_summary(
        data={"mentions": filtered_mentions},
        visualization=lambda: helpers.stacked_bar(
            x=mention_values,
            y_s=entities,
            title=metric.description,
        ),
    )


def f1(name: str, query: Optional[str] = None) -> MetricSummary:
    """Computes F1 metrics for a dataset based on entity-level.

    Args:
        name: The dataset name.
        query: An ElasticSearch query with the
            `query string syntax <https://docs.v1.argilla.io/en/latest/practical_guides/filter_dataset.html>`_

    Returns:
        The F1 metric summary containing precision, recall and the F1 score (averaged and per label).

    Examples:
        >>> from argilla_v1.metrics.token_classification import f1
        >>> summary = f1(name="example-dataset")
        >>> summary.visualize() # will plot three bar charts with the results
        >>> summary.data # returns the raw result data

        To display the results as a table:

        >>> import pandas as pd
        >>> pd.DataFrame(summary.data.values(), index=summary.data.keys())
    """
    metric = singleton.active_api().compute_metric(name, metric="F1", query=query)

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.f1(metric.results, metric.description),
    )
