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
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, Field, root_validator, validator

from rubrix._constants import MAX_KEYWORD_LENGTH
from rubrix.server.apis.v0.models.commons.model import (
    BaseAnnotation,
    BaseRecord,
    BaseSearchResults,
    BaseSearchResultsAggregations,
    EsRecordDataFieldNames,
    PredictionStatus,
    ScoreRange,
    SortableField,
    TaskType,
)
from rubrix.server.apis.v0.models.datasets import DatasetDB, UpdateDatasetRequest
from rubrix.server.services.search.model import BaseSearchQuery
from rubrix.utils.span_utils import SpanUtils

PREDICTED_MENTIONS_ES_FIELD_NAME = "predicted_mentions"
MENTIONS_ES_FIELD_NAME = "mentions"


class EntitySpan(BaseModel):
    """
    The tokens span for a labeled text.

    Entity spans will be defined between from start to end - 1

    Attributes:
    -----------

    start: int
        character start position
    end: int
        character end position, must be higher than the starting character.
    label: str
        the label related to tokens that conforms the entity span
    score:
        A higher score means, the model/annotator is more confident about its predicted/annotated entity.
    """

    start: int
    end: int
    label: str = Field(min_length=1, max_length=MAX_KEYWORD_LENGTH)
    score: float = Field(default=1.0, ge=0.0, le=1.0)

    @validator("end")
    def check_span_offset(cls, end: int, values):
        """Validates span offset"""
        assert (
            end > values["start"]
        ), "End character cannot be placed before the starting character, it must be at least one character after."
        return end

    def __hash__(self):
        return hash(type(self)) + hash(self.__dict__.values())


class TokenClassificationAnnotation(BaseAnnotation):
    """Annotation class for the Token classification task.

    Attributes:
    -----------
    entities: List[EntitiesSpan]
        a list of detected entities spans in tokenized text, if any.
    score: float
        score related to annotated entities. The higher is score value, the
        more likely is that entities were properly annotated.
    """

    entities: List[EntitySpan] = Field(default_factory=list)
    score: Optional[float] = None


class CreationTokenClassificationRecord(BaseRecord[TokenClassificationAnnotation]):
    """
    Dataset record for token classification task

    Attributes:
    -----------

    tokens: List[str]
        The input tokens
    text: str
        Textual representation of token list

    """

    tokens: List[str] = Field(min_items=1)
    text: str = Field()
    _raw_text: Optional[str] = Field(alias="raw_text")
    _span_utils: SpanUtils

    @root_validator(pre=True)
    def accept_old_fashion_text_field(cls, values):
        text, raw_text = values.get("text"), values.get("raw_text")
        text = text or raw_text
        values["text"] = cls.check_text_content(text)

        return values

    def __init__(self, **data):
        super().__init__(**data)

        if self.annotation:
            self._validate_spans(self.annotation)
        if self.prediction:
            self._validate_spans(self.prediction)

    @root_validator()
    def _init_span_utils(cls, values):
        values["_span_utils"] = SpanUtils(values["text"], values["tokens"])
        return values

    @staticmethod
    def _validate_spans(
        span_utils: SpanUtils, annotation: TokenClassificationAnnotation
    ):
        """Validates the spans with respect to the tokens.

        If necessary, also performs an automatic correction of the spans.

        Args:
            span_utils: Helper class to perform the checks.
            annotation: Contains the spans to validate.

        Raises:
            ValidationError: If spans are not valid or misaligned.
        """
        spans = [(ent.label, ent.start, ent.end) for ent in annotation.entities]
        try:
            span_utils.validate(spans)
        except ValueError:
            corrected_spans = span_utils.correct(spans)
            span_utils.validate(corrected_spans)
            for ent, span in zip(annotation.entities, corrected_spans):
                ent.start, ent.end = span[1], span[2]

    @validator("text")
    def check_text_content(cls, text: str):
        assert text and text.strip(), "No text or empty text provided"
        return text

    def task(cls) -> TaskType:
        """The record task type"""
        return TaskType.token_classification

    @property
    def span_utils(self) -> SpanUtils:
        """Utility class for span operations."""
        return self._span_utils

    @property
    def predicted(self) -> Optional[PredictionStatus]:
        if self.annotation and self.prediction:
            return (
                PredictionStatus.OK
                if self.annotation.entities == self.prediction.entities
                else PredictionStatus.KO
            )
        return None

    @property
    def predicted_as(self) -> List[str]:
        return [ent.label for ent in self.predicted_entities()]

    @property
    def annotated_as(self) -> List[str]:
        return [ent.label for ent in self.annotated_entities()]

    @property
    def scores(self) -> List[float]:
        if not self.prediction:
            return []
        if self.prediction.score is not None:
            return [self.prediction.score]
        return [e.score for e in self.prediction.entities]

    def all_text(self) -> str:
        return self.text

    def predicted_mentions(self) -> List[Tuple[str, EntitySpan]]:
        return [
            (mention, entity)
            for mention, entity in self.__mentions_from_entities__(
                self.predicted_entities()
            ).items()
        ]

    def annotated_mentions(self) -> List[Tuple[str, EntitySpan]]:
        return [
            (mention, entity)
            for mention, entity in self.__mentions_from_entities__(
                self.annotated_entities()
            ).items()
        ]

    def annotated_entities(self) -> Set[EntitySpan]:
        """Shortcut for real annotated entities, if provided"""
        if self.annotation is None:
            return set()
        return set(self.annotation.entities)

    def predicted_entities(self) -> Set[EntitySpan]:
        """Predicted entities"""
        if self.prediction is None:
            return set()
        return set(self.prediction.entities)

    def __mentions_from_entities__(
        self, entities: Set[EntitySpan]
    ) -> Dict[str, EntitySpan]:
        return {
            mention: entity
            for entity in entities
            for mention in [self.text[entity.start : entity.end]]
        }

    class Config:
        allow_population_by_field_name = True
        underscore_attrs_are_private = True


