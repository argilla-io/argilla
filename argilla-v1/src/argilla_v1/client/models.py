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
import uuid
import warnings
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from deprecated import deprecated

from argilla_v1 import _messages
from argilla_v1._constants import DEFAULT_MAX_KEYWORD_LENGTH
from argilla_v1.pydantic_v1 import BaseModel, Field, PrivateAttr, root_validator, validator
from argilla_v1.utils.span_utils import SpanUtils

_LOGGER = logging.getLogger(__name__)

Vectors = Dict[str, List[float]]


FRAMEWORK_TO_NAME_MAPPING = {
    "transformers": "Transformers",
    "peft": "PEFT Transformers library",
    "setfit": "SetFit Transformers library",
    "spacy": "Spacy Explosion",
    "spacy-transformers": "Spacy Transformers Explosion library",
    "span_marker": "SpanMarker Tom Aarsen library",
    "spark-nlp": "Spark NLP John Snow Labs library",
    "openai": "OpenAI LLMs",
    "trl": "Transformer Reinforcement Learning",
    "sentence-transformers": "Sentence Transformers library",
}


class Framework(Enum):
    """Frameworks supported by Argilla

    Options:
        transformers: Transformers
        peft: PEFT Transformers library
        setfit: SetFit Transformers library
        spacy: Spacy Explosion
        spacy-transformers: Spacy Transformers Explosion library
        span_marker: SpanMarker Tom Aarsen library
        spark-nlp: Spark NLP John Snow Labs library
        openai: OpenAI LLMs
        trl: Transformer Reinforcement Learning
        sentence-transformers: Sentence Transformers library
    """

    TRANSFORMERS = "transformers"
    PEFT = "peft"
    SETFIT = "setfit"
    SPACY = "spacy"
    SPACY_TRANSFORMERS = "spacy-transformers"
    SPAN_MARKER = "span_marker"
    SPARK_NLP = "spark-nlp"
    OPENAI = "openai"
    TRL = "trl"
    SENTENCE_TRANSFORMERS = "sentence-transformers"
    # AUTOTRAIN = "autotrain"

    @classmethod
    def _missing_(cls, value):
        raise ValueError(
            f"{value!r} is not a valid {cls.__name__.lower()}, please select one of {list(cls._value2member_map_.keys())}"
        )

    def __str__(self) -> str:
        return self.value


