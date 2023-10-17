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

from argilla.client.api import ArgillaSingleton
from argilla.client.feedback.constants import PUSHING_BATCH_SIZE
from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
from argilla.client.feedback.schemas.enums import FieldTypes, MetadataPropertyTypes, QuestionTypes
from argilla.client.feedback.schemas.fields import TextField
from argilla.client.feedback.schemas.questions import (
    LabelQuestion,
    MultiLabelQuestion,
    RatingQuestion,
    TextQuestion,
)
from argilla.client.feedback.schemas.remote.fields import RemoteTextField
from argilla.client.feedback.schemas.remote.metadata import (
    RemoteFloatMetadataProperty,
    RemoteIntegerMetadataProperty,
    RemoteTermsMetadataProperty,
)
from argilla.client.feedback.schemas.remote.questions import (
    RemoteLabelQuestion,
    RemoteMultiLabelQuestion,
    RemoteRankingQuestion,
    RemoteRatingQuestion,
    RemoteTextQuestion,
)
from argilla.client.feedback.utils import feedback_dataset_in_argilla
from argilla.client.sdk.v1.datasets import api as datasets_api_v1
from argilla.client.workspaces import Workspace
from tqdm import trange

if TYPE_CHECKING:
    import httpx
    from argilla.client.client import Argilla as ArgillaClient
    from argilla.client.feedback.dataset.local import FeedbackDataset
    from argilla.client.feedback.dataset.local.dataset import FeedbackDataset
    from argilla.client.feedback.schemas.records import FeedbackRecord
    from argilla.client.feedback.schemas.types import (
        AllowedFieldTypes,
        AllowedMetadataPropertyTypes,
        AllowedQuestionTypes,
        AllowedRemoteFieldTypes,
        AllowedRemoteMetadataPropertyTypes,
        AllowedRemoteQuestionTypes,
    )
    from argilla.client.sdk.v1.datasets.models import (
        FeedbackDatasetModel,
        FeedbackFieldModel,
        FeedbackMetadataPropertyModel,
        FeedbackQuestionModel,
    )


