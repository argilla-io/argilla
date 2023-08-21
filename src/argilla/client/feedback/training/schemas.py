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
from abc import ABC
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterator, List, Optional, Tuple, Union

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


TASK_STRUCTURE = {
    "text_classification": {
        "field": (TextField),
        "question": (
            LabelQuestion,
            MultiLabelQuestion,
            RatingQuestion,
            RankingQuestion,
        ),
        "unification": (
            LabelQuestionUnification,
            MultiLabelQuestionUnification,
            RatingQuestionUnification,
            RankingQuestionUnification,
        ),
    }
}


class TrainingData(ABC):
    def _format_data(self, dataset: "FeedbackDataset"):
        formatted_data = []
        explode_columns = set()
        for record in dataset.records:
            data = {}
            for pydantic_field in self:
                # with default and formatting_func either one can be None
                if pydantic_field[-1] is not None:
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
        formatting_func: Callable[[Dict[str, Any]], Union[None, str, List[str], Iterator[str]]] = None,
        text: Optional[TextField] = None,
        label: Optional[
            Union[
                RatingQuestion,
                LabelQuestion,
                RankingQuestion,
                MultiLabelQuestion,
                RatingQuestionUnification,
                LabelQuestionUnification,
                MultiLabelQuestionUnification,
                RankingQuestionUnification,
            ]
        ] = None,
        label_strategy: str = None,
    ) -> "TrainingTaskForTextClassification":
        """
        Define a task configuration for text classification. It takes default values for `text` and `label` using datasets Fields and Questions or a custom `formatting_func` as Callable. See Examples underneath for more details.

        Args:
            formatting_func: A formatting function. Defaults to None.
            text: The TextField to use for training. Defaults to None.
            label: The *Question to use for training. Defaults to None.
            label_strategy: A strategy to unify responses. Defaults to None. This means it will initialize the default strategy for the label type. Defaults to None.

        Raises:
            ValueError: if label is not a valid type with the question type.
            ValueError: if label_strategy is defined and label is already a Unification class.

        Returns:
            TrainingTaskForTextClassification: A task mapping instance to be used in `FeedbackDataset.prepare_for_training()`

        Examples:
            >>> from argilla import LabelQuestion, TrainingTask
            >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
            >>> task = TrainingTask.for_text_classification(
            ...     text=dataset.fields[0],
            ...     label=dataset.questions[0]
            ... )
            >>> dataset.prepare_for_training(framework="...", task=task)

            >>> from argilla import LabelQuestion, TrainingTask
            >>> from collections import Counter
            >>> import random
            >>> def formatting_func(sample: Dict[str, Any]) -> Union[Tuple[str, str], Tuple[str, List[str]]]:
            ...     text = sample["text"]
            ...     values = [annotation["value"] for annotation in sample["label"]]
            ...     counter = Counter(values)
            ...     if counter:
            ...         most_common = counter.most_common()
            ...         max_frequency = most_common[0][1]
            ...         most_common_elements = [element for element, frequency in most_common if frequency == max_frequency]
            ...         label = random.choice(most_common_elements)
            ...         return (text, label)
            ...     else:
            ...         return None
            >>> task = TrainingTask.for_text_classification(formatting_func=formatting_func)
            >>> dataset.prepare_for_training(framework="...", task=task)
        """
        if (text and label) and formatting_func is not None:
            raise ValueError("You must provide either `text` and `label`, or a `formatting_func`, not both.")

        if formatting_func is not None:
            if text or label:
                raise ValueError("`formatting_func` is already defined, so you cannot define `text` and `label`.")
            return TrainingTaskForTextClassification(formatting_func=formatting_func)
        else:
            if isinstance(label, TASK_STRUCTURE["text_classification"]["unification"]):
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
            return TrainingTaskForTextClassification(text=text, label=label)

    @classmethod
    def for_supervised_fine_tuning(
        cls,
        formatting_func: Callable[[Dict[str, Any]], Union[None, str, List[str], Iterator[str]]],
    ) -> "TrainingTaskForSFT":
        """
        Return a task that can be used in `FeedbackDataset.prepare_for_training(framework="...", task)`
        to extract data from the Feedback Dataset in an immediately useful format.

        Args:
            formatting_func (Callable[[Dict[str, Any]], Union[None, str, List[str], Iterator[str]]]): A formatting function
                converting a dictionary of records into zero, one or more text strings.

        Returns:
            TrainingTaskForSFT: A task mapping instance to be used in `FeedbackDataset.prepare_for_training()`

        Examples:
            >>> from argilla import TrainingTask
            >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
            >>> def formatting_func(sample: Dict[str, Any]):
            ...     annotations = sample["good]
            ...     if annotations and annotations[0]["value"] == "Bad":
            ...         return
            ...     return template.format(prompt=sample["prompt"][0]["value"], response=sample["response"][0]["value"])
            >>> task = TrainingTask.for_supervised_fine_tuning(formatting_func=formatting_func)
            >>> dataset.prepare_for_training(framework="...", task=task)

        """
        return TrainingTaskForSFT(formatting_func=formatting_func)

    @classmethod
    def for_reward_modelling(
        cls,
        formatting_func: Callable[
            [Dict[str, Any]], Union[None, Tuple[str, str], List[Tuple[str, str]], Iterator[Tuple[str, str]]]
        ],
    ) -> "TrainingTaskForRM":
        """
        Return a task that can be used in `FeedbackDataset.prepare_for_training(framework="...", task)`
        to extract data from the Feedback Dataset in an immediately useful format.

        Args:
            formatting_func (Callable[[Dict[str, Any]], Union[None, Tuple[str, str], List[Tuple[str, str]], Iterator[Tuple[str, str]]]]):
                A formatting function converting a dictionary of records into zero, one or more chosen-rejected text tuples.

        Returns:
            TrainingTaskForRM: A task mapping instance to be used in `FeedbackDataset.prepare_for_training()`

        Examples:
            >>> from argilla import TrainingTask
            >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
            >>> def formatting_func(sample: Dict[str, Any]):
            ...     values = [annotation["value"] for annotation in sample["ranking"]]
            ...     if values.count("1") >= values.count("2"):
            ...         chosen = sample["response-1"]
            ...         rejected = sample["response-2"]
            ...     else:
            ...         chosen = sample["response-2"]
            ...         rejected = sample["response-1"]
            ...     return chosen, rejected
            >>> task = TrainingTask.for_reward_modelling(formatting_func=formatting_func)
            >>> dataset.prepare_for_training(framework="...", task=task)

        """
        return TrainingTaskForRM(formatting_func=formatting_func)

    @classmethod
    def for_proximal_policy_optimization(
        cls, formatting_func: Callable[[Dict[str, Any]], Union[None, str, Iterator[str]]]
    ) -> "TrainingTaskForPPO":
        """
        Return a task that can be used in `FeedbackDataset.prepare_for_training(text: TextField)`
        to extract data from the Feedback Dataset in an immediately useful format.

        Args:
            formatting_func (Callable[[Dict[str, Any]], Union[None, str, Iterator[str]]]):
                A formatting function converting a dictionary of records into zero, one or more prompts.

        Returns:
            TrainingTaskForPPO: A task mapping instance to be used in `FeedbackDataset.prepare_for_training()`
        """
        return TrainingTaskForPPO(formatting_func=formatting_func)

    @classmethod
    def for_direct_preference_optimization(
        cls,
        formatting_func: Callable[[Dict[str, Any]], Union[None, Tuple[str, str, str], Iterator[Tuple[str, str, str]]]],
    ) -> "TrainingTaskForDPO":
        """
        Provide `TrainingTask.for_direct_preference_optimization(formatting_func: Callable)`
        Return a task that can be used in `FeedbackDataset.prepare_for_training(framework="...", task)`
        to extract data from the Feedback Dataset in an immediately useful format.

        Args:
            formatting_func (Callable[[Dict[str, Any]], Union[None, Tuple[str, str, str], Iterator[Tuple[str, str, str]]]]):
                A formatting function converting a dictionary of records into zero, one or more prompt-chosen-rejected text tuples.

        Returns:
            TrainingTaskForDPO: A task mapping instance to be used in `FeedbackDataset.prepare_for_training()`

        Examples:
            >>> from argilla import TrainingTask
            >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
            >>> def formatting_func(sample: Dict[str, Any]):
            ...     values = [annotation["value"] for annotation in sample["ranking"]]
            ...     if values.count("1") >= values.count("2"):
            ...         chosen = sample["response-1"]
            ...         rejected = sample["response-2"]
            ...     else:
            ...         chosen = sample["response-2"]
            ...         rejected = sample["response-1"]
            ...     return sample["prompt"], chosen, rejected
            >>> task = TrainingTask.for_direct_preference_optimization(formatting_func=formatting_func)
            >>> dataset.prepare_for_training(framework="...", task=task)

        """
        return TrainingTaskForDPO(formatting_func=formatting_func)


