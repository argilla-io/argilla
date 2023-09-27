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

from typing import TYPE_CHECKING, Dict, List, Optional, Type, Union
from uuid import UUID

from tqdm import trange

from argilla.client.api import ArgillaSingleton
from argilla.client.feedback.constants import PUSHING_BATCH_SIZE
from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
from argilla.client.feedback.schemas.enums import FieldTypes, QuestionTypes
from argilla.client.feedback.schemas.fields import TextField
from argilla.client.feedback.schemas.questions import (
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    TextQuestion,
)
from argilla.client.feedback.schemas.remote.fields import RemoteTextField
from argilla.client.feedback.schemas.remote.questions import (
    RemoteLabelQuestion,
    RemoteMultiLabelQuestion,
    RemoteRankingQuestion,
    RemoteRatingQuestion,
    RemoteTextQuestion,
)
from argilla.client.feedback.unification import (
    LabelQuestionStrategy,
    MultiLabelQuestionStrategy,
    RankingQuestionStrategy,
    RatingQuestionStrategy,
    TextQuestionStrategy,
)
from argilla.client.feedback.utils import feedback_dataset_in_argilla
from argilla.client.sdk.v1.datasets import api as datasets_api_v1
from argilla.client.workspaces import Workspace

if TYPE_CHECKING:
    import httpx

    from argilla.client.client import Argilla as ArgillaClient
    from argilla.client.feedback.dataset.local import FeedbackDataset
    from argilla.client.feedback.schemas.types import AllowedRemoteFieldTypes, AllowedRemoteQuestionTypes
    from argilla.client.sdk.v1.datasets.models import FeedbackDatasetModel

from argilla.client.feedback.schemas.records import FeedbackRecord