class ArgillaMixin:
    @staticmethod
    def __delete_dataset(client: "httpx.Client", id: UUID) -> None:
        try:
            datasets_api_v1.delete_dataset(client=client, id=id)
        except Exception as e:
            raise Exception(
                f"Failed while deleting the `FeedbackDataset` with ID '{id}' from Argilla with" f" exception: {e}"
            ) from e

    @staticmethod
    def _parse_to_remote_field(field: "FeedbackFieldModel") -> "AllowedRemoteFieldTypes":
        if field.settings["type"] == FieldTypes.text:
            field = RemoteTextField.from_api(field)
        else:
            raise ValueError(
                f"Field '{field.name}' is not a supported field in the current Python package version,"
                f" supported field types are: `{'`, `'.join([arg.value for arg in FieldTypes])}`."
            )
        return field

    @staticmethod
    def __add_fields(
        fields: List["AllowedFieldTypes"], client: "httpx.Client", id: UUID
    ) -> List["AllowedRemoteFieldTypes"]:
        uploaded_fields = []
        for field in fields:
            try:
                new_field = datasets_api_v1.add_field(client=client, id=id, field=field.to_server_payload()).parsed
                uploaded_fields.append(ArgillaMixin._parse_to_remote_field(new_field))
            except Exception as e:
                ArgillaMixin.__delete_dataset(client=client, id=id)
                raise Exception(
                    f"Failed while adding the field '{field.name}' to the `FeedbackDataset` in Argilla with"
                    f" exception: {e}"
                ) from e
        return uploaded_fields

    @staticmethod
    def _parse_to_remote_question(question: "FeedbackQuestionModel") -> "AllowedRemoteQuestionTypes":
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

        return question

    @staticmethod
    def __add_questions(
        questions: List["AllowedQuestionTypes"], client: "httpx.Client", id: UUID
    ) -> List["AllowedRemoteQuestionTypes"]:
        uploaded_questions = []
        for question in questions:
            try:
                new_question = datasets_api_v1.add_question(
                    client=client, id=id, question=question.to_server_payload()
                ).parsed
                uploaded_questions.append(ArgillaMixin._parse_to_remote_question(new_question))
            except Exception as e:
                ArgillaMixin.__delete_dataset(client=client, id=id)
                raise Exception(
                    f"Failed while adding the question '{question.name}' to the `FeedbackDataset` in Argilla with"
                    f" exception: {e}"
                ) from e
        return uploaded_questions

    @staticmethod
    def _parse_to_remote_metadata_property(
        metadata_property: "FeedbackMetadataPropertyModel",
        client: Optional["httpx.Client"] = None,
    ) -> "AllowedRemoteMetadataPropertyTypes":
        if metadata_property.settings["type"] == MetadataPropertyTypes.terms:
            metadata_property = RemoteTermsMetadataProperty.from_api(payload=metadata_property, client=client)
        elif metadata_property.settings["type"] == MetadataPropertyTypes.integer:
            metadata_property = RemoteIntegerMetadataProperty.from_api(payload=metadata_property, client=client)
        elif metadata_property.settings["type"] == MetadataPropertyTypes.float:
            metadata_property = RemoteFloatMetadataProperty.from_api(payload=metadata_property, client=client)
        else:
            raise ValueError(
                f"Metadata property '{metadata_property.name}' is not a supported metadata property in the current"
                " Python package version, supported metadata property types are: "
                f"`{'`, `'.join([arg.value for arg in MetadataPropertyTypes])}`."
            )

        return metadata_property

    @staticmethod
    def __add_metadata_properties(
        metadata_properties: List["AllowedMetadataPropertyTypes"], client: "httpx.Client", id: UUID
    ) -> Union[List["AllowedRemoteMetadataPropertyTypes"], None]:
        if not metadata_properties:
            return None

        uploaded_metadata_properties = []
        for metadata_property in metadata_properties:
            try:
                new_metadata_property = datasets_api_v1.add_metadata_property(
                    client=client, id=id, metadata_property=metadata_property.to_server_payload()
                ).parsed
                uploaded_metadata_properties.append(
                    ArgillaMixin._parse_to_remote_metadata_property(
                        metadata_property=new_metadata_property, client=client
                    )
                )
            except Exception as e:
                ArgillaMixin.__delete_dataset(client=client, id=id)
                raise Exception(
                    f"Failed while adding the metadata property '{metadata_property.name}' to the `FeedbackDataset` in"
                    f" Argilla with exception: {e}"
                ) from e
        return uploaded_metadata_properties

    @staticmethod
    def __publish_dataset(client: "httpx.Client", id: UUID) -> None:
        try:
            datasets_api_v1.publish_dataset(client=client, id=id)
        except Exception as e:
            ArgillaMixin.__delete_dataset(client=client, id=id)
            raise Exception(f"Failed while publishing the `FeedbackDataset` in Argilla with exception: {e}") from e

    @staticmethod
    def __push_records(
        records: List["FeedbackRecord"],
        client: "httpx.Client",
        id: UUID,
        question_name_to_id: Dict[str, UUID],
        show_progress: bool = True,
    ) -> None:
        if len(records) == 0:
            return

        for i in trange(
            0, len(records), PUSHING_BATCH_SIZE, desc="Pushing records to Argilla...", disable=show_progress
        ):
            try:
                datasets_api_v1.add_records(
                    client=client,
                    id=id,
                    records=[
                        record.to_server_payload(question_name_to_id=question_name_to_id)
                        for record in records[i : i + PUSHING_BATCH_SIZE]
                    ],
                )
            except Exception as e:
                ArgillaMixin.__delete_dataset(client=client, id=id)
                raise Exception(
                    f"Failed while adding the records to the `FeedbackDataset` in Argilla with exception: {e}"
                ) from e

    def push_to_argilla(
        self: Union["FeedbackDataset", "ArgillaMixin"],
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
                client=httpx_client,
                name=name,
                workspace_id=workspace.id,
                guidelines=self.guidelines,
                allow_extra_metadata=self.allow_extra_metadata,
            ).parsed
            argilla_id = new_dataset.id
        except Exception as e:
            raise Exception(f"Failed while creating the `FeedbackDataset` in Argilla with exception: {e}") from e

        ArgillaMixin.__add_fields(fields=self.fields, client=httpx_client, id=argilla_id)
        fields = ArgillaMixin.__get_fields(client=httpx_client, id=argilla_id)

        ArgillaMixin.__add_questions(questions=self.questions, client=httpx_client, id=argilla_id)
        questions = ArgillaMixin.__get_questions(client=httpx_client, id=argilla_id)
        question_name_to_id = {question.name: question.id for question in questions}

        metadata_properties = ArgillaMixin.__add_metadata_properties(
            metadata_properties=self.metadata_properties, client=httpx_client, id=argilla_id
        )

        ArgillaMixin.__publish_dataset(client=httpx_client, id=argilla_id)

        ArgillaMixin.__push_records(
            records=list(self.records),
            client=httpx_client,
            id=argilla_id,
            show_progress=show_progress,
            question_name_to_id=question_name_to_id,
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
            metadata_properties=metadata_properties,
            guidelines=self.guidelines,
            allow_extra_metadata=self.allow_extra_metadata,
        )

    @staticmethod
    def __get_fields(client: "httpx.Client", id: UUID) -> List["AllowedRemoteFieldTypes"]:
        fields = []
        for field in datasets_api_v1.get_fields(client=client, id=id).parsed:
            fields.append(ArgillaMixin._parse_to_remote_field(field))
        return fields

    @staticmethod
    def __get_questions(client: "httpx.Client", id: UUID) -> List["AllowedRemoteQuestionTypes"]:
        questions = []
        for question in datasets_api_v1.get_questions(client=client, id=id).parsed:
            questions.append(ArgillaMixin._parse_to_remote_question(question))
        return questions

    @staticmethod
    def __get_metadata_properties(client: "httpx.Client", id: UUID) -> List["AllowedRemoteMetadataPropertyTypes"]:
        metadata_properties = []
        for metadata_prop in datasets_api_v1.get_metadata_properties(client=client, id=id).parsed:
            metadata_properties.append(
                ArgillaMixin._parse_to_remote_metadata_property(metadata_property=metadata_prop, client=client)
            )
        return metadata_properties

    @classmethod
    def from_argilla(
        cls: Type["FeedbackDataset"],
        name: Optional[str] = None,
        *,
        workspace: Optional[str] = None,
        id: Optional[Union[UUID, str]] = None,
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

        fields = ArgillaMixin.__get_fields(client=httpx_client, id=existing_dataset.id)
        questions = ArgillaMixin.__get_questions(client=httpx_client, id=existing_dataset.id)
        metadata_properties = ArgillaMixin.__get_metadata_properties(client=httpx_client, id=existing_dataset.id)

        return RemoteFeedbackDataset(
            client=httpx_client,
            id=existing_dataset.id,
            name=existing_dataset.name,
            workspace=Workspace.from_id(existing_dataset.workspace_id),
            created_at=existing_dataset.inserted_at,
            updated_at=existing_dataset.updated_at,
            fields=fields,
            questions=questions,
            metadata_properties=metadata_properties,
            guidelines=existing_dataset.guidelines or None,
            allow_extra_metadata=existing_dataset.allow_extra_metadata,
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
                fields=ArgillaMixin.__get_fields(client=httpx_client, id=dataset.id),
                questions=ArgillaMixin.__get_questions(client=httpx_client, id=dataset.id),
                guidelines=dataset.guidelines or None,
            )
            for dataset in datasets
        ]

