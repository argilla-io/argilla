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
import types
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
    TextQuestion,
)
from argilla.client.feedback.unification import (
    LabelQuestionUnification,
    MultiLabelQuestionUnification,
    RankingQuestionUnification,
    RatingQuestionUnification,
)
from argilla.client.models import Framework
from argilla.utils.dependency import require_dependencies, requires_dependencies

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    import datasets
    import spacy
    from sentence_transformers import InputExample

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
    },
    "question_answering": {
        "field": (TextField),
        "question": (TextQuestion),
        "unification": (),
    },
}


class TrainingData(ABC):
    _formatting_func_return_types = None

    def _test_output_formatting_func(self, sample: Any):
        """
        Test if the formatting function returns the expected format.
        """
        try:
            if not isinstance(sample, types.GeneratorType):
                self._formatting_func_return_types(format=sample)
            return True
        except Exception:
            raise ValueError(
                f"formatting_func must return {self._formatting_func_return_types.__annotations__['format']}, not {type(sample)}"
            )

    def _format_data(self, dataset: "FeedbackDataset") -> List[Dict[str, Any]]:
        formatted_data = []
        explode_columns = set()
        for record in dataset.records:
            data = {}
            for pydantic_field in self:
                # with default and formatting_func either one can be None
                if pydantic_field[-1] is not None:
                    pydantic_field_name, pydantic_field_value = pydantic_field
                    if isinstance(pydantic_field_value, (list, tuple, set)):
                        # NOTE: In the case of TrainingTaskForSentenceSimilarity with defaults,
                        # we need to grab multiple values, not just the text.
                        for pydantic_field_value_i in pydantic_field_value:
                            if isinstance(pydantic_field_value_i, (TextField,)):
                                data[pydantic_field_value_i.name] = record.fields[pydantic_field_value_i.name]
                            else:
                                if pydantic_field_value_i.question.name not in record._unified_responses:
                                    continue
                                else:
                                    data[pydantic_field_name] = [
                                        resp.value
                                        for resp in record._unified_responses[pydantic_field_value_i.question.name]
                                    ]
                                explode_columns.add(pydantic_field_name)

                    elif isinstance(pydantic_field_value, (TextField,)):
                        data[pydantic_field_name] = record.fields[pydantic_field_value.name]
                    elif isinstance(pydantic_field_value, (TextQuestion,)):
                        if pydantic_field_value.name not in record._unified_responses:
                            continue
                        else:
                            data[pydantic_field_name] = record._unified_responses[pydantic_field_value.name].value
                        explode_columns.add(pydantic_field_name)
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
        # In cases of MultiLabel datasets the label column contains a list,
        # which is unhashable, so for those cases we transform the rows in the
        # dataframe to tuples to drop duplicates and reconstruct the original
        # dataframe format.
        if df.applymap(lambda x: isinstance(x, list)).any().any():
            df = pd.DataFrame(df.apply(tuple, 1).drop_duplicates().to_list(), columns=df.columns)
        else:
            df = df.drop_duplicates()
        df = df.dropna(how="any")
        return df.to_dict(orient="records")

    @property
    def supported_frameworks(self) -> List[Framework]:
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
            >>> # with defaults
            >>> from argilla.feedback import LabelQuestion, TrainingTask
            >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
            >>> task = TrainingTask.for_text_classification(
            ...     text=dataset.field_by_name("text"),
            ...     label=dataset.question_by_name("label")
            ... )
            >>> dataset.prepare_for_training(framework="...", task=task)
            >>> # with formatting_func
            >>> from argilla.feedback import LabelQuestion, TrainingTask
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
            formatting_func: A formatting function converting a dictionary of records into zero,
                one or more text strings.

        Returns:
            TrainingTaskForSFT: A task mapping instance to be used in `FeedbackDataset.prepare_for_training()`

        Examples:
            >>> from argilla.feedback import TrainingTask
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
    def for_reward_modeling(
        cls,
        formatting_func: Callable[
            [Dict[str, Any]], Union[None, Tuple[str, str], List[Tuple[str, str]], Iterator[Tuple[str, str]]]
        ],
    ) -> "TrainingTaskForRM":
        """
        Return a task that can be used in `FeedbackDataset.prepare_for_training(framework="...", task)`
        to extract data from the Feedback Dataset in an immediately useful format.

        Args:
            formatting_func: A formatting function converting a dictionary of records into zero,
                one or more chosen-rejected text tuples.

        Returns:
            TrainingTaskForRM: A task mapping instance to be used in `FeedbackDataset.prepare_for_training()`

        Examples:
            >>> from argilla.feedback import TrainingTask
            >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
            >>> def formatting_func(sample: Dict[str, Any]):
            ...     values = [annotation["value"] for annotation in sample["ranking"]]
            ...     if values.count("1") >= values.count("2"):
            ...         chosen = sample["response-1"]
            ...         rejected = sample["response-2"]
            ...     else:
            ...         chosen = sample["response-2"]
            ...         rejected = sample["response-1"]
            ...     yield chosen, rejected
            >>> task = TrainingTask.for_reward_modeling(formatting_func=formatting_func)
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
            formatting_func: A formatting function converting a dictionary of records into zero,
                one or more prompts.

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
            formatting_func: A formatting function converting a dictionary of records into zero,
                one or more prompt-chosen-rejected text tuples.

        Returns:
            TrainingTaskForDPO: A task mapping instance to be used in `FeedbackDataset.prepare_for_training()`

        Examples:
            >>> from argilla.feedback import TrainingTask
            >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
            >>> def formatting_func(sample: Dict[str, Any]):
            ...     values = [annotation["value"] for annotation in sample["ranking"]]
            ...     if values.count("1") >= values.count("2"):
            ...         chosen = sample["response-1"]
            ...         rejected = sample["response-2"]
            ...     else:
            ...         chosen = sample["response-2"]
            ...         rejected = sample["response-1"]
            ...     yield sample["prompt"], chosen, rejected
            >>> task = TrainingTask.for_direct_preference_optimization(formatting_func=formatting_func)
            >>> dataset.prepare_for_training(framework="...", task=task)

        """
        return TrainingTaskForDPO(formatting_func=formatting_func)

    @classmethod
    def for_chat_completion(
        cls,
        formatting_func: Callable[
            [Dict[str, Any]], Union[None, Tuple[str, str, str, str], Iterator[Tuple[str, str, str, str]]]
        ],
    ) -> "TrainingTaskForChatCompletion":
        """Training data for chat completion
        Args:
            formatting_func: A formatting function converting a dictionary of records into zero,
                one or more chat-turn-role-content text tuples.

        Examples:
            >>> from argilla.feedback import TrainingTaskForChatCompletion
            >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
            >>> def formatting_func(sample: Dict[str, Any]):
            ...     from uuid import uuid4
            ...     chat_id = str(uuid4())
            ...     if sample["response"]:
            ...         chat = str(uuid4())
            ...         user_message = sample["prompt"][0]["value"]
            ...         system_message = sample["response"][0]["value"]
            ...         yield [(chat, "0", "user", user_message), (chat, "1", "assistant", system_message)]
            >>> task = TrainingTaskForChatCompletion(formatting_func=formatting_func)
            >>> dataset.prepare_for_training(framework="...", task=task)
        """
        return TrainingTaskForChatCompletion(formatting_func=formatting_func)

    @classmethod
    def for_question_answering(
        cls,
        formatting_func: Optional[
            Callable[[Dict[str, Any]], Union[None, Tuple[str, str, str], Iterator[Tuple[str, str, str]]]]
        ] = None,
        question: Optional[TextField] = None,
        context: Optional[TextField] = None,
        answer: Optional[TextQuestion] = None,
    ) -> "TrainingTaskForQuestionAnswering":
        """Training data for question answering

        Args:
            formatting_func: A formatting function converting a dictionary of records into zero,
                one or more question-context-answer text tuples.
            question: The TextField to use for training.
            context: The TextField to use for training.
            answer: The TextQuestion to use for training.

        Examples:
            >>> # with defaults
            >>> from argilla.feedback import TrainingTaskForQuestionAnswering
            >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
            >>> task = TrainingTaskForQuestionAnswering(
            ...     question=dataset.field_by_name("question"),
            ...     context=dataset.field_by_name("context"),
            ...     answer=dataset.question_by_name("answer"),
            ... )
            >>> dataset.prepare_for_training(framework="...", task=task)
            >>> # with formatting_func
            >>> from argilla.feedback import TrainingTaskForQuestionAnswering
            >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
            >>> def formatting_func(sample: Dict[str, Any]):
            ...     question = sample["question"]
            ...     context = sample["context"]
            ...     for answer in sample["answer"]:
            ...         if not all([question, context, answer["value"]]):
            ...             continue
            ...         yield question, context, answer["value"]
            >>> task = TrainingTaskForQuestionAnswering(formatting_func=formatting_func)
            >>> dataset.prepare_for_training(framework="...", task=task)
        """
        if (question and context and answer) and formatting_func is not None:
            raise ValueError(
                "You must provide either `question`, `context` and `answer`, or a `formatting_func`, not both."
            )

        if formatting_func is not None:
            if question or context or answer:
                raise ValueError(
                    "`formatting_func` is already defined, so you cannot define `question`, `context` and `answer`."
                )
            return TrainingTaskForQuestionAnswering(formatting_func=formatting_func)
        else:
            return TrainingTaskForQuestionAnswering(question=question, context=context, answer=answer)

    @classmethod
    def for_sentence_similarity(
        cls,
        texts: Optional[List[TextField]] = None,
        label: Optional[Union[LabelQuestion, RankingQuestion]] = None,
        formatting_func: Callable[
            [Dict[str, Any]],
            Union[
                None,
                Dict[str, Union[float, int]],
                Dict[str, str],
                List[Dict[str, Union[float, int]]],
                List[Dict[str, str]],
            ],
        ] = None,
        label_strategy: Optional[LabelQuestionUnification] = None,
    ) -> "TrainingTaskForSentenceSimilarity":
        """

        Return a task that can be used in `FeedbackDataset.prepare_for_training(framework="...", task)`
        to extract data from the Feedback Dataset in a format suitable for sentence similarity.

        Args:
            texts: A list of TextFields to use for training, typically two text pieces, can be a triplet also.
                Defaults to None.
            label: The `LabelQuestion` or `RankingQuestion` to use for training. These models can be trained without
                explicit use of labels, just with pairs or triplets of texts. Defaults to None.
            formatting_func: A formatting function converting a dictionary of records into a dict
                of `sentence-1`-`sentence-2` pairs or triplets `sentence-1`-`sentence-2`-`sentence-3`,
                optionally including a `label` field.
            label_strategy: A strategy to unify responses. Defaults to None. This means it will initialize the default strategy for the label type.

        Raises:
            ValueError: If label is not a valid type.
            ValueError: if label_strategy is defined and label is already a Unification class.

        Returns:
            TrainingTaskForSentenceSimilarity: A task mapping instance to be used in `FeedbackDataset.prepare_for_training()`

        Examples:
            >>> from argilla.feedback import LabelQuestion, TrainingTask
            >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
            >>> task = TrainingTask.for_text_classification(
            ...     texts=[dataset.field_by_name("premise"), dataset.field_by_name("hypothesis")],
            ...     label=dataset.question_by_name("label")
            ... )
            >>> dataset.prepare_for_training(framework="...", task=task)

            >>> from argilla.feedback import LabelQuestion, TrainingTask
            >>> from collections import Counter
            >>> import random
            >>> def formatting_func(sample: Dict[str, Any]) -> Union[Tuple[str, str], Tuple[str, List[str]]]:
            ...     record = {"sentence-1": sample["premise"], "sentence-2": sample["hypothesis"]}
            ...     values = [annotation["value"] for annotation in sample["label"]]
            ...     counter = Counter(values)
            ...     if counter:
            ...         most_common = counter.most_common()
            ...         max_frequency = most_common[0][1]
            ...         most_common_elements = [element for element, frequency in most_common if frequency == max_frequency]
            ...         record["label"] = label
            ...         return record
            ...     else:
            ...         return None
            >>> task = TrainingTask.for_sentence_similarity(formatting_func=formatting_func)
            >>> dataset.prepare_for_training(framework="...", task=task)
        """

        if (texts or label) and formatting_func is not None:
            raise ValueError(
                "You must provide either `texts` and (optionally) `label`, or a `formatting_func`, not both."
            )

        if formatting_func is not None:
            return TrainingTaskForSentenceSimilarity(formatting_func=formatting_func)
        else:
            if not label:
                return TrainingTaskForSentenceSimilarity(texts=texts)

            if isinstance(label, LabelQuestionUnification):
                if label_strategy is not None:
                    raise ValueError("label_strategy is already defined via Unification class.")
            else:
                unification_kwargs = {"question": label}
                if label_strategy is not None:
                    unification_kwargs["strategy"] = label_strategy
                else:
                    _LOGGER.info(f"No label strategy defined. Using default strategy for {type(label)}.")
                if isinstance(label, LabelQuestion):
                    label = LabelQuestionUnification(**unification_kwargs)
                elif isinstance(label, RankingQuestion):
                    label = RankingQuestionUnification(**unification_kwargs)
                else:
                    raise ValueError(f"Label type {type(label)} is not supported.")
            return TrainingTaskForSentenceSimilarity(texts=texts, label=label)


