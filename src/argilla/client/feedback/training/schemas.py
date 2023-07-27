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
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterator, List, Tuple, Union

import pandas as pd
from pydantic import BaseModel

from argilla._constants import OPENAI_SEPARATOR, OPENAI_WHITESPACE
from argilla.client.feedback.schemas import (
    FeedbackRecord,
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    TextField,
)
from argilla.client.feedback.unification import (
    LabelQuestionUnification,
    MultiLabelQuestionUnification,
    RankingQuestionUnification,
    RatingQuestionUnification,
)
from argilla.client.models import Framework
from argilla.utils.dependency import require_version, requires_version

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    import datasets
    import spacy

    from argilla.client.feedback.dataset import FeedbackDataset


class TrainingData(ABC):
    def _format_data(self, dataset: "FeedbackDataset"):
        formatted_data = []
        explode_columns = set()
        for record in dataset.records:
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
        if explode_columns:
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

    def _prepare_for_training_with_transformers(
        self, data: List[dict], train_size, seed: int, framework: Union[str, Framework]
    ) -> Union["datasets.Dataset", "datasets.DatasetDict"]:
        raise ValueError(f"{self.__class__.__name__} does not support the {framework} framework.")

    def _prepare_for_training_with_spacy(
        self, data: List[dict], train_size, seed: int, lang: str
    ) -> Union["spacy.token.DocBin", Tuple["spacy.token.DocBin", "spacy.token.DocBin"]]:
        raise ValueError(f"{self.__class__.__name__} does not support the spaCy framework.")

    def _prepare_for_training_with_spark_nlp(
        self, data: List[dict], train_size, seed: int
    ) -> Union["pd.DataFrame", Tuple["pd.DataFrame", "pd.DataFrame"]]:
        raise ValueError(f"{self.__class__.__name__} does not support the Spark NLP framework.")

    def _prepare_for_training_with_openai(
        self, data: List[dict], train_size, seed: int
    ) -> Union[List[dict], Tuple[List[dict], List[dict]]]:
        raise ValueError(f"{self.__class__.__name__} does not support the OpenAI framework.")

    def _prepare_for_training_with_trl(
        self, data: List[dict], train_size, seed: int
    ) -> Union[List[dict], Tuple[List[dict], List[dict]]]:
        raise ValueError(f"{self.__class__.__name__} does not support the TRL framework.")

    def _prepare_for_training_with_trlx(
        self, data: List[dict], train_size, seed: int
    ) -> Union[List[dict], Tuple[List[dict], List[dict]]]:
        raise ValueError(f"{self.__class__.__name__} does not support the TRLX framework.")


class TrainingTask:
    @classmethod
    def for_text_classification(
        cls,
        text: TextField,
        label: Union[
            RatingQuestion,
            LabelQuestion,
            RankingQuestion,
            MultiLabelQuestion,
            RatingQuestionUnification,
            LabelQuestionUnification,
            MultiLabelQuestionUnification,
            RankingQuestionUnification,
        ],
        label_strategy: str = None,
    ) -> "TrainingTaskForTextClassification":
        """
        _summary_

        Args:
            text (TextField): The TextField to use for training.
            label (Union[RatingQuestion, LabelQuestion, RankingQuestion, MultiLabelQuestion, RatingQuestionUnification, LabelQuestionUnification, MultiLabelQuestionUnification, RankingQuestionUnification]): _description_
            label_strategy (str, optional): A strategy to unify responses. Defaults to None. This means it will initialize the default strategy for the label type.

        Raises:
            ValueError: if label is not a valid type with the question type.
            ValueError: if label_strategy is defined and label is alraedy a Unification class.

        Returns:
            TrainingTaskForTextClassification: _description_

        Examples:
            >>> from argilla import LabelQuestion, TrainingTask
            >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
            >>> task = TrainingTask.for_text_classification(
            ...     text=dataset.fields[0],
            ...     label=dataset.questions[0],
            ... )
            >>> dataset.prepare_for_training(framework="...", task=task)

        """
        if isinstance(
            label,
            (
                LabelQuestionUnification,
                MultiLabelQuestionUnification,
                RatingQuestionUnification,
                RankingQuestionUnification,
            ),
        ):
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
            elif isinstance(label, RankingQuestion):
                label = RankingQuestionUnification(**unification_kwargs)
            else:
                raise ValueError(f"Label type {type(label)} is not supported.")
        return TrainingTaskForTextClassification(
            text=text,
            label=label,
            label_strategy=label_strategy,
        )

    @classmethod
    def for_supervised_fine_tuning(
        cls,
        formatting_func: Callable[[Dict[str, Any]], Union[None, str, List[str], Iterator[str]]],
    ) -> "TrainingTaskForTextClassification":
        """
        Return a task mapping that can be used in `FeedbackDataset.prepare_for_training(framework="...", task)`
        to extract data from the Feedback Dataset in an immediately useful format.

        Args:
            formatting_func (Callable[[Dict[str, Any]], Union[None, str, List[str], Iterator[str]]]): A formatting function
                converting a dictionary of records into zero, one or more text strings.

        Returns:
            TrainingTaskForSupervisedFinetuning: A task mapping instance to be used in `FeedbackDataset.prepare_for_training()`

        Examples:
            >>> from argilla import LabelQuestion, TrainingTaskForSupervisedFinetuning
            >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
            >>> def formatting_func(sample: Dict[str, Any]):
            ...     if sample["good"]["value"] == "Bad":
            ...         return
            ...     return template.format(prompt=sample["prompt"]["value"], response=sample["response"]["value"])
            >>> task = TrainingTaskForSupervisedFinetuning(formatting_func=formatting_func)
            >>> dataset.prepare_for_training(framework="...", task=task)

        """
        return TrainingTaskForSupervisedFinetuning(formatting_func=formatting_func)


