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

import pytest
from argilla_server.apis.v0.models.token_classification import (
    TokenClassificationAnnotation,
    TokenClassificationQuery,
    TokenClassificationRecord,
)
from argilla_server.commons.models import PredictionStatus
from argilla_server.daos.backend.search.query_builder import EsQueryBuilder
from argilla_server.services.tasks.token_classification.model import (
    EntitySpan,
    ServiceTokenClassificationRecord,
)

from tests.pydantic_v1 import ValidationError


def test_char_position():
    with pytest.raises(
        ValidationError,
        match="End character cannot be placed before the starting character,"
        " it must be at least one character after.",
    ):
        EntitySpan(start=1, end=1, label="label")

    text = "I am Maxi"
    ServiceTokenClassificationRecord(
        text=text,
        tokens=text.split(),
        prediction=TokenClassificationAnnotation(
            agent="test",
            entities=[
                EntitySpan(start=0, end=1, label="test"),
                EntitySpan(start=2, end=len(text), label="test"),
            ],
        ),
    )


def test_fix_substrings():
    text = "On one ones o no"
    ServiceTokenClassificationRecord(
        text=text,
        tokens=text.split(),
        prediction=TokenClassificationAnnotation(
            agent="test",
            entities=[
                EntitySpan(start=3, end=6, label="test"),
            ],
        ),
    )


def test_entities_with_spaces():
    text = "This is  a  great  space"
    ServiceTokenClassificationRecord(
        text=text,
        tokens=["This", "is", " ", "a", " ", "great", " ", "space"],
        prediction=TokenClassificationAnnotation(
            agent="test",
            entities=[
                EntitySpan(start=9, end=len(text), label="test"),
            ],
        ),
    )


def test_model_dict():
    text = "This is  a  great  space"
    tokens = ["This", "is", " ", "a", " ", "great", " ", "space"]
    record = TokenClassificationRecord(
        id="1",
        text=text,
        tokens=tokens,
        prediction=TokenClassificationAnnotation(agent="test", entities=[EntitySpan(start=9, end=24, label="test")]),
    )

    assert record.dict(exclude_none=True) == {
        "id": "1",
        "metrics": {},
        "prediction": {
            "agent": "test",
            "entities": [{"end": 24, "label": "test", "score": 1.0, "start": 9}],
        },
        "predictions": {
            "test": {
                "entities": [{"end": 24, "label": "test", "score": 1.0, "start": 9}],
            }
        },
        "status": "Default",
        "text": "This is  a  great  space",
        "tokens": ["This", "is", " ", "a", " ", "great", " ", "space"],
    }


def test_model_with_predictions():
    record = TokenClassificationRecord.parse_obj(
        {
            "id": 1,
            "metrics": {},
            "predictions": {
                "test": {
                    "entities": [{"end": 24, "label": "test", "score": 1.0, "start": 9}],
                }
            },
            "status": "Default",
            "text": "This is  a  great  space",
            "tokens": ["This", "is", " ", "a", " ", "great", " ", "space"],
        }
    )
    assert record.dict(exclude_none=True) == {
        "id": 1,
        "metrics": {},
        "prediction": {
            "agent": "test",
            "entities": [{"end": 24, "label": "test", "score": 1.0, "start": 9}],
        },
        "predictions": {
            "test": {
                "entities": [{"end": 24, "label": "test", "score": 1.0, "start": 9}],
            }
        },
        "status": "Default",
        "text": "This is  a  great  space",
        "tokens": ["This", "is", " ", "a", " ", "great", " ", "space"],
    }


def test_too_long_metadata():
    text = "On one ones o no"
    record = ServiceTokenClassificationRecord.parse_obj(
        {
            "text": text,
            "tokens": text.split(),
            "metadata": {"too_long": "a" * 1000},
        }
    )

    assert len(record.metadata["too_long"]) == 128


def test_entity_label_too_long():
    text = "On one ones o no"
    with pytest.raises(ValidationError, match="ensure this value has at most 128 character"):
        ServiceTokenClassificationRecord(
            text=text,
            tokens=text.split(),
            prediction=TokenClassificationAnnotation(
                agent="test",
                entities=[
                    EntitySpan(
                        start=9,
                        end=len(text),
                        label="a" * 1000,
                    ),
                ],
            ),
        )


def test_to_es_query():
    query = TokenClassificationQuery(ids=[1, 2, 3])
    assert EsQueryBuilder._to_es_query(query) == {"ids": {"values": query.ids}}


def test_misaligned_entity_mentions_with_spaces_left():
    assert ServiceTokenClassificationRecord(
        text="according to analysts.\n     Dart Group Corp was not",
        tokens=[
            "according",
            "to",
            "analysts",
            ".",
            "\n     ",
            "Dart",
            "Group",
            "Corp",
            "was",
            "not",
        ],
        annotation=TokenClassificationAnnotation(
            agent="heuristics",
            entities=[EntitySpan(start=22, end=43, label="COMPANY", score=1.0)],
            score=None,
        ),
    )


