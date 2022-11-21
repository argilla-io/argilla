#  coding=utf-8
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

"""
This module contains the data models for the interface
"""

import datetime
import logging
import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from deprecated import deprecated
from pydantic import BaseModel, Field, PrivateAttr, root_validator, validator

from argilla import _messages
from argilla._constants import DEFAULT_MAX_KEYWORD_LENGTH
from argilla.utils.span_utils import SpanUtils

_LOGGER = logging.getLogger(__name__)


class _Validators(BaseModel):
    """Base class for our record models that takes care of general validations"""

    @validator("metadata", check_fields=False)
    def _check_value_length(cls, metadata):
        """Checks metadata values length and warn message for large values"""
        if not metadata:
            return metadata

        default_length_exceeded = False
        for v in metadata.values():
            if isinstance(v, str) and len(v) > DEFAULT_MAX_KEYWORD_LENGTH:
                default_length_exceeded = True
                break

        if default_length_exceeded:
            message = (
                "Some metadata values could exceed the max length. For those cases, values will be"
                f" truncated by keeping only the last {DEFAULT_MAX_KEYWORD_LENGTH} characters. "
                + _messages.ARGILLA_METADATA_FIELD_WARNING_MESSAGE
            )
            warnings.warn(message, UserWarning)

        return metadata

    @validator("metadata", check_fields=False)
    def _none_to_empty_dict(cls, v):
        if v is None:
            return {}
        return v

    @validator("prediction_agent", check_fields=False)
    def _check_prediction_agent(cls, v, values):
        """Triggers a warning when ONLY prediction agent is provided"""
        if v and values["prediction"] is None:
            warnings.warn(
                "You provided an `prediction_agent`, but no `prediction`. "
                "The `prediction_agent` will not be logged to the server."
            )
        return v

    @validator("annotation_agent", check_fields=False)
    def _check_annotation_agent(cls, v, values):
        """Triggers a warning when ONLY annotation agent is provided"""
        if v and values["annotation"] is None:
            warnings.warn(
                "You provided an `annotation_agent`, but no `annotation`. "
                "The `annotation_agent` will not be logged to the server."
            )
        return v

    @validator("event_timestamp", check_fields=False)
    def _nat_to_none(cls, v):
        """Converts pandas `NaT`s to `None`s"""
        if v is pd.NaT:
            return None
        return v

    @root_validator
    def _check_and_update_status(cls, values):
        """Updates the status if an annotation is provided and no status is specified."""
        values["status"] = values.get("status") or (
            "Default" if values.get("annotation") is None else "Validated"
        )

        return values

    class Config:
        extra = "forbid"


class BulkResponse(BaseModel):
    """Summary response when logging records to the argilla server.

    Args:
        dataset: The dataset name.
        processed: Number of records in bulk.
        failed: Number of failed records.
    """

    dataset: str
    processed: int
    failed: Optional[int] = 0


class TokenAttributions(BaseModel):
    """Attribution of the token to the predicted label.

    In the argilla app this is only supported for ``TextClassificationRecord`` and the ``multi_label=False`` case.

    Args:
        token: The input token.
        attributions: A dictionary containing label-attribution pairs.
    """

    token: str
    attributions: Dict[str, float] = Field(default_factory=dict)


