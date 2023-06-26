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
from argilla import (
    LabelQuestion,
    MultiLabelQuestion,
    RatingQuestion,
    TextField,
)
from argilla.client.feedback.training.schemas import TrainingTaskMapping
from argilla.client.feedback.unification import (
    LabelQuestionUnification,
    MultiLabelQuestionUnification,
    RatingQuestionUnification,
)
from argilla.client.models import Framework
from datasets import Dataset, DatasetDict
from spacy.tokens import DocBin

rating_question_payload = {
    "name": "label",
    "description": "label",
    "required": True,
    "values": ["1", "2"],
}
label_question_payload = {
    "name": "label",
    "description": "label",
    "required": True,
    "labels": ["1", "2"],
}


@pytest.mark.parametrize(
    "framework, label, train_size, seed, expected",
    [
        (
            Framework("spacy"),
            RatingQuestionUnification(question=RatingQuestion(**rating_question_payload)),
            0.5,
            None,
            (DocBin, DocBin),
        ),
        (
            Framework("spacy"),
            LabelQuestionUnification(question=LabelQuestion(**label_question_payload)),
            0.5,
            None,
            (DocBin, DocBin),
        ),
        (
            Framework("spacy"),
            MultiLabelQuestionUnification(question=MultiLabelQuestion(**label_question_payload)),
            0.5,
            None,
            (DocBin, DocBin),
        ),
        (
            Framework("spacy"),
            RatingQuestionUnification(question=RatingQuestion(**rating_question_payload)),
            1,
            42,
            DocBin,
        ),
        (Framework("spacy"), LabelQuestionUnification(question=LabelQuestion(**label_question_payload)), 1, 42, DocBin),
        (
            Framework("spacy"),
            MultiLabelQuestionUnification(question=MultiLabelQuestion(**label_question_payload)),
            1,
            42,
            DocBin,
        ),
        (
            Framework("openai"),
            RatingQuestionUnification(question=RatingQuestion(**rating_question_payload)),
            0.5,
            None,
            (list, list),
        ),
        (
            Framework("openai"),
            LabelQuestionUnification(question=LabelQuestion(**label_question_payload)),
            0.5,
            None,
            (list, list),
        ),
        (
            Framework("openai"),
            MultiLabelQuestionUnification(question=MultiLabelQuestion(**label_question_payload)),
            0.5,
            None,
            (list, list),
        ),
        (
            Framework("openai"),
            RatingQuestionUnification(question=RatingQuestion(**rating_question_payload)),
            1,
            42,
            list,
        ),
        (Framework("openai"), LabelQuestionUnification(question=LabelQuestion(**label_question_payload)), 1, 42, list),
        (
            Framework("openai"),
            MultiLabelQuestionUnification(question=MultiLabelQuestion(**label_question_payload)),
            1,
            42,
            list,
        ),
        (
            Framework("transformers"),
            RatingQuestionUnification(question=RatingQuestion(**rating_question_payload)),
            0.5,
            None,
            DatasetDict,
        ),
        (
            Framework("transformers"),
            LabelQuestionUnification(question=LabelQuestion(**label_question_payload)),
            0.5,
            None,
            DatasetDict,
        ),
        (
            Framework("transformers"),
            MultiLabelQuestionUnification(question=MultiLabelQuestion(**label_question_payload)),
            0.5,
            None,
            DatasetDict,
        ),
        (
            Framework("transformers"),
            RatingQuestionUnification(question=RatingQuestion(**rating_question_payload)),
            1,
            42,
            Dataset,
        ),
        (
            Framework("transformers"),
            LabelQuestionUnification(question=LabelQuestion(**label_question_payload)),
            1,
            42,
            Dataset,
        ),
        (
            Framework("transformers"),
            MultiLabelQuestionUnification(question=MultiLabelQuestion(**label_question_payload)),
            1,
            42,
            Dataset,
        ),
        (
            Framework("spark-nlp"),
            RatingQuestionUnification(question=RatingQuestion(**rating_question_payload)),
            0.5,
            None,
            (pd.DataFrame, pd.DataFrame),
        ),
        (
            Framework("spark-nlp"),
            LabelQuestionUnification(question=LabelQuestion(**label_question_payload)),
            0.5,
            None,
            (pd.DataFrame, pd.DataFrame),
        ),
        (
            Framework("spark-nlp"),
            MultiLabelQuestionUnification(question=MultiLabelQuestion(**label_question_payload)),
            0.5,
            None,
            (pd.DataFrame, pd.DataFrame),
        ),
        (
            Framework("spark-nlp"),
            RatingQuestionUnification(question=RatingQuestion(**rating_question_payload)),
            1,
            42,
            pd.DataFrame,
        ),
        (
            Framework("spark-nlp"),
            LabelQuestionUnification(question=LabelQuestion(**label_question_payload)),
            1,
            42,
            pd.DataFrame,
        ),
        (
            Framework("spark-nlp"),
            MultiLabelQuestionUnification(question=MultiLabelQuestion(**label_question_payload)),
            1,
            42,
            pd.DataFrame,
        ),
    ],
)
def test_task_mapping_for_text_classification(framework, label, train_size, seed, expected):
    data = [{"text": "This is a text", "label": "1"}, {"text": "This is a text", "label": "2"}]
    field = TextField(name="text")
    task_mapping = TrainingTaskMapping.for_text_classification(text=field, label=label)
    if framework == Framework.SPACY:
        data = task_mapping._prepare_for_training_with_spacy(
            data=data, train_size=train_size, seed=seed, lang=spacy.blank("en")
        )
    elif framework == Framework.OPENAI:
        data = task_mapping._prepare_for_training_with_openai(data=data, train_size=train_size, seed=seed)
    elif framework == Framework.TRANSFORMERS:
        data = task_mapping._prepare_for_training_with_transformers(
            data=data, train_size=train_size, seed=seed, framework=Framework.TRANSFORMERS
        )
    elif framework == Framework.SPARK_NLP:
        data = task_mapping._prepare_for_training_with_spark_nlp(data=data, train_size=train_size, seed=seed)
    else:
        raise ValueError(f"Framework {framework} not supported")
    if isinstance(data, tuple):
        for d, e in zip(data, expected):
            assert isinstance(d, e)
    else:
        assert isinstance(data, expected)