def test_misaligned_entity_mentions_with_spaces_right():
    assert ServiceTokenClassificationRecord(
        text="\nvs 9.91 billion\n    Note\n REUTER\n",
        tokens=["\n", "vs", "9.91", "billion", "\n    ", "Note", "\n ", "REUTER", "\n"],
        annotation=TokenClassificationAnnotation(
            agent="heuristics",
            entities=[EntitySpan(start=4, end=21, label="MONEY", score=1.0)],
            score=None,
        ),
    )


def test_custom_tokens_splitting():
    ServiceTokenClassificationRecord(
        text="ThisisMr.Bean, a character  playedby actor RowanAtkinson",
        tokens=[
            "This",
            "is",
            "Mr.",
            "Bean",
            "a",
            "character",
            "played",
            "by",
            "actor",
            "Rowan",
            "Atkinson",
        ],
        annotation=TokenClassificationAnnotation(
            agent="test",
            entities=[
                EntitySpan(start=9, end=13, label="PERSON"),
                EntitySpan(start=43, end=48, label="NAME"),
                EntitySpan(start=48, end=56, label="SURNAME"),
            ],
        ),
    )


def test_record_scores():
    record = ServiceTokenClassificationRecord(
        text="\nvs 9.91 billion\n    Note\n REUTER\n",
        tokens=["\n", "vs", "9.91", "billion", "\n    ", "Note", "\n ", "REUTER", "\n"],
        prediction=TokenClassificationAnnotation(
            agent="heuristics",
            entities=[
                EntitySpan(start=4, end=21, label="MONEY", score=0.8),
                EntitySpan(start=4, end=21, label="ORG", score=0.1),
                EntitySpan(start=4, end=21, label="PERSON", score=0.2),
            ],
        ),
    )
    assert record.scores == [0.8, 0.1, 0.2]


def test_annotated_without_entities():
    text = "The text that i wrote"
    record = ServiceTokenClassificationRecord(
        text=text,
        tokens=text.split(),
        prediction=TokenClassificationAnnotation(agent="pred.test", entities=[EntitySpan(start=0, end=3, label="DET")]),
        annotation=TokenClassificationAnnotation(agent="test", entities=[]),
    )

    assert record.annotated_by == [record.annotation.agent]
    assert record.predicted_by == [record.prediction.agent]
    assert record.predicted == PredictionStatus.KO


def test_adjust_spans():
    text = "A text with  some empty     spaces  that could    bring  not cleany   annotated spans"
    record = ServiceTokenClassificationRecord(
        text=text,
        tokens=text.split(),
        prediction=TokenClassificationAnnotation(
            agent="pred.test",
            entities=[
                EntitySpan(start=-3, end=2, label="DET"),
                EntitySpan(start=24, end=36, label="NAME"),
            ],
        ),
        annotation=TokenClassificationAnnotation(
            agent="test",
            entities=[
                EntitySpan(start=48, end=61, label="VERB"),
                EntitySpan(start=68, end=100, label="DET"),
            ],
        ),
    )

    assert record.prediction.entities == [
        EntitySpan(start=0, end=1, label="DET"),
        EntitySpan(start=28, end=34, label="NAME"),
    ]

    assert record.annotation.entities == [
        EntitySpan(start=50, end=60, label="VERB"),
        EntitySpan(start=70, end=85, label="DET"),
    ]


def test_whitespace_in_tokens():
    data = {
        "text": "every four (4)  ",
        "tokens": ["every", "four", "(", "4", ")", " "],
        "prediction": {"agent": "mock", "entities": [{"end": 16, "label": "mock", "start": 0}]},
    }

    record = ServiceTokenClassificationRecord.parse_obj(data)
    assert record.tokens == ["every", "four", "(", "4", ")", " "]


def test_predicted_ok_ko_computation():
    text = "A text with some empty spaces that could bring not cleanly annotated spans"
    record = ServiceTokenClassificationRecord(
        text=text,
        tokens=text.split(),
        prediction=TokenClassificationAnnotation(
            agent="pred.test",
            entities=[
                EntitySpan(
                    start=0,
                    end=6,
                    label="VERB",
                ),
                EntitySpan(
                    start=47,
                    end=68,
                    label="VERB",
                    score=0.5,
                ),
            ],
        ),
        annotation=TokenClassificationAnnotation(
            agent="test",
            entities=[
                EntitySpan(
                    start=0,
                    end=6,
                    label="VERB",
                ),
                EntitySpan(
                    start=47,
                    end=68,
                    label="VERB",
                ),
            ],
        ),
    )

    assert record.predicted == PredictionStatus.OK

    record.annotation.entities = record.annotation.entities[1:]
    assert record.predicted == PredictionStatus.KO
