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
from typing import TYPE_CHECKING, Optional, Type, Union
from uuid import UUID

from tqdm import tqdm, trange

from argilla.client.api import ArgillaSingleton
from argilla.client.feedback.constants import PUSHING_BATCH_SIZE
from argilla.client.feedback.dataset.remote import ArgillaFeedbackDataset
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
    from argilla.client.sdk.v1.datasets.models import FeedbackDatasetModel


class ArgillaToFromMixin:
    def push_to_argilla(
        self: "FeedbackDataset",
        name: Optional[str] = None,
        workspace: Optional[Union[str, Workspace]] = None,
        show_progress: bool = False,
    ) -> ArgillaFeedbackDataset:
        """Pushes the `FeedbackDataset` to Argilla. If the dataset has been previously pushed to Argilla, it will be updated
        with the new records.

        Note that you may need to `rg.init(...)` with your Argilla credentials before calling this function, otherwise
        the default http://localhost:6900 will be used, which will fail if Argilla is not deployed locally.

        Args:
            name: the name of the dataset to push to Argilla. If not provided, the `argilla_id` will be used if the dataset
                has been previously pushed to Argilla.
            workspace: the workspace where to push the dataset to. If not provided, the active workspace will be used.
            show_progress: the option to choose to show/hide tqdm progress bar while looping over records.

        Returns:
            The `FeedbackDataset` pushed to Argilla, which is now an instance of `ArgillaFeedbackDataset`.
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
                " `FeedbackDataset` from Argilla.",
                DeprecationWarning,
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

        # TODO(alvarobartt): remove when `delete` is implemented
        def delete_dataset(dataset_id: UUID) -> None:
            try:
                datasets_api_v1.delete_dataset(client=httpx_client, id=dataset_id)
            except Exception as e:
                raise Exception(
                    f"Failed while deleting the `FeedbackDataset` with ID '{dataset_id}' from Argilla with"
                    f" exception: {e}"
                ) from e

        fields = []
        for field in self._fields:
            try:
                new_field = datasets_api_v1.add_field(
                    client=httpx_client, id=argilla_id, field=field.dict(exclude={"id"})
                ).parsed
                field.id = new_field.id
                fields.append(field)
            except Exception as e:
                delete_dataset(dataset_id=argilla_id)
                raise Exception(
                    f"Failed while adding the field '{field.name}' to the `FeedbackDataset` in Argilla with"
                    f" exception: {e}"
                ) from e

        question_name2id = {}
        questions = []
        for question in self._questions:
            try:
                new_question = datasets_api_v1.add_question(
                    client=httpx_client, id=argilla_id, question=question.dict(exclude={"id"})
                ).parsed
                question.id = new_question.id
                questions.append(question)
                question_name2id[new_question.name] = new_question.id
            except Exception as e:
                delete_dataset(dataset_id=argilla_id)
                raise Exception(
                    f"Failed while adding the question '{question.name}' to the `FeedbackDataset` in Argilla"
                    f" with exception: {e}"
                ) from e

        try:
            datasets_api_v1.publish_dataset(client=httpx_client, id=argilla_id)
        except Exception as e:
            delete_dataset(dataset_id=argilla_id)
            raise Exception(f"Failed while publishing the `FeedbackDataset` in Argilla with exception: {e}") from e

        for i in trange(
            0, len(self.records), PUSHING_BATCH_SIZE, desc="Pushing records to Argilla...", disable=show_progress
        ):
            try:
                records = []
                for record in self.records[i : i + PUSHING_BATCH_SIZE]:
                    if record.suggestions:
                        for suggestion in record.suggestions:
                            suggestion.question_id = question_name2id[suggestion.question_name]
                    records.append(
                        record.dict(
                            exclude={"id": ..., "suggestions": {"__all__": {"question_name"}}}, exclude_none=True
                        )
                    )
                datasets_api_v1.add_records(
                    client=httpx_client,
                    id=argilla_id,
                    records=records,
                )
            except Exception as e:
                delete_dataset(dataset_id=argilla_id)
                raise Exception(
                    f"Failed while adding the records to the `FeedbackDataset` in Argilla with exception: {e}"
                ) from e

        # if self.argilla_id is not None:
        #     _LOGGER.warning(
        #         "Since the current object is already a `FeedbackDataset` pushed to Argilla, you'll keep on"
        #         " interacting with the same dataset in Argilla, even though the one you just pushed holds a"
        #         f" different ID ({argilla_id}). So on, if you want to switch to the newly pushed `FeedbackDataset`"
        #         f" instead, please use `FeedbackDataset.from_argilla(id='{argilla_id}')`."
        #     )
        #     return

        # self.argilla_id = argilla_id

        # for record in self._new_records:
        #     record._reset_updated()
        # self._records += self._new_records
        # self._new_records = []

        return ArgillaFeedbackDataset(
            id=argilla_id,
            name=name,
            workspace=workspace,
            fields=fields,
            questions=questions,
            guidelines=self.guidelines,
        )

    @classmethod
    def from_argilla(
        cls: Type["FeedbackDataset"],
        name: Optional[str] = None,
        *,
        workspace: Optional[str] = None,
        id: Optional[str] = None,
        with_records: bool = True,  # TODO(alvarobartt): deprecate `with_records`
    ) -> ArgillaFeedbackDataset:
        """Retrieves an existing `FeedbackDataset` from Argilla (must have been pushed in advance).

        Note that even though no argument is mandatory, you must provide either the `name`,
        the combination of `name` and `workspace`, or the `id`, otherwise an error will be raised.

        Args:
            name: the name of the `FeedbackDataset` to retrieve from Argilla. Defaults to `None`.
            workspace: the workspace of the `FeedbackDataset` to retrieve from Argilla. If not provided, the active
                workspace will be used.
            id: the ID of the `FeedbackDataset` to retrieve from Argilla. Defaults to `None`.
            with_records: whether to retrieve the records of the `FeedbackDataset` from Argilla. Defaults to `True`.

        Returns:
            The `ArgillaFeedbackDataset` retrieved from Argilla.

        Raises:
            ValueError: if no `FeedbackDataset` with the provided `name` and `workspace` exists in Argilla.
            ValueError: if no `FeedbackDataset` with the provided `id` exists in Argilla.

        Examples:
            >>> import argilla as rg
            >>> rg.init(...)
            >>> dataset = rg.FeedbackDataset.from_argilla(name="my_dataset")
        """
        if with_records:
            warnings.warn(
                "`with_records` will no longer be used to retrieve the records of a"
                " `FeedbackDataset` from Argilla, as by default no records will be"
                " fetched from Argilla. To retrieve the records you will need to explicitly"
                " fetch those via `fetch_records` from the returned `ArgillaFeedbackDataset`."
            )
        httpx_client: "httpx.Client" = ArgillaSingleton.get().http_client.httpx

        existing_dataset = feedback_dataset_in_argilla(name=name, workspace=workspace, id=id)
        if existing_dataset is None:
            raise ValueError(
                f"Could not find a `FeedbackDataset` in Argilla with name='{name}'."
                if name and not workspace
                else (
                    "Could not find a `FeedbackDataset` in Argilla with" f" name='{name}' and workspace='{workspace}'."
                    if name and workspace
                    else (f"Could not find a `FeedbackDataset` in Argilla with ID='{id}'.")
                )
            )

        fields = []
        for field in datasets_api_v1.get_fields(client=httpx_client, id=existing_dataset.id).parsed:
            base_field = field.dict(include={"id", "name", "title", "required"})
            if field.settings["type"] == "text":
                field = TextField(**base_field, use_markdown=field.settings["use_markdown"])
            else:
                raise ValueError(
                    f"Field '{field.name}' is not a supported field in the current Python package version,"
                    " supported field types are: `TextField`."
                )
            fields.append(field)

        questions = []
        for question in datasets_api_v1.get_questions(client=httpx_client, id=existing_dataset.id).parsed:
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

        return ArgillaFeedbackDataset(
            id=existing_dataset.id,
            name=existing_dataset.name,
            workspace=Workspace.from_id(existing_dataset.workspace_id),
            fields=fields,
            questions=questions,
            guidelines=existing_dataset.guidelines or None,
        )
