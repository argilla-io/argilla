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

import inspect
import logging
import textwrap
import typing
import warnings
from abc import ABC
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterator, List, Optional, Tuple, Union

import pandas as pd
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
from argilla.client.feedback.training.schemas.defaults import (
    QuestionAnsweringDefaults,
    SentenceSimilarityDefaults,
    TextClassificationDefaults,
)
from argilla.client.feedback.training.schemas.return_types import (
    ChatCompletionReturnTypes,
    DPOReturnTypes,
    PPOReturnTypes,
    QuestionAnsweringReturnTypes,
    RMReturnTypes,
    SentenceSimilarityReturnTypes,
    SFTReturnTypes,
    TextClassificationReturnTypes,
)
from argilla.client.feedback.unification import (
    LabelQuestionUnification,
    MultiLabelQuestionUnification,
    RankingQuestionUnification,
    RatingQuestionUnification,
)
from argilla.client.models import Framework
from argilla.pydantic_v1 import BaseModel
from argilla.utils.dependency import require_dependencies, requires_dependencies

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    import datasets
    import spacy
    from argilla.client.feedback.dataset import FeedbackDataset
    from sentence_transformers import InputExample


class TrainingData(ABC):
    formatting_func: Optional[BaseModel] = None
    defaults: Optional[BaseModel] = None
    _formatting_func_return_types = None
    _supported_frameworks_names: list = []

    @property
    def formatting_func_return_types(self) -> BaseModel:
        return self._formatting_func_return_types

    @property
    def supported_frameworks(self) -> List[Framework]:
        return [Framework(name) for name in self._supported_frameworks_names]

    def __repr__(self) -> str:
        def get_func_repr(func: Callable) -> str:
            func_source = inspect.getsource(func)
            return func_source

        return textwrap.dedent(
            f"{self.__class__.__name__}\nformatting_func:\n{get_func_repr(self.formatting_func)}"
            if self.formatting_func
            else f"\ndefaults:\n{self.defaults})"
        )

    def test_framework_support(self, framework: Union[str, Framework]):
        """
        Test if the framework is supported by this task.
        """
        if isinstance(framework, str):
            framework = Framework(framework)
        if framework not in self.supported_frameworks:
            raise NotImplementedError(f"Framework {framework} is not supported for this {self.__class__}.")

    def _execute_formatting_func(self, dataset: "FeedbackDataset") -> Any:
        """
        Execute the formatting function on the dataset and return the output.
        """

        def test_none_sample(sample: Any) -> list:
            """
            Check for None values in the sample. If there are None values, return an empty list.
            """

            if sample is None:
                return []
            if isinstance(sample, (list, typing.Generator)):
                values = [test_none_sample(entry) for entry in sample]
                values = [value for value in values if value]
                values = [value[0] for value in values]
                return values
            else:
                return [sample]

        def test_output_formatting_func(sample: Any) -> list:
            """
            Test if the formatting function returns the expected format.
            """
            try:
                if isinstance(sample, list):
                    return [self._formatting_func_return_types(format=entry).format for entry in sample]
                else:
                    return [self._formatting_func_return_types(format=sample).format]
            except Exception:
                raise ValueError(
                    f"formatting_func must return {self._formatting_func_return_types.__annotations__['format']}, not {type(sample)}"
                )

        formatted_output = []
        for sample in dataset.format_as("datasets"):
            formatted_sample = self.formatting_func(sample)
            formatted_sample = test_none_sample(formatted_sample)
            if not formatted_sample:
                continue
            formatted_output += test_output_formatting_func(formatted_sample)
        return formatted_output

    def _format_data(self, dataset: "FeedbackDataset") -> List[Dict[str, Any]]:
        formatted_data = []
        explode_columns = set()
        for record in dataset.records:
            data = {}
            for pydantic_field in self.defaults:
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
        records = df.to_dict(orient="records")

        # Validate record format
        if isinstance(self.defaults, SentenceSimilarityDefaults):
            validated_records = []
            for rec in records:
                try:
                    self._formatting_func_return_types(format=rec)
                    validated_records.append(rec)
                except Exception:
                    continue
        elif isinstance(self.defaults, (QuestionAnsweringDefaults, TextClassificationDefaults)):
            required_keys = list(self.defaults.__fields__.keys())
            validated_records = [item for item in records if all(key in item for key in required_keys)]
        else:
            raise NotImplementedError(
                f"Defaults {self.defaults} is not supported. Choose from: {[e.value for e in Framework]}"
            )
        if not validated_records:
            raise ValueError(
                f"Your dataset does not contain any records with required responses for {required_keys}. "
                "Try different `filter_by`and `max_records` params or a annotate some more records."
            )
        return records

    def _train_test_split(self, data: List[dict], train_size: float, seed: int) -> Tuple[List[dict], List[dict]]:
        """Overwritten by subclasses"""

    def prepare_for_training(
        self, framework: Framework, dataset: "FeedbackDataset", train_size: float, seed: int, lang: str
    ) -> Any:
        data = self._format_data(dataset)
        if framework in [
            Framework.TRANSFORMERS,
            Framework.SETFIT,
            Framework.SPAN_MARKER,
            Framework.PEFT,
        ]:
            return self._prepare_for_training_with_transformers(
                data=data, train_size=train_size, seed=seed, framework=framework
            )
        elif framework in [Framework.SPACY, Framework.SPACY_TRANSFORMERS]:
            require_dependencies("spacy")
            import spacy

            if lang is None:
                _LOGGER.warning("spaCy `lang` is not provided. Using `en`(English) as default language.")
                lang = spacy.blank("en")
            elif lang.isinstance(str):
                if len(lang) == 2:
                    lang = spacy.blank(lang)
                else:
                    lang = spacy.load(lang)
            return self._prepare_for_training_with_spacy(data=data, train_size=train_size, seed=seed, lang=lang)
        elif framework is Framework.SPARK_NLP:
            return self._prepare_for_training_with_spark_nlp(data=data, train_size=train_size, seed=seed)
        elif framework is Framework.OPENAI:
            return self._prepare_for_training_with_openai(data=data, train_size=train_size, seed=seed)
        elif framework is Framework.TRL:
            return self._prepare_for_training_with_trl(data=data, train_size=train_size, seed=seed)

        elif framework is Framework.SENTENCE_TRANSFORMERS:
            return self._prepare_for_training_with_sentence_transformers(data=data, train_size=train_size, seed=seed)
        else:
            raise NotImplementedError(
                f"Framework {framework} is not supported. Choose from: {[e.value for e in Framework]}"
            )

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
            >>> from argilla import LabelQuestion, TrainingTask
            >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
            >>> task = TrainingTask.for_text_classification(
            ...     text=dataset.field_by_name("text"),
            ...     label=dataset.question_by_name("label")
            ... )
            >>> dataset.prepare_for_training(framework="...", task=task)
            >>> # with formatting_func
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
            defaults = TextClassificationDefaults(text=text, label=label)
            return TrainingTaskForTextClassification(defaults=defaults)

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
            >>> from argilla import TrainingTaskForChatCompletion
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
            >>> from argilla import TrainingTaskForQuestionAnswering
            >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
            >>> task = TrainingTaskForQuestionAnswering(
            ...     question=dataset.field_by_name("question"),
            ...     context=dataset.field_by_name("context"),
            ...     answer=dataset.question_by_name("answer"),
            ... )
            >>> dataset.prepare_for_training(framework="...", task=task)
            >>> # with formatting_func
            >>> from argilla import TrainingTaskForQuestionAnswering
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
            defaults = QuestionAnsweringDefaults(question=question, context=context, answer=answer)
            return TrainingTaskForQuestionAnswering(defaults=defaults)

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
        label_strategy: Optional[Union[LabelQuestionUnification, RatingQuestionUnification]] = None,
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
            >>> from argilla import LabelQuestion, TrainingTask
            >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
            >>> task = TrainingTask.for_text_classification(
            ...     texts=[dataset.field_by_name("premise"), dataset.field_by_name("hypothesis")],
            ...     label=dataset.question_by_name("label")
            ... )
            >>> dataset.prepare_for_training(framework="...", task=task)

            >>> from argilla import LabelQuestion, TrainingTask
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
                defaults = SentenceSimilarityDefaults(texts=texts)
                return TrainingTaskForSentenceSimilarity(defaults=defaults)

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
                elif isinstance(label, RatingQuestion):
                    label = RatingQuestionUnification(**unification_kwargs)
                else:
                    raise ValueError(f"Label type {type(label)} is not supported.")
            defaults = SentenceSimilarityDefaults(texts=texts, label=label)
            return TrainingTaskForSentenceSimilarity(defaults=defaults)


