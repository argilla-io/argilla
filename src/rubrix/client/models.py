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
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from pydantic import BaseModel, Field, PrivateAttr, root_validator, validator

from rubrix._constants import MAX_KEYWORD_LENGTH
from rubrix.utils import limit_value_length

_LOGGER = logging.getLogger(__name__)


class _Validators(BaseModel):
    """Base class for our record models that takes care of general validations"""

    @validator("metadata", check_fields=False)
    def _check_value_length(cls, v):
        """Checks metadata values length and apply value truncation for large values"""
        new_metadata = limit_value_length(v, max_length=MAX_KEYWORD_LENGTH)
        if new_metadata != v:
            warnings.warn(
                "Some metadata values exceed the max length. "
                f"Those values will be truncated by keeping only the last {MAX_KEYWORD_LENGTH} characters."
            )

        return new_metadata

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
    """Summary response when logging records to the Rubrix server.

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

    In the Rubrix app this is only supported for ``TextClassificationRecord`` and the ``multi_label=False`` case.

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
            READ ONLY! Metrics at record level provided by the server when using `rb.load`.
            This attribute will be ignored when using `rb.log`.
        search_keywords:
            READ ONLY! Relevant record keywords/terms for provided query when using `rb.load`.
            This attribute will be ignored when using `rb.log`.
    Examples:
        >>> # Single text input
        >>> import rubrix as rb
        >>> record = rb.TextClassificationRecord(
        ...     text="My first rubrix example",
        ...     prediction=[('eng', 0.9), ('esp', 0.1)]
        ... )
        >>>
        >>> # Various inputs
        >>> record = rb.TextClassificationRecord(
        ...     inputs={
        ...         "subject": "Has ganado 1 million!",
        ...         "body": "Por usar Rubrix te ha tocado este premio: <link>"
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
                "In the future, the `inputs` argument of the `TextClassificationRecord` will not accept strings."
                "Please use the `text` argument in that case. Make sure to adapt your code accordingly.",
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
                "For a TextClassificationRecord you must provide either 'text' or 'inputs'"
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
            READ ONLY! Metrics at record level provided by the server when using `rb.load`.
            This attribute will be ignored when using `rb.log`.
        search_keywords:
            READ ONLY! Relevant record keywords/terms for provided query when using `rb.load`.
            This attribute will be ignored when using `rb.log`.
    Examples:
        >>> import rubrix as rb
        >>> record = rb.TokenClassificationRecord(
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

    __chars2tokens__: Dict[int, int] = PrivateAttr(default=None)
    __tokens2chars__: Dict[int, Tuple[int, int]] = PrivateAttr(default=None)

    def __init__(
        self,
        text: str = None,
        tokens: List[str] = None,
        tags: Optional[List[str]] = None,
        **data,
    ):
        if text is None and tokens is None:
            raise AssertionError(
                "Missing fields: At least one of `text` or `tokens` argument must be provided!"
            )

        if (data.get("annotation") or data.get("prediction")) and text is None:
            raise AssertionError(
                "Missing field `text`: "
                "char level spans must be provided with a raw text sentence"
            )

        if text is None:
            text = " ".join(tokens)

        super().__init__(text=text, tokens=tokens, **data)
        if self.annotation and tags:
            _LOGGER.warning("Annotation already provided, `tags` won't be used")
            return
        if tags:
            self.annotation = self.__tags2entities__(tags)

    def __tags2entities__(self, tags: List[str]) -> List[Tuple[str, int, int]]:
        idx = 0
        entities = []
        entity_starts = False
        while idx < len(tags):
            tag = tags[idx]
            if tag == "O":
                entity_starts = False
            if tag != "O":
                prefix, entity = tag.split("-")
                if prefix in ["B", "U"]:
                    if prefix == "B":
                        entity_starts = True
                    char_start, char_end = self.token_span(token_idx=idx)
                    entities.append(
                        {"entity": entity, "start": char_start, "end": char_end + 1}
                    )
                elif prefix in ["I", "L"]:
                    if not entity_starts:
                        _LOGGER.warning(
                            "Detected non-starting tag and first entity token was not found."
                            f"Assuming {tag} as first entity token"
                        )
                        entity_starts = True
                        char_start, char_end = self.token_span(token_idx=idx)
                        entities.append(
                            {"entity": entity, "start": char_start, "end": char_end + 1}
                        )

                    _, char_end = self.token_span(token_idx=idx)
                    entities[-1]["end"] = char_end + 1
            idx += 1
        return [(value["entity"], value["start"], value["end"]) for value in entities]

    def __setattr__(self, name: str, value: Any):
        """Make text and tokens immutable"""
        if name in ["text", "tokens"]:
            raise AttributeError(f"You cannot assign a new value to `{name}`")
        super().__setattr__(name, value)

    @validator("tokens", pre=True)
    def _normalize_tokens(cls, value):
        if isinstance(value, list):
            value = tuple(value)

        assert len(value) > 0, "At least one token should be provided"
        return value

    @validator("prediction")
    def add_default_score(
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

    @staticmethod
    def __build_indices_map__(
        text: str, tokens: Tuple[str, ...]
    ) -> Tuple[Dict[int, int], Dict[int, Tuple[int, int]]]:
        """
        Build the indices mapping between text characters and tokens where belongs to,
        and vice versa.

        chars2tokens index contains is the token idx where i char is contained (if any).

        Out-of-token characters won't be included in this map,
        so access should be using ``chars2tokens_map.get(i)``
        instead of ``chars2tokens_map[i]``.

        """

        def chars2tokens_index(text_, tokens_):
            chars_map = {}
            current_token = 0
            current_token_char_start = 0
            for idx, char in enumerate(text_):
                relative_idx = idx - current_token_char_start
                if (
                    relative_idx < len(tokens_[current_token])
                    and char == tokens_[current_token][relative_idx]
                ):
                    chars_map[idx] = current_token
                elif (
                    current_token + 1 < len(tokens_)
                    and relative_idx >= len(tokens_[current_token])
                    and char == tokens_[current_token + 1][0]
                ):
                    current_token += 1
                    current_token_char_start += relative_idx
                    chars_map[idx] = current_token
            return chars_map

        def tokens2chars_index(
            chars2tokens: Dict[int, int]
        ) -> Dict[int, Tuple[int, int]]:
            tokens2chars_map = defaultdict(list)
            for c, t in chars2tokens.items():
                tokens2chars_map[t].append(c)

            return {
                token_idx: (min(chars), max(chars))
                for token_idx, chars in tokens2chars_map.items()
            }

        chars2tokens_idx = chars2tokens_index(text_=text, tokens_=tokens)
        return chars2tokens_idx, tokens2chars_index(chars2tokens_idx)

    def char_id2token_id(self, char_idx: int) -> Optional[int]:
        """
        Given a character id, returns the token id it belongs to.
        ``None`` otherwise
        """

        if self.__chars2tokens__ is None:
            self.__chars2tokens__, self.__tokens2chars__ = self.__build_indices_map__(
                self.text, tuple(self.tokens)
            )
        return self.__chars2tokens__.get(char_idx)

    def token_span(self, token_idx: int) -> Tuple[int, int]:
        """
        Given a token id, returns the start and end characters.
        Raises an ``IndexError`` if token id is out of tokens list indices
        """
        if self.__tokens2chars__ is None:
            self.__chars2tokens__, self.__tokens2chars__ = self.__build_indices_map__(
                self.text, tuple(self.tokens)
            )
        if token_idx not in self.__tokens2chars__:
            raise IndexError(f"Token id {token_idx} out of bounds")
        return self.__tokens2chars__[token_idx]

    def spans2iob(
        self, spans: Optional[List[Tuple[str, int, int]]] = None
    ) -> Optional[List[str]]:
        """Build the iob tags sequence for a list of spans annoations"""

        if spans is None:
            return None

        tags = ["O"] * len(self.tokens)
        for label, start, end in spans:
            token_start = self.char_id2token_id(start)
            token_end = self.char_id2token_id(end - 1)
            assert (
                token_start is not None and token_end is not None
            ), "Provided spans are missaligned at token level"
            tags[token_start] = f"B-{label}"
            for idx in range(token_start + 1, token_end + 1):
                tags[idx] = f"I-{label}"

        return tags


class Text2TextRecord(_Validators):
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
            READ ONLY! Metrics at record level provided by the server when using `rb.load`.
            This attribute will be ignored when using `rb.log`.
        search_keywords:
            READ ONLY! Relevant record keywords/terms for provided query when using `rb.load`.
            This attribute will be ignored when using `rb.log`.

    Examples:
        >>> import rubrix as rb
        >>> record = rb.Text2TextRecord(
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


Record = Union[TextClassificationRecord, TokenClassificationRecord, Text2TextRecord]
