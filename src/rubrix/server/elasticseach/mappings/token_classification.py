from rubrix.server.apis.v0.models.metrics.token_classification import (
    MentionMetrics,
    TokenMetrics,
    TokenTagMetrics,
)
from rubrix.server.elasticseach.mappings.helpers import mappings
from rubrix.server.elasticseach.query_helpers import nested_mappings_from_base_model


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
    metrics_tags_mappings = nested_mappings_from_base_model(TokenTagMetrics)
    _mentions_mappings = mentions_mappings()  # TODO: remove
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
            "annotated_as": mappings.keyword_field(enable_text_search=True),
            "predicted_as": mappings.keyword_field(enable_text_search=True),
            "score": {"type": "float"},
            "predicted_mentions": _mentions_mappings,  # TODO: remove
            "mentions": _mentions_mappings,  # TODO: remove
            "tokens": mappings.keyword_field(),
            "metrics.tokens": nested_mappings_from_base_model(TokenMetrics),
            "metrics.predicted.mentions": metrics_mentions_mappings,
            "metrics.annotated.mentions": metrics_mentions_mappings,
            "metrics.predicted.tags": metrics_tags_mappings,
            "metrics.annotated.tags": metrics_tags_mappings,
        },
    }