class _Validators(BaseModel):
    """Base class for our record models that takes care of general validations"""

    # The metadata field name prefix defined for protected (non-searchable) values
    _PROTECTED_METADATA_FIELD_PREFIX = "_"

    _JS_MAX_SAFE_INTEGER = 9007199254740991

    @validator("metadata", check_fields=False)
    def _check_value_length(cls, metadata):
        """Checks metadata values length and warn message for large values"""
        if not metadata:
            return metadata

        default_length_exceeded = False
        for k, v in metadata.items():
            if k.startswith(cls._PROTECTED_METADATA_FIELD_PREFIX):
                continue
            if isinstance(v, str) and len(v) > DEFAULT_MAX_KEYWORD_LENGTH:
                default_length_exceeded = True
                break

        if default_length_exceeded:
            message = (
                "Some metadata values could exceed the max length. For those cases,"
                " values will be truncated by keeping only the last"
                f" {DEFAULT_MAX_KEYWORD_LENGTH} characters. " + _messages.ARGILLA_METADATA_FIELD_WARNING_MESSAGE
            )
            warnings.warn(message, UserWarning, stacklevel=2)

        return metadata

    @validator("metadata", check_fields=False)
    def _none_to_empty_dict(cls, v):
        if v is None:
            return {}
        return v

    @validator("id", check_fields=False, pre=True, always=True)
    def _normalize_id(cls, v):
        if v is None:
            return str(uuid.uuid4())
        if isinstance(v, int):
            message = (
                "Integer ids won't be supported in future versions. We recommend to start using strings instead. "
                "For datasets already containing integer values we recommend migrating them to avoid deprecation issues. "
                "See https://docs.v1.argilla.io/en/latest/getting_started/installation/configurations"
                "/database_migrations.html#elasticsearch"
            )
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            # See https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/MAX_SAFE_INTEGER
            if v > cls._JS_MAX_SAFE_INTEGER:
                message = (
                    "You've provided a big integer value. Use a string instead, otherwise you may experience some "
                    "problems using the UI. See "
                    "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number"
                    "/MAX_SAFE_INTEGER"
                )
                warnings.warn(message, UserWarning, stacklevel=2)
        elif not isinstance(v, str):
            raise TypeError(f"Invalid type for id. Expected {int} or {str}; found:{type(v)}")
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

    @validator("event_timestamp", check_fields=False, always=True)
    def _nat_to_none_and_one_to_now(cls, v):
        """Converts pandas `NaT`s to `None`s and None´s to datetime.now()"""
        if v is pd.NaT:
            v = None

        v = v or datetime.datetime.now()

        return v

    @root_validator(skip_on_failure=True)
    def _check_and_update_status(cls, values):
        """Updates the status if an annotation is provided and no status is specified."""
        values["status"] = values.get("status") or ("Default" if values.get("annotation") is None else "Validated")

        return values

    class Config:
        # https://docs.pydantic.dev/usage/model_config/#options
        extra = "forbid"
        validate_assignment = True


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
        vectors:
            Vectors data mappings of the natural language text containing class attributes
        multi_label:
            Is the prediction/annotation for a multi label classification task? Defaults to `False`.
        explanation:
            A dictionary containing the attributions of each token to the prediction.
            The keys map the input of the record (see `inputs`) to the `TokenAttributions`.
        id:
            The id of the record. By default (`None`), we will generate a unique ID for you.
        metadata:
            Metadata for the record. Defaults to `{}`.
        status:
            The status of the record. Options: 'Default', 'Edited', 'Discarded', 'Validated'.
            If an annotation is provided, this defaults to 'Validated', otherwise 'Default'.
        event_timestamp:
            The timestamp for the creation of the record. Defaults to `datetime.datetime.now()`.
        metrics:
            READ ONLY! Metrics at record level provided by the server when using `rg.load`.
            This attribute will be ignored when using `rg.log`.
        search_keywords:
            READ ONLY! Relevant record keywords/terms for provided query when using `rg.load`.
            This attribute will be ignored when using `rg.log`.
    Examples:
        >>> # Single text input
        >>> import argilla_v1 as rg
        >>> record = rg.TextClassificationRecord(
        ...     text="My first argilla example",
        ...     prediction=[('eng', 0.9), ('esp', 0.1)],
        ...     vectors = {
        ...         "english_bert_vector": [1.2, 2.3, 3.1, 3.3]
        ...     }
        ... )
        >>>
        >>> # Various inputs
        >>> record = rg.TextClassificationRecord(
        ...     inputs={
        ...         "subject": "Has ganado 1 million!",
        ...         "body": "Por usar argilla te ha tocado este premio: <link>"
        ...     },
        ...     prediction=[('spam', 0.99), ('ham', 0.01)],
        ...     annotation="spam",
        ...     vectors = {
        ...                     "distilbert_uncased":  [1.13, 4.1, 6.3, 4.2, 9.1],
        ...                     "xlm_roberta_cased": [1.1, 2.1, 3.3, 4.2, 2.1],
        ...             }
        ...     )
    """

    text: Optional[str] = None
    inputs: Optional[Union[str, List[str], Dict[str, Union[str, List[str]]]]] = None

    prediction: Optional[List[Tuple[str, float]]] = None
    prediction_agent: Optional[str] = None

    annotation: Optional[Union[str, List[str]]] = None
    annotation_agent: Optional[str] = None

    vectors: Optional[Vectors] = None

    multi_label: bool = False
    explanation: Optional[Dict[str, List[TokenAttributions]]] = None

    id: Optional[Union[int, str]] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    status: Optional[str] = None
    event_timestamp: Optional[datetime.datetime] = None

    metrics: Optional[Dict[str, Any]] = None
    search_keywords: Optional[List[str]] = None

    @root_validator(skip_on_failure=True)
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
            raise ValueError("For a TextClassificationRecord you must provide either 'text' or 'inputs'")

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
        vectors:
            Vector data mappings of the natural language text containing class attributes'
        id:
            The id of the record. By default (None), we will generate a unique ID for you.
        metadata:
            Metadata for the record. Defaults to `{}`.
        status:
            The status of the record. Options: 'Default', 'Edited', 'Discarded', 'Validated'.
            If an annotation is provided, this defaults to 'Validated', otherwise 'Default'.
        event_timestamp:
            The timestamp for the creation of the record. Defaults to `datetime.datetime.now()`.
        metrics:
            READ ONLY! Metrics at record level provided by the server when using `rg.load`.
            This attribute will be ignored when using `rg.log`.
        search_keywords:
            READ ONLY! Relevant record keywords/terms for provided query when using `rg.load`.
            This attribute will be ignored when using `rg.log`.
    Examples:
        >>> import argilla_v1 as rg
        >>> record = rg.TokenClassificationRecord(
        ...     text = "Michael is a professor at Harvard",
        ...     tokens = ["Michael", "is", "a", "professor", "at", "Harvard"],
        ...     prediction = [('NAME', 0, 7), ('LOC', 26, 33)],
        ...     vectors = {
        ...            "bert_base_uncased": [3.2, 4.5, 5.6, 8.9]
        ...          }
        ... )
    """

    text: Optional[str] = Field(None, min_length=1)
    tokens: Optional[Union[List[str], Tuple[str, ...]]] = None

    prediction: Optional[List[Union[Tuple[str, int, int], Tuple[str, int, int, Optional[float]]]]] = None
    prediction_agent: Optional[str] = None
    annotation: Optional[List[Tuple[str, int, int]]] = None
    annotation_agent: Optional[str] = None
    vectors: Optional[Vectors] = None

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
            raise AssertionError("Missing fields: At least one of `text` or `tokens` argument must be provided!")

        if (data.get("annotation") or data.get("prediction")) and text is None:
            raise AssertionError("Missing field `text`: " "char level spans must be provided with a raw text sentence")

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

    def _validate_spans(self, spans: List[Tuple[str, int, int]]) -> List[Tuple[str, int, int]]:
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
        prediction: Optional[List[Union[Tuple[str, int, int], Tuple[str, int, int, Optional[float]]]]],
    ):
        """Adds the default score to the predictions if it is missing"""
        if prediction is None:
            return prediction
        return [
            (pred[0], pred[1], pred[2], 0.0) if len(pred) == 3 else (pred[0], pred[1], pred[2], pred[3] or 0.0)
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

    def spans2iob(self, spans: Optional[List[Tuple[str, int, int]]] = None) -> Optional[List[str]]:
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
        vectors:
            Embedding data mappings of the natural language text containing class attributes'
        id:
            The id of the record. By default (None), we will generate a unique ID for you.
        metadata:
            Metadata for the record. Defaults to `{}`.
        status:
            The status of the record. Options: 'Default', 'Edited', 'Discarded', 'Validated'.
            If an annotation is provided, this defaults to 'Validated', otherwise 'Default'.
        event_timestamp:
            The timestamp for the creation of the record. Defaults to `datetime.datetime.now()`.
        metrics:
            READ ONLY! Metrics at record level provided by the server when using `rg.load`.
            This attribute will be ignored when using `rg.log`.
        search_keywords:
            READ ONLY! Relevant record keywords/terms for provided query when using `rg.load`.
            This attribute will be ignored when using `rg.log`.

    Examples:
        >>> import argilla_v1 as rg
        >>> record = rg.Text2TextRecord(
        ...     text="My name is Sarah and I love my dog.",
        ...     prediction=["Je m'appelle Sarah et j'aime mon chien."],
        ...     vectors = {
        ...         "bert_base_uncased": [1.2, 2.3, 3.4, 5.2, 6.5],
        ...         "xlm_multilingual_uncased": [2.2, 5.3, 5.4, 3.2, 2.5]
        ...     }
        ... )
    """

    text: str

    prediction: Optional[List[Union[str, Tuple[str, float]]]] = None
    prediction_agent: Optional[str] = None
    annotation: Optional[str] = None
    annotation_agent: Optional[str] = None
    vectors: Optional[Vectors] = None

    id: Optional[Union[int, str]] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    status: Optional[str] = None
    event_timestamp: Optional[datetime.datetime] = None

    metrics: Optional[Dict[str, Any]] = None
    search_keywords: Optional[List[str]] = None

    @validator("prediction")
    def prediction_as_tuples(cls, prediction: Optional[List[Union[str, Tuple[str, float]]]]):
        """Preprocess the predictions and wraps them in a tuple if needed"""
        if prediction is None:
            return prediction
        return [(pred, 1.0) if isinstance(pred, str) else pred for pred in prediction]


@deprecated("Use Text2TextRecord instead.")
class TextGenerationRecord(Text2TextRecord):  # TODO Remove TextGenerationRecord
    pass


Record = Union[
    TextClassificationRecord,
    TokenClassificationRecord,
    Text2TextRecord,
    TextGenerationRecord,
]
