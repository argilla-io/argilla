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

import logging
import warnings
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Union

import pandas as pd
from pydantic import BaseModel

from argilla._constants import OPENAI_SEPARATOR, OPENAI_WHITESPACE
from argilla.client.feedback.schemas import (
    FeedbackRecord,
    LabelQuestion,
    LabelQuestionStrategy,
    LabelQuestionUnification,
    MultiLabelQuestion,
    MultiLabelQuestionStrategy,
    RatingQuestion,
    RatingQuestionStrategy,
    RatingQuestionUnification,
    TextField,
)
from argilla.client.models import Framework
from argilla.utils.dependency import require_version, requires_version

_LOGGER = logging.getLogger(__name__)


class TrainingData(ABC):
    def _format_data(self, records):
        formatted_data = []
        explode_columns = set()
        for record in records:
            data = {}
            for pydantic_field in self:
                pydantic_field_name, pydantic_field_value = pydantic_field
                if isinstance(pydantic_field_value, (TextField,)):
                    data[pydantic_field_name] = record.fields[pydantic_field_value.name]
                else:
                    data[pydantic_field_name] = [
                        resp.value for resp in record.unified_responses[pydantic_field_value.question.name]
                    ]
                    explode_columns.add(pydantic_field_name)
            formatted_data.append(data)
        df = pd.DataFrame(formatted_data)
        df = df.explode(list(explode_columns))
        df = df.drop_duplicates()
        return df.to_dict(orient="records")

    @abstractmethod
    def _train_test_split(self, data: List[dict], train_size: float, seed: int) -> Tuple[List[dict], List[dict]]:
        """Overwritten by subclasses"""

    @abstractmethod
    def _prepare_for_training_with_transformers(
        self, data: List[dict], train_size, seed: int
    ) -> Union["datasets.Dataset", "datasets.DatasetDict"]:
        """Overwritten by subclasses"""

    @abstractmethod
    def _prepare_for_training_with_spacy(
        self, data: List[dict], train_size, seed: int, lang: str
    ) -> Union["spacy.token.DocBin", Tuple["spacy.token.DocBin", "spacy.token.DocBin"]]:
        """Overwritten by subclasses"""

    @abstractmethod
    def _prepare_for_training_with_spark_nlp(
        self, data: List[dict], train_size, seed: int
    ) -> Union["pd.DataFrame", Tuple["pd.DataFrame", "pd.DataFrame"]]:
        """Overwritten by subclasses"""

    @abstractmethod
    def _prepare_for_training_with_openai(
        self, data: List[dict], train_size, seed: int
    ) -> Union[List[dict], Tuple[List[dict], List[dict]]]:
        """Overwritten by subclasses"""