class TrainingTaskForTextClassificationFormat(BaseModel):
    """
    Union[
        Tuple[str, str], Tuple[str, List[str]],
        List[Tuple[str, str]], List[Tuple[str, List[str]]]
    ]
    """

    format: Union[Tuple[str, str], Tuple[str, List[str]], List[Tuple[str, str]], List[Tuple[str, List[str]]]]


class TrainingTaskForTextClassification(BaseModel, TrainingData):
    """Training data for text classification

    Args:
        formatting_func: A formatting function returning the text to classify. Either a formatting function or
            the text and label parameters are provided. Defaults to None.
        text: The text field to take as the text to classify.
        label: The question denoting the label of the text to classify.

        Examples:
            >>> # with defaults
            >>> from argilla.feedback import LabelQuestion, TrainingTask
            >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
            >>> task = TrainingTask.for_text_classification(
            ...     text=dataset.field_by_name("text"),
            ...     label=dataset.question_by_name("label")
            ... )
            >>> dataset.prepare_for_training(framework="...", task=task)
            >>> # with formatting_func
            >>> from argilla.feedback import LabelQuestion, TrainingTask
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
            ...         yield text, label
            >>> task = TrainingTask.for_text_classification(formatting_func=formatting_func)
            >>> dataset.prepare_for_training(framework="...", task=task)
    """

    formatting_func: Optional[Callable[[Dict[str, Any]], Union[None, str, List[str], Iterator[str]]]] = None
    _formatting_func_return_types = TrainingTaskForTextClassificationFormat
    text: Optional[TextField] = None
    label: Optional[
        Union[
            RatingQuestionUnification,
            LabelQuestionUnification,
            MultiLabelQuestionUnification,
            RankingQuestionUnification,
        ]
    ] = None

    @property
    def supported_frameworks(self) -> List[Framework]:
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

    def _format_data(self, dataset: "FeedbackDataset") -> List[Dict[str, Any]]:
        if self.formatting_func is not None:
            output = set()

            for sample in dataset.format_as("datasets"):
                text_label = self.formatting_func(sample)
                if text_label is None:
                    continue

                self._test_output_formatting_func(text_label)

                if isinstance(text_label, tuple):
                    text_label = {text_label}

                output |= set(text_label)

            data = []
            _all_labels = set()
            for text_label in output:
                if text_label is None:
                    continue
                else:
                    text, label = text_label
                data.append({"text": text, "label": label})
                if isinstance(label, list):
                    _multi_label = True
                    _all_labels |= set(label)
                else:
                    _all_labels.add(label)
                    _multi_label = False

            # infer label type from output custom formatting function
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

    @requires_dependencies("scikit-learn")
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
        if self.formatting_func is not None:
            return f"{self.__class__.__name__}\n\t formatting_func={self.formatting_func}"
        else:
            return (
                f"{self.__class__.__name__}"
                f"\n\t text={self.text.name}"
                f"\n\t label={self.label.question.name}"
                f"\n\t multi_label={self.__multi_label__}"
                f"\n\t all_labels={self.__all_labels__}"
            )

    @requires_dependencies("datasets>1.17.0")
    def _prepare_for_training_with_transformers(
        self, data: List[dict], train_size: float, seed: int, framework: Union[str, Framework]
    ) -> Union["datasets.Dataset", "datasets.DatasetDict"]:
        self.test_framework_support(framework)
        import datasets

        multi_label = self.__multi_label__

        datasets_dict = {"id": [], "text": [], "label": []}
        for index, entry in enumerate(data):
            if any([entry.get("label") is None, entry.get("text") is None]):
                warnings.warn(f"Skipping entry {entry} because it has no label or text.")
                continue
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
            require_dependencies("scikit-learn")
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

    @requires_dependencies("spacy")
    def _prepare_for_training_with_spacy(
        self, data: List[dict], train_size: float, seed: int, lang: str
    ) -> Union["spacy.token.DocBin", Tuple["spacy.token.DocBin", "spacy.token.DocBin"]]:
        from spacy.tokens import DocBin

        all_labels = self.__all_labels__

        def _prepare(data):
            db = DocBin(store_user_data=True)
            # Creating the DocBin object as in https://spacy.io/usage/training#training-data
            for entry in data:
                if any([entry.get("label") is None, entry.get("text") is None]):
                    warnings.warn(f"Skipping entry {entry} because it has no label or text.")
                    continue
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
                if any([entry.get("label") is None, entry.get("text") is None]):
                    warnings.warn(f"Skipping entry {entry} because it has no label or text.")
                    continue
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


