from rubrix import _client_instance as client
from rubrix.metrics import helpers
from rubrix.metrics.models import MetricSummary


def tokens_length(name: str, interval: int = 1) -> MetricSummary:
    current_client = client()

    metric = current_client.calculate_metric(
        name, metric="tokens_length", interval=interval
    )

    return MetricSummary(
        data=metric.results,
        build_visualization=lambda: helpers.histogram(
            metric.results,
            title=metric.description,
            x_legend="# tokens",
        ),
    )


def mention_length(name: str, interval: int = 1) -> MetricSummary:
    current_client = client()

    metric = current_client.calculate_metric(
        name, metric="mention_length", interval=interval
    )

    return MetricSummary(
        data=metric.results,
        build_visualization=lambda: helpers.histogram(
            metric.results,
            title=metric.description,
            x_legend="# tokens",
        ),
    )


def entity_tags(name: str, entities: int = 50) -> MetricSummary:
    current_client = client()

    metric = current_client.calculate_metric(name, metric="entity_tags", size=entities)

    return MetricSummary(
        data=metric.results,
        build_visualization=lambda: helpers.bar(
            metric.results,
            title=metric.description,
        ),
    )


def entity_density(name: str, interval: float = 0.005) -> MetricSummary:
    current_client = client()
    metric = current_client.calculate_metric(
        name, metric="entity_density", interval=interval
    )

    return MetricSummary(
        data=metric.results,
        build_visualization=lambda: helpers.histogram(
            metric.results,
            title=metric.description,
        ),
    )


def entity_capitalness(name: str) -> MetricSummary:
    current_client = client()
    metric = current_client.calculate_metric(name, metric="entity_capitalness")

    return MetricSummary(
        data=metric.results,
        build_visualization=lambda: helpers.bar(
            metric.results,
            title=metric.description,
        ),
    )


def mention_consistency(name: str, mentions: int = 10):
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

    return MetricSummary(
        data=metric.results,
        build_visualization=lambda: helpers.multilevel_pie(
            labels,
            parents,
            values,
            title="\n".join([metric.name, metric.description or ""]),
        ),
    )