class TrainingDataForTextClassification(BaseModel, TrainingData):
    """Training data for text classification

    Args:
        text: TextField
        label: Union[RatingUnification, LabelUnification, MultiLabelUnification]

    Examples:
        >>> from argilla import LabelQuestion, TrainingDataForTextClassification
        >>> dataset = rg.FeedbackDataset.from_argilla(argilla_id="...")
        >>> label = RatingQuestionUnification(question=dataset.questions[0], strategy="mean")
        >>> training_data = TrainingDataForTextClassification(
        ...     text=dataset.fields[0],
        ...     label=label
        ... )
        >>> dataset.prepare_training_data(training_data=training_data)

    """

    text: TextField
    label: Union[RatingQuestionUnification, LabelQuestionUnification]

    @property
    def __multi_label__(self):
        return isinstance(self.label.question, MultiLabelQuestion)

    @property
    def __all_labels__(self):
        return self.label.question.__all_labels__

    @property
    def __label2id__(self):
        return self.label.question.__label2id__

    @property
    def __id2label__(self):
        return self.label.question.__id2label__

    def unify_responses(self, responses: List[FeedbackRecord]):
        self.label.strategy.unify_responses(responses=responses, field=self.label.question)

    @requires_version("scikit-learn")
    def _train_test_split(self, data: List[dict], train_size: float, seed: int) -> Tuple[List[dict], List[dict]]:
        from sklearn.model_selection import train_test_split

        # TODO: Stratify by label
        return train_test_split(
            data,
            train_size=train_size,
            shuffle=True,
            random_state=seed,
        )

    @requires_version("datasets>1.17.0")
    def _prepare_for_training_with_transformers(
        self, data: List[dict], train_size: float, seed: int
    ) -> Union["datasets.Dataset", "datasets.DatasetDict"]:
        import datasets

        multi_label = isinstance(self.label.question, MultiLabelQuestion)

        datasets_dict = {"text": [], "label": []}
        for entry in data:
            datasets_dict["text"].append(entry["text"])
            datasets_dict["label"].append(entry["label"])

        all_labels = self.label.question.__all_labels__
        class_label = datasets.ClassLabel(names=all_labels)
        feature_dict = {
            # "id": datasets.Value("string"),
            "text": datasets.Value("string"),
            "label": [class_label] if multi_label else class_label,
        }

        ds = datasets.Dataset.from_dict(datasets_dict, features=datasets.Features(feature_dict))

        if multi_label:
            require_version("scikit-learn")
            from sklearn.preprocessing import MultiLabelBinarizer

            labels = [rec["label"] for rec in ds]
            mlb = MultiLabelBinarizer()
            binarized_labels = mlb.fit_transform(labels)
            feature_dict["binarized_label"] = feature_dict["label"]
            ds = datasets.Dataset.from_dict(
                {
                    # "id": ds["id"],
                    "text": ds["text"],
                    "label": labels,
                    "binarized_label": binarized_labels,
                },
                features=datasets.Features(feature_dict),
            )
        if train_size != 1:
            ds = ds.train_test_split(train_size=train_size, test_size=1 - train_size, seed=seed)

        return ds

    @requires_version("spacy")
    def _prepare_for_training_with_spacy(
        self, data: List[dict], train_size: float, seed: int, lang: str
    ) -> Union["spacy.token.DocBin", Tuple["spacy.token.DocBin", "spacy.token.DocBin"]]:
        from spacy.tokens import DocBin

        all_labels = self.label.question.__all_labels__

        def _prepare(data):
            db = DocBin(store_user_data=True)
            # Creating the DocBin object as in https://spacy.io/usage/training#training-data
            for entry in data:
                doc = lang.make_doc(entry["text"])
                # doc.user_data["id"] = record.id

                cats = dict.fromkeys(all_labels, 0)
                if isinstance(entry["label"], list):
                    for label in entry["label"]:
                        cats[label] = 1
                else:
                    cats[entry["label"]] = 1

                doc.cats = cats
                db.add(doc)
            return db

        isinstance(self.label.question, MultiLabelQuestion)
        if train_size != 1:
            train_data, test_data = self._train_test_split(data, train_size, seed)
            return _prepare(train_data), _prepare(test_data)
        else:
            return _prepare(data)

    def _prepare_for_training_with_spark_nlp(
        self, data: List[dict], train_size: float, seed: int
    ) -> Union["pd.DataFrame", Tuple["pd.DataFrame", "pd.DataFrame"]]:
        def _prepare(data):
            df = pd.DataFrame(data)
            if multi_label:
                df.rename(columns={"label": "labels"}, inplace=True)
            return df

        multi_label = isinstance(self.label.question, MultiLabelQuestion)
        if train_size != 1:
            train_data, test_data = self._train_test_split(data, train_size, seed)
            return _prepare(train_data), _prepare(test_data)
        else:
            return _prepare(data)

    def _prepare_for_training_with_openai(
        self, data: List[dict], train_size: float, seed: int
    ) -> Union[List[dict], Tuple[List[dict], List[dict]]]:
        """Prepares the dataset for training using the "openai" framework.

        Args:
            **kwargs: Specific to the task of the dataset.

        Returns:
            A pd.DataFrame.
        """
        separator = OPENAI_SEPARATOR
        whitespace = OPENAI_WHITESPACE
        label2id = self.label.question.__label2id__

        if len(data) * train_size <= len(label2id) * 100:
            _LOGGER.warning("OpenAI recommends at least 100 examples per class for training a classification model.")

        def _prepare(data):
            jsonl = []
            for entry in data:
                prompt = entry["text"]
                prompt += separator  # needed for better performance

                if multi_label:
                    completion = " ".join([str(label2id[annotation]) for annotation in entry["label"]])
                else:
                    completion = str(label2id[entry["label"]])

                jsonl.append(
                    {
                        # "id": rec.id,
                        "prompt": prompt,
                        "completion": whitespace + completion,
                    }
                )

            return jsonl

        multi_label = isinstance(self.label.question, MultiLabelQuestion)
        if train_size != 1:
            train_data, test_data = self._train_test_split(data, train_size, seed)
            return _prepare(train_data), _prepare(test_data)
        else:
            return _prepare(data)