class TrainingTaskForSFTFormat(BaseModel):
    """
    Union[str, List[str]]
    """

    format: Union[str, List[str]]


class TrainingTaskForSFT(BaseModel, TrainingData):
    """Training data for supervised finetuning

    Args:
        formatting_func: A formatting function converting a dictionary of records into zero,
            one or more text strings.

    Examples:
        >>> from argilla.feedback import TrainingTaskForSFT
        >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
        >>> def formatting_func(sample: Dict[str, Any]):
        ...     annotations = sample["good]
        ...     if annotations and annotations[0]["value"] == "Bad":
        ...         return
        ...     yield template.format(prompt=sample["prompt"][0]["value"], response=sample["response"][0]["value"])
        >>> task = TrainingTaskForSFT(formatting_func=formatting_func)
        >>> dataset.prepare_for_training(framework="...", task=task)

    """

    _formatting_func_return_types = TrainingTaskForSFTFormat
    formatting_func: Callable[[Dict[str, Any]], Union[None, str, List[str], Iterator[str]]]

    def _format_data(self, dataset: "FeedbackDataset") -> List[Dict[str, str]]:
        formatted_texts = set()
        for sample in dataset.format_as("datasets"):
            if texts := self.formatting_func(sample):
                if texts is None:
                    continue

                self._test_output_formatting_func(texts)

                if isinstance(texts, str):
                    texts = {texts}

                formatted_texts |= set(texts)
        return [{"text": text} for text in formatted_texts]

    @property
    def supported_frameworks(self) -> List[Framework]:
        names = ["trl"]
        return [Framework(name) for name in names]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}\n\t formatting_func={self.formatting_func}"

    @requires_dependencies("datasets>1.17.0")
    def _prepare_for_training_with_trl(
        self, data: List[dict], train_size: float, seed: int
    ) -> Union["datasets.Dataset", "datasets.DatasetDict"]:
        import datasets

        datasets_dict = {"id": [], "text": []}
        for index, sample in enumerate(data):
            if any([sample.get("text") is None]):
                warnings.warn(f"Skipping entry {sample} because it has no text.")
                continue
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


