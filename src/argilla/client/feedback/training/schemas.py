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
from abc import ABC, abstractmethod
from typing import List, Tuple, Union

import pandas as pd
from pydantic import BaseModel

from argilla._constants import OPENAI_SEPARATOR, OPENAI_WHITESPACE
from argilla.client.feedback.schemas import (
    FeedbackRecord,
    LabelQuestion,
    MultiLabelQuestion,
    RatingQuestion,
    TextField,
)
from argilla.client.feedback.unification import (
    LabelQuestionUnification,
    MultiLabelQuestionUnification,
    RatingQuestionUnification,
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
                    if pydantic_field_value.question.name not in record._unified_responses:
                        continue
                    else:
                        data[pydantic_field_name] = [
                            resp.value for resp in record._unified_responses[pydantic_field_value.question.name]
                        ]
                    explode_columns.add(pydantic_field_name)
            formatted_data.append(data)
        df = pd.DataFrame(formatted_data)
        df = df.explode(list(explode_columns))
        df = df.drop_duplicates()
        df = df.dropna(how="any")
        return df.to_dict(orient="records")

    @property
    def supported_frameworks(self):
        return []

    def test_framework_support(self, framework: Union[str, Framework]):
        if isinstance(framework, str):
            framework = Framework(framework)
        if framework not in self.supported_frameworks:
            raise NotImplementedError(f"Framework {framework} is not supported for this {self.__class__}.")

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


class TrainingTaskMapping:
    @classmethod
    def for_text_classification(
        cls,
        text: TextField,
        label: Union[
            RatingQuestion,
            LabelQuestion,
            MultiLabelQuestion,
            RatingQuestionUnification,
            LabelQuestionUnification,
            MultiLabelQuestionUnification,
        ],
        label_strategy: str = None,
    ) -> "TrainingTaskMappingForTextClassification":
        """
        _summary_

        Args:
            text (TextField): The TextField to use for training.
            label (Union[RatingQuestion, LabelQuestion, MultiLabelQuestion, RatingQuestionUnification, LabelQuestionUnification, MultiLabelQuestionUnification]): _description_
            label_strategy (str, optional): A strategy to unify responses. Defaults to None. This means it will initialize the default strategy for the label type.

        Raises:
            ValueError: if label is not a valid type with the question type.
            ValueError: if label_strategy is defined and label is alraedy a Unification class.

        Returns:
            TrainingTaskMappingForTextClassification: _description_

        Examples:
            >>> from argilla import LabelQuestion, TrainingTaskMapping
            >>> dataset = rg.FeedbackDataset.from_argilla(argilla_id="...")
            >>> training_data = TrainingTaskMapping.for_text_classification(
            ...     text=dataset.fields[0],
            ...     label=dataset.questions[0]
            ... )
            >>> dataset.prepare_training_data(training_data=training_data)

        """
        if isinstance(label, (LabelQuestionUnification, MultiLabelQuestionUnification, RatingQuestionUnification)):
            if label_strategy is not None:
                raise ValueError("label_strategy is already defined via Unification class.")
        else:
            unification_kwargs = {"question": label}
            if label_strategy is not None:
                unification_kwargs["strategy"] = label_strategy
            else:
                _LOGGER.info(f"No label strategy defined. Using default strategy for {type(label)}.")
            if isinstance(label, RatingQuestion):
                label = RatingQuestionUnification(**unification_kwargs)
            elif isinstance(label, MultiLabelQuestion):
                label = MultiLabelQuestionUnification(**unification_kwargs)
            elif isinstance(label, LabelQuestion):
                label = LabelQuestionUnification(**unification_kwargs)
            else:
                raise ValueError(f"Label type {type(label)} is not supported.")
        return TrainingTaskMappingForTextClassification(
            text=text,
            label=label,
            label_strategy=label_strategy,
        )


class TrainingTaskMappingForTextClassification(BaseModel, TrainingData):
    """Training data for text classification

    Args:
        text: TextField
        label: Union[RatingUnification, LabelUnification, MultiLabelUnification]

    Examples:
        >>> from argilla import LabelQuestion, TrainingTaskMappingForTextClassification
        >>> dataset = rg.FeedbackDataset.from_argilla(argilla_id="...")
        >>> label = RatingQuestionUnification(question=dataset.questions[0], strategy="mean")
        >>> training_data = TrainingTaskMappingForTextClassification(
        ...     text=dataset.fields[0],
        ...     label=label
        ... )
        >>> dataset.prepare_training_data(training_data=training_data)

    """

    text: TextField
    label: Union[RatingQuestionUnification, LabelQuestionUnification]

    @property
    def supported_frameworks(self):
        names = ["transformers", "spacy", "openai", "setfit", "peft", "spark-nlp", "spacy-transformers"]
        return [Framework(name) for name in names]

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
        # TODO: provide label overview
        return train_test_split(
            data,
            train_size=train_size,
            shuffle=True,
            random_state=seed,
        )

    def __repr__(self) -> str:
        return (
            "TrainingTaskMappingForTextClassification",
            f"\n\t text={self.text.name}",
            f"\n\t label={self.label.question.name}",
            f"\n\t multi_label={self.__multi_label__}",
            f"\n\t all_labels={self.__all_labels__}",
        )

    @requires_version("datasets>1.17.0")
    def _prepare_for_training_with_transformers(
        self, data: List[dict], train_size: float, seed: int, framework: Union[str, Framework]
    ) -> Union["datasets.Dataset", "datasets.DatasetDict"]:
        self.test_framework_support(framework)
        import datasets

        multi_label = isinstance(self.label.question, MultiLabelQuestion)

        datasets_dict = {"id": [], "text": [], "label": []}
        for entry in data:
            datasets_dict["id"].append("None")
            datasets_dict["text"].append(entry["text"])
            datasets_dict["label"].append(entry["label"])

        all_labels = self.label.question.__all_labels__
        class_label = datasets.ClassLabel(names=all_labels)
        feature_dict = {
            "id": datasets.Value("string"),
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
                    "id": ds["id"],
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
        separator = OPENAI_SEPARATOR
        whitespace = OPENAI_WHITESPACE
        label2id = self.__label2id__

        if len(data) * train_size <= len(label2id) * 100:
            _LOGGER.warning("OpenAI recommends at least 100 examples per class for training a classification model.")

        def _prepare(data):
            jsonl = []
            for entry in data:
                prompt = entry["text"]
                prompt += separator  # needed for better performance

                try:
                    if multi_label:
                        completion = " ".join([str(label2id[str(annotation)]) for annotation in entry["label"]])
                    else:
                        completion = str(label2id[str(entry["label"])])
                except KeyError:
                    if multi_label:
                        completion = " ".join([str(label2id[int(annotation)]) for annotation in entry["label"]])
                    else:
                        completion = str(label2id[int(entry["label"])])

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
