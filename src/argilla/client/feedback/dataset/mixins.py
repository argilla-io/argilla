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

import warnings
from typing import TYPE_CHECKING, Dict, List, Optional, Type, Union
from uuid import UUID

from tqdm import trange

from argilla.client.api import ArgillaSingleton
from argilla.client.feedback.constants import PUSHING_BATCH_SIZE
from argilla.client.feedback.dataset.remote import RemoteFeedbackDataset
from argilla.client.feedback.schemas import (
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    TextField,
    TextQuestion,
)
from argilla.client.feedback.types import AllowedQuestionTypes
from argilla.client.feedback.utils import feedback_dataset_in_argilla
from argilla.client.sdk.v1.datasets import api as datasets_api_v1
from argilla.client.workspaces import Workspace

if TYPE_CHECKING:
    import httpx

    from argilla.client.client import Argilla as ArgillaClient
    from argilla.client.feedback.dataset.local import FeedbackDataset
    from argilla.client.feedback.types import AllowedFieldTypes
    from argilla.client.sdk.v1.datasets.models import FeedbackDatasetModel

warnings.simplefilter("always", DeprecationWarning)


class ArgillaToFromMixin:
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
        name: Optional[str] = None,
        workspace: Optional[Union[str, Workspace]] = None,
        show_progress: bool = False,
    ) -> Optional[RemoteFeedbackDataset]:
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

        if name is None:
            warnings.warn(
                "`push_to_argilla` will no longer be used to push changes to an existing"
                " `FeedbackDataset` in Argilla, but to create a new one instead. So on,"
                " please use `push_to_argilla` with the `name` argument and the `workspace`"
                " if applicable. If you want to update an existing `FeedbackDataset` in"
                " Argilla, you will need to either keep the returned dataset from the"
                " `push_to_argilla` call and the functions will automatically call Argilla"
                " or just call this function and then `from_argilla` to retrieve the"
                " `FeedbackDataset` from Argilla.\n`push_to_argilla` with no arguments will"
                " be deprecated in Argilla v1.15.0.",
                DeprecationWarning,
                stacklevel=1,
            )
            return

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

        warnings.warn(
            "Calling `push_to_argilla` no longer implies that the `FeedbackDataset` can"
            " be updated in Argilla. If you want to push a `FeedbackDataset` and then"
            " update it in Argilla, you need to catch the returned object and use it"
            " instead: `remote_ds = ds.push_to_argilla(...)`. Otherwise, you can just"
            " call `push_to_argilla` and then `from_argilla` to retrieve the"
            " `FeedbackDataset` from Argilla, so the current `FeedbackDataset` can be"
            f" retrieved as `FeedbackDataset.from_argilla(id='{argilla_id}')`.",
            DeprecationWarning,
            stacklevel=1,
        )

        return RemoteFeedbackDataset(
            client=httpx_client,
            id=argilla_id,
            name=name,
            workspace=workspace,
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
        with_records: Optional[bool] = None,  # TODO(alvarobartt): deprecate `with_records`
    ) -> RemoteFeedbackDataset:
        """Retrieves an existing `FeedbackDataset` from Argilla (must have been pushed in advance).

        Note that even though no argument is mandatory, you must provide either the `name`,
        the combination of `name` and `workspace`, or the `id`, otherwise an error will be raised.

        Args:
            name: the name of the `FeedbackDataset` to retrieve from Argilla. Defaults to `None`.
            workspace: the workspace of the `FeedbackDataset` to retrieve from Argilla.
                If not provided, the active workspace will be used.
            id: the ID of the `FeedbackDataset` to retrieve from Argilla. Defaults to `None`.
            with_records: whether to retrieve the records of the `FeedbackDataset` from
                Argilla. Defaults to `None`.

        Returns:
            The `RemoteFeedbackDataset` retrieved from Argilla.

        Raises:
            ValueError: if no `FeedbackDataset` with the provided `name`, `workspace`, or `id` exists in Argilla.

        Examples:
            >>> import argilla as rg
            >>> rg.init(...)
            >>> dataset = rg.FeedbackDataset.from_argilla(name="my_dataset")
        """
        if with_records is not None:
            warnings.warn(
                "`with_records` will no longer be used to retrieve the records of a"
                " `FeedbackDataset` from Argilla, as by default no records will be"
                " fetched from Argilla. To retrieve the records you will need to explicitly"
                " fetch those via `fetch_records` from the returned `RemoteFeedbackDataset`.",
                "\n`with_records` will be deprecated in Argilla v1.15.0.",
                DeprecationWarning,
                stacklevel=1,
            )

        httpx_client: "httpx.Client" = ArgillaSingleton.get().http_client.httpx

        existing_dataset = feedback_dataset_in_argilla(name=name, workspace=workspace, id=id)
        if existing_dataset is None:
            raise ValueError(
                f"Could not find a `FeedbackDataset` in Argilla with name='{name}'."
                if name and not workspace
                else (
                    "Could not find a `FeedbackDataset` in Argilla with name='{name}' and workspace='{workspace}'."
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
            fields=fields,
            questions=questions,
            guidelines=existing_dataset.guidelines or None,
        )