class TrainingTaskForRMFormat(BaseModel):
    """
    Union[
        Tuple[str, str], Tuple[str, List[str]],
        List[Tuple[str, str]], List[Tuple[str, List[str]]]
    ]
    """

    format: Union[Tuple[str, str], Tuple[str, List[str]], List[Tuple[str, str]], List[Tuple[str, List[str]]]]


class TrainingTaskForRM(BaseModel, TrainingData):
    """Training data for reward modeling

    Args:
        formatting_func: A formatting function converting a dictionary of records into zero,
            one or more chosen-rejected text tuples.

    Examples:
        >>> from argilla.feedback import TrainingTaskForRM
        >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
        >>> def formatting_func(sample: Dict[str, Any]):
        ...     values = [annotation["value"] for annotation in sample["ranking"]]
        ...     if values.count("1") >= values.count("2"):
        ...         chosen = sample["response-1"]
        ...         rejected = sample["response-2"]
        ...     else:
        ...         chosen = sample["response-2"]
        ...         rejected = sample["response-1"]
        ...     yield chosen, rejected
        >>> task = TrainingTaskForRM(formatting_func=formatting_func)
        >>> dataset.prepare_for_training(framework="...", task=task)
    """

    _formatting_func_return_types = TrainingTaskForRMFormat
    formatting_func: Callable[
        [Dict[str, Any]], Union[None, Tuple[str, str], List[Tuple[str, str]], Iterator[Tuple[str, str]]]
    ]

    def _format_data(self, dataset: "FeedbackDataset") -> List[Dict[str, str]]:
        output = set()
        for sample in dataset.format_as("datasets"):
            chosen_rejecteds = self.formatting_func(sample)
            if chosen_rejecteds is None:
                continue

            self._test_output_formatting_func(chosen_rejecteds)

            if isinstance(chosen_rejecteds, tuple):
                chosen_rejecteds = {chosen_rejecteds}

            output |= set(chosen_rejecteds)
        return [{"chosen": chosen, "rejected": rejected} for chosen, rejected in output]

    @property
    def supported_frameworks(self) -> List[Framework]:
        names = ["trl"]
        return [Framework(name) for name in names]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}\n\t formatting_func={self.formatting_func}"

    @requires_dependencies("datasets>1.17.0")
    def _prepare_for_training_with_trl(
        self, data: List[dict], train_size: float, seed: int
    ) -> Union["datasets.Dataset", "datasets.DatasetDict"]:
        import datasets

        datasets_dict = {"chosen": [], "rejected": []}
        for sample in data:
            if any([sample.get("chosen") is None, sample.get("rejected") is None]):
                warnings.warn(f"Skipping entry {sample} because it has no chosen or rejected.")
                continue
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