class TextClassificationRecord(_Validators):
    """Record for text classification

    Args:
        text:
            The input of the record. Provide either 'text' or 'inputs'.
        inputs:
            Various inputs of the record (see examples below).
            Provide either 'text' or 'inputs'.
        prediction:
            A list of tuples containing the predictions for the record.
            The first entry of the tuple is the predicted label, the second entry is its corresponding score.
        prediction_agent:
            Name of the prediction agent. By default, this is set to the hostname of your machine.
        annotation:
            A string or a list of strings (multilabel) corresponding to the annotation (gold label) for the record.
        annotation_agent:
            Name of the prediction agent. By default, this is set to the hostname of your machine.
        multi_label:
            Is the prediction/annotation for a multi label classification task? Defaults to `False`.
        explanation:
            A dictionary containing the attributions of each token to the prediction.
            The keys map the input of the record (see `inputs`) to the `TokenAttributions`.
        id:
            The id of the record. By default (`None`), we will generate a unique ID for you.
        metadata:
            Meta data for the record. Defaults to `{}`.
        status:
            The status of the record. Options: 'Default', 'Edited', 'Discarded', 'Validated'.
            If an annotation is provided, this defaults to 'Validated', otherwise 'Default'.
        event_timestamp:
            The timestamp of the record.
        metrics:
            READ ONLY! Metrics at record level provided by the server when using `rg.load`.
            This attribute will be ignored when using `rg.log`.
        search_keywords:
            READ ONLY! Relevant record keywords/terms for provided query when using `rg.load`.
            This attribute will be ignored when using `rg.log`.
    Examples:
        >>> # Single text input
        >>> import argilla as rg
        >>> record = rg.TextClassificationRecord(
        ...     text="My first argilla example",
        ...     prediction=[('eng', 0.9), ('esp', 0.1)]
        ... )
        >>>
        >>> # Various inputs
        >>> record = rg.TextClassificationRecord(
        ...     inputs={
        ...         "subject": "Has ganado 1 million!",
        ...         "body": "Por usar argilla te ha tocado este premio: <link>"
        ...     },
        ...     prediction=[('spam', 0.99), ('ham', 0.01)],
        ...     annotation="spam"
        ... )
    """

    text: Optional[str] = None
    inputs: Optional[Union[str, List[str], Dict[str, Union[str, List[str]]]]] = None

    prediction: Optional[List[Tuple[str, float]]] = None
    prediction_agent: Optional[str] = None
    annotation: Optional[Union[str, List[str]]] = None
    annotation_agent: Optional[str] = None

    multi_label: bool = False
    explanation: Optional[Dict[str, List[TokenAttributions]]] = None

    id: Optional[Union[int, str]] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    status: Optional[str] = None
    event_timestamp: Optional[datetime.datetime] = None

    metrics: Optional[Dict[str, Any]] = None
    search_keywords: Optional[List[str]] = None

    @root_validator
    def _check_text_and_inputs(cls, values):
        """Check if either text or inputs were provided. Copy text to inputs."""
        if isinstance(values.get("inputs"), str):
            warnings.warn(
                "In the future, the `inputs` argument of the `TextClassificationRecord`"
                " will not accept strings. Please use the `text` argument in that case."
                " Make sure to adapt your code accordingly.",
                category=FutureWarning,
            )

        if values.get("inputs") is not None and not isinstance(values["inputs"], dict):
            values["inputs"] = dict(text=values["inputs"])

        if (values.get("text") is None and values.get("inputs") is None) or (
            values.get("text") is not None
            and values.get("inputs") is not None
            and values["text"] != values["inputs"].get("text")
        ):
            raise ValueError(
                "For a TextClassificationRecord you must provide either 'text' or"
                " 'inputs'"
            )

        if values.get("text") is not None:
            values["inputs"] = dict(text=values["text"])
        elif len(values["inputs"]) == 1 and "text" in values["inputs"]:
            values["text"] = values["inputs"]["text"]

        return values

    def __setattr__(self, name: str, value: Any):
        """Make text and inputs immutable"""
        if name in ["text", "inputs"]:
            raise AttributeError(f"You cannot assign a new value to `{name}`")
        super().__setattr__(name, value)


