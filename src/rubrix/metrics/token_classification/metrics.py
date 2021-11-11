from typing import Optional

from rubrix import _client_instance as client
from rubrix.metrics import helpers
from rubrix.metrics.models import MetricSummary


def tokens_length(
    name: str, query: Optional[str] = None, interval: int = 1
) -> MetricSummary:
    """Computes the tokens length distribution

    Args:
        name:
            The dataset name.
        query:
            An ElasticSearch query with the [query string syntax](https://rubrix.readthedocs.io/en/stable/reference/rubrix_webapp_reference.html#search-input)
        interval:
            The bins or bucket for result histogram

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


def mention_length(
    name: str, query: Optional[str] = None, level: str = "token", interval: int = 1
) -> MetricSummary:
    """Computes mentions length distribution (in number of tokens)

    Args:
        name:
            The dataset name.
        query:
            An ElasticSearch query with the [query string syntax](https://rubrix.readthedocs.io/en/stable/reference/rubrix_webapp_reference.html#search-input)
        level:
            The mention length level. Accepted values are "token" and "char"
        interval:
            The bins or bucket for result histogram

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
        name, metric=f"mention_{level}_length", query=query, interval=interval
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
    name: str, query: Optional[str] = None, labels: int = 50
) -> MetricSummary:
    """Computes the entity labels distribution

    Args:
        name:
            The dataset name.
        query:
            An ElasticSearch query with the [query string syntax](https://rubrix.readthedocs.io/en/stable/reference/rubrix_webapp_reference.html#search-input)
        labels:
            The number of top entities to retrieve. Lower numbers will be better performants

    Returns:
        The summary for entity tags distribution

    Examples:
        >>> from rubrix.metrics.token_classification import entity_labels
        >>> summary = entity_labels(name="example-dataset", labels=10)
        >>> summary.visualize() # will plot a bar chart with results
        >>> summary.data # The top-20 entity tags
    """
    current_client = client()

    metric = current_client.compute_metric(
        name, metric="entity_labels", query=query, size=labels
    )

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.bar(
            metric.results,
            title=metric.description,
        ),
    )


def entity_density(
    name: str, query: Optional[str] = None, interval: float = 0.005
) -> MetricSummary:
    """Computes the entity density distribution. Then entity density is calculated at
    record level for each mention as ``mention_length/tokens_length``

    Args:
        name:
            The dataset name.
        query:
            An ElasticSearch query with the [query string syntax](https://rubrix.readthedocs.io/en/stable/reference/rubrix_webapp_reference.html#search-input)
        interval:
            The interval for histogram. The entity density is defined in the range 0-1

    Returns:
        The summary entity density distribution

    Examples:
        >>> from rubrix.metrics.token_classification import entity_density
        >>> summary = entity_density(name="example-dataset")
        >>> summary.visualize()
    """
    current_client = client()
    metric = current_client.compute_metric(
        name, metric="entity_density", query=query, interval=interval
    )

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.histogram(
            metric.results,
            title=metric.description,
        ),
    )


def entity_capitalness(name: str, query: Optional[str] = None) -> MetricSummary:
    """Computes the entity capitalness. The entity capitalness splits the entity
    mention shape in 4 groups:

        ``UPPER``: All charactes in entity mention are upper case

        ``LOWER``: All charactes in entity mention are lower case

        ``FIRST``: The mention is capitalized

        ``MIDDLE``: Some character in mention between first and last is capitalized

    Args:
        name:
            The dataset name.
        query:
            An ElasticSearch query with the [query string syntax](https://rubrix.readthedocs.io/en/stable/reference/rubrix_webapp_reference.html#search-input)

    Returns:
        The summary entity capitalness distribution

    Examples:
        >>> from rubrix.metrics.token_classification import entity_capitalness
        >>> summary = entity_capitalness(name="example-dataset")
        >>> summary.visualize()
    """
    current_client = client()
    metric = current_client.compute_metric(
        name, metric="entity_capitalness", query=query
    )

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.bar(
            metric.results,
            title=metric.description,
        ),
    )


def entity_consistency(
    name: str, query: Optional[str] = None, mentions: int = 10, threshold: int = 2
):
    """Computes the consistency for top entity mentions in the dataset.

    Entity consistency defines the label variability for a given mention. For example, a mention `first` identified
    in the whole dataset as `Cardinal`, `Person` and `Time` is less consistent than a mention `Peter` identified as
    `Person` in the dataset.

    Args:
        name:
            The dataset name.
        query:
            An ElasticSearch query with the [query string syntax](https://rubrix.readthedocs.io/en/stable/reference/rubrix_webapp_reference.html#search-input)
        mentions:
            The number of top mentions to retrieve
        threshold:
            The entity variability threshold (Must be greater or equal to 2)

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
        metric="entity_consistency",
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