class TrainingTaskForPPOFormat(BaseModel):
    """
    Union[str, List[str]]
    """

    format: Union[str, List[str]]


class TrainingTaskForPPO(BaseModel, TrainingData):
    """Training data for proximal policy optimization

    Args:
        text: The TextField to use for training.

    Examples:
        >>> from argilla.feedback import TrainingTaskForPPO
        >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
        >>> task = TrainingTaskForPPO(text=dataset.fields[0],)
        >>> dataset.prepare_for_training(framework="...", task=task)
    """

    _formatting_func_return_types = TrainingTaskForPPOFormat
    formatting_func: Callable[[Dict[str, Any]], Union[None, str, Iterator[str]]]

    def _format_data(self, dataset: "FeedbackDataset") -> List[Dict[str, str]]:
        formatted_texts = set()
        for sample in dataset.format_as("datasets"):
            if texts := self.formatting_func(sample):
                if texts is None:
                    continue

                self._test_output_formatting_func(texts)

                if isinstance(texts, str):
                    texts = {texts}
                formatted_texts |= set(texts)
        return [{"query": text} for text in formatted_texts]

    @property
    def supported_frameworks(self) -> List[Framework]:
        names = ["trl"]
        return [Framework(name) for name in names]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}\n\t formatting_func={self.formatting_func}"

    @requires_dependencies("datasets>1.17.0")
    def _prepare_for_training_with_trl(
        self, data: List[dict], train_size: float, seed: int
    ) -> Union["datasets.Dataset", "datasets.DatasetDict"]:
        import datasets

        datasets_dict = {"id": [], "query": []}
        for index, entry in enumerate(data):
            if entry.get("query") is None:
                warnings.warn(f"Skipping entry {entry} because it has no query.")
                continue
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


class TrainingTaskForDPOFormat(BaseModel):
    """
    Union[Tuple[str, str, str], List[Tuple[str, str, str]]]
    """

    format: Union[Tuple[str, str, str], List[Tuple[str, str, str]]]


class TrainingTaskForDPO(BaseModel, TrainingData):
    """Training data for direct preference optimization

    Args:
        formatting_func: A formatting function converting a dictionary of records into zero,
            one or more prompt-chosen-rejected text tuples.

    Examples:
        >>> from argilla.feedback import TrainingTaskForDPO
        >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
        >>> def formatting_func(sample: Dict[str, Any]):
        ...     values = [annotation["value"] for annotation in sample["ranking"]]
        ...     if values.count("1") >= values.count("2"):
        ...         chosen = sample["response-1"]
        ...         rejected = sample["response-2"]
        ...     else:
        ...         chosen = sample["response-2"]
        ...         rejected = sample["response-1"]
        ...     yield sample["prompt"], chosen, rejected
        >>> task = TrainingTaskForDPO(formatting_func=formatting_func)
        >>> dataset.prepare_for_training(framework="...", task=task)
    """

    _formatting_func_return_types = TrainingTaskForDPOFormat
    formatting_func: Callable[[Dict[str, Any]], Union[None, Tuple[str, str, str], Iterator[Tuple[str, str, str]]]]

    def _format_data(self, dataset: "FeedbackDataset") -> List[Dict[str, str]]:
        output = set()
        for sample in dataset.format_as("datasets"):
            prompt_chosen_rejecteds = self.formatting_func(sample)
            if prompt_chosen_rejecteds is None:
                continue

            self._test_output_formatting_func(prompt_chosen_rejecteds)

            if isinstance(prompt_chosen_rejecteds, tuple):
                prompt_chosen_rejecteds = {prompt_chosen_rejecteds}

            output |= set(prompt_chosen_rejecteds)
        return [{"prompt": prompt, "chosen": chosen, "rejected": rejected} for prompt, chosen, rejected in output]

    @property
    def supported_frameworks(self) -> List[Framework]:
        names = ["trl"]
        return [Framework(name) for name in names]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}\n\t formatting_func={self.formatting_func}"

    @requires_dependencies("datasets>1.17.0")
    def _prepare_for_training_with_trl(
        self, data: List[dict], train_size: float, seed: int
    ) -> Union["datasets.Dataset", "datasets.DatasetDict"]:
        import datasets

        datasets_dict = {"prompt": [], "chosen": [], "rejected": []}
        for sample in data:
            if any([sample.get("prompt") is None, sample.get("chosen") is None, sample.get("rejected") is None]):
                warnings.warn(f"Skipping entry {sample} because it has no prompt, chosen or rejected.")
                continue
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


class TrainingTaskForQuestionAnsweringFormat(BaseModel):
    """
    Union[Tuple[str, str, str], List[Tuple[str, str, str]]]
    """

    format: Union[Tuple[str, str, str], List[Tuple[str, str, str]]]


