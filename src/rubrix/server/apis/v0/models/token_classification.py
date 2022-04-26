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
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, Field, root_validator, validator

from rubrix._constants import MAX_KEYWORD_LENGTH
from rubrix.server.apis.v0.models.commons.model import (
    BaseAnnotation,
    BaseRecord,
    BaseSearchResults,
    BaseSearchResultsAggregations,
    PredictionStatus,
    ScoreRange,
    SortableField,
    TaskType,
)
from rubrix.server.apis.v0.models.datasets import DatasetDB, UpdateDatasetRequest
from rubrix.server.services.search.model import BaseSearchQuery

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

    __chars2tokens__: Dict[int, int] = None
    __tokens2chars__: Dict[int, Tuple[int, int]] = None

    @root_validator(pre=True)
    def accept_old_fashion_text_field(cls, values):
        text, raw_text = values.get("text"), values.get("raw_text")
        text = text or raw_text
        values["text"] = cls.check_text_content(text)

        return values

    def __init__(self, **data):
        super().__init__(**data)

        self.__chars2tokens__, self.__tokens2chars__ = self.__build_indices_map__()

        self.check_annotation(self.prediction)
        self.check_annotation(self.annotation)

    def char_id2token_id(self, char_idx: int) -> Optional[int]:
        return self.__chars2tokens__.get(char_idx)

    def token_span(self, token_idx: int) -> Tuple[int, int]:
        if token_idx not in self.__tokens2chars__:
            raise IndexError(f"Token id {token_idx} out of bounds")
        return self.__tokens2chars__[token_idx]

    @validator("text")
    def check_text_content(cls, text: str):
        assert text and text.strip(), "No text or empty text provided"
        return text

    def __build_indices_map__(
        self,
    ) -> Tuple[Dict[int, int], Dict[int, Tuple[int, int]]]:
        """
        Build the indices mapping between text characters and tokens where belongs to,
        and vice versa.

        chars2tokens index contains is the token idx where i char is contained (if any).

        Out-of-token characters won't be included in this map,
        so access should be using ``chars2tokens_map.get(i)``
        instead of ``chars2tokens_map[i]``.

        """

        def chars2tokens_index():
            chars_map = {}
            current_token = 0
            current_token_char_start = 0
            for idx, char in enumerate(self.text):
                relative_idx = idx - current_token_char_start
                if (
                    relative_idx < len(self.tokens[current_token])
                    and char == self.tokens[current_token][relative_idx]
                ):
                    chars_map[idx] = current_token
                elif (
                    current_token + 1 < len(self.tokens)
                    and relative_idx >= len(self.tokens[current_token])
                    and char == self.tokens[current_token + 1][0]
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

        chars2tokens_idx = chars2tokens_index()
        return chars2tokens_idx, tokens2chars_index(chars2tokens_idx)

    def check_annotation(
        self,
        annotation: Optional[TokenClassificationAnnotation],
    ):
        """Validates entities in terms of offset spans"""
        if annotation:
            for entity in annotation.entities:
                mention = self.text[entity.start : entity.end]
                assert len(mention) > 0, f"Empty offset defined for entity {entity}"

                token_start = self.char_id2token_id(entity.start)
                token_end = self.char_id2token_id(entity.end - 1)

                assert not (
                    token_start is None or token_end is None
                ), f"Provided entity span {self.text[entity.start: entity.end]} is not aligned with provided tokens."
                "Some entity chars could be reference characters out of tokens"

                span_start, _ = self.token_span(token_start)
                _, span_end = self.token_span(token_end)

                assert (
                    self.text[span_start : span_end + 1] == mention
                ), f"Defined offset [{self.text[entity.start: entity.end]}] is a misaligned entity mention"

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

    def predicted_iob_tags(self) -> Optional[List[str]]:
        if self.prediction is None:
            return None
        return self.spans2iob(self.prediction.entities)

    def annotated_iob_tags(self) -> Optional[List[str]]:
        if self.annotation is None:
            return None
        return self.spans2iob(self.annotation.entities)

    def spans2iob(self, spans: List[EntitySpan]) -> Optional[List[str]]:
        if spans is None:
            return None
        tags = ["O"] * len(self.tokens)
        for entity in spans:
            token_start = self.char_id2token_id(entity.start)
            token_end = self.char_id2token_id(entity.end - 1)
            tags[token_start] = f"B-{entity.label}"
            for idx in range(token_start + 1, token_end + 1):
                tags[idx] = f"I-{entity.label}"

        return tags

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
            "words": self.all_text(),
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