class TrainingTaskForTextClassification(BaseModel, TrainingData):
    """Training data for text classification

    Args:
        formatting_func: A formatting function returning the text to classify. Either a formatting function or
            the text and label parameters are provided. Defaults to None.
        text: The text field to take as the text to classify.
        label: The question denoting the label of the text to classify.

        Examples:
            >>> # with defaults
            >>> from argilla import LabelQuestion, TrainingTask
            >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
            >>> task = TrainingTask.for_text_classification(
            ...     text=dataset.field_by_name("text"),
            ...     label=dataset.question_by_name("label")
            ... )
            >>> dataset.prepare_for_training(framework="...", task=task)
            >>> # with formatting_func
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
            ...         yield text, label
            >>> task = TrainingTask.for_text_classification(formatting_func=formatting_func)
            >>> dataset.prepare_for_training(framework="...", task=task)
    """

    formatting_func: Optional[Callable[[Dict[str, Any]], Union[None, str, List[str], Iterator[str]]]] = None
    defaults: Optional[TextClassificationDefaults] = TextClassificationDefaults()
    _formatting_func_return_types = TextClassificationReturnTypes
    _supported_frameworks_names = [
        "transformers",
        "spacy",
        "openai",
        "setfit",
        "peft",
        "spark-nlp",
        "spacy-transformers",
    ]

    @property
    def __multi_label__(self) -> bool:
        return isinstance(self.label.question, MultiLabelQuestion)

    @property
    def __all_labels__(self) -> Union[Any, List[str]]:
        return self.label.question.__all_labels__

    @property
    def __label2id__(self) -> Union[Any, Dict[str, int]]:
        return self.label.question.__label2id__

    @property
    def __id2label__(self) -> Dict[int, str]:
        return self.label.question.__id2label__

    @property
    def label(
        self,
    ) -> Optional[
        Union[
            RatingQuestion,
            LabelQuestion,
            MultiLabelQuestion,
            RankingQuestion,
            LabelQuestionUnification,
            MultiLabelQuestionUnification,
            RankingQuestionUnification,
            RatingQuestionUnification,
        ]
    ]:
        return self.defaults.label

    @property
    def text(self) -> Optional[TextField]:
        return self.defaults.text

    def _format_data(self, dataset: "FeedbackDataset") -> List[Dict[str, Any]]:
        if self.formatting_func is not None:
            output = self._execute_formatting_func(dataset)

            data = []
            _all_labels = set()
            for text_label in output:
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
                self.defaults.label = MultiLabelQuestionUnification(
                    question=MultiLabelQuestion(name="custom_func", labels=list(_all_labels))
                )
            else:
                self.defaults.label = LabelQuestionUnification(
                    question=LabelQuestion(name="custom_func", labels=list(_all_labels))
                )
            return data
        else:
            return super()._format_data(dataset)

    def compute_unified_responses(self, responses: List[FeedbackRecord]):
        self.defaults.label.strategy.compute_unified_responses(responses=responses, field=self.defaults.label.question)

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

    @requires_dependencies("datasets>1.17.0")
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
        formatting_func: A formatting function converting a dictionary of records into zero,
            one or more text strings.

    Examples:
        >>> from argilla import TrainingTaskForSFT
        >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
        >>> def formatting_func(sample: Dict[str, Any]):
        ...     annotations = sample["good]
        ...     if annotations and annotations[0]["value"] == "Bad":
        ...         return
        ...     yield template.format(prompt=sample["prompt"][0]["value"], response=sample["response"][0]["value"])
        >>> task = TrainingTaskForSFT(formatting_func=formatting_func)
        >>> dataset.prepare_for_training(framework="...", task=task)

    """

    formatting_func: Callable[[Dict[str, Any]], Union[None, str, List[str], Iterator[str]]]
    _formatting_func_return_types = SFTReturnTypes
    _supported_frameworks_names = ["trl"]

    def _format_data(self, dataset: "FeedbackDataset") -> List[Dict[str, str]]:
        formatted_output = self._execute_formatting_func(dataset)
        return [{"text": text} for text in formatted_output]

    @requires_dependencies("datasets>1.17.0")
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
    """Training data for reward modeling

    Args:
        formatting_func: A formatting function converting a dictionary of records into zero,
            one or more chosen-rejected text tuples.

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
        ...     yield chosen, rejected
        >>> task = TrainingTaskForRM(formatting_func=formatting_func)
        >>> dataset.prepare_for_training(framework="...", task=task)
    """

    formatting_func: Callable[
        [Dict[str, Any]], Union[None, Tuple[str, str], List[Tuple[str, str]], Iterator[Tuple[str, str]]]
    ]
    _formatting_func_return_types = RMReturnTypes
    _supported_frameworks_names = ["trl"]

    def _format_data(self, dataset: "FeedbackDataset") -> List[Dict[str, str]]:
        output = self._execute_formatting_func(dataset)
        return [{"chosen": chosen, "rejected": rejected} for chosen, rejected in output]

    @requires_dependencies("datasets>1.17.0")
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
        text: The TextField to use for training.

    Examples:
        >>> from argilla import TrainingTaskForPPO
        >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
        >>> task = TrainingTaskForPPO(text=dataset.fields[0],)
        >>> dataset.prepare_for_training(framework="...", task=task)
    """

    formatting_func: Callable[[Dict[str, Any]], Union[None, str, Iterator[str]]]
    _formatting_func_return_types = PPOReturnTypes
    _supported_frameworks_names = ["trl"]

    def _format_data(self, dataset: "FeedbackDataset") -> List[Dict[str, str]]:
        output = self._execute_formatting_func(dataset)
        return [{"query": text} for text in output]

    @requires_dependencies("datasets>1.17.0")
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
        formatting_func: A formatting function converting a dictionary of records into zero,
            one or more prompt-chosen-rejected text tuples.

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
        ...     yield sample["prompt"], chosen, rejected
        >>> task = TrainingTaskForDPO(formatting_func=formatting_func)
        >>> dataset.prepare_for_training(framework="...", task=task)
    """

    formatting_func: Callable[[Dict[str, Any]], Union[None, Tuple[str, str, str], Iterator[Tuple[str, str, str]]]]
    _formatting_func_return_types = DPOReturnTypes
    _supported_frameworks_names = ["trl"]

    def _format_data(self, dataset: "FeedbackDataset") -> List[Dict[str, str]]:
        output = self._execute_formatting_func(dataset)
        return [{"prompt": prompt, "chosen": chosen, "rejected": rejected} for prompt, chosen, rejected in output]

    @requires_dependencies("datasets>1.17.0")
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
        >>> from argilla import TrainingTaskForQuestionAnswering
        >>> dataset = rg.FeedbackDataset.from_argilla(name="...")
        >>> task = TrainingTaskForQuestionAnswering(
        ...     question=dataset.field_by_name("question"),
        ...     context=dataset.field_by_name("context"),
        ...     answer=dataset.question_by_name("answer"),
        ... )
        >>> dataset.prepare_for_training(framework="...", task=task)
        >>> # with formatting_func
        >>> from argilla import TrainingTaskForQuestionAnswering
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

    defaults: Optional[QuestionAnsweringDefaults] = None
    formatting_func: Optional[Callable[[Dict[str, Any]], Union[None, str, Iterator[str]]]] = None
    _formatting_func_return_types = QuestionAnsweringReturnTypes
    _supported_frameworks_names = ["transformers"]

    @property
    def question(self) -> TextField:
        return self.defaults.question

    @property
    def context(self) -> TextField:
        return self.defaults.context

    @property
    def answer(self) -> TextQuestion:
        return self.defaults.answer

    def _format_data(self, dataset: "FeedbackDataset") -> List[Dict[str, str]]:
        if self.formatting_func is not None:
            output = self._execute_formatting_func(dataset)
            return [
                {"question": question, "context": context, "answer": answer} for question, context, answer in output
            ]
        else:
            return super()._format_data(dataset)

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
            if any([entry["question"] is None, entry["context"] is None, entry["answer"] is None]):
                continue
            if entry["answer"] not in entry["context"]:
                warnings.warn("This is extractive QnA but the answer is not in the context.")
                continue
            # get index of answer in context
            answer_start = entry["context"].index(entry["answer"])
            datasets_dict["question"].append(entry["question"])
            datasets_dict["context"].append(entry["context"])
            datasets_dict["answer"].append({"answer_start": [answer_start], "text": [entry["answer"]]})

        datasets_dict["id"] = list(range(len(data)))
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
            "id": datasets.Value(dtype="int32"),
        }

        ds = datasets.Dataset.from_dict(datasets_dict, features=datasets.Features(feature_dict))

        if train_size != 1:
            ds = ds.train_test_split(train_size=train_size, test_size=1 - train_size, seed=seed)

        return ds


class TrainingTaskForChatCompletion(BaseModel, TrainingData):
    """Training data for chat completion

    Args:
        formatting_func: A formatting function converting a dictionary of records into zero,
            one or more chat-turn-role-content text tuples.

    Examples:
        >>> from argilla import TrainingTaskForChatCompletion
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

    formatting_func: Callable[[Dict[str, Any]], Union[None, Dict[str, str], Iterator[Dict[str, str]]]]
    _formatting_func_return_types = ChatCompletionReturnTypes
    _supported_frameworks_names = ["openai"]

    def _format_data(self, dataset: "FeedbackDataset") -> List[Dict[str, str]]:
        output = self._execute_formatting_func(dataset)
        return [{"chat": chat, "turn": turn, "role": role, "content": content} for chat, turn, role, content in output]

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


class TrainingTaskForSentenceSimilarity(BaseModel, TrainingData):
    """Training data for sentence similarity.

    Args:
        formatting_func: A formatting function converting a dictionary of records into
            a dictionary of a pair of sentences, a pair of sentences and a label,
            a sentence and a label or a triplet of sentences.

    Examples:
        Example for argilla/emotion dataset:
        >>> from argilla import TrainingTaskForSentenceSimilarity
        >>> dataset = rg.FeedbackDataset.from_argilla(name="argilla/emotion")
        >>> def formatting_func(sample: Dict[str, Any]):
        ...     return {"sentence": sample["text"], "label": int(sample["label"][0]["value"])}
        >>> task = TrainingTaskForSentenceSimilarity(formatting_func=formatting_func)
        >>> dataset.prepare_for_training(framework="...", task=task)
    """

    defaults: Optional[SentenceSimilarityDefaults] = SentenceSimilarityDefaults()
    formatting_func: Callable[
        [Dict[str, Any]],
        Union[
            None, Dict[str, Union[float, int]], Dict[str, str], List[Dict[str, Union[float, int]]], List[Dict[str, str]]
        ],
    ] = None
    _formatting_func_return_types = SentenceSimilarityReturnTypes
    _supported_frameworks_names = ["sentence-transformers"]

    @property
    def __all_labels__(self) -> Optional[List[str]]:
        if self.label:
            return self.label.question.__all_labels__

    @property
    def __label2id__(self) -> Optional[Dict[str, int]]:
        if self.label:
            return self.label.question.__label2id__

    @property
    def __id2label__(self) -> Optional[Dict[int, str]]:
        if self.label:
            return self.label.question.__id2label__

    @property
    def label(
        self,
    ) -> Optional[Union[LabelQuestion, RatingQuestion, LabelQuestionUnification, RankingQuestionUnification]]:
        return self.defaults.label

    @property
    def texts(self) -> Optional[List[str]]:
        return self.defaults.texts

    def _format_data(self, dataset: "FeedbackDataset") -> List[Dict[str, Any]]:
        if self.formatting_func:
            output = self._execute_formatting_func(dataset)

            if "label" in output[0]:
                _all_labels = set()
                for sample in output:
                    if isinstance(sample, (list, tuple, set)):
                        for response in sample:
                            _all_labels.add(response["label"])
                    else:
                        _all_labels.add(sample["label"])

                if self.defaults.label is None:
                    labels = list(_all_labels)
                    if isinstance(labels[0], int):
                        label = RatingQuestionUnification(
                            question=RatingQuestion(name="custom_func", values=labels), strategy="majority"
                        )
                    else:
                        label = LabelQuestionUnification(question=LabelQuestion(name="custom_func", labels=labels))
                    self.defaults.label = label

            return output

        else:
            formatted_data = super()._format_data(dataset)
            # NOTE: Maybe this post processing of the formatted data can be simplified
            # or directly done in super()._format_data(dataset).
            new_keys = {field.name: f"sentence-{i}" for i, field in enumerate(self.texts, start=1)}
            if self.defaults.label:
                new_keys.update({self.defaults.label.question.name: "label"})

            outputs = []
            for example in formatted_data:
                record = {}
                for k, v in new_keys.items():
                    if v == "label":
                        value = example[v]
                        # At this point the label must be either an int or a float, determine which one is it.
                        if isinstance(value, str):
                            if value.lstrip("-").isdigit():
                                value = int(value)
                            else:
                                value = float(value)
                    else:
                        value = example[k]

                    record[v] = value
                outputs.append(record)

            return outputs

    def compute_unified_responses(self, responses: List[FeedbackRecord]):
        self.label.strategy.compute_unified_responses(responses=responses, field=self.label.question)

    @requires_dependencies("scikit-learn")
    def _train_test_split(
        self, data: List[dict], train_size: float, seed: int, stratify=None
    ) -> Tuple[List[dict], List[dict]]:
        from sklearn.model_selection import train_test_split

        return train_test_split(data, train_size=train_size, shuffle=True, random_state=seed, stratify=stratify)

    @requires_dependencies("sentence-transformers")
    def _prepare_for_training_with_sentence_transformers(
        self, data: Union[List[dict], List[List[dict]]], train_size: float, seed: int
    ) -> Union["InputExample", Tuple["InputExample", "InputExample"]]:
        from sentence_transformers import InputExample

        if not len(data) > 0:
            raise ValueError("The dataset must contain at least one sample to be able to train.")

        # Use the first sample to decide what type of dataset to generate:
        if isinstance(data[0], list):
            # In case we are returning lists, extract the first element of that list to check the fields.
            sample_keys = set(data[0][0].keys())
        elif isinstance(data[0], dict):
            sample_keys = set(data[0].keys())
        else:
            raise ValueError(f"The type is not supported: {type(data[0])}.")

        if sample_keys == {"label", "sentence-1", "sentence-2"}:

            def dataset_fields(sample):
                return {"texts": [sample["sentence-1"], sample["sentence-2"]], "label": sample["label"]}

        elif sample_keys == {"label", "sentence-1", "sentence-2", "sentence-3"}:

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

    @classmethod
    def for_chat_completion(cls, *args, **kwargs) -> TrainingTaskForChatCompletion:
        cls.warn()
        return super().for_chat_completion(*args, **kwargs)

    @classmethod
    def for_sentence_similarity(cls, *args, **kwargs) -> TrainingTaskForSentenceSimilarity:
        cls.warn()
        return super().for_sentence_similarity(*args, **kwargs)

    @classmethod
    def for_question_answering(cls, *args, **kwargs) -> TrainingTaskForQuestionAnswering:
        cls.warn()
        return super().for_question_answering(*args, **kwargs)


class TrainingTaskMappingForTextClassification(TrainingTaskForTextClassification, RenamedDeprecationMixin):
    def __init__(self, *args, **kwargs) -> None:
        self.warn()
        return super().__init__(*args, **kwargs)