class TokenClassificationRecordDB(CreationTokenClassificationRecord):
    """
    The main token classification task record

    Attributes:
    -----------

    last_updated: datetime
        Last record update (read only)
    predicted: Optional[PredictionStatus]
        The record prediction status. Optional
    """

    last_updated: datetime = None
    _predicted: Optional[PredictionStatus] = Field(alias="predicted")

    def extended_fields(self) -> Dict[str, Any]:

        return {
            **super().extended_fields(),
            # See ../service/service.py
            PREDICTED_MENTIONS_ES_FIELD_NAME: [
                {"mention": mention, "entity": entity.label, "score": entity.score}
                for mention, entity in self.predicted_mentions()
            ],
            MENTIONS_ES_FIELD_NAME: [
                {"mention": mention, "entity": entity.label}
                for mention, entity in self.annotated_mentions()
            ],
            EsRecordDataFieldNames.words: self.all_text(),
        }


class TokenClassificationRecord(TokenClassificationRecordDB):
    def extended_fields(self) -> Dict[str, Any]:
        return {
            "raw_text": self.text,  # Maintain results compatibility
        }


class TokenClassificationBulkData(UpdateDatasetRequest):
    """
    API bulk data for text classification

    Attributes:
    -----------

    records: List[TextClassificationRecord]
        The text classification record list

    """

    records: List[CreationTokenClassificationRecord]


class TokenClassificationQuery(BaseSearchQuery):
    """
    API Filters for text classification

    Attributes:
    -----------

    predicted_as: List[str]
        List of predicted terms
    annotated_as: List[str]
        List of annotated terms
    predicted: Optional[PredictionStatus]
        The task prediction status

    """

    predicted_as: List[str] = Field(default_factory=list)
    annotated_as: List[str] = Field(default_factory=list)
    score: Optional[ScoreRange] = Field(default=None)
    predicted: Optional[PredictionStatus] = Field(default=None, nullable=True)


class TokenClassificationSearchRequest(BaseModel):

    """
    API SearchRequest request

    Attributes:
    -----------

    query: TokenClassificationQuery
        The search query configuration
    sort:
        The sort by order in search results
    """

    query: TokenClassificationQuery = Field(default_factory=TokenClassificationQuery)
    sort: List[SortableField] = Field(default_factory=list)


class TokenClassificationAggregations(BaseSearchResultsAggregations):
    """
    Extends base aggregation with mentions

    Attributes:
    -----------
    mentions: Dict[str,Dict[str,int]]
        The annotated entity spans
    predicted_mentions: Dict[str,Dict[str,int]]
        The prediction entity spans
    """

    predicted_mentions: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    mentions: Dict[str, Dict[str, int]] = Field(default_factory=dict)


class TokenClassificationSearchResults(
    BaseSearchResults[TokenClassificationRecord, TokenClassificationAggregations]
):
    pass


class TokenClassificationDatasetDB(DatasetDB):
    task: TaskType = Field(default=TaskType.token_classification, const=True)
    pass
