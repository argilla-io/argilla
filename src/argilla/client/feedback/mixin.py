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
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Union
from uuid import UUID

from pydantic import ValidationError
from tqdm import tqdm, trange

from argilla.client.api import ArgillaSingleton
from argilla.client.feedback.constants import (
    FETCHING_BATCH_SIZE,
    PUSHING_BATCH_SIZE,
)
from argilla.client.feedback.schemas import (
    FeedbackRecord,
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    TextField,
    TextQuestion,
)
from argilla.client.feedback.types import AllowedQuestionTypes
from argilla.client.feedback.utils import (
    feedback_dataset_in_argilla,
    generate_pydantic_schema,
)
from argilla.client.sdk.v1.datasets import api as datasets_api_v1
from argilla.client.workspaces import Workspace

if TYPE_CHECKING:
    import httpx

    from argilla.client.client import Argilla as ArgillaClient
    from argilla.client.feedback.dataset import FeedbackDataset
    from argilla.client.sdk.v1.datasets.models import FeedbackDatasetModel


_LOGGER = logging.getLogger(__name__)


class ArgillaDatasetMixin:
    def fetch_records(self: "FeedbackDataset") -> None:
        """Fetches the records from Argilla or HuggingFace and stores them locally.

        If the dataset has not been saved in Argilla or HuggingFace, a warning will be
        raised and the current records will be returned instead.
        """
        if not self.argilla_id:
            _LOGGER.warning(
                "No records have been logged into neither Argilla nor HuggingFace, so"
                " no records will be fetched. The current records will be returned"
                " instead."
            )
            return self.records

        if self.argilla_id:
            httpx_client: "httpx.Client" = ArgillaSingleton.get().http_client.httpx
            first_batch = datasets_api_v1.get_records(
                client=httpx_client, id=self.argilla_id, offset=0, limit=FETCHING_BATCH_SIZE
            ).parsed

            question_id2name = {question.id: question.name for question in self._questions}
            self._records = []
            for record in first_batch.items:
                record = record.dict(
                    exclude={
                        "inserted_at": ...,
                        "updated_at": ...,
                        "responses": {"__all__": {"id", "inserted_at", "updated_at"}},
                        "suggestions": {"__all__": {"id"}},
                    },
                    exclude_none=True,
                )
                for suggestion in record.get("suggestions", []):
                    suggestion.update({"question_name": question_id2name[suggestion["question_id"]]})
                self._records.append(FeedbackRecord(**record))
            current_batch = 1
            # TODO(alvarobartt): use `total` from Argilla Metrics API
            with tqdm(
                initial=current_batch,
                desc="Fetching records from Argilla",
            ) as pbar:
                while True:
                    batch = datasets_api_v1.get_records(
                        client=httpx_client,
                        id=self.argilla_id,
                        offset=FETCHING_BATCH_SIZE * current_batch,
                        limit=FETCHING_BATCH_SIZE,
                    ).parsed
                    for record in batch.items:
                        record = record.dict(
                            exclude={
                                "inserted_at": ...,
                                "updated_at": ...,
                                "responses": {"__all__": {"id", "inserted_at", "updated_at"}},
                                "suggestions": {"__all__": {"id"}},
                            },
                            exclude_none=True,
                        )
                        for suggestion in record.get("suggestions", []):
                            suggestion.update({"question_name": question_id2name[suggestion["question_id"]]})
                        self._records.append(FeedbackRecord(**record))
                    current_batch += 1
                    pbar.update(1)

                    if len(batch.items) < FETCHING_BATCH_SIZE:
                        break

    def add_records(
        self: "FeedbackDataset",
        records: Union[FeedbackRecord, Dict[str, Any], List[Union[FeedbackRecord, Dict[str, Any]]]],
    ) -> None:
        """Adds the given records to the dataset, and stores them locally. If you're planning to add those
        records either to Argilla or HuggingFace, make sure to call `push_to_argilla` or `push_to_huggingface`,
        respectively, after adding the records.

        Args:
            records: the records to add to the dataset. Can be a single record, a list of records or a dictionary
                with the fields of the record.

        Raises:
            ValueError: if the given records are an empty list.
            ValueError: if the given records are neither: `FeedbackRecord`, list of `FeedbackRecord`,
                list of dictionaries as a record or dictionary as a record.
            ValueError: if the given records do not match the expected schema.

        Examples:
            >>> import argilla as rg
            >>> rg.init(api_url="...", api_key="...")
            >>> dataset = rg.FeedbackDataset(
            ...     fields=[
            ...         rg.TextField(name="text", required=True),
            ...         rg.TextField(name="label", required=True),
            ...     ],
            ...     questions=[
            ...         rg.TextQuestion(
            ...             name="question-1",
            ...             description="This is the first question",
            ...             required=True,
            ...         ),
            ...         rg.RatingQuestion(
            ...             name="question-2",
            ...             description="This is the second question",
            ...             required=True,
            ...             values=[1, 2, 3, 4, 5],
            ...         ),
            ...         rg.LabelQuestion(
            ...             name="question-3",
            ...             description="This is the third question",
            ...             required=True,
            ...             labels=["positive", "negative"],
            ...         ),
            ...         rg.MultiLabelQuestion(
            ...             name="question-4",
            ...             description="This is the fourth question",
            ...             required=True,
            ...             labels=["category-1", "category-2", "category-3"],
            ...         ),
            ...     ],
            ...     guidelines="These are the annotation guidelines.",
            ... )
            >>> dataset.add_records(
            ...     [
            ...         rg.FeedbackRecord(
            ...             fields={"text": "This is the first record", "label": "positive"},
            ...             responses=[{"values": {"question-1": {"value": "This is the first answer"}, "question-2": {"value": 5}, "question-3": {"value": "positive"}, "question-4": {"value": ["category-1"]}}}],
            ...             external_id="entry-1",
            ...         ),
            ...     ]
            ... )
            >>> dataset.records
            [FeedbackRecord(fields={"text": "This is the first record", "label": "positive"}, responses=[ResponseSchema(user_id=None, values={"question-1": ValueSchema(value="This is the first answer"), "question-2": ValueSchema(value=5), "question-3": ValueSchema(value="positive"), "question-4": ValueSchema(value=["category-1"])})], external_id="entry-1")]
        """
        if isinstance(records, list):
            if len(records) == 0:
                raise ValueError("Expected `records` to be a non-empty list of `dict` or `rg.FeedbackRecord`.")
            new_records = []
            for record in records:
                if isinstance(record, dict):
                    new_records.append(FeedbackRecord(**record))
                elif isinstance(record, FeedbackRecord):
                    new_records.append(record)
                else:
                    raise ValueError(
                        f"Expected `records` to be a list of `dict` or `rg.FeedbackRecord`, got type {type(record)} instead."
                    )
            records = new_records
        elif isinstance(records, dict):
            records = [FeedbackRecord(**records)]
        elif isinstance(records, FeedbackRecord):
            records = [records]
        else:
            raise ValueError(
                f"Expected `records` to be a `dict` or `rg.FeedbackRecord`, got type {type(records)} instead."
            )

        if self._fields_schema is None:
            self._fields_schema = generate_pydantic_schema(self.fields)

        for record in records:
            try:
                self._fields_schema.parse_obj(record.fields)
            except ValidationError as e:
                raise ValueError(
                    f"`rg.FeedbackRecord.fields` does not match the expected schema, with exception: {e}"
                ) from e

        if len(self._new_records) > 0:
            self._new_records += records
        else:
            self._new_records = records

    def push_to_argilla(
        self: "FeedbackDataset",
        name: Optional[str] = None,
        workspace: Optional[Union[str, Workspace]] = None,
        show_progress: bool = False,
    ) -> None:
        """Pushes the `FeedbackDataset` to Argilla. If the dataset has been previously pushed to Argilla, it will be updated
        with the new records.

        Note that you may need to `rg.init(...)` with your Argilla credentials before calling this function, otherwise
        the default http://localhost:6900 will be used, which will fail if Argilla is not deployed locally.

        Args:
            name: the name of the dataset to push to Argilla. If not provided, the `argilla_id` will be used if the dataset
                has been previously pushed to Argilla.
            workspace: the workspace where to push the dataset to. If not provided, the active workspace will be used.
            show_progress: the option to choose to show/hide tqdm progress bar while looping over records.
        """
        client: "ArgillaClient" = ArgillaSingleton.get()
        httpx_client: "httpx.Client" = client.http_client.httpx

        if name is None:
            if self.argilla_id is None:
                _LOGGER.warning(
                    "No `name` has been provided, and no dataset has been pushed to Argilla yet, so no records will be"
                    " pushed to Argilla."
                )
                return

            try:
                updated_records: List[FeedbackRecord] = []
                for record in self._records[:]:
                    if record._updated:
                        self._records.remove(record)
                        record._reset_updated()
                        updated_records.append(record)

                if len(self._new_records) < 1 and len(updated_records) < 1:
                    _LOGGER.warning(
                        "Neither new records have been added nor existing records updated"
                        " in the current `FeedbackDataset`, which means there are no"
                        " records to push to Argilla."
                    )
                    return

                question_name2id = {question.name: question.id for question in self._questions}
                if len(updated_records) > 0:
                    for i in trange(
                        0,
                        len(updated_records),
                        PUSHING_BATCH_SIZE,
                        desc="Updating records in Argilla...",
                        disable=show_progress,
                    ):
                        for record in updated_records[i : i + PUSHING_BATCH_SIZE]:
                            for suggestion in record.suggestions:
                                suggestion.question_id = question_name2id[suggestion.question_name]
                                datasets_api_v1.set_suggestion(
                                    client=httpx_client,
                                    record_id=record.id,
                                    **suggestion.dict(exclude={"question_name"}, exclude_none=True),
                                )

                if len(self._new_records) > 0:
                    for i in trange(
                        0,
                        len(self._new_records),
                        PUSHING_BATCH_SIZE,
                        desc="Adding new records to Argilla...",
                        disable=show_progress,
                    ):
                        records = []
                        for record in self._new_records[i : i + PUSHING_BATCH_SIZE]:
                            if record.suggestions:
                                for suggestion in record.suggestions:
                                    suggestion.question_id = question_name2id[suggestion.question_name]
                            records.append(
                                record.dict(
                                    exclude={"id": ..., "suggestions": {"__all__": {"question_name"}}},
                                    exclude_none=True,
                                )
                            )
                        datasets_api_v1.add_records(
                            client=httpx_client,
                            id=self.argilla_id,
                            records=records,
                        )

                self._new_records += updated_records
                for record in self._new_records:
                    record._reset_updated()
                self._records += self._new_records
                self._new_records = []
            except Exception as e:
                raise Exception(
                    f"Failed while adding records to the current `FeedbackDataset` in Argilla with exception: {e}"
                ) from e
        else:
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

            for field in self.fields:
                try:
                    new_field = datasets_api_v1.add_field(
                        client=httpx_client, id=argilla_id, field=field.dict(exclude={"id"})
                    ).parsed
                    if self.argilla_id is None:
                        field.id = new_field.id
                except Exception as e:
                    delete_dataset(dataset_id=argilla_id)
                    raise Exception(
                        f"Failed while adding the field '{field.name}' to the `FeedbackDataset` in Argilla with"
                        f" exception: {e}"
                    ) from e

            question_name2id = {}
            for question in self._questions:
                try:
                    new_question = datasets_api_v1.add_question(
                        client=httpx_client, id=argilla_id, question=question.dict(exclude={"id"})
                    ).parsed
                    if self.argilla_id is None:
                        question.id = new_question.id
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

            if self.argilla_id is not None:
                _LOGGER.warning(
                    "Since the current object is already a `FeedbackDataset` pushed to Argilla, you'll keep on"
                    " interacting with the same dataset in Argilla, even though the one you just pushed holds a"
                    f" different ID ({argilla_id}). So on, if you want to switch to the newly pushed `FeedbackDataset`"
                    f" instead, please use `FeedbackDataset.from_argilla(id='{argilla_id}')`."
                )
                return

            self.argilla_id = argilla_id

            for record in self._new_records:
                record._reset_updated()
            self._records += self._new_records
            self._new_records = []

    @classmethod
    def from_argilla(
        cls: Type["FeedbackDataset"],
        name: Optional[str] = None,
        *,
        workspace: Optional[str] = None,
        id: Optional[str] = None,
        with_records: bool = True,
    ) -> "FeedbackDataset":
        """Retrieves an existing `FeedbackDataset` from Argilla (must have been pushed in advance).

        Note that even no argument is mandatory, you must provide either the `name`, the combination of
        `name` and `workspace`, or the `id`, otherwise an error will be raised.

        Args:
            name: the name of the `FeedbackDataset` to retrieve from Argilla. Defaults to `None`.
            workspace: the workspace of the `FeedbackDataset` to retrieve from Argilla. If not provided, the active
                workspace will be used.
            id: the ID of the `FeedbackDataset` to retrieve from Argilla. Defaults to `None`.
            with_records: whether to retrieve the records of the `FeedbackDataset` from Argilla. Defaults to `True`.

        Returns:
            The `FeedbackDataset` retrieved from Argilla.

        Raises:
            ValueError: if no `FeedbackDataset` with the provided `name` and `workspace` exists in Argilla.
            ValueError: if no `FeedbackDataset` with the provided `id` exists in Argilla.

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
        instance = cls(
            fields=fields,
            questions=questions,
            guidelines=existing_dataset.guidelines or None,
        )
        instance.argilla_id = existing_dataset.id
        if with_records:
            instance.fetch_records()
        return instance