class TrainingTaskForQuestionAnswering(BaseModel, TrainingData):
    """
    Training data for question answering

    Args:
        formatting_func: A formatting function converting a dictionary of records into zero,
            one or more question-context-answer text tuples.
        question: The TextField to use for training.
        context: The TextField to use for training.
        answer: The TextQuestion to use for training.

    Examples:
        >>> # with defaults
        >>> from argilla.feedback import TrainingTaskForQuestionAnswering
        >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
        >>> task = TrainingTaskForQuestionAnswering(
        ...     question=dataset.field_by_name("question"),
        ...     context=dataset.field_by_name("context"),
        ...     answer=dataset.question_by_name("answer"),
        ... )
        >>> dataset.prepare_for_training(framework="...", task=task)
        >>> # with formatting_func
        >>> from argilla.feedback import TrainingTaskForQuestionAnswering
        >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
        >>> def formatting_func(sample: Dict[str, Any]):
        ...     question = sample["question"]
        ...     context = sample["context"]
        ...     for answer in sample["answer"]:
        ...         if not all([question, context, answer["value"]]):
        ...             continue
        ...         yield question, context, answer["value"]
        >>> task = TrainingTaskForQuestionAnswering(formatting_func=formatting_func)
        >>> dataset.prepare_for_training(framework="...", task=task)
    """

    _formatting_func_return_types = TrainingTaskForQuestionAnsweringFormat
    formatting_func: Optional[Callable[[Dict[str, Any]], Union[None, str, Iterator[str]]]] = None
    question: Optional[TextField] = None
    context: Optional[TextField] = None
    answer: Optional[TextQuestion] = None

    def _format_data(self, dataset: "FeedbackDataset") -> List[Dict[str, str]]:
        if self.formatting_func is not None:
            output = set()
            for sample in dataset.format_as("datasets"):
                question_context_answer = self.formatting_func(sample)
                if question_context_answer is None:
                    continue

                self._test_output_formatting_func(question_context_answer)

                if isinstance(question_context_answer, tuple):
                    question_context_answer = {question_context_answer}

                output |= set(question_context_answer)
            return [
                {"question": question, "context": context, "answer": answer} for question, context, answer in output
            ]
        else:
            return super()._format_data(dataset)

    @property
    def supported_frameworks(self) -> List[Framework]:
        names = ["transformers"]
        return [Framework(name) for name in names]

    def __repr__(self) -> str:
        if self.formatting_func is not None:
            return f"{self.__class__.__name__}\n\t formatting_func={self.formatting_func}"
        else:
            return (
                f"{self.__class__.__name__}"
                f"\n\t question={self.question.name}"
                f"\n\t context={self.context.name}"
                f"\n\t answer={self.answer.name}"
            )

    @requires_dependencies("transformers")
    def _prepare_for_training_with_transformers(
        self, data: List[dict], train_size: float, seed: int, framework=None
    ) -> Union["datasets.Dataset", "datasets.DatasetDict"]:
        import datasets

        datasets_dict = {
            "question": [],
            "context": [],
            "answer": [],
        }
        for entry in data:
            if any([entry.get("question") is None, entry.get("context") is None, entry.get("answer") is None]):
                warnings.warn(f"Skipping entry {entry} because it has no question, context or answer.")
                continue
            if entry.get("answer") not in entry.get("context"):
                warnings.warn(f"Skipping entry {entry} because answer is not in context.")
                continue
            # get index of answer in context
            answer_start = entry["context"].index(entry["answer"])
            datasets_dict["question"].append(entry["question"])
            datasets_dict["context"].append(entry["context"])
            datasets_dict["answer"].append({"answer_start": [answer_start], "text": [entry["answer"]]})

        feature_dict = {
            "question": datasets.Value("string"),
            "context": datasets.Value("string"),
            "answer": datasets.Sequence(
                feature={
                    "text": datasets.Value(dtype="string", id=None),
                    "answer_start": datasets.Value(dtype="int32", id=None),
                },
                length=-1,
                id=None,
            ),
        }

        ds = datasets.Dataset.from_dict(datasets_dict, features=datasets.Features(feature_dict))

        if train_size != 1:
            ds = ds.train_test_split(train_size=train_size, test_size=1 - train_size, seed=seed)

        return ds


class TrainingTaskForChatCompletionFormat(BaseModel):
    """
    Union[Tuple[str, str, str, str], List[Tuple[str, str, str, str]]]
    """

    format: Union[Tuple[str, str, str, str], List[Tuple[str, str, str, str]]]


