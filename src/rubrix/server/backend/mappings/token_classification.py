from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from rubrix.server.backend.mappings.helpers import mappings
from rubrix.server.backend.query_helpers import nested_mappings_from_base_model


class MentionMetrics(BaseModel):
    """Mention metrics model"""

    value: str
    label: str
    score: float = Field(ge=0.0)
    capitalness: Optional[str] = Field(None)
    density: float = Field(ge=0.0)
    tokens_length: int = Field(g=0)
    chars_length: int = Field(g=0)


class TokenTagMetrics(BaseModel):
    value: str
    tag: str


class TokenMetrics(BaseModel):

    idx: int
    value: str
    char_start: int
    char_end: int
    length: int
    capitalness: Optional[str] = None
    score: Optional[float] = None
    tag: Optional[str] = None  # TODO: remove!
    custom: Dict[str, Any] = None


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
