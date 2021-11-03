from rubrix import _client_instance as client
from rubrix.metrics import helpers
from rubrix.metrics.models import MetricSummary


def tokens_length(name: str, interval: int = 1) -> MetricSummary:
    """Computes the tokens length distribution

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
    """Computes mentions length distribution (in number of tokens)

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


def entity_labels(name: str, labels: int = 50) -> MetricSummary:
    """Computes the entity labels distribution

    Args:
        name:
            The dataset name.
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

    metric = current_client.calculate_metric(name, metric="entity_labels", size=labels)

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.bar(
            metric.results,
            title=metric.description,
        ),
    )


def entity_density(name: str, interval: float = 0.005) -> MetricSummary:
    """Computes the entity density distribution. Then entity density is calculated at
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
    """Computes the entity capitalness. The entity capitalness splits the entity
    mention shape in 4 groups:

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


def entity_consistency(name: str, mentions: int = 10, threshold: int = 2):
    """Computes the consistency for top entity mentions in the dataset.

    Entity consistency defines the label variability for a given mention. For example, a mention `first` identified
    in the whole dataset as `Cardinal`, `Person` and `Time` is less consistent than a mention `Peter` identified as
    `Person` in the dataset.

    Args:
        name:
            The dataset name.
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
    metric = current_client.calculate_metric(
        name, metric="entity_consistency", size=mentions, interval=threshold
    )
    labels = ["Mentions"]
    parents = [""]
    values = [len(metric.results["mentions"])]
    for mention in metric.results["mentions"]:
        labels.append(mention["mention"])
        parents.append("Mentions")
        values.append(len(mention["entities"]))
        for entity in mention["entities"]:
            labels.append(entity["label"])
            parents.append(mention["mention"])
            values.append(1)

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.tree_map(
            labels, parents, values, title=metric.description
        ),
    )