class TrainingTaskForChatCompletion(BaseModel, TrainingData):
    """Training data for chat completion

    Args:
        formatting_func: A formatting function converting a dictionary of records into zero,
            one or more chat-turn-role-content text tuples.

    Examples:
        >>> from argilla.feedback import TrainingTaskForChatCompletion
        >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
        >>> def formatting_func(sample: Dict[str, Any]):
        ...     from uuid import uuid4
        ...     chat_id = str(uuid4())
        ...     if sample["response"]:
        ...         chat = str(uuid4())
        ...         user_message = sample["prompt"][0]["value"]
        ...         system_message = sample["response"][0]["value"]
        ...         yield [(chat, "0", "user", user_message), (chat, "1", "assistant", system_message)]
        >>> task = TrainingTaskForChatCompletion(formatting_func=formatting_func)
        >>> dataset.prepare_for_training(framework="...", task=task)
    """

    _formatting_func_return_types = TrainingTaskForChatCompletionFormat
    formatting_func: Callable[[Dict[str, Any]], Union[None, Dict[str, str], Iterator[Dict[str, str]]]]

    def _format_data(self, dataset: "FeedbackDataset") -> List[Dict[str, str]]:
        output = set()
        for sample in dataset.format_as("datasets"):
            chat_turn_role_content = self.formatting_func(sample)
            if chat_turn_role_content is None:
                continue

            self._test_output_formatting_func(chat_turn_role_content)

            if isinstance(chat_turn_role_content, tuple):
                chat_turn_role_content = {chat_turn_role_content}

            output |= set(chat_turn_role_content)
        return [{"chat": chat, "turn": turn, "role": role, "content": content} for chat, turn, role, content in output]

    @property
    def supported_frameworks(self) -> List[Framework]:
        names = ["openai"]
        return [Framework(name) for name in names]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}\n\t formatting_func={self.formatting_func}"

    @requires_dependencies("openai>=0.27.10")
    def _prepare_for_training_with_openai(self, data: List[dict], train_size: float, seed: int) -> List[dict]:
        import datasets

        def _dict_to_format(ds: datasets.Dataset) -> List[Dict[str, List[Dict[str, str]]]]:
            """OpenAI expects a list of chats, each chat is a dict with a list of messages.
            Each message {"role": "user", "content": "Hello!"}
            """
            chats = []
            df = ds.to_pandas()
            for chat_id in df["chat"].unique():
                df_filter = df[df["chat"] == chat_id]
                new_chat = {"messages": []}
                for entry in df_filter.to_dict(orient="records"):
                    new_chat["messages"].append({"role": entry["role"], "content": entry["content"]})
                chats.append(new_chat)

            return chats

        datasets_dict = {"chat": [], "turn": [], "role": [], "content": []}
        for entry in data:
            if any([entry.get("prompt") is None, entry.get("response") is None]):
                warnings.warn(f"Skipping entry {entry} because it has no prompt or response.")
                continue
            if entry["role"] not in ["system", "user", "assistant"]:
                raise ValueError("Role must be one of 'system', 'user', 'assistant'")
            datasets_dict["chat"].append(entry["chat"])
            datasets_dict["turn"].append(entry["turn"])
            datasets_dict["role"].append(entry["role"])
            datasets_dict["content"].append(entry["content"])

        feature_dict = {
            "chat": datasets.Value("string"),
            "turn": datasets.Value("string"),
            "role": datasets.Value("string"),
            "content": datasets.Value("string"),
        }

        ds = datasets.Dataset.from_dict(datasets_dict, features=datasets.Features(feature_dict))
        ds = ds.sort(column_names=["chat", "turn"])

        if train_size != 1:
            ds = ds.train_test_split(
                train_size=train_size, test_size=1 - train_size, seed=seed, stratify_by_column="chat"
            )
            return _dict_to_format(ds["train"]), _dict_to_format(ds["test"])
        else:
            return _dict_to_format(ds)


class TrainingTaskForSentenceSimilarityFormat(BaseModel):
    r"""
    Union[
        Dict[str, Union[float, int]],  # case 1 with with two string elements and one int/float, case 3 with one or three strings and one int/float.
        Dict[str, str],                # case 2 with two elements, case 4 with three elements
    ]

    For a reference of the different cases take a look at:
    https://huggingface.co/blog/how-to-train-sentence-transformers#how-to-prepare-your-dataset-for-training-a-sentence-transformers-model
    """

    format: Union[
        Dict[str, Union[float, int]], Dict[str, str], List[Dict[str, Union[float, int]]], List[Dict[str, str]]
    ]


