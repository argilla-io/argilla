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
    """Data info for bulk results.

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


class DatasetSnapshot(BaseModel):
    """The dataset snapshot info.

    Args:
        id:
            Id of the snapshot.
        task:
            Task of the snapshot.
        creation_date:
            Creation date of the snapshot.
    """

    id: str
    task: str
    creation_date: datetime.datetime


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


def limit_metadata_values(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Checks metadata values length and apply value truncation for large values"""
    new_value = limit_value_length(metadata, max_length=MAX_KEYWORD_LENGTH)
    if new_value != metadata:
        warnings.warn(
            "Some metadata values exceed the max length. "
            f"Those values will be truncated by keeping only the last {MAX_KEYWORD_LENGTH} characters."
        )
    return new_value


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
            Name of the prediction agent.
        annotation_agent:
            Name of the annotation agent.
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
        return limit_metadata_values(metadata)

    def __init__(self, *args, **kwargs):
        """Custom init to handle dynamic defaults"""
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
        prediction
            A list of tuples containing the predictions for the record. The first entry of the tuple is the name of
            predicted entity, the second and third entry correspond to the start and stop character index of the entity.
        annotation:
            A list of tuples containing annotations (gold labels) for the record. The first entry of the tuple is the
            name of the entity, the second and third entry correspond to the start and stop char index of the entity.
        prediction_agent:
            Name of the prediction agent.
        annotation_agent:
            Name of the annotation agent.
        id:
            The id of the record. By default (None), we will generate a unique ID for you.
        metadata:
            Meta data for the record. Defaults to `{}`.
        status:
            The status of the record. Options: 'Default', 'Edited', 'Discarded', 'Validated'.
            If an annotation is provided, this defaults to 'Validated', otherwise 'Default'.
        event_timestamp:
            The timestamp of the record.
    """

    text: str
    tokens: List[str]

    prediction: Optional[List[Tuple[str, int, int]]] = None
    annotation: Optional[List[Tuple[str, int, int]]] = None
    prediction_agent: Optional[str] = None
    annotation_agent: Optional[str] = None

    id: Optional[Union[int, str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    status: Optional[str] = None
    event_timestamp: Optional[datetime.datetime] = None

    @validator("metadata", pre=True)
    def check_value_length(cls, metadata):
        return limit_metadata_values(metadata)

    def __init__(self, *args, **kwargs):
        """Custom init to handle dynamic defaults"""
        super().__init__(*args, **kwargs)
        self.status = self.status or (
            "Default" if self.annotation is None else "Validated"
        )


Record = Union[TextClassificationRecord, TokenClassificationRecord]