class TaskTemplateMixin:
    """
    Mixin to add task template functionality to a `FeedbackDataset`.
    The NLP tasks covered are:
        "text_classification"
        "extractive_question_answering"
        "summarization"
        "translation"
        "sentence_similarity"
        "natural_language_inference"
        "supervised_fine_tuning"
        "preference_modeling/reward_modeling"
        "proximal_policy_optimization"
        "direct_preference_optimization"
        "retrieval_augmented_generation"
    """

    @classmethod
    def for_text_classification(
        cls: Type["FeedbackDataset"],
        labels: List[str],
        multi_label: bool = False,
        use_markdown: bool = False,
        guidelines: str = None,
    ) -> "FeedbackDataset":
        """
        You can use this method to create a basic dataset for text classification tasks.

        Args:
            labels: A list of labels for your dataset
            multi_label: Set this parameter to True if you want to add multiple labels to your dataset
            use_markdown: Set this parameter to True if you want to use markdown in your dataset

        Returns:
            A `FeedbackDataset` object for text classification containing "text" field and LabelQuestion or MultiLabelQuestion named "label"
        """
        default_guidelines = "This is a text classification dataset that contains texts and labels. Given a set of texts and a predefined set of labels, the goal of text classification is to assign one or more labels to each text based on its content. Please classify the texts by making the correct selection."

        description = "Classify the text by selecting the correct label from the given list of labels."
        return cls(
            fields=[TextField(name="text", use_markdown=use_markdown)],
            questions=[
                LabelQuestion(
                    name="label",
                    labels=labels,
                    description=description,
                )
                if not multi_label
                else MultiLabelQuestion(
                    name="label",
                    labels=labels,
                    description=description,
                )
            ],
            guidelines=guidelines
            if guidelines is not None
            else default_guidelines
            if multi_label
            else default_guidelines.replace("one or more labels", "one label"),
        )

    @classmethod
    def for_question_answering(
        cls: Type["FeedbackDataset"], use_markdown: bool = False, guidelines: str = None
    ) -> "FeedbackDataset":
        """
        You can use this method to create a basic dataset for question answering tasks.

        Args:
            use_markdown: Set this parameter to True if you want to use markdown in your dataset

        Returns:
            A `FeedbackDataset` object for question answering containing "context" and "question" fields and a TextQuestion named "answer"
        """
        default_guidelines = "This is a question answering dataset that contains questions and contexts. Please answer the question by using the context."
        return cls(
            fields=[
                TextField(name="question", use_markdown=use_markdown),
                TextField(name="context", use_markdown=use_markdown),
            ],
            questions=[
                TextQuestion(
                    name="answer",
                    description="Answer the question. Note that the answer must exactly be in the context.",
                    use_markdown=use_markdown,
                    required=True,
                )
            ],
            guidelines=default_guidelines if guidelines is None else guidelines,
        )

    @classmethod
    def for_summarization(
        cls: Type["FeedbackDataset"],
        use_markdown: bool = False,
        guidelines: str = None,
    ) -> "FeedbackDataset":
        """
        You can use this method to create a basic dataset for summarization tasks.

        Args:
            use_markdown: Set this parameter to True if you want to use markdown in your dataset

        Returns:
            A `FeedbackDataset` object for summarization containing "text" field and a TextQuestion named "summary"
        """
        default_guidelines = (
            "This is a summarization dataset that contains texts. Please summarize the text in the text field."
        )
        return cls(
            fields=[TextField(name="text", use_markdown=use_markdown)],
            questions=[
                TextQuestion(name="summary", description="Write a summary of the text.", use_markdown=use_markdown)
            ],
            guidelines=default_guidelines if guidelines is None else guidelines,
        )

    @classmethod
    def for_translation(
        cls: Type["FeedbackDataset"],
        use_markdown: bool = False,
        guidelines: str = None,
    ) -> "FeedbackDataset":
        """
        You can use this method to create a basic dataset for translation tasks.

        Args:
            use_markdown: Set this parameter to True if you want to use markdown in your dataset

        Returns:
            A `FeedbackDataset` object for translation containing "source" field and a TextQuestion named "target"
        """
        default_guidelines = (
            "This is a translation dataset that contains texts. Please translate the text in the text field."
        )
        return cls(
            fields=[TextField(name="source", use_markdown=use_markdown)],
            questions=[TextQuestion(name="target", description="Translate the text.", use_markdown=use_markdown)],
            guidelines=default_guidelines if guidelines is None else guidelines,
        )

    @classmethod
    def for_sentence_similarity(
        cls: Type["FeedbackDataset"],
        rating_scale: int = 10,
        use_markdown: bool = False,
        guidelines: str = None,
    ) -> "FeedbackDataset":
        """
        You can use this method to create a basic dataset for sentence similarity tasks.

        Args:
            rating_scale: Set this parameter to the number of similarity scale you want to add to your dataset
            use_markdown: Set this parameter to True if you want to use markdown in your dataset

        Returns:
            A `FeedbackDataset` object for sentence similarity containing "sentence1" and "sentence2" fields and a RatingQuestion named "similarity"
        """
        default_guidelines = "This is a sentence similarity dataset that contains two sentences. Please rate the similarity between the two sentences."
        return cls(
            fields=[
                TextField(name="sentence1", use_markdown=use_markdown),
                TextField(name="sentence2", use_markdown=use_markdown),
            ],
            questions=[
                RatingQuestion(
                    name="similarity",
                    values=list(range(1, rating_scale + 1)),
                    description="Rate the similarity between the two sentences.",
                )
            ],
            guidelines=default_guidelines if guidelines is None else guidelines,
        )

    @classmethod
    def for_natural_language_inference(
        cls: Type["FeedbackDataset"],
        labels: Optional[List[str]] = None,
        use_markdown: bool = False,
        guidelines: str = None,
    ) -> "FeedbackDataset":
        """
        You can use this method to create a basic dataset for natural language inference tasks.

        Args:
            labels: A list of labels for your dataset
            use_markdown: Set this parameter to True if you want to use markdown in your dataset

        Returns:
            A `FeedbackDataset` object for natural language inference containing "premise" and "hypothesis" fields and a LabelQuestion named "label"
        """
        default_guidelines = "This is a natural language inference dataset that contains premises and hypotheses. Please choose the correct label for the given premise and hypothesis."
        if labels is None:
            labels = ["entailment", "neutral", "contradiction"]
        return cls(
            fields=[
                TextField(name="premise", use_markdown=use_markdown),
                TextField(name="hypothesis", use_markdown=use_markdown),
            ],
            questions=[LabelQuestion(name="label", labels=labels, description="Choose one of the labels.")],
            guidelines=default_guidelines if guidelines is None else guidelines,
        )

    @classmethod
    def for_supervised_fine_tuning(
        cls: Type["FeedbackDataset"],
        context: bool = False,
        use_markdown: bool = False,
        guidelines: str = None,
    ) -> "FeedbackDataset":
        """
        You can use this method to create a basic dataset for supervised fine-tuning tasks.

        Args:
            context: Set this parameter to True if you want to add context to your dataset
            use_markdown: Set this parameter to True if you want to use markdown in your dataset

        Returns:
            A `FeedbackDataset` object for supervised fine-tuning containing "instruction" and optional "context" field and a TextQuestion named "response"
        """
        default_guidelines = "This is a supervised fine-tuning dataset that contains instructions. Please write the response to the instruction in the response field."
        fields = [
            TextField(name="prompt", use_markdown=use_markdown),
        ]
        if context:
            fields.append(TextField(name="context", use_markdown=use_markdown, required=False))
        return cls(
            fields=fields,
            questions=[
                TextQuestion(
                    name="response", description="Write the response to the instruction.", use_markdown=use_markdown
                )
            ],
            guidelines=guidelines
            if guidelines is not None
            else default_guidelines + " Take the context into account when writing the response."
            if context
            else default_guidelines,
        )

    @classmethod
    def for_preference_modeling(
        cls: Type["FeedbackDataset"],
        context: bool = False,
        use_markdown: bool = False,
        guidelines: str = None,
    ) -> "FeedbackDataset":
        """
        You can use this method to create a basic dataset for preference tasks.

        Args:
            use_markdown: Set this parameter to True if you want to use markdown in your dataset

        Returns:
            A `FeedbackDataset` object for preference containing "prompt", "option1" and "option2" fields and a LabelQuestion named "preference"
        """
        default_guidelines = "This is a preference dataset that contains contexts and options. Please choose the option that you would prefer in the given context."
        fields = [
            TextField(name="prompt", use_markdown=use_markdown),
            TextField(name="response1", title="Response 1", use_markdown=use_markdown),
            TextField(name="response2", title="Response 2", use_markdown=use_markdown),
        ]
        if context:
            fields.insert(1, TextField(name="context", use_markdown=use_markdown, required=False))
        return cls(
            fields=fields,
            questions=[
                LabelQuestion(
                    name="preference", labels=["Response 1", "Response 2"], description="Choose your preference."
                )
            ],
            guidelines=default_guidelines if guidelines is None else guidelines,
        )

    @classmethod
    def for_reward_modeling(
        cls: Type["FeedbackDataset"],
        context: bool = False,
        use_markdown: bool = False,
        guidelines: str = None,
    ) -> "FeedbackDataset":
        return cls.for_preference_modeling(context=context, use_markdown=use_markdown, guidelines=guidelines)

    @classmethod
    def for_proximal_policy_optimization(
        cls: Type["FeedbackDataset"],
        context: bool = False,
        use_markdown: bool = False,
        guidelines: str = None,
    ) -> "FeedbackDataset":
        """
        You can use this method to create a basic dataset for proximal policy optimization tasks.

        Args:
            use_markdown: Set this parameter to True if you want to use markdown in your dataset

        Returns:
            A `FeedbackDataset` object for proximal policy optimization containing "context" and "action" fields and a LabelQuestion named "label"
        """
        default_guidelines = "This is a proximal policy optimization dataset that contains contexts and prompts. Please choose the label that best prompt."
        fields = [TextField(name="prompt", use_markdown=use_markdown)]
        if context:
            fields.append(TextField(name="context", use_markdown=use_markdown, required=False))

        return cls(
            fields=fields,
            questions=[
                LabelQuestion(
                    name="prompt",
                    labels=["good", "bad"],
                    description="Choose one of the labels that best describes the prompt.",
                )
            ],
            guidelines=default_guidelines if guidelines is None else guidelines,
        )

    @classmethod
    def for_direct_preference_optimization(
        cls: Type["FeedbackDataset"],
        context: bool = False,
        use_markdown: bool = False,
        guidelines: str = None,
    ) -> "FeedbackDataset":
        """
        You can use this method to create a basic dataset for direct preference optimization tasks.

        Args:
            context: Set this parameter to True if you want to add context to your dataset
            use_markdown: Set this parameter to True if you want to use markdown in your dataset

        Returns:
            A `FeedbackDataset` object for direct preference optimization containing "prompt", "response1", "response2" with the optional "context" fields and a LabelQuestion named "preference"
        """
        default_guidelines = "This is a direct preference optimization dataset that contains contexts and options. Please choose the option that you would prefer in the given context."
        fields = [
            TextField(name="prompt", use_markdown=use_markdown),
            TextField(name="response1", title="Response 1", use_markdown=use_markdown),
            TextField(name="response2", title="Response 2", use_markdown=use_markdown),
        ]
        if context:
            fields.insert(1, TextField(name="context", use_markdown=use_markdown, required=False))
        return cls(
            fields=fields,
            questions=[
                LabelQuestion(
                    name="preference",
                    labels=["Response 1", "Response 2"],
                    description="Choose the label that is your preference.",
                )
            ],
            guidelines=default_guidelines if guidelines is None else guidelines,
        )

    @classmethod
    def for_retrieval_augmented_generation(
        cls: Type["FeedbackDataset"],
        number_of_retrievals: int = 1,
        rating_scale: int = 10,
        use_markdown: bool = False,
        guidelines: str = None,
    ) -> "FeedbackDataset":
        """
        You can use this method to create a basic dataset for retrieval augmented generation tasks.

        Args:
            number_of_retrievals: Set this parameter to the number of documents you want to add to your dataset
            use_markdown: Set this parameter to True if you want to use markdown in your dataset

        Returns:
            A `FeedbackDataset` object for retrieval augmented generation containing "query" and "retrieved_document" fields and a TextQuestion named "response"
        """
        default_guidelines = "This is a retrieval augmented generation dataset that contains queries and retrieved documents. Please rate the relevancy of retrieved document and write the response to the query in the response field."
        document_fields = [
            TextField(
                name="retrieved_document_" + str(doc + 1),
                title="Retrieved Document " + str(doc + 1),
                use_markdown=use_markdown,
                required=True if doc == 0 else False,
            )
            for doc in range(number_of_retrievals)
        ]

        rating_questions = [
            RatingQuestion(
                name="question_rating_" + str(doc + 1),
                title="Rate the relevance of the user question" + str(doc + 1),
                values=list(range(1, rating_scale + 1)),
                description="Rate the relevance of the retrieved document.",
                required=True if doc == 0 else False,
            )
            for doc in range(number_of_retrievals)
        ]

        total_questions = rating_questions + [
            TextQuestion(
                name="response",
                title="Write a helpful, harmless, accurate response to the query.",
                description="Write the response to the query.",
                use_markdown=use_markdown,
                required=False,
            )
        ]

        return cls(
            fields=[TextField(name="query", use_markdown=use_markdown, required=True)] + document_fields,
            questions=total_questions,
            guidelines=default_guidelines if guidelines is None else guidelines,
        )

