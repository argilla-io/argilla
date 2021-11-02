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

from pydantic import BaseModel, Field, validator
from rubrix.server.commons.helpers import limit_value_length
from rubrix._constants import MAX_KEYWORD_LENGTH


class BulkResponse(BaseModel):
    """Summary response when logging records to the Rubrix server.

    Args:
        dataset:
            The dataset name.
        processed:
            Number of records in bulk.
        failed:
            Number of failed records.
    """

    dataset: str
    processed: int
    failed: Optional[int] = 0


class TokenAttributions(BaseModel):
    """Attribution of the token to the predicted label.

    In the Rubrix app this is only supported for ``TextClassificationRecord`` and the ``multi_label=False`` case.

    Args:
        token:
            The input token.
        attributions:
            A dictionary containing label-attribution pairs.
    """

    token: str
    attributions: Dict[str, float] = Field(default_factory=dict)


class TextClassificationRecord(BaseModel):
    """Record for text classification

    Args:
        inputs:
            The inputs of the record
        prediction:
            A list of tuples containing the predictions for the record.
            The first entry of the tuple is the predicted label, the second entry is its corresponding score.
        annotation:
            A string or a list of strings (multilabel) corresponding to the annotation (gold label) for the record.
        prediction_agent:
            Name of the prediction agent. By default, this is set to the hostname of your machine.
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

    Examples:
        >>> import rubrix as rb
        >>> record = rb.TextClassificationRecord(
        ...     inputs={"text": "my first rubrix example"},
        ...     prediction=[('spam', 0.8), ('ham', 0.2)]
        ... )
    """

    inputs: Union[str, List[str], Dict[str, Union[str, List[str]]]]

    prediction: Optional[List[Tuple[str, float]]] = None
    annotation: Optional[Union[str, List[str]]] = None
    prediction_agent: Optional[str] = None
    annotation_agent: Optional[str] = None
    multi_label: bool = False

    explanation: Optional[Dict[str, List[TokenAttributions]]] = None

    id: Optional[Union[int, str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    status: Optional[str] = None
    event_timestamp: Optional[datetime.datetime] = None

    @validator("inputs", pre=True)
    def input_as_dict(cls, inputs):
        """Preprocess record inputs and wraps as dictionary if needed"""
        if isinstance(inputs, dict):
            return inputs
        return dict(text=inputs)

    @validator("metadata", pre=True)
    def check_value_length(cls, metadata):
        return _limit_metadata_values(metadata)

    def __init__(self, *args, **kwargs):
        """Custom init to handle dynamic defaults"""
        # noinspection PyArgumentList
        super().__init__(*args, **kwargs)
        self.status = self.status or (
            "Default" if self.annotation is None else "Validated"
        )


class TokenClassificationRecord(BaseModel):
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
            EXPERIMENTAL: The fourth entry is optional and corresponds to the score of the entity.
        annotation:
            A list of tuples containing annotations (gold labels) for the record. The first entry of the tuple is the
            name of the entity, the second and third entry correspond to the start and stop char index of the entity.
        prediction_agent:
            Name of the prediction agent. By default, this is set to the hostname of your machine.
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
    annotation: Optional[List[Tuple[str, int, int]]] = None
    prediction_agent: Optional[str] = None
    annotation_agent: Optional[str] = None

    id: Optional[Union[int, str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    status: Optional[str] = None
    event_timestamp: Optional[datetime.datetime] = None

    @validator("metadata", pre=True)
    def check_value_length(cls, metadata):
        return _limit_metadata_values(metadata)

    def __init__(self, *args, **kwargs):
        """Custom init to handle dynamic defaults"""
        super().__init__(*args, **kwargs)
        self.status = self.status or (
            "Default" if self.annotation is None else "Validated"
        )


class Text2TextRecord(BaseModel):
    """Record for a text to text task

    Args:
        text:
            The input of the record
        prediction:
            A list of strings or tuples containing predictions for the input text.
            If tuples, the first entry is the predicted text, the second entry is its corresponding score.
        annotation:
            A string representing the expected output text for the given input text.
        prediction_agent:
            Name of the prediction agent. By default, this is set to the hostname of your machine.
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
    
    Examples:
        >>> import rubrix as rb
        >>> record = rb.Text2TextRecord(
        ...     text="My name is Sarah and I love my dog.",
        ...     prediction=["Je m'appelle Sarah et j'aime mon chien."]
        ... )    
    """

    text: str

    prediction: Optional[List[Union[str, Tuple[str, float]]]] = None
    annotation: Optional[str] = None
    prediction_agent: Optional[str] = None
    annotation_agent: Optional[str] = None

    id: Optional[Union[int, str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    status: Optional[str] = None
    event_timestamp: Optional[datetime.datetime] = None

    @validator("prediction")
    def prediction_as_tuples(
        cls, prediction: Optional[List[Union[str, Tuple[str, float]]]]
    ):
        """Preprocess the predictions and wraps them in a tuple if needed"""
        if prediction is None:
            return prediction
        if all([isinstance(pred, tuple) for pred in prediction]):
            return prediction
        return [(text, 1.0) for text in prediction]

    @validator("metadata", pre=True)
    def check_value_length(cls, metadata):
        return _limit_metadata_values(metadata)

    def __init__(self, *args, **kwargs):
        """Custom init to handle dynamic defaults"""
        super().__init__(*args, **kwargs)
        self.status = self.status or (
            "Default" if self.annotation is None else "Validated"
        )


def _limit_metadata_values(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Checks metadata values length and apply value truncation for large values"""
    new_value = limit_value_length(metadata, max_length=MAX_KEYWORD_LENGTH)
    if new_value != metadata:
        warnings.warn(
            "Some metadata values exceed the max length. "
            f"Those values will be truncated by keeping only the last {MAX_KEYWORD_LENGTH} characters."
        )
    return new_value


Record = Union[TextClassificationRecord, TokenClassificationRecord, Text2TextRecord]