class TrainingTaskForTextClassification(BaseModel, TrainingData):
    """Training data for text classification

    Args:
        formatting_func (Callable[[Dict[str, Any]], Union[None, str, List[str], Iterator[str]]], optional): A formatting function. Defaults to None.
        text: TextField
        label: Union[RatingQuestionUnification, LabelQuestionUnification, MultiLabelQuestionUnification, RankingQuestionUnification]

    Examples:
        >>> from argilla import LabelQuestion, TrainingTask
        >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
        >>> task = TrainingTask.for_text_classification(
        ...     text=dataset.fields[0],
        ...     label=dataset.questions[0]
        ... )
        >>> dataset.prepare_for_training(framework="...", task=task)

        >>> from argilla import LabelQuestion, TrainingTask
        >>> from collections import Counter
        >>> def formatting_func(sample: Dict[str, Any]) -> Union[Tuple[str, str], Tuple[str, List[str]]]:
        ...     text = sample["text"]
        ...     values = [annotation["value"] for annotation in sample["label"]]
        ...     counter = Counter(values)
        ...     if counter:
        ...         most_common = counter.most_common()
        ...         max_frequency = most_common[0][1]
        ...         most_common_elements = [element for element, frequency in most_common if frequency == max_frequency]
        ...         label = random.choice(most_common_elements)
        ...         return (text, label)
        ...     else:
        ...         return None
        >>> task = TrainingTask.for_text_classification(formatting_func=formatting_func)
        >>> dataset.prepare_for_training(framework="...", task=task)

    """

    formatting_func: Callable[[Dict[str, Any]], Union[None, str, List[str], Iterator[str]]] = None
    text: TextField = None
    label: Union[
        RatingQuestionUnification, LabelQuestionUnification, MultiLabelQuestionUnification, RankingQuestionUnification
    ] = None

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

    def _format_data(self, dataset: "FeedbackDataset"):
        if self.formatting_func is not None:
            output = set()
            for sample in dataset.format_as("datasets"):
                text_label = self.formatting_func(sample)
                if text_label is None:
                    continue

                if isinstance(text_label, tuple) and isinstance(text_label[0], str):
                    text_label = {text_label}
                else:
                    raise ValueError(
                        "formatting_func must return (text,label) as a Tuple[str, str] or a Tuple[str, List[str]]"
                    )

                output |= set(text_label)

            data = []
            _all_labels = set()
            for text, label in output:
                data.append({"text": text, "label": label})
                if isinstance(label, list):
                    _multi_label = True
                    _all_labels |= set(label)
                else:
                    _all_labels.add(label)
                    _multi_label = False

            # infer label type from output custum formatting function
            if _multi_label:
                self.label = MultiLabelQuestionUnification(
                    question=MultiLabelQuestion(name="custom_func", labels=list(_all_labels))
                )
            else:
                self.label = LabelQuestionUnification(
                    question=LabelQuestion(name="custom_func", labels=list(_all_labels))
                )
            return data
        else:
            return super()._format_data(dataset)

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
            f"{self.__class__.__name__}"
            f"\n\t text={self.text.name}"
            f"\n\t label={self.label.question.name}"
            f"\n\t multi_label={self.__multi_label__}"
            f"\n\t all_labels={self.__all_labels__}"
        )

    @requires_version("datasets>1.17.0")
    def _prepare_for_training_with_transformers(
        self, data: List[dict], train_size: float, seed: int, framework: Union[str, Framework]
    ) -> Union["datasets.Dataset", "datasets.DatasetDict"]:
        self.test_framework_support(framework)
        import datasets

        multi_label = self.__multi_label__

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

        all_labels = self.__all_labels__

        def _prepare(data):
            db = DocBin(store_user_data=True)
            # Creating the DocBin object as in https://spacy.io/usage/training#training-data
            for entry in data:
                doc = lang.make_doc(entry["text"])

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