def validate_train_test_split(train_size, test_size):
    if train_size is None:
        train_size = 1
    if test_size is None:
        test_size = 1 - train_size

    # check if all numbers are larger than 0
    if not [abs(train_size), abs(test_size)] == [train_size, test_size]:
        raise ValueError("`train_size` and `test_size` must be larger than 0.")
    # check if train sizes sum up to 1
    if not (train_size + test_size) == 1:
        raise ValueError("`train_size` and `test_size` must sum to 1.")

    if test_size == 0:
        test_size = None

    return train_size, test_size


class FeedbackDatasetTrainingMixin:
    records: List[FeedbackRecord]

    @abstractmethod
    def unify_responses(
        self,
        question: Union[str, LabelQuestion, MultiLabelQuestion, RatingQuestion],
        strategy: Union[str, LabelQuestionStrategy, MultiLabelQuestionStrategy, RatingQuestionStrategy],
    ):
        """Overwritten by subclasses"""

    @abstractmethod
    def stratify_unified_responses(self, *args, **kwargs):
        pass

    def prepare_for_training(
        self,
        framework: Union[Framework, str],
        training_data: TrainingDataForTextClassification,
        train_size: Optional[float] = 1,
        test_size: Optional[float] = None,
        seed: Optional[int] = None,
        fetch_records: bool = True,
        lang: Optional[str] = None,
    ):
        if isinstance(framework, str):
            framework = Framework(framework)

        # validate train and test sizes
        train_size, _ = validate_train_test_split(train_size, test_size)

        if fetch_records:
            self.fetch_records()

        if isinstance(training_data, TrainingDataForTextClassification):
            self.unify_responses(question=training_data.label.question, strategy=training_data.label.strategy)
        else:
            raise ValueError(f"Training data {type(training_data)} is not supported yet")

        data = training_data._format_data(self.records)
        if framework in [
            Framework.TRANSFORMERS,
            Framework.SETFIT,
            Framework.SPAN_MARKER,
            Framework.PEFT,
            Framework.AUTOTRAIN,
        ]:
            return training_data._prepare_for_training_with_transformers(data=data, train_size=train_size, seed=seed)
        elif framework is Framework.SPACY:
            require_version("spacy")
            import spacy

            if lang is None:
                warnings.warn("spaCy `lang` is not provided. Using `en`(English) as default language.")
                lang = spacy.blank("en")
            elif lang.isinstance(str):
                if len(lang) == 2:
                    lang = spacy.blank(lang)
                else:
                    lang = spacy.load(lang)
            return training_data._prepare_for_training_with_spacy(
                data=data, train_size=train_size, seed=seed, lang=lang
            )
        elif framework is Framework.SPARK_NLP:
            return training_data._prepare_for_training_with_spark_nlp(data=data, train_size=train_size, seed=seed)
        elif framework is Framework.OPENAI:
            return training_data._prepare_for_training_with_openai(data=data, train_size=train_size, seed=seed)
        else:
            raise NotImplementedError(
                f"Framework {framework} is not supported. Choose from: {[e.value for e in Framework]}"
            )
