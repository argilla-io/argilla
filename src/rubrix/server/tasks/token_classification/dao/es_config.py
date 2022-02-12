from rubrix.server.commons.es_helpers import nested_mappings_from_base_model
from rubrix.server.tasks.commons.dao.es_config import mappings
from rubrix.server.tasks.token_classification.metrics import (
    MentionMetrics,
    TokenMetrics,
)


def mentions_mappings():
    return {
        "type": "nested",
        "properties": {
            "mention": mappings.keyword_field(),
            "entity": mappings.keyword_field(),
            "score": mappings.decimal_field(),
        },
    }


def token_classification_mappings():
    metrics_mentions_mappings = nested_mappings_from_base_model(MentionMetrics)
    _mentions_mappings = mentions_mappings()
    return {
        "_source": mappings.source(
            excludes=[
                # "words", # Cannot be exclude since comment text_length metric  is computed using this source fields
                "predicted",
                "predicted_as",
                "predicted_by",
                "annotated_as",
                "annotated_by",
                "score",
                "predicted_mentions",
                "mentions",
            ]
        ),
        "properties": {
            "predicted": mappings.keyword_field(),
            "annotated_as": mappings.keyword_field(),
            "predicted_as": mappings.keyword_field(),
            "score": {"type": "float"},
            "predicted_mentions": _mentions_mappings,
            "mentions": _mentions_mappings,
            "tokens": mappings.keyword_field(),
            # TODO: This must be unified with metrics.py module
            "metrics.tokens": nested_mappings_from_base_model(TokenMetrics),
            "metrics.predicted.mentions": metrics_mentions_mappings,
            "metrics.annotated.mentions": metrics_mentions_mappings,
        },
    }