class TrainingTaskForSFT(BaseModel, TrainingData):
    """Training data for supervised finetuning

    Args:
        formatting_func (Callable[[Dict[str, Any]], Union[None, str, List[str], Iterator[str]]]): A formatting function
            converting a dictionary of records into zero, one or more text strings.

    Examples:
        >>> from argilla import TrainingTaskForSFT
        >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
        >>> def formatting_func(sample: Dict[str, Any]):
        ...     annotations = sample["good]
        ...     if annotations and annotations[0]["value"] == "Bad":
        ...         return
        ...     return template.format(prompt=sample["prompt"][0]["value"], response=sample["response"][0]["value"])
        >>> task = TrainingTaskForSFT(formatting_func=formatting_func)
        >>> dataset.prepare_for_training(framework="...", task=task)

    """

    formatting_func: Callable[[Dict[str, Any]], Union[None, str, List[str], Iterator[str]]]

    def _format_data(self, dataset: "FeedbackDataset"):
        formatted_texts = set()
        for sample in dataset.format_as("datasets"):
            if texts := self.formatting_func(sample):
                if isinstance(texts, str):
                    texts = {texts}
                formatted_texts |= set(texts)
        return [{"text": text} for text in formatted_texts]

    @property
    def supported_frameworks(self):
        names = ["trl"]
        return [Framework(name) for name in names]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}\n\t formatting_func={self.formatting_func}"

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