class ArgillaMixin:
    def __delete_dataset(self: "FeedbackDataset", client: "httpx.Client", id: UUID) -> None:
        try:
            datasets_api_v1.delete_dataset(client=client, id=id)
        except Exception as e:
            raise Exception(
                f"Failed while deleting the `FeedbackDataset` with ID '{id}' from Argilla with" f" exception: {e}"
            ) from e

    def __add_fields(self: "FeedbackDataset", client: "httpx.Client", id: UUID) -> List["AllowedRemoteFieldTypes"]:
        fields = []
        for field in self._fields:
            try:
                new_field = datasets_api_v1.add_field(client=client, id=id, field=field.to_server_payload()).parsed
                fields.append(new_field)
            except Exception as e:
                self.__delete_dataset(client=client, id=id)
                raise Exception(
                    f"Failed while adding the field '{field.name}' to the `FeedbackDataset` in Argilla with"
                    f" exception: {e}"
                ) from e
        return fields

    def __add_questions(
        self: "FeedbackDataset", client: "httpx.Client", id: UUID
    ) -> List["AllowedRemoteQuestionTypes"]:
        questions = []
        for question in self._questions:
            try:
                new_question = datasets_api_v1.add_question(
                    client=client, id=id, question=question.to_server_payload()
                ).parsed
                questions.append(new_question)
            except Exception as e:
                self.__delete_dataset(client=client, id=id)
                raise Exception(
                    f"Failed while adding the question '{question.name}' to the `FeedbackDataset` in Argilla with"
                    f" exception: {e}"
                ) from e
        return questions

    def __publish_dataset(self: "FeedbackDataset", client: "httpx.Client", id: UUID) -> None:
        try:
            datasets_api_v1.publish_dataset(client=client, id=id)
        except Exception as e:
            self.__delete_dataset(client=client, id=id)
            raise Exception(f"Failed while publishing the `FeedbackDataset` in Argilla with exception: {e}") from e

    def __push_records(
        self: "FeedbackDataset",
        client: "httpx.Client",
        id: UUID,
        question_name_to_id: Dict[str, UUID],
        show_progress: bool = True,
    ) -> None:
        if len(self.records) == 0:
            return

        for i in trange(
            0, len(self.records), PUSHING_BATCH_SIZE, desc="Pushing records to Argilla...", disable=show_progress
        ):
            try:
                datasets_api_v1.add_records(
                    client=client,
                    id=id,
                    records=[
                        record.to_server_payload(question_name_to_id=question_name_to_id)
                        for record in self.records[i : i + PUSHING_BATCH_SIZE]
                    ],
                )
            except Exception as e:
                self.__delete_dataset(client=client, id=id)
                raise Exception(
                    f"Failed while adding the records to the `FeedbackDataset` in Argilla with exception: {e}"
                ) from e

    def push_to_argilla(
        self: "FeedbackDataset",
        name: str,
        workspace: Optional[Union[str, Workspace]] = None,
        show_progress: bool = False,
    ) -> RemoteFeedbackDataset:
        """Pushes the `FeedbackDataset` to Argilla.

        Note that you may need to `rg.init(...)` with your Argilla credentials before calling this function, otherwise
        the default http://localhost:6900 will be used, which will fail if Argilla is not deployed locally.

        Args:
            name: the name of the dataset to push to Argilla.
            workspace: the workspace where to push the dataset to. If not provided, the active workspace will be used.
            show_progress: the option to choose to show/hide tqdm progress bar while looping over records.

        Returns:
            The `FeedbackDataset` pushed to Argilla, which is now an instance of `RemoteFeedbackDataset`.
        """
        client: "ArgillaClient" = ArgillaSingleton.get()
        httpx_client: "httpx.Client" = client.http_client.httpx

        if workspace is None:
            workspace = Workspace.from_name(client.get_workspace())

        if isinstance(workspace, str):
            workspace = Workspace.from_name(workspace)

        dataset = feedback_dataset_in_argilla(name=name, workspace=workspace)
        if dataset is not None:
            raise RuntimeError(
                f"Dataset with name=`{name}` and workspace=`{workspace.name}` already exists in Argilla, please"
                " choose another name and/or workspace."
            )

        try:
            new_dataset: "FeedbackDatasetModel" = datasets_api_v1.create_dataset(
                client=httpx_client, name=name, workspace_id=workspace.id, guidelines=self.guidelines
            ).parsed
            argilla_id = new_dataset.id
        except Exception as e:
            raise Exception(f"Failed while creating the `FeedbackDataset` in Argilla with exception: {e}") from e

        fields = self.__add_fields(client=httpx_client, id=argilla_id)

        questions = self.__add_questions(client=httpx_client, id=argilla_id)
        question_name_to_id = {question.name: question.id for question in questions}

        self.__publish_dataset(client=httpx_client, id=argilla_id)

        self.__push_records(
            client=httpx_client, id=argilla_id, show_progress=show_progress, question_name_to_id=question_name_to_id
        )

        return RemoteFeedbackDataset(
            client=httpx_client,
            id=argilla_id,
            name=name,
            workspace=workspace,
            created_at=new_dataset.inserted_at,
            updated_at=new_dataset.updated_at,
            fields=fields,
            questions=questions,
            guidelines=self.guidelines,
        )

    @staticmethod
    def __get_fields(client: "httpx.Client", id: UUID) -> List["AllowedRemoteFieldTypes"]:
        fields = []
        for field in datasets_api_v1.get_fields(client=client, id=id).parsed:
            if field.settings["type"] == FieldTypes.text:
                field = RemoteTextField.from_api(field)
            else:
                raise ValueError(
                    f"Field '{field.name}' is not a supported field in the current Python package version,"
                    f" supported field types are: `{'`, `'.join([arg.value for arg in FieldTypes])}`."
                )
            fields.append(field)
        return fields

    @staticmethod
    def __get_questions(client: "httpx.Client", id: UUID) -> List["AllowedRemoteQuestionTypes"]:
        questions = []
        for question in datasets_api_v1.get_questions(client=client, id=id).parsed:
            if question.settings["type"] == QuestionTypes.rating:
                question = RemoteRatingQuestion.from_api(question)
            elif question.settings["type"] == QuestionTypes.text:
                question = RemoteTextQuestion.from_api(question)
            elif question.settings["type"] == QuestionTypes.label_selection:
                question = RemoteLabelQuestion.from_api(question)
            elif question.settings["type"] == QuestionTypes.multi_label_selection:
                question = RemoteMultiLabelQuestion.from_api(question)
            elif question.settings["type"] == QuestionTypes.ranking:
                question = RemoteRankingQuestion.from_api(question)
            else:
                raise ValueError(
                    f"Question '{question.name}' is not a supported question in the current Python package"
                    f" version, supported question types are: `{'`, `'.join([arg.value for arg in QuestionTypes])}`."
                )
            questions.append(question)
        return questions

    @classmethod
    def from_argilla(
        cls: Type["FeedbackDataset"],
        name: Optional[str] = None,
        *,
        workspace: Optional[str] = None,
        id: Optional[str] = None,
    ) -> RemoteFeedbackDataset:
        """Retrieves an existing `FeedbackDataset` from Argilla (must have been pushed in advance).

        Note that even though no argument is mandatory, you must provide either the `name`,
        the combination of `name` and `workspace`, or the `id`, otherwise an error will be raised.

        Args:
            name: the name of the `FeedbackDataset` to retrieve from Argilla. Defaults to `None`.
            workspace: the workspace of the `FeedbackDataset` to retrieve from Argilla.
                If not provided, the active workspace will be used.
            id: the ID of the `FeedbackDataset` to retrieve from Argilla. Defaults to `None`.

        Returns:
            The `RemoteFeedbackDataset` retrieved from Argilla.

        Raises:
            ValueError: if no `FeedbackDataset` with the provided `name`, `workspace`, or `id` exists in Argilla.

        Examples:
            >>> import argilla as rg
            >>> rg.init(...)
            >>> dataset = rg.FeedbackDataset.from_argilla(name="my_dataset")
        """
        httpx_client: "httpx.Client" = ArgillaSingleton.get().http_client.httpx

        existing_dataset = feedback_dataset_in_argilla(name=name, workspace=workspace, id=id)
        if existing_dataset is None:
            raise ValueError(
                f"Could not find a `FeedbackDataset` in Argilla with name='{name}'."
                if name and not workspace
                else (
                    f"Could not find a `FeedbackDataset` in Argilla with name='{name}' and workspace='{workspace}'."
                    if name and workspace
                    else (f"Could not find a `FeedbackDataset` in Argilla with ID='{id}'.")
                )
            )

        fields = cls.__get_fields(client=httpx_client, id=existing_dataset.id)
        questions = cls.__get_questions(client=httpx_client, id=existing_dataset.id)

        return RemoteFeedbackDataset(
            client=httpx_client,
            id=existing_dataset.id,
            name=existing_dataset.name,
            workspace=Workspace.from_id(existing_dataset.workspace_id),
            created_at=existing_dataset.inserted_at,
            updated_at=existing_dataset.updated_at,
            fields=fields,
            questions=questions,
            guidelines=existing_dataset.guidelines or None,
        )

    @classmethod
    def list(cls: Type["FeedbackDataset"], workspace: Optional[str] = None) -> List[RemoteFeedbackDataset]:
        """Lists the `FeedbackDataset`s pushed to Argilla.

        Note that you may need to `rg.init(...)` with your Argilla credentials before
        calling this function, otherwise, the default http://localhost:6900 will be used,
        which will fail if Argilla is not deployed locally.

        Args:
            workspace: the workspace where to list the datasets from. If not provided,
                then the workspace filtering won't be applied. Defaults to `None`.

        Returns:
            A list of `RemoteFeedbackDataset` datasets, which are `FeedbackDataset`
            datasets previously pushed to Argilla via `push_to_argilla`.
        """
        client: "ArgillaClient" = ArgillaSingleton.get()
        httpx_client: "httpx.Client" = client.http_client.httpx

        if workspace is not None:
            workspace = Workspace.from_name(workspace)

        try:
            datasets = datasets_api_v1.list_datasets(
                client=httpx_client, workspace_id=workspace.id if workspace is not None else None
            ).parsed
        except Exception as e:
            raise RuntimeError(
                f"Failed while listing the `FeedbackDataset` datasets in Argilla with exception: {e}"
            ) from e

        if len(datasets) == 0:
            return []
        return [
            RemoteFeedbackDataset(
                client=httpx_client,
                id=dataset.id,
                name=dataset.name,
                workspace=workspace if workspace is not None else Workspace.from_id(dataset.workspace_id),
                created_at=dataset.inserted_at,
                updated_at=dataset.updated_at,
                fields=cls.__get_fields(client=httpx_client, id=dataset.id),
                questions=cls.__get_questions(client=httpx_client, id=dataset.id),
                guidelines=dataset.guidelines or None,
            )
            for dataset in datasets
        ]