class TokenClassificationRecord(_Validators):
    """Record for a token classification task

    Args:
        text:
            The input of the record
        tokens:
            The tokenized input of the record. We use this to guide the annotation process
            and to cross-check the spans of your `prediction`/`annotation`.
        prediction:
            A list of tuples containing the predictions for the record. The first entry of the tuple is the name of
            predicted entity, the second and third entry correspond to the start and stop character index of the entity.
            The fourth entry is optional and corresponds to the score of the entity (a float number between 0 and 1).
        prediction_agent:
            Name of the prediction agent. By default, this is set to the hostname of your machine.
        annotation:
            A list of tuples containing annotations (gold labels) for the record. The first entry of the tuple is the
            name of the entity, the second and third entry correspond to the start and stop char index of the entity.
        annotation_agent:
            Name of the prediction agent. By default, this is set to the hostname of your machine.
        id:
            The id of the record. By default (None), we will generate a unique ID for you.
        metadata:
            Meta data for the record. Defaults to `{}`.
        status:
            The status of the record. Options: 'Default', 'Edited', 'Discarded', 'Validated'.
            If an annotation is provided, this defaults to 'Validated', otherwise 'Default'.
        event_timestamp:
            The timestamp of the record.
        metrics:
            READ ONLY! Metrics at record level provided by the server when using `rg.load`.
            This attribute will be ignored when using `rg.log`.
        search_keywords:
            READ ONLY! Relevant record keywords/terms for provided query when using `rg.load`.
            This attribute will be ignored when using `rg.log`.
    Examples:
        >>> import argilla as rg
        >>> record = rg.TokenClassificationRecord(
        ...     text = "Michael is a professor at Harvard",
        ...     tokens = ["Michael", "is", "a", "professor", "at", "Harvard"],
        ...     prediction = [('NAME', 0, 7), ('LOC', 26, 33)]
        ... )
    """

    text: Optional[str] = Field(None, min_length=1)
    tokens: Optional[Union[List[str], Tuple[str, ...]]] = None

    prediction: Optional[
        List[Union[Tuple[str, int, int], Tuple[str, int, int, Optional[float]]]]
    ] = None
    prediction_agent: Optional[str] = None
    annotation: Optional[List[Tuple[str, int, int]]] = None
    annotation_agent: Optional[str] = None

    id: Optional[Union[int, str]] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    status: Optional[str] = None
    event_timestamp: Optional[datetime.datetime] = None

    metrics: Optional[Dict[str, Any]] = None
    search_keywords: Optional[List[str]] = None

    _span_utils: SpanUtils = PrivateAttr()

    def __init__(
        self,
        text: str = None,
        tokens: List[str] = None,
        tags: Optional[List[str]] = None,
        **data,
    ):
        if text is None and tokens is None:
            raise AssertionError(
                "Missing fields: At least one of `text` or `tokens` argument must be"
                " provided!"
            )

        if (data.get("annotation") or data.get("prediction")) and text is None:
            raise AssertionError(
                "Missing field `text`: "
                "char level spans must be provided with a raw text sentence"
            )

        if text is None:
            text = " ".join(tokens)

        super().__init__(text=text, tokens=tokens, **data)

        self._span_utils = SpanUtils(self.text, self.tokens)

        if self.annotation:
            self.annotation = self._validate_spans(self.annotation)
        if self.prediction:
            self.prediction = self._validate_spans(self.prediction)

        if self.annotation and tags:
            _LOGGER.warning("Annotation already provided, `tags` won't be used")
        elif tags:
            self.annotation = self._span_utils.from_tags(tags)

    def __setattr__(self, name: str, value: Any):
        """Make text and tokens immutable"""
        if name in ["text", "tokens"]:
            raise AttributeError(f"You cannot assign a new value to `{name}`")
        super().__setattr__(name, value)

    def _validate_spans(
        self, spans: List[Tuple[str, int, int]]
    ) -> List[Tuple[str, int, int]]:
        """Validates the entity spans with respect to the tokens.

        If necessary, also performs an automatic correction of the spans.

        Args:
            spans: The entity spans to validate.

        Returns:
            The optionally corrected spans.

        Raises:
            ValidationError: If spans are not valid or misaligned.
        """
        try:
            self._span_utils.validate(spans)
        except ValueError:
            spans = self._span_utils.correct(spans)
            self._span_utils.validate(spans)

        return spans

    @validator("tokens", pre=True)
    def _normalize_tokens(cls, value):
        if isinstance(value, list):
            value = tuple(value)

        assert len(value) > 0, "At least one token should be provided"
        return value

    @validator("prediction")
    def _add_default_score(
        cls,
        prediction: Optional[
            List[Union[Tuple[str, int, int], Tuple[str, int, int, Optional[float]]]]
        ],
    ):
        """Adds the default score to the predictions if it is missing"""
        if prediction is None:
            return prediction
        return [
            (pred[0], pred[1], pred[2], 0.0)
            if len(pred) == 3
            else (pred[0], pred[1], pred[2], pred[3] or 0.0)
            for pred in prediction
        ]

    @validator("text")
    def _check_if_empty_after_strip(cls, text: str):
        assert text.strip(), "The provided `text` contains only whitespaces."
        return text

    @property
    def __chars2tokens__(self) -> Dict[int, int]:
        """DEPRECATED, please use the ``argilla.utils.span_utils.SpanUtils.chars_to_token_idx`` attribute."""
        warnings.warn(
            "The `__chars2tokens__` attribute is deprecated and will be removed in a"
            " future version. Please use the"
            " `argilla.utils.span_utils.SpanUtils.char_to_token_idx` attribute"
            " instead.",
            FutureWarning,
        )
        return self._span_utils.char_to_token_idx

    @property
    def __tokens2chars__(self) -> Dict[int, Tuple[int, int]]:
        """DEPRECATED, please use the ``argilla.utils.span_utils.SpanUtils.chars_to_token_idx`` attribute."""
        warnings.warn(
            "The `__tokens2chars__` attribute is deprecated and will be removed in a"
            " future version. Please use the"
            " `argilla.utils.span_utils.SpanUtils.token_to_char_idx` attribute"
            " instead.",
            FutureWarning,
        )
        return self._span_utils.token_to_char_idx

    def char_id2token_id(self, char_idx: int) -> Optional[int]:
        """DEPRECATED, please use the ``argilla.utisl.span_utils.SpanUtils.char_to_token_idx`` dict instead."""
        warnings.warn(
            "The `char_id2token_id` method is deprecated and will be removed in a"
            " future version. Please use the"
            " `argilla.utils.span_utils.SpanUtils.char_to_token_idx` dict instead.",
            FutureWarning,
        )
        return self._span_utils.char_to_token_idx.get(char_idx)

    def token_span(self, token_idx: int) -> Tuple[int, int]:
        """DEPRECATED, please use the ``argilla.utisl.span_utils.SpanUtils.token_to_char_idx`` dict instead."""
        warnings.warn(
            "The `token_span` method is deprecated and will be removed in a future"
            " version. Please use the"
            " `argilla.utils.span_utils.SpanUtils.token_to_char_idx` dict instead.",
            FutureWarning,
        )
        if token_idx not in self._span_utils.token_to_char_idx:
            raise IndexError(f"Token id {token_idx} out of bounds")
        return self._span_utils.token_to_char_idx[token_idx]

    def spans2iob(
        self, spans: Optional[List[Tuple[str, int, int]]] = None
    ) -> Optional[List[str]]:
        """DEPRECATED, please use the ``argilla.utils.SpanUtils.to_tags()`` method."""
        warnings.warn(
            "'spans2iob' is deprecated and will be removed in a future version. Please"
            " use the `argilla.utils.SpanUtils.to_tags()` method instead, and adapt"
            " your code accordingly.",
            FutureWarning,
        )

        if spans is None:
            return None
        return self._span_utils.to_tags(spans)


