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
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from pydantic import BaseModel, Field, root_validator, validator
from rubrix.server.datasets.model import UpdateDatasetRequest
from rubrix.server.tasks.commons import (
    BaseAnnotation,
    BaseRecord,
    BaseSearchResults,
    BaseSearchResultsAggregations,
    PredictionStatus,
    ScoreRange,
    SortableField,
    TaskStatus,
    TaskType,
)
from rubrix._constants import MAX_KEYWORD_LENGTH

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

    tokens: List[str]
    text: str = Field(alias="raw_text")

    @root_validator
    def data_validation(cls, values):
        prediction = values.get("prediction")
        annotation = values.get("annotation")
        text = values["text"]
        tokens = values["tokens"]

        cls.check_annotation(prediction, text, tokens)
        cls.check_annotation(annotation, text, tokens)

        return values

    @staticmethod
    def check_annotation(
        annotation: Optional[TokenClassificationAnnotation],
        text: str,
        tokens: List[str],
    ):
        """Validates entities in terms of offset spans"""
        if annotation:
            tokens = [t for t in tokens if t.strip()]  # clean empty tokens (if any)
            for entity in annotation.entities:
                mention = text[entity.start : entity.end]
                assert len(mention) > 0, f"Empty offset defined for entity {entity}"

                idx = 0
                while mention and idx < len(tokens):
                    current_token = tokens[idx]
                    current_mention = mention
                    jdx = idx
                    while (
                        current_mention.startswith(current_token)
                        and current_mention
                        and jdx <= len(tokens)
                    ):
                        current_mention = current_mention[len(current_token) :]
                        current_mention = current_mention.lstrip()
                        jdx += 1
                        if jdx < len(tokens):
                            current_token = tokens[jdx]

                    if not current_mention:
                        mention = current_mention
                    idx += 1

                assert (
                    not mention
                ), f"Defined offset [{text[entity.start: entity.end]}] is a misaligned entity mention"

    def task(cls) -> TaskType:
        """The record task type"""
        return TaskType.token_classification

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
        return [ent.label for ent in self._predicted_entities()]

    @property
    def annotated_as(self) -> List[str]:
        return [ent.label for ent in self._entities()]

    @property
    def scores(self) -> List[float]:
        if not self.prediction:
            return []
        return [self.prediction.score]

    @property
    def words(self) -> str:
        return self.text

    def extended_fields(self) -> Dict[str, Any]:
        return {
            # See ../service/service.py
            PREDICTED_MENTIONS_ES_FIELD_NAME: [
                {"mention": mention, "entity": entity.label, "score": entity.score}
                for mention, entity in self._predicted_mentions()
            ],
            MENTIONS_ES_FIELD_NAME: [
                {"mention": mention, "entity": entity.label}
                for mention, entity in self._mentions()
            ],
        }

    def _predicted_mentions(self) -> List[Tuple[str, EntitySpan]]:
        return [
            (mention, entity)
            for mention, entity in self.__mentions_from_entities__(
                self._predicted_entities()
            ).items()
        ]

    def _mentions(self) -> List[Tuple[str, EntitySpan]]:
        return [
            (mention, entity)
            for mention, entity in self.__mentions_from_entities__(
                self._entities()
            ).items()
        ]

    def _entities(self) -> Set[EntitySpan]:
        """Shortcut for real annotated entities, if provided"""
        if self.annotation is None:
            return set()
        return set(self.annotation.entities)

    def _predicted_entities(self) -> Set[EntitySpan]:
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


class TokenClassificationRecord(CreationTokenClassificationRecord):
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


class TokenClassificationBulkData(UpdateDatasetRequest):
    """
    API bulk data for text classification

    Attributes:
    -----------

    records: List[TextClassificationRecord]
        The text classification record list

    """

    records: List[CreationTokenClassificationRecord]


class TokenClassificationQuery(BaseModel):
    """
    API Filters for text classification

    Attributes:
    -----------
    ids: Optional[List[Union[str, int]]]
        Record ids list

    query_text: str
        Text query over inputs
    metadata: Optional[Dict[str, Union[str, List[str]]]]
        Text query over metadata fields. Default=None

    predicted_as: List[str]
        List of predicted terms
    annotated_as: List[str]
        List of annotated terms
    annotated_by: List[str]
        List of annotation agents
    predicted_by: List[str]
        List of predicted agents
    status: List[TaskStatus]
        List of task status
    predicted: Optional[PredictionStatus]
        The task prediction status

    """

    ids: Optional[List[Union[str, int]]]

    query_text: str = Field(default=None)
    metadata: Optional[Dict[str, Union[str, List[str]]]] = None

    predicted_as: List[str] = Field(default_factory=list)
    annotated_as: List[str] = Field(default_factory=list)
    annotated_by: List[str] = Field(default_factory=list)
    predicted_by: List[str] = Field(default_factory=list)
    score: Optional[ScoreRange] = Field(default=None)
    status: List[TaskStatus] = Field(default_factory=list)
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