class UnificationMixin:
    def unify_responses(
        self,
        question: Union[str, LabelQuestion, MultiLabelQuestion, RatingQuestion],
        strategy: Union[
            str, LabelQuestionStrategy, MultiLabelQuestionStrategy, RatingQuestionStrategy, RankingQuestionStrategy
        ],
    ) -> None:
        """
        The `unify_responses` function takes a question and a strategy as input and applies the strategy
        to unify the responses for that question.

        Args:
            question The `question` parameter can be either a string representing the name of the
                question, or an instance of one of the question classes (`LabelQuestion`, `MultiLabelQuestion`,
                `RatingQuestion`, `RankingQuestion`).
            strategy The `strategy` parameter is used to specify the strategy to be used for unifying
                responses for a given question. It can be either a string or an instance of a strategy class.
        """
        if isinstance(question, str):
            question = self.question_by_name(question)

        if isinstance(strategy, str):
            if isinstance(question, LabelQuestion):
                strategy = LabelQuestionStrategy(strategy)
            elif isinstance(question, MultiLabelQuestion):
                strategy = MultiLabelQuestionStrategy(strategy)
            elif isinstance(question, RatingQuestion):
                strategy = RatingQuestionStrategy(strategy)
            elif isinstance(question, RankingQuestion):
                strategy = RankingQuestionStrategy(strategy)
            elif isinstance(question, TextQuestion):
                strategy = TextQuestionStrategy(strategy)
            else:
                raise ValueError(f"Question {question} is not supported yet")

        strategy.unify_responses(self.records, question)


