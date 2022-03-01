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
import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from pydantic import BaseModel, Field, root_validator, validator

from rubrix._constants import MAX_KEYWORD_LENGTH
from rubrix.server.commons.helpers import limit_value_length


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
                "You provided an `prediction_agent`, but no `prediction`. The `prediction_agent` will not be logged to the server."
            )
        return v

    @validator("annotation_agent", check_fields=False)
    def _check_annotation_agent(cls, v, values):
        """Triggers a warning when ONLY annotation agent is provided"""
        if v and values["annotation"] is None:
            warnings.warn(
                "You provided an `annotation_agent`, but no `annotation`. The `annotation_agent` will not be logged to the server."
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
        inputs:
            The inputs of the record
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
        >>> import rubrix as rb
        >>> record = rb.TextClassificationRecord(
        ...     inputs={"text": "my first rubrix example"},
        ...     prediction=[('spam', 0.8), ('ham', 0.2)]
        ... )
    """

    inputs: Union[str, List[str], Dict[str, Union[str, List[str]]]]

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

    @validator("inputs", pre=True)
    def input_as_dict(cls, inputs):
        """Preprocess record inputs and wraps as dictionary if needed"""
        if isinstance(inputs, dict):
            return inputs
        return dict(text=inputs)


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

    text: str
    tokens: List[str]

    prediction: Optional[
        List[Union[Tuple[str, int, int], Tuple[str, int, int, float]]]
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

    @validator("prediction")
    def add_default_score(
        cls,
        prediction: Optional[
            List[Union[Tuple[str, int, int], Tuple[str, int, int, float]]]
        ],
    ):
        """Adds the default score to the predictions if it is missing"""
        if prediction is None:
            return prediction
        return [
            (pred[0], pred[1], pred[2], 1.0) if len(pred) == 3 else pred
            for pred in prediction
        ]


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