class TextGenerationRecord(_Validators):
    """Record for a text to text task

    Args:
        text:
            The input of the record
        prediction:
            A list of strings or tuples containing predictions for the input text.
            If tuples, the first entry is the predicted text, the second entry is its corresponding score.
        prediction_agent:
            Name of the prediction agent. By default, this is set to the hostname of your machine.
        annotation:
            A string representing the expected output text for the given input text.
        annotation_agent:
            Name of the prediction agent. By default, this is set to the hostname of your machine.
        id:
            The id of the record. By default (None), we will generate a unique ID for you.
        metadata:
            Meta data for the record. Defaults to `{}`.
        status:
            The status of the record. Options: 'Default', 'Edited', 'Discarded', 'Validated'.
            If an annotation is provided, this defaults to 'Validated', otherwise 'Default'.
        event_timestamp:
            The timestamp of the record.
        metrics:
            READ ONLY! Metrics at record level provided by the server when using `rg.load`.
            This attribute will be ignored when using `rg.log`.
        search_keywords:
            READ ONLY! Relevant record keywords/terms for provided query when using `rg.load`.
            This attribute will be ignored when using `rg.log`.

    Examples:
        >>> import argilla as rg
        >>> record = rg.Text2TextRecord(
        ...     text="My name is Sarah and I love my dog.",
        ...     prediction=["Je m'appelle Sarah et j'aime mon chien."]
        ... )
    """

    text: str

    prediction: Optional[List[Union[str, Tuple[str, float]]]] = None
    prediction_agent: Optional[str] = None
    annotation: Optional[str] = None
    annotation_agent: Optional[str] = None

    id: Optional[Union[int, str]] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    status: Optional[str] = None
    event_timestamp: Optional[datetime.datetime] = None

    metrics: Optional[Dict[str, Any]] = None
    search_keywords: Optional[List[str]] = None

    @validator("prediction")
    def prediction_as_tuples(
        cls, prediction: Optional[List[Union[str, Tuple[str, float]]]]
    ):
        """Preprocess the predictions and wraps them in a tuple if needed"""
        if prediction is None:
            return prediction
        return [(pred, 1.0) if isinstance(pred, str) else pred for pred in prediction]


@deprecated("Use TextGenerationRecord instead.")
class Text2TextRecord(TextGenerationRecord):
    pass


Record = Union[
    TextClassificationRecord,
    TokenClassificationRecord,
    Text2TextRecord,
    TextGenerationRecord,
]