class TrainingTaskForRM(BaseModel, TrainingData):
    """Training data for reward modelling

    Args:
        formatting_func (Callable[[Dict[str, Any]], Union[None, Tuple[str, str], List[Tuple[str, str]], Iterator[Tuple[str, str]]]]):
            A formatting function converting a dictionary of records into zero, one or more chosen-rejected text tuples.

    Examples:
        >>> from argilla import TrainingTaskForRM
        >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
        >>> def formatting_func(sample: Dict[str, Any]):
        ...     values = [annotation["value"] for annotation in sample["ranking"]]
        ...     if values.count("1") >= values.count("2"):
        ...         chosen = sample["response-1"]
        ...         rejected = sample["response-2"]
        ...     else:
        ...         chosen = sample["response-2"]
        ...         rejected = sample["response-1"]
        ...     return chosen, rejected
        >>> task = TrainingTaskForRM(formatting_func=formatting_func)
        >>> dataset.prepare_for_training(framework="...", task=task)
    """

    formatting_func: Callable[
        [Dict[str, Any]], Union[None, Tuple[str, str], List[Tuple[str, str]], Iterator[Tuple[str, str]]]
    ]

    def _format_data(self, dataset: "FeedbackDataset"):
        output = set()
        for sample in dataset.format_as("datasets"):
            chosen_rejecteds = self.formatting_func(sample)
            if chosen_rejecteds is None:
                continue

            if isinstance(chosen_rejecteds, tuple) and isinstance(chosen_rejecteds[0], str):
                chosen_rejecteds = {chosen_rejecteds}

            output |= set(chosen_rejecteds)
        return [{"chosen": chosen, "rejected": rejected} for chosen, rejected in output]

    @property
    def supported_frameworks(self):
        names = ["trl"]
        return [Framework(name) for name in names]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}\n\t formatting_func={self.formatting_func}"

    @requires_version("datasets>1.17.0")
    def _prepare_for_training_with_trl(
        self, data: List[dict], train_size: float, seed: int
    ) -> Union["datasets.Dataset", "datasets.DatasetDict"]:
        import datasets

        datasets_dict = {"chosen": [], "rejected": []}
        for sample in data:
            datasets_dict["chosen"].append(sample["chosen"])
            datasets_dict["rejected"].append(sample["rejected"])

        feature_dict = {
            "rejected": datasets.Value("string"),
            "chosen": datasets.Value("string"),
        }

        ds = datasets.Dataset.from_dict(datasets_dict, features=datasets.Features(feature_dict))
        if train_size != 1:
            ds = ds.train_test_split(train_size=train_size, test_size=1 - train_size, seed=seed)

        return ds


class TrainingTaskForPPO(BaseModel, TrainingData):
    """Training data for proximal policy optimization

    Args:
        text (TextField): The TextField to use for training.

    Examples:
        >>> from argilla import TrainingTaskForPPO
        >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
        >>> task = TrainingTaskForPPO(text=dataset.fields[0],)
        >>> dataset.prepare_for_training(framework="...", task=task)
    """

    formatting_func: Callable[[Dict[str, Any]], Union[None, str, Iterator[str]]]

    def _format_data(self, dataset: "FeedbackDataset"):
        formatted_texts = set()
        for sample in dataset.format_as("datasets"):
            if texts := self.formatting_func(sample):
                if isinstance(texts, str):
                    texts = {texts}
                formatted_texts |= set(texts)
        return [{"query": text} for text in formatted_texts]

    @property
    def supported_frameworks(self):
        names = ["trl"]
        return [Framework(name) for name in names]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}\n\t formatting_func={self.formatting_func}"

    @requires_version("datasets>1.17.0")
    def _prepare_for_training_with_trl(
        self, data: List[dict], train_size: float, seed: int
    ) -> Union["datasets.Dataset", "datasets.DatasetDict"]:
        import datasets

        datasets_dict = {"id": [], "query": []}
        for index, entry in enumerate(data):
            datasets_dict["id"].append(index)
            datasets_dict["query"].append(entry["query"])

        feature_dict = {
            "id": datasets.Value(dtype="int32"),
            "query": datasets.Value("string"),
        }

        ds = datasets.Dataset.from_dict(datasets_dict, features=datasets.Features(feature_dict))

        if train_size != 1:
            ds = ds.train_test_split(train_size=train_size, test_size=1 - train_size, seed=seed)

        return ds


