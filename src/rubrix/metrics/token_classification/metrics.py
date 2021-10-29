from rubrix import _client_instance as client
from rubrix.metrics import helpers
from rubrix.metrics.models import MetricSummary


def tokens_length(name: str, interval: int = 1) -> MetricSummary:
    """Calculates the tokens length distribution

    Args:
        name:
            The dataset name.
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

    metric = current_client.calculate_metric(
        name, metric="tokens_length", interval=interval
    )

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.histogram(
            metric.results,
            title=metric.description,
            x_legend="# tokens",
        ),
    )


def mention_length(name: str, interval: int = 1) -> MetricSummary:
    """Calculates the mention tokens length distribution

    Args:
        name:
            The dataset name.
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

    metric = current_client.calculate_metric(
        name, metric="mention_length", interval=interval
    )

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.histogram(
            metric.results,
            title=metric.description,
            x_legend="# tokens",
        ),
    )


def entity_tags(name: str, entities: int = 50) -> MetricSummary:
    """Calculates the entity tags distribution

    Args:
        name:
            The dataset name.
        entities:
            The number of top entities to retrieve. Lower numbers will be better performants

    Returns:
        The summary for entity tags distribution

    Examples:
        >>> from rubrix.metrics.token_classification import entity_tags
        >>> summary = entity_tags(name="example-dataset", entities=10)
        >>> summary.visualize() # will plot a bar chart with results
        >>> summary.data # The top-20 entity tags
    """
    current_client = client()

    metric = current_client.calculate_metric(name, metric="entity_tags", size=entities)

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.bar(
            metric.results,
            title=metric.description,
        ),
    )


def entity_density(name: str, interval: float = 0.005) -> MetricSummary:
    """Calculates the entity density distribution. Then entity density is calculated at
    record level for each mention as ``mention_length/tokens_length``

    Args:
        name:
            The dataset name.
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
    metric = current_client.calculate_metric(
        name, metric="entity_density", interval=interval
    )

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.histogram(
            metric.results,
            title=metric.description,
        ),
    )


def entity_capitalness(name: str) -> MetricSummary:
    """Calculates the entity capitalness. The entity capitalness splits the entity
    mention shape in 4 grous:

        ``UPPER``: All charactes in entity mention are upper case

        ``LOWER``: All charactes in entity mention are lower case

        ``FIRST``: The mention is capitalized

        ``MIDDLE``: Some character in mention between first and last is capitalized

    Args:
        name:
            The dataset name.

    Returns:
        The summary entity capitalness distribution

    Examples:
        >>> from rubrix.metrics.token_classification import entity_capitalness
        >>> summary = entity_capitalness(name="example-dataset")
        >>> summary.visualize()
    """
    current_client = client()
    metric = current_client.calculate_metric(name, metric="entity_capitalness")

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.bar(
            metric.results,
            title=metric.description,
        ),
    )


def mention_consistency(name: str, mentions: int = 10):
    """Calculates the entity consistency for top mentions in dataset.
    The entity consistency defines entity variability for a given mention. For example, a mention `first` identified
    in the whole dataset as `Cardinal`, `Person` and `Time` is less consistent than a mention `Peter` identified as
    `Person` in the whole dataset.

    Args:
        name:
            The dataset name.
        mentions:
            The number of top mentions top retrieve

    Returns:
        The summary entity capitalness distribution

    Examples:
        >>> from rubrix.metrics.token_classification import mention_consistency
        >>> summary = entity_capitalness(name="example-dataset")
        >>> summary.visualize()
    """
    current_client = client()
    metric = current_client.calculate_metric(
        name, metric="mention_consistency", size=mentions
    )
    labels = ["Mentions"]
    parents = [""]
    values = [len(metric.results["mentions"])]
    for mention in metric.results["mentions"]:
        labels.append(mention["mention"])
        parents.append("Mentions")
        values.append(len(mention["entities"]))
        for entity in mention["entities"]:
            labels.append(entity["entity"])
            parents.append(mention["mention"])
            values.append(1)

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.multilevel_pie(
            labels, parents, values, title=metric.description
        ),
    )