class TaskTemplateMixin:
    """
    Mixin to add task template functionality to a `FeedbackDataset`.
    The NLP tasks covered are:
    task:
        "question_answering"
        "text_classification"
        "token_classification"
        "summarization"
        "translation"
        "supervised-fine-tuning"
        "conversational"
        "retrieval-augmented-generation"
        "sentence-similarity"
    """

    @classmethod
    def for_question_answering(cls: Type["FeedbackDataset"], use_markdown: bool = False) -> "FeedbackDataset":
        """
        You can use this method to create a basic dataset for question answering tasks.
        To add items to your dataset, use the "add_item" method.

        Args:
            use_markdown: Set this parameter to True if you want to use markdown in your dataset

        Returns:
            A `FeedbackDataset` object for question answering containing "context" and "question" fields and a TextQuestion named "answer"
        """
        return cls(
            fields=[
                TextField(name="question", use_markdown=use_markdown),
                TextField(name="context", use_markdown=use_markdown),
            ],
            questions=[
                TextQuestion(
                    name="answer",
                    description="Answer the question. Note that the answer must exactly be in the context.",
                )
            ],
            guidelines="This is a question answering dataset that contains questions and contexts. Please answer the questions by selecting the answer in the context.",
        )

    @classmethod
    def for_text_classification(
        cls: Type["FeedbackDataset"], labels: List[str], multi_label: bool = False, use_markdown: bool = False
    ) -> "FeedbackDataset":
        """
        You can use this method to create a basic dataset for text classification tasks.
        To add items to your dataset, use the "add_item" method.

        Args:
            labels: A list of labels for your dataset
            multi_label: Set this parameter to True if you want to add multiple labels to your dataset
            use_markdown: Set this parameter to True if you want to use markdown in your dataset

        Returns:
            A `FeedbackDataset` object for text classification containing "text" field and LabelQuestion or MultiLabelQuestion named "label"
        """
        return cls(
            fields=[
                TextField(name="text", use_markdown=use_markdown),
            ],
            questions=[
                LabelQuestion(name="label", labels=labels, description="Choose one of the labels.")
                if not multi_label
                else MultiLabelQuestion(name="label", labels=labels, description="Choose one or more of the labels.")
            ],
            guidelines="This is a text classification dataset ... ",
        )

    @classmethod
    def for_supervised_fine_tuning(
        cls: Type["FeedbackDataset"], context: bool = True, use_markdown: bool = False
    ) -> "FeedbackDataset":
        """
        You can use this method to create a basic dataset for supervised fine-tuning tasks.
        To add items to your dataset, use the "add_item" method.

        Args:
            context: Set this parameter to True if you want to add context to your dataset
            use_markdown: Set this parameter to True if you want to use markdown in your dataset

        Returns:
            A `FeedbackDataset` object for supervised fine-tuning containing "instruction" and optional "context" field and a TextQuestion named "response"
        """
        return cls(
            fields=[
                TextField(name="instruction", use_markdown=use_markdown),
                TextField(name="context", use_markdown=use_markdown),
            ]
            if context
            else [
                TextField(name="instruction", use_markdown=use_markdown),
            ],
            questions=[TextQuestion(name="response")],
        )

    @classmethod
    def for_sentence_similarity(cls: Type["FeedbackDataset"]) -> "FeedbackDataset":
        """
        You can use this method to create a basic dataset for sentence similarity tasks.
        To add items to your dataset, use the "add_item" method.

        Args:
            None

        Returns:
            A `FeedbackDataset` object for sentence similarity containing "sentence1" and "sentence2" fields and a RatingQuestion named "similarity"
        """
        return cls(
            fields=[
                TextField(name="sentence1"),
                TextField(name="sentence2"),
            ],
            questions=[RatingQuestion(name="similarity", values=[1, 2, 3, 4, 5])],
        )

    @classmethod
    def for_summarization(cls: Type["FeedbackDataset"]) -> "FeedbackDataset":
        """
        You can use this method to create a basic dataset for summarization tasks.
        To add items to your dataset, use the "add_item" method.

        Args:
            None

        Returns:
            A `FeedbackDataset` object for summarization containing "text" field and a TextQuestion named "summary"
        """
        return cls(
            fields=[
                TextField(name="text"),
            ],
            questions=[TextQuestion(name="summary")],
        )

    @classmethod
    def for_translation(cls: Type["FeedbackDataset"], labels: bool = False) -> "FeedbackDataset":
        """
        You can use this method to create a basic dataset for translation tasks.
        To add items to your dataset, use the "add_item" method.

        Args:
            labels: Set this parameter to True if you want to add labels to your dataset

        Returns:
            A `FeedbackDataset` object for translation containing "text" field and a TextQuestion named "translation"
        """
        return cls(
            fields=[TextField(name="text")],
            questions=[
                TextQuestion(name="translation") if not labels else TextQuestion(name="translation"),
                LabelQuestion(name="labels", labels=labels),
            ],
        )

    @classmethod
    def for_conversational(cls: Type["FeedbackDataset"], system_prompt: bool = False) -> "FeedbackDataset":
        """
        You can use this method to create a basic dataset for conversational tasks.
        To add items to your dataset, use the "add_item" method.

        Args:
            system_prompt: Set this parameter to True if you want to add system prompt to your dataset

        Returns:
            A `FeedbackDataset` object for conversational containing "context" and optional "system_prompt" field and a TextQuestion named "response"
        """
        return cls(
            fields=[TextField(name="system_prompt", title="System Prompt"), TextField(name="context")]
            if system_prompt
            else [TextField(name="context")],
            questions=[TextQuestion(name="response")],
        )

    @classmethod
    def for_retrieval_augmented_generation(
        cls: Type["FeedbackDataset"], retrieval_source: bool = False
    ) -> "FeedbackDataset":
        """
        You can use this method to create a basic dataset for conversational tasks.
        To add items to your dataset, use the "add_item" method.

        Args:
            system_prompt: Set this parameter to True if you want to add system prompt to your dataset

        Returns:
            A `FeedbackDataset` object for conversational containing "context" and optional "system_prompt" field and a TextQuestion named "response"
        """
        return cls(
            fields=[
                TextField(name="query"),
                TextField(name="retrieved_document", title="Retrieved Document"),
                TextField(name="retrieval_source", title="Retrieval Source"),
            ]
            if retrieval_source
            else [TextField(name="query"), TextField(name="retrieved_document", title="Retrieved Document")],
            questions=[TextQuestion(name="response")],
        )

    # ADD ITEM
    def add_item(self, items):
        """
        You can use this method to add items to your dataset.
        Make sure that the keys of the dictionary are the same as the names of the fields.

        Args:
            items: A dictionary containing the fields of the dataset and their values.

        Returns:
            None
        """

        dataset_fields = [self.fields[i].name for i in range(len(self.fields))]
        record_fields = list(items.keys())  # {'context', 'question'}

        if not set(record_fields).issubset(set(dataset_fields)):
            raise ValueError("Item fields are not subset of dataset fields")

        text_fields = {}
        for indx, field_name in enumerate(dataset_fields):
            text_fields[field_name] = items[dataset_fields[indx]]

        dataset_length = [len(value) for key, value in items.items()][0]

        for item in range(dataset_length):
            record = FeedbackRecord(
                fields={dataset_fields[index]: text_fields[field][item] for index, field in enumerate(dataset_fields)}
            )
            self.add_records(record)
