import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field


class BulkResponse(BaseModel):
    """Data info for bulk results

    Attributes:
    -----------

    dataset:
        The dataset name
    processed:
        Number of records in bulk
    failed:
        Number of failed records
    """

    dataset: str
    processed: int
    failed: Optional[int] = 0


class DatasetSnapshot(BaseModel):
    """The dataset snapshot info"""

    id: str
    task: str
    creation_date: datetime.datetime


class TokenAttributions(BaseModel):
    """The token attributions explaining predicted labels

    Attributes:
    -----------

    token: str
        The input token
    attributions: Dict[str, float]
        A dictionary containing label class-attribution pairs
    """

    token: str
    attributions: Dict[str, float] = Field(default_factory=dict)


class TextClassificationRecord(BaseModel):
    """Record for text classification

    Attributes
    ----------
    inputs : `Dict[str, Any]`
        The inputs of the record
    prediction : `List[Tuple[str, float]]`, optional
        A list of tuples containing the predictions for the record. The first entry of the tuple is the predicted label,
        the second entry is its corresponding score. Default: None
    annotation : `Union[str, List[str]]`, optional
        A string or a list of strings (multilabel) corresponding to the annotation (gold label) for the record.
        Default: None
    prediction_agent : `str`, optional
        Name of the prediction agent. Default: None
    annotation_agent : `str`, optional
        Name of the annotation agent. Default: None
    multi_label : `bool`, optional
        Is the prediction/annotation for a multi label classification task? Default: False
    explanation : `Dict[str, List[TokenAttributions]]`, optional
        A dictionary containing the attributions of each token to the prediction. The keys map the input of the record
        (see `inputs`) to the `TokenAttributions`. Default: None
    id : `Union[int, str]`, optional
        The id of the record. By default (None), we will generate a unique ID for you.
    metadata : `Dict[str, Any]`, optional
        Meta data for the record. Default: None
    status : `str`, optional
        The status of the record. Options: 'Default', 'Edited', 'Discarded', 'Validated'.
        If an annotation is provided, this defaults to 'Validated', otherwise 'Default'.
    event_timestamp : `datatime.datetime`, optional
        The timestamp of the record. Default: None
    """

    inputs: Dict[str, Any]

    prediction: Optional[List[Tuple[str, float]]] = None
    annotation: Optional[Union[str, List[str]]] = None
    prediction_agent: Optional[str] = None
    annotation_agent: Optional[str] = None
    multi_label: Optional[bool] = False

    explanation: Optional[Dict[str, List[TokenAttributions]]] = None

    id: Optional[Union[int, str]] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    status: Optional[str] = None
    event_timestamp: Optional[datetime.datetime] = None

    def __init__(self, *args, **kwargs):
        """Custom init to handle dynamic defaults"""
        super().__init__(*args, **kwargs)
        self.status = self.status or (
            "Default" if self.annotation is None else "Validated"
        )


class TokenClassificationRecord(BaseModel):
    """Record for a token classification task

    Attributes
    ----------
    text : `str`
        The input of the record
    tokens : `List[str]`
        The tokenized input of the record. We use this to guide the annotation process and to cross-check the spans of
        your `prediction`/`annotation`.
    prediction : `List[Tuple[str, int, int]]`, optional
        A list of tuples containing the predictions for the record. The first entry of the tuple is the name of
        predicted entity, the second and third entry correspond to the start and stop character index of the entity.
        Default: None
    annotation : `List[Tuple[str, int, int]]`, optional
        A list of tuples containing annotations (gold labels) for the record. The first entry of the tuple is the name
        of the entity, the second and third entry correspond to the start and stop character index of the entity.
        Default: None
    prediction_agent : `str`, optional
        Name of the prediction agent. Default: None
    annotation_agent : `str`, optional
        Name of the annotation agent. Default: None
    id : `Union[int, str]`, optional
        The id of the record. By default (None), we will generate a unique ID for you.
    metadata : `Dict[str, Any]`, optional
        Meta data for the record. Default: None
    status : `str`, optional
        The status of the record. Options: 'Default', 'Edited', 'Discarded', 'Validated'.
        If an annotation is provided, this defaults to 'Validated', otherwise 'Default'.
    event_timestamp : `datatime.datetime`, optional
        The timestamp of the record. Default: None
    """

    text: str
    tokens: List[str]

    prediction: Optional[List[Tuple[str, int, int]]] = None
    annotation: Optional[List[Tuple[str, int, int]]] = None
    prediction_agent: Optional[str] = None
    annotation_agent: Optional[str] = None

    id: Optional[Union[int, str]] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    status: Optional[str] = None
    event_timestamp: Optional[datetime.datetime] = None

    def __init__(self, *args, **kwargs):
        """Custom init to handle dynamic defaults"""
        super().__init__(*args, **kwargs)
        self.status = self.status or (
            "Default" if self.annotation is None else "Validated"
        )


Record = Union[TextClassificationRecord, TokenClassificationRecord]