class TrainingTaskForDPO(BaseModel, TrainingData):
    """Training data for direct preference optimization

    Args:
        formatting_func (Callable[[Dict[str, Any]], Union[None, Tuple[str, str, str], Iterator[Tuple[str, str, str]]]]):
            A formatting function converting a dictionary of records into zero, one or more prompt-chosen-rejected text tuples.

    Examples:
        >>> from argilla import TrainingTaskForDPO
        >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
        >>> def formatting_func(sample: Dict[str, Any]):
        ...     values = [annotation["value"] for annotation in sample["ranking"]]
        ...     if values.count("1") >= values.count("2"):
        ...         chosen = sample["response-1"]
        ...         rejected = sample["response-2"]
        ...     else:
        ...         chosen = sample["response-2"]
        ...         rejected = sample["response-1"]
        ...     return sample["prompt"], chosen, rejected
        >>> task = TrainingTaskForDPO(formatting_func=formatting_func)
        >>> dataset.prepare_for_training(framework="...", task=task)
    """

    formatting_func: Callable[[Dict[str, Any]], Union[None, Tuple[str, str, str], Iterator[Tuple[str, str, str]]]]

    def _format_data(self, dataset: "FeedbackDataset"):
        output = set()
        for sample in dataset.format_as("datasets"):
            prompt_chosen_rejecteds = self.formatting_func(sample)
            if prompt_chosen_rejecteds is None:
                continue

            if isinstance(prompt_chosen_rejecteds, tuple) and isinstance(prompt_chosen_rejecteds[0], str):
                prompt_chosen_rejecteds = {prompt_chosen_rejecteds}

            output |= set(prompt_chosen_rejecteds)
        return [{"prompt": prompt, "chosen": chosen, "rejected": rejected} for prompt, chosen, rejected in output]

    @property
    def supported_frameworks(self):
        names = ["trl"]
        return [Framework(name) for name in names]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}\n\t formatting_func={self.formatting_func}"

    @requires_version("datasets>1.17.0")
    def _prepare_for_training_with_trl(
        self, data: List[dict], train_size: float, seed: int
    ) -> Union["datasets.Dataset", "datasets.DatasetDict"]:
        import datasets

        datasets_dict = {"prompt": [], "chosen": [], "rejected": []}
        for sample in data:
            datasets_dict["prompt"].append(sample["prompt"])
            datasets_dict["chosen"].append(sample["chosen"])
            datasets_dict["rejected"].append(sample["rejected"])

        feature_dict = {
            "prompt": datasets.Value("string"),
            "rejected": datasets.Value("string"),
            "chosen": datasets.Value("string"),
        }

        ds = datasets.Dataset.from_dict(datasets_dict, features=datasets.Features(feature_dict))
        if train_size != 1:
            ds = ds.train_test_split(train_size=train_size, test_size=1 - train_size, seed=seed)

        return ds


TrainingTaskTypes = Union[
    TrainingTaskForTextClassification,
    TrainingTaskForSFT,
    TrainingTaskForRM,
    TrainingTaskForPPO,
    TrainingTaskForDPO,
]


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
    def for_supervised_fine_tuning(cls, *args, **kwargs) -> TrainingTaskForSFT:
        cls.warn()
        return super().for_supervised_fine_tuning(*args, **kwargs)

    @classmethod
    def for_reward_modelling(cls, *args, **kwargs) -> TrainingTaskForRM:
        cls.warn()
        return super().for_reward_modelling(*args, **kwargs)

    @classmethod
    def for_proximal_policy_optimization(cls, *args, **kwargs) -> TrainingTaskForPPO:
        cls.warn()
        return super().for_proximal_policy_optimization(cls, *args, **kwargs)

    @classmethod
    def for_direct_preference_optimization(cls, *args, **kwargs) -> TrainingTaskForDPO:
        cls.warn()
        return super().for_direct_preference_optimization(*args, **kwargs)


class TrainingTaskMappingForTextClassification(TrainingTaskForTextClassification, RenamedDeprecationMixin):
    def __init__(self, *args, **kwargs) -> None:
        self.warn()
        return super().__init__(*args, **kwargs)
