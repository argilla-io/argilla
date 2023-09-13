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
from argilla.client.feedback.schemas import (
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    TextField,
    TextQuestion,
)
from argilla.client.feedback.schemas.types import AllowedQuestionTypes
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
    from argilla.client.feedback.schemas.types import AllowedFieldTypes
    from argilla.client.sdk.v1.datasets.models import FeedbackDatasetModel


class ArgillaMixin:
    # TODO(alvarobartt): remove when `delete` is implemented
    def __delete_dataset(self: "FeedbackDataset", client: "httpx.Client", id: UUID) -> None:
        try:
            datasets_api_v1.delete_dataset(client=client, id=id)
        except Exception as e:
            raise Exception(
                f"Failed while deleting the `FeedbackDataset` with ID '{id}' from Argilla with" f" exception: {e}"
            ) from e

    def __add_fields(self: "FeedbackDataset", client: "httpx.Client", id: UUID) -> List["AllowedFieldTypes"]:
        fields = []
        for field in self._fields:
            try:
                new_field = datasets_api_v1.add_field(client=client, id=id, field=field.dict(exclude={"id"})).parsed
                field.id = new_field.id
                fields.append(field)
            except Exception as e:
                self.__delete_dataset(client=client, id=id)
                raise Exception(
                    f"Failed while adding the field '{field.name}' to the `FeedbackDataset` in Argilla with"
                    f" exception: {e}"
                ) from e
        return fields

    def __add_questions(self: "FeedbackDataset", client: "httpx.Client", id: UUID) -> List["AllowedQuestionTypes"]:
        questions = []
        for question in self._questions:
            try:
                new_question = datasets_api_v1.add_question(
                    client=client, id=id, question=question.dict(exclude={"id"})
                ).parsed
                question.id = new_question.id
                questions.append(question)
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
        question_mapping: Dict[str, UUID],
        show_progress: bool = True,
    ) -> None:
        for i in trange(
            0, len(self.records), PUSHING_BATCH_SIZE, desc="Pushing records to Argilla...", disable=show_progress
        ):
            try:
                records = []
                for record in self.records[i : i + PUSHING_BATCH_SIZE]:
                    if record.suggestions:
                        for suggestion in record.suggestions:
                            suggestion.question_id = question_mapping[suggestion.question_name]
                    records.append(
                        record.dict(
                            exclude={"id": ..., "suggestions": {"__all__": {"question_name"}}}, exclude_none=True
                        )
                    )
                datasets_api_v1.add_records(client=client, id=id, records=records)
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
        question_name2id = {question.name: question.id for question in questions}

        self.__publish_dataset(client=httpx_client, id=argilla_id)

        self.__push_records(
            client=httpx_client, id=argilla_id, show_progress=show_progress, question_mapping=question_name2id
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
    def __get_fields(client: "httpx.Client", id: UUID) -> List["AllowedFieldTypes"]:
        fields = []
        for field in datasets_api_v1.get_fields(client=client, id=id).parsed:
            base_field = field.dict(include={"id", "name", "title", "required"})
            if field.settings["type"] == "text":
                field = TextField(**base_field, use_markdown=field.settings["use_markdown"])
            else:
                raise ValueError(
                    f"Field '{field.name}' is not a supported field in the current Python package version,"
                    " supported field types are: `TextField`."
                )
            fields.append(field)
        return fields

    @staticmethod
    def __get_questions(client: "httpx.Client", id: UUID) -> List["AllowedQuestionTypes"]:
        questions = []
        for question in datasets_api_v1.get_questions(client=client, id=id).parsed:
            question_dict = question.dict(include={"id", "name", "title", "description", "required"})
            if question.settings["type"] == "rating":
                question = RatingQuestion(**question_dict, values=[v["value"] for v in question.settings["options"]])
            elif question.settings["type"] == "text":
                question = TextQuestion(**question_dict, use_markdown=question.settings["use_markdown"])
            elif question.settings["type"] in ["label_selection", "multi_label_selection", "ranking"]:
                if all([label["value"] == label["text"] for label in question.settings["options"]]):
                    labels = [label["value"] for label in question.settings["options"]]
                else:
                    labels = {label["value"]: label["text"] for label in question.settings["options"]}

                if question.settings["type"] == "label_selection":
                    question = LabelQuestion(
                        **question_dict, labels=labels, visible_labels=question.settings["visible_options"]
                    )
                elif question.settings["type"] == "multi_label_selection":
                    question = MultiLabelQuestion(
                        **question_dict, labels=labels, visible_labels=question.settings["visible_options"]
                    )
                elif question.settings["type"] == "ranking":
                    question = RankingQuestion(**question_dict, values=labels)
            else:
                raise ValueError(
                    f"Question '{question.name}' is not a supported question in the current Python package"
                    f" version, supported question types are: `{'`, `'.join([arg.__name__ for arg in AllowedQuestionTypes.__args__])}`."
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