class TrainingTaskForSentenceSimilarity(BaseModel, TrainingData):
    """Training data for sentence similarity.

    Args:
        formatting_func: A formatting function converting a dictionary of records into
            a dictionary of a pair of sentences, a pair of sentences and a label,
            a sentence and a label or a triplet of sentences.

    Examples:
        Example for argilla/emotion dataset:
        >>> from argilla.feedback import TrainingTaskForSentenceSimilarity
        >>> dataset = rg.FeedbackDataset.from_argilla(name="argilla/emotion")
        >>> def formatting_func(sample: Dict[str, Any]):
        ...     return {"sentence": sample["text"], "label": int(sample["label"][0]["value"])}
        >>> task = TrainingTaskForSentenceSimilarity(formatting_func=formatting_func)
        >>> dataset.prepare_for_training(framework="...", task=task)
    """

    _formatting_func_return_types = TrainingTaskForSentenceSimilarityFormat
    formatting_func: Callable[
        [Dict[str, Any]],
        Union[
            None, Dict[str, Union[float, int]], Dict[str, str], List[Dict[str, Union[float, int]]], List[Dict[str, str]]
        ],
    ] = None
    texts: Optional[List[TextField]] = None
    label: Optional[Union[LabelQuestionUnification, RankingQuestionUnification]] = None

    @property
    def supported_frameworks(self):
        names = ["sentence-transformers"]
        return [Framework(name) for name in names]

    @property
    def __all_labels__(self):
        if self.label:
            return self.label.question.__all_labels__

    @property
    def __label2id__(self):
        if self.label:
            return self.label.question.__label2id__

    @property
    def __id2label__(self):
        if self.label:
            return self.label.question.__id2label__

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"\n\t texts={self.texts.name if self.texts else None}"
            f"\n\t label={self.label.question.name if self.label else None}"
            f"\n\t all_labels={self.__all_labels__}"
            f"\n\t formatting_funct={self.formatting_func}"
        )

    def _format_data(self, dataset: "FeedbackDataset") -> List[Dict[str, Any]]:
        if self.formatting_func:
            outputs = []
            for sample in dataset.format_as("datasets"):
                output = self.formatting_func(sample)
                if output is None:
                    continue

                self._test_output_formatting_func(output)

                outputs.append(output)

            if "label" in outputs[0]:
                _all_labels = set()
                for sample in outputs:
                    if isinstance(sample, (list, tuple, set)):
                        for response in sample:
                            _all_labels.add(response["label"])
                    else:
                        _all_labels.add(sample["label"])

                self.label = LabelQuestionUnification(
                    question=LabelQuestion(name="custom_func", labels=list(_all_labels))
                )

            return outputs

        else:
            formatted_data = super()._format_data(dataset)
            # NOTE: Maybe this post processing of the formatted data can be simplified
            # or directly done in super()._format_data(dataset).
            new_keys = {field.name: f"sentence-{i}" for i, field in enumerate(self.texts, start=1)}
            if self.label:
                new_keys.update({self.label.question.name: "label"})

            outputs = []
            for example in formatted_data:
                record = {}
                for k, v in new_keys.items():
                    value = example[k]
                    if v == "label":
                        # At this point the label must be either an int or a float, determine which one is it.
                        if value.lstrip("-").isdigit():
                            value = int(value)
                        else:
                            value = float(value)
                        if isinstance(self.label, RankingQuestionUnification):
                            max_value = max([float(x) for x in self.label.question.__all_labels__])
                            value = (value / 100) * float(max_value)
                    record[v] = value
                outputs.append(record)

            return outputs

    def unify_responses(self, responses: List[FeedbackRecord]):
        self.label.strategy.unify_responses(responses=responses, field=self.label.question)

    @requires_dependencies("scikit-learn")
    def _train_test_split(
        self, data: List[dict], train_size: float, seed: int, stratify=None
    ) -> Tuple[List[dict], List[dict]]:
        from sklearn.model_selection import train_test_split

        return train_test_split(data, train_size=train_size, shuffle=True, random_state=seed, stratify=stratify)

    @requires_dependencies("sentence-transformers")
    def _prepare_for_training_with_sentence_transformers(
        self, data: List[dict], train_size: float, seed: int
    ) -> Union["InputExample", Tuple["InputExample", "InputExample"]]:
        from sentence_transformers import InputExample

        if not len(data) > 0:
            raise ValueError("The dataset must contain at least one sample to be able to train.")

        # Use the first sample to decide what type of dataset to generate:
        sample_keys = set(data[0].keys())
        if sample_keys == {"label", "sentence-1", "sentence-2"}:

            def dataset_fields(sample):
                return {"texts": [sample["sentence-1"], sample["sentence-2"]], "label": sample["label"]}

        elif sample_keys == sample_keys == {"label", "sentence-1", "sentence-2", "sentence-3"}:

            def dataset_fields(sample):
                return {
                    "texts": [sample["sentence-1"], sample["sentence-2"], sample["sentence-3"]],
                    "label": sample["label"],
                }

        elif sample_keys == {"sentence-1", "sentence-2"}:

            def dataset_fields(sample):
                return {"texts": [sample["sentence-1"], sample["sentence-2"]]}

        elif sample_keys == {"sentence-1", "sentence-2", "sentence-3"}:

            def dataset_fields(sample):
                return {"texts": [sample["sentence-1"], sample["sentence-2"], sample["sentence-3"]]}

        elif sample_keys == {"label", "sentence"}:
            raise ValueError(
                "Datasets containing a `sentence` and a `label` should be transformed "
                "to contain triplets of `sentence-1`, `sentence-2`, `sentence-3` and `label`."
                r"An example can be seen at: https://github.com/UKPLab/sentence-transformers/blob/master/examples/training/other/training_batch_hard_trec.py"
            )
        else:
            raise ValueError(
                "Labeled datasets must contain a pair of `sentence-1` and "
                "`sentence-2` or triplets `sentence-1`, `sentence-2`, `sentence-3` "
                "and an optional `label`."
            )

        train_samples = []
        for sample in data:
            if isinstance(sample, list):
                for record in sample:
                    train_samples.append(InputExample(**dataset_fields(record)))
            else:
                train_samples.append(InputExample(**dataset_fields(sample)))

        if train_size != 1:
            stratify = None
            if (label := train_samples[0].label) and isinstance(label, int):
                stratify = [example.label for example in train_samples]

            train_data, test_data = self._train_test_split(train_samples, train_size, seed, stratify=stratify)
            return train_data, test_data
        else:
            return train_samples


TrainingTaskTypes = Union[
    TrainingTaskForTextClassification,
    TrainingTaskForSFT,
    TrainingTaskForRM,
    TrainingTaskForPPO,
    TrainingTaskForDPO,
    TrainingTaskForChatCompletion,
    TrainingTaskForSentenceSimilarity,
]

# Helper map fr the creation of the model cards.
TRAINING_TASK_MAPPING = {
    TrainingTaskForTextClassification: "for_text_classification",
    TrainingTaskForSFT: "for_supervised_fine_tuning",
    TrainingTaskForRM: "for_reward_modeling",
    TrainingTaskForPPO: "for_proximal_policy_optimization",
    TrainingTaskForDPO: "for_direct_preference_optimization",
    TrainingTaskForChatCompletion: "for_chat_completion",
    TrainingTaskForQuestionAnswering: "for_question_answering",
    TrainingTaskForSentenceSimilarity: "for_sentence_similarity",
}


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
    def for_reward_modeling(cls, *args, **kwargs) -> TrainingTaskForRM:
        cls.warn()
        return super().for_reward_modeling(*args, **kwargs)

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
