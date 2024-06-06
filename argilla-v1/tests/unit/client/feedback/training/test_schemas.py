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

import pandas as pd
import pytest
import spacy
from argilla_v1 import (
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    TextField,
)
from argilla_v1.client.feedback.training.schemas.base import TrainingTask
from argilla_v1.client.feedback.unification import (
    LabelQuestionUnification,
    MultiLabelQuestionUnification,
    RankingQuestionUnification,
    RatingQuestionUnification,
)
from argilla_v1.client.models import Framework
from datasets import Dataset, DatasetDict
from spacy.tokens import DocBin


@pytest.mark.parametrize(
    "framework, label, train_size, seed, expected",
    [
        (
            Framework("spacy"),
            RatingQuestionUnification,
            0.5,
            None,
            (DocBin, DocBin),
        ),
        (
            Framework("spacy"),
            RankingQuestionUnification,
            0.5,
            None,
            (DocBin, DocBin),
        ),
        (
            Framework("spacy"),
            LabelQuestionUnification,
            0.5,
            None,
            (DocBin, DocBin),
        ),
        (
            Framework("spacy"),
            MultiLabelQuestionUnification,
            0.5,
            None,
            (DocBin, DocBin),
        ),
        (
            Framework("spacy"),
            RatingQuestionUnification,
            1,
            42,
            DocBin,
        ),
        (
            Framework("spacy"),
            RankingQuestionUnification,
            1,
            42,
            DocBin,
        ),
        (Framework("spacy"), LabelQuestionUnification, 1, 42, DocBin),
        (
            Framework("spacy"),
            MultiLabelQuestionUnification,
            1,
            42,
            DocBin,
        ),
        (
            Framework("spacy-transformers"),
            RatingQuestionUnification,
            0.5,
            None,
            (DocBin, DocBin),
        ),
        (
            Framework("spacy-transformers"),
            RankingQuestionUnification,
            0.5,
            None,
            (DocBin, DocBin),
        ),
        (
            Framework("spacy-transformers"),
            LabelQuestionUnification,
            0.5,
            None,
            (DocBin, DocBin),
        ),
        (
            Framework("spacy-transformers"),
            MultiLabelQuestionUnification,
            0.5,
            None,
            (DocBin, DocBin),
        ),
        (
            Framework("spacy-transformers"),
            RatingQuestionUnification,
            1,
            42,
            DocBin,
        ),
        (
            Framework("spacy-transformers"),
            RankingQuestionUnification,
            1,
            42,
            DocBin,
        ),
        (
            Framework("spacy-transformers"),
            LabelQuestionUnification,
            1,
            42,
            DocBin,
        ),
        (
            Framework("spacy-transformers"),
            MultiLabelQuestionUnification,
            1,
            42,
            DocBin,
        ),
        (
            Framework("openai"),
            RatingQuestionUnification,
            0.5,
            None,
            (list, list),
        ),
        (
            Framework("openai"),
            RankingQuestionUnification,
            0.5,
            None,
            (list, list),
        ),
        (
            Framework("openai"),
            LabelQuestionUnification,
            0.5,
            None,
            (list, list),
        ),
        (
            Framework("openai"),
            MultiLabelQuestionUnification,
            0.5,
            None,
            (list, list),
        ),
        (
            Framework("openai"),
            RatingQuestionUnification,
            1,
            42,
            list,
        ),
        (
            Framework("openai"),
            RankingQuestionUnification,
            1,
            42,
            list,
        ),
        (Framework("openai"), LabelQuestionUnification, 1, 42, list),
        (
            Framework("openai"),
            MultiLabelQuestionUnification,
            1,
            42,
            list,
        ),
        (
            Framework("transformers"),
            RatingQuestionUnification,
            0.5,
            None,
            DatasetDict,
        ),
        (
            Framework("transformers"),
            RankingQuestionUnification,
            0.5,
            None,
            DatasetDict,
        ),
        (
            Framework("transformers"),
            LabelQuestionUnification,
            0.5,
            None,
            DatasetDict,
        ),
        (
            Framework("transformers"),
            MultiLabelQuestionUnification,
            0.5,
            None,
            DatasetDict,
        ),
        (
            Framework("transformers"),
            RatingQuestionUnification,
            1,
            42,
            Dataset,
        ),
        (
            Framework("transformers"),
            RankingQuestionUnification,
            1,
            42,
            Dataset,
        ),
        (
            Framework("transformers"),
            LabelQuestionUnification,
            1,
            42,
            Dataset,
        ),
        (
            Framework("transformers"),
            MultiLabelQuestionUnification,
            1,
            42,
            Dataset,
        ),
        (
            Framework("spark-nlp"),
            RatingQuestionUnification,
            0.5,
            None,
            (pd.DataFrame, pd.DataFrame),
        ),
        (
            Framework("spark-nlp"),
            RankingQuestionUnification,
            0.5,
            None,
            (pd.DataFrame, pd.DataFrame),
        ),
        (
            Framework("spark-nlp"),
            LabelQuestionUnification,
            0.5,
            None,
            (pd.DataFrame, pd.DataFrame),
        ),
        (
            Framework("spark-nlp"),
            MultiLabelQuestionUnification,
            0.5,
            None,
            (pd.DataFrame, pd.DataFrame),
        ),
        (
            Framework("spark-nlp"),
            RatingQuestionUnification,
            1,
            42,
            pd.DataFrame,
        ),
        (
            Framework("spark-nlp"),
            RankingQuestionUnification,
            1,
            42,
            pd.DataFrame,
        ),
        (
            Framework("spark-nlp"),
            LabelQuestionUnification,
            1,
            42,
            pd.DataFrame,
        ),
        (
            Framework("spark-nlp"),
            MultiLabelQuestionUnification,
            1,
            42,
            pd.DataFrame,
        ),
    ],
)
def test_task_for_text_classification(
    framework,
    label,
    train_size,
    seed,
    expected,
    rating_question_payload,
    ranking_question_payload,
    label_question_payload,
):
    if label == RatingQuestionUnification:
        label = RatingQuestionUnification(question=RatingQuestion(**rating_question_payload))
    elif label == RankingQuestionUnification:
        label = RankingQuestionUnification(question=RankingQuestion(**ranking_question_payload))
    elif label == LabelQuestionUnification:
        label = LabelQuestionUnification(question=LabelQuestion(**label_question_payload))
    elif label == MultiLabelQuestionUnification:
        label = MultiLabelQuestionUnification(question=MultiLabelQuestion(**label_question_payload))
    data = [{"text": "This is a text", "label": "1"}, {"text": "This is a text", "label": "2"}]
    field = TextField(name="text")
    task = TrainingTask.for_text_classification(text=field, label=label)
    if framework == Framework.SPACY or framework == Framework.SPACY_TRANSFORMERS:
        data = task._prepare_for_training_with_spacy(
            data=data, train_size=train_size, seed=seed, lang=spacy.blank("en")
        )
    elif framework == Framework.OPENAI:
        data = task._prepare_for_training_with_openai(data=data, train_size=train_size, seed=seed)
    elif framework == Framework.TRANSFORMERS:
        data = task._prepare_for_training_with_transformers(
            data=data, train_size=train_size, seed=seed, framework=Framework.TRANSFORMERS
        )
    elif framework == Framework.SPARK_NLP:
        data = task._prepare_for_training_with_spark_nlp(data=data, train_size=train_size, seed=seed)
    else:
        raise ValueError(f"Framework {framework} not supported")
    if isinstance(data, tuple):
        for d, e in zip(data, expected):
            assert isinstance(d, e)
    else:
        assert isinstance(data, expected)


def test_training_task_repr(label_question_payload):
    field = TextField(name="text")
    label = LabelQuestion(**label_question_payload)
    task_mapping = TrainingTask.for_text_classification(text=field, label=label)
    assert isinstance(repr(task_mapping), str)