class TrainingTaskForTextClassification(BaseModel, TrainingData):
    """Training data for text classification

    Args:
        text: TextField
        label: Union[RatingQuestionUnification, LabelQuestionUnification, MultiLabelQuestionUnification, RankingQuestionUnification]

    Examples:
        >>> from argilla import LabelQuestion, TrainingTaskForTextClassification
        >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
        >>> label = RatingQuestionUnification(question=dataset.questions[0], strategy="mean")
        >>> task = TrainingTaskForTextClassification(
        ...     text=dataset.fields[0],
        ...     label=label,
        ... )
        >>> dataset.prepare_for_training(framework="...", task=task)

    """

    text: TextField
    label: Union[
        RatingQuestionUnification, LabelQuestionUnification, MultiLabelQuestionUnification, RankingQuestionUnification
    ]

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
            "TrainingTaskForTextClassification",
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
        for index, entry in enumerate(data):
            datasets_dict["id"].append(index)
            datasets_dict["text"].append(entry["text"])
            datasets_dict["label"].append(entry["label"])

        all_labels = self.label.question.__all_labels__
        class_label = datasets.ClassLabel(names=all_labels)
        feature_dict = {
            "id": datasets.Value(dtype="int32"),
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


class TrainingTaskForSupervisedFinetuning(BaseModel, TrainingData):
    """Training data for supervised finetuning

    Args:
        formatting_func (Callable[[Dict[str, Any]], Union[None, str, List[str], Iterator[str]]]): A formatting function
            converting a dictionary of records into zero, one or more text strings.

    Examples:
        >>> from argilla import LabelQuestion, TrainingTaskForSupervisedFinetuning
        >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
        >>> def formatting_func(sample: Dict[str, Any]):
        ...     if sample["good"]["value"] == "Bad":
        ...         return
        ...     return template.format(prompt=sample["prompt"]["value"], response=sample["response"]["value"])
        >>> task = TrainingTaskForSupervisedFinetuning(formatting_func=formatting_func)
        >>> dataset.prepare_for_training(framework="...", task=task)

    """

    formatting_func: Callable[[Dict[str, Any]], Union[None, str, List[str], Iterator[str]]]

    def _format_data(self, dataset: "FeedbackDataset"):
        formatted_texts = []
        for sample in dataset.format_as("datasets"):
            if texts := self.formatting_func(sample):
                if isinstance(texts, str):
                    texts = [texts]
                for text in texts:
                    formatted_texts.append({"text": text})
        return formatted_texts

    @property
    def supported_frameworks(self):
        names = ["trl", "trlx"]
        return [Framework(name) for name in names]

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
            "TrainingTaskForSupervisedFinetuning",
            f"\n\t formatting_func={self.formatting_func}",
        )

    @requires_version("datasets>1.17.0")
    def _prepare_for_training_with_trl(
        self, data: List[dict], train_size: float, seed: int
    ) -> Union["datasets.Dataset", "datasets.DatasetDict"]:
        import datasets

        datasets_dict = {"id": [], "text": []}
        for index, sample in enumerate(data):
            datasets_dict["id"].append(index)
            datasets_dict["text"].append(sample["text"])

        feature_dict = {
            "id": datasets.Value(dtype="int32"),
            "text": datasets.Value("string"),
        }

        ds = datasets.Dataset.from_dict(datasets_dict, features=datasets.Features(feature_dict))
        if train_size != 1:
            ds = ds.train_test_split(train_size=train_size, test_size=1 - train_size, seed=seed)

        return ds

    def _prepare_for_training_with_trlx(self, data: List[dict], train_size: float, seed: int):
        raise NotImplementedError()


# Old, deprecated variants.
class RenamedDeprecationMixin:
    @classmethod
    def warn(cls) -> None:
        this_class_name = cls.__name__
        first_subclass_name = cls.__mro__[1].__name__
        warnings.warn(
            (f"`{this_class_name}` has been renamed to `{first_subclass_name}`, please use the latter."),
            DeprecationWarning,
            stacklevel=3,
        )


class TrainingTaskMapping(TrainingTask, RenamedDeprecationMixin):
    @classmethod
    def for_text_classification(cls, *args, **kwargs) -> TrainingTaskForTextClassification:
        cls.warn()
        return super().for_text_classification(*args, **kwargs)

    @classmethod
    def for_supervised_fine_tuning(cls, *args, **kwargs) -> TrainingTaskForSupervisedFinetuning:
        cls.warn()
        return super().for_supervised_fine_tuning(*args, **kwargs)


class TrainingTaskMappingForTextClassification(TrainingTaskForTextClassification, RenamedDeprecationMixin):
    def __init__(self, *args, **kwargs) -> None:
        self.warn()
        return super().__init__(*args, **kwargs)
