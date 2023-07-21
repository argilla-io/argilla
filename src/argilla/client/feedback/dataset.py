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
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Literal, Optional, Union
from uuid import UUID

from pydantic import ValidationError
from tqdm import tqdm, trange

from argilla.client.api import ArgillaSingleton
from argilla.client.feedback.constants import (
    FETCHING_BATCH_SIZE,
    PUSHING_BATCH_SIZE,
)
from argilla.client.feedback.integrations.huggingface import HuggingFaceDatasetMixin
from argilla.client.feedback.schemas import (
    FeedbackRecord,
    FieldSchema,
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    TextField,
    TextQuestion,
)
from argilla.client.feedback.training.schemas import (
    TrainingTaskMappingForTextClassification,
)
from argilla.client.feedback.types import AllowedFieldTypes, AllowedQuestionTypes
from argilla.client.feedback.unification import (
    LabelQuestionStrategy,
    MultiLabelQuestionStrategy,
    RankingQuestionStrategy,
    RatingQuestionStrategy,
)
from argilla.client.feedback.utils import (
    feedback_dataset_in_argilla,
    generate_pydantic_schema,
)
from argilla.client.models import Framework
from argilla.client.sdk.v1.datasets import api as datasets_api_v1
from argilla.client.workspaces import Workspace
from argilla.utils.dependency import require_version, requires_version

if TYPE_CHECKING:
    import httpx
    from datasets import Dataset

    from argilla.client.client import Argilla as ArgillaClient
    from argilla.client.sdk.v1.datasets.models import FeedbackDatasetModel

_LOGGER = logging.getLogger(__name__)


class FeedbackDataset(HuggingFaceDatasetMixin):
    """Class to work with `FeedbackDataset`s either locally, or remotely (Argilla or HuggingFace Hub).

    Args:
        guidelines: contains the guidelines for annotating the dataset.
        fields: contains the fields that will define the schema of the records in the dataset.
        questions: contains the questions that will be used to annotate the dataset.

    Attributes:
        guidelines: contains the guidelines for annotating the dataset.
        fields: contains the fields that will define the schema of the records in the dataset.
        questions: contains the questions that will be used to annotate the dataset.
        records: contains the records of the dataset if any. Otherwise it is an empty list.
        argilla_id: contains the id of the dataset in Argilla, if it has been uploaded (via `self.push_to_argilla()`). Otherwise, it is `None`.

    Raises:
        TypeError: if `guidelines` is not a string.
        TypeError: if `fields` is not a list of `FieldSchema`.
        ValueError: if `fields` does not contain at least one required field.
        TypeError: if `questions` is not a list of `TextQuestion`, `RatingQuestion`,
            `LabelQuestion`, and/or `MultiLabelQuestion`.
        ValueError: if `questions` does not contain at least one required question.

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
        ...             responses=[{"values": {"question-1": {"value": "This is the first answer"}, "question-2": {"value": 5}}}],
        ...             external_id="entry-1",
        ...         ),
        ...     ]
        ... )
        >>> dataset.records
        [FeedbackRecord(fields={"text": "This is the first record", "label": "positive"}, responses=[ResponseSchema(user_id=None, values={"question-1": ValueSchema(value="This is the first answer"), "question-2": ValueSchema(value=5), "question-3": ValueSchema(value="positive"), "question-4": ValueSchema(value=["category-1"])})], external_id="entry-1")]
        >>> dataset.push_to_argilla(name="my-dataset", workspace="my-workspace")
        >>> dataset.argilla_id
        "..."
        >>> dataset = rg.FeedbackDataset.from_argilla(argilla_id="...")
        >>> dataset.records
        [FeedbackRecord(fields={"text": "This is the first record", "label": "positive"}, responses=[ResponseSchema(user_id=None, values={"question-1": ValueSchema(value="This is the first answer"), "question-2": ValueSchema(value=5), "question-3": ValueSchema(value="positive"), "question-4": ValueSchema(value=["category-1"])})], external_id="entry-1")]
    """

    argilla_id: Optional[UUID] = None

    def __init__(
        self,
        *,
        fields: List[AllowedFieldTypes],
        questions: List[AllowedQuestionTypes],
        guidelines: Optional[str] = None,
    ) -> None:
        """Initializes a `FeedbackDataset` instance locally.

        Args:
            fields: contains the fields that will define the schema of the records in the dataset.
            questions: contains the questions that will be used to annotate the dataset.
            guidelines: contains the guidelines for annotating the dataset. Defaults to `None`.

        Raises:
            TypeError: if `fields` is not a list of `FieldSchema`.
            ValueError: if `fields` does not contain at least one required field.
            TypeError: if `questions` is not a list of `TextQuestion`, `RatingQuestion`,
                `LabelQuestion`, and/or `MultiLabelQuestion`.
            ValueError: if `questions` does not contain at least one required question.
            TypeError: if `guidelines` is not None and not a string.
            ValueError: if `guidelines` is an empty string.

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
        """
        if not isinstance(fields, list):
            raise TypeError(f"Expected `fields` to be a list, got {type(fields)} instead.")

        any_required = False
        unique_names = set()
        for field in fields:
            if not isinstance(field, FieldSchema):
                raise TypeError(f"Expected `fields` to be a list of `FieldSchema`, got {type(field)} instead.")
            if field.name in unique_names:
                raise ValueError(f"Expected `fields` to have unique names, got {field.name} twice instead.")
            unique_names.add(field.name)
            if not any_required and field.required:
                any_required = True
        if not any_required:
            raise ValueError("At least one `FieldSchema` in `fields` must be required (`required=True`).")
        self.__fields = fields
        self.__fields_schema = None

        if not isinstance(questions, list):
            raise TypeError(f"Expected `questions` to be a list, got {type(questions)} instead.")

        any_required = False
        unique_names = set()
        for question in questions:
            if not isinstance(question, AllowedQuestionTypes.__args__):
                raise TypeError(
                    "Expected `questions` to be a list of"
                    f" `{'`, `'.join([arg.__name__ for arg in AllowedQuestionTypes.__args__])}` got a"
                    f" question in the list with type {type(question)} instead."
                )
            if question.name in unique_names:
                raise ValueError(f"Expected `questions` to have unique names, got {question.name} twice instead.")
            unique_names.add(question.name)
            if not any_required and question.required:
                any_required = True
        if not any_required:
            raise ValueError("At least one question in `questions` must be required (`required=True`).")
        self.__questions = questions

        if guidelines is not None:
            if not isinstance(guidelines, str):
                raise TypeError(
                    f"Expected `guidelines` to be either None (default) or a string, got {type(guidelines)} instead."
                )
            if len(guidelines) < 1:
                raise ValueError(
                    "Expected `guidelines` to be either None (default) or a non-empty string, minimum length is 1."
                )
        self.__guidelines = guidelines

        self.__records: List[FeedbackRecord] = []
        self.__new_records: List[FeedbackRecord] = []

    def __len__(self) -> int:
        """Returns the number of records in the dataset."""
        return len(self.records)

    def __getitem__(self, key: Union[slice, int]) -> Union[FeedbackRecord, List[FeedbackRecord]]:
        """Returns the record(s) at the given index(es).

        Args:
            key: the index(es) of the record(s) to return. Can either be a single index or a slice.

        Returns:
            Either the record of the given index, or a list with the records at the given indexes.
        """
        if len(self.records) < 1:
            raise RuntimeError(
                "In order to get items from `rg.FeedbackDataset` you need to either add"
                " them first with `add_records` or fetch them from Argilla or"
                " HuggingFace with `fetch_records`."
            )
        if isinstance(key, int) and len(self.records) < key:
            raise IndexError(f"This dataset contains {len(self)} records, so index {key} is out of range.")
        return self.records[key]

    def __del__(self) -> None:
        """When the dataset object is deleted, delete all the records as well to avoid memory leaks."""
        if hasattr(self, "__records") and self.__records is not None:
            del self.__records
        if hasattr(self, "__new_records") and self.__new_records is not None:
            del self.__new_records

    def __enter__(self) -> "FeedbackDataset":
        """Allows the dataset to be used as a context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """When the context manager is exited, delete all the records as well to avoid memory leaks."""
        self.__del__()

    @property
    def guidelines(self) -> str:
        """Returns the guidelines for annotating the dataset."""
        return self.__guidelines

    @guidelines.setter
    def guidelines(self, guidelines: str) -> None:
        """Sets the guidelines for annotating the dataset."""
        if not isinstance(guidelines, str):
            raise TypeError(f"Expected `guidelines` to be a string, got {type(guidelines)} instead.")
        self.__guidelines = guidelines

    @property
    def fields(self) -> List[AllowedFieldTypes]:
        """Returns the fields that define the schema of the records in the dataset."""
        return self.__fields

    def field_by_name(self, name: str) -> AllowedFieldTypes:
        for field in self.__fields:
            if field.name == name:
                return field
        raise ValueError(
            f"Field with name='{name}' not found, available field names are:"
            f" {', '.join(f.name for f in self.__fields)}"
        )

    @property
    def questions(self) -> List[AllowedQuestionTypes]:
        """Returns the questions that will be used to annotate the dataset."""
        return self.__questions

    def question_by_name(self, name: str) -> AllowedQuestionTypes:
        for question in self.__questions:
            if question.name == name:
                return question
        raise ValueError(
            f"Question with name='{name}' not found, available question names are:"
            f" {', '.join(q.name for q in self.__questions)}"
        )

    @property
    def records(self) -> List[FeedbackRecord]:
        """Returns the all the records in the dataset."""
        return self.__records + self.__new_records

    def fetch_records(self) -> None:
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

            question_id2name = {question.id: question.name for question in self.__questions}
            self.__records = []
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
                self.__records.append(FeedbackRecord(**record))
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
                        self.__records.append(FeedbackRecord(**record))
                    current_batch += 1
                    pbar.update(1)

                    if len(batch.items) < FETCHING_BATCH_SIZE:
                        break

    def add_records(
        self,
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

        if self.__fields_schema is None:
            self.__fields_schema = generate_pydantic_schema(self.__fields)

        for record in records:
            try:
                self.__fields_schema.parse_obj(record.fields)
            except ValidationError as e:
                raise ValueError(
                    f"`rg.FeedbackRecord.fields` does not match the expected schema, with exception: {e}"
                ) from e

        if len(self.__new_records) > 0:
            self.__new_records += records
        else:
            self.__new_records = records

    def iter(self, batch_size: Optional[int] = FETCHING_BATCH_SIZE) -> Iterator[List[FeedbackRecord]]:
        """Returns an iterator over the records in the dataset.

        Args:
            batch_size: the size of the batches to return. Defaults to 100.
        """
        for i in range(0, len(self.records), batch_size):
            yield self.records[i : i + batch_size]

    def push_to_argilla(
        self,
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
                for record in self.__records[:]:
                    if record._updated:
                        self.__records.remove(record)
                        record._reset_updated()
                        updated_records.append(record)

                if len(self.__new_records) < 1 and len(updated_records) < 1:
                    _LOGGER.warning(
                        "Neither new records have been added nor existing records updated"
                        " in the current `FeedbackDataset`, which means there are no"
                        " records to push to Argilla."
                    )
                    return

                question_name2id = {question.name: question.id for question in self.__questions}
                if len(updated_records) > 0:
                    for i in trange(
                        0,
                        len(updated_records),
                        PUSHING_BATCH_SIZE,
                        desc="Updating records in Argilla...",
                        disable=show_progress,
                    ):
                        for record in updated_records[i : i + PUSHING_BATCH_SIZE]:
                            if not record.id:
                                warnings.warn(
                                    "A record is already pushed to Argilla but no record id found, which means"
                                    " that the `FeedbackRecord` has been pushed to  Argilla, but hasn't been fetched,"
                                    " so the `id` is missing. Record update will be skipped for this record"
                                )
                                if record.suggestions:
                                    warnings.warn(
                                        "The `suggestions` have been provided, but the `id`"
                                        " is not set. To solve that, you can simply call"
                                        " `FeedbackDataset.fetch_records()` to fetch them and"
                                        " automatically set the `id`, to call `set_suggestions` on top of that."
                                    )
                                continue
                            for suggestion in record.suggestions:
                                suggestion.question_id = question_name2id[suggestion.question_name]
                                datasets_api_v1.set_suggestion(
                                    client=httpx_client,
                                    record_id=record.id,
                                    **suggestion.dict(exclude={"question_name"}, exclude_none=True),
                                )

                if len(self.__new_records) > 0:
                    for i in trange(
                        0,
                        len(self.__new_records),
                        PUSHING_BATCH_SIZE,
                        desc="Adding new records to Argilla...",
                        disable=show_progress,
                    ):
                        records = []
                        for record in self.__new_records[i : i + PUSHING_BATCH_SIZE]:
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

                self.__new_records += updated_records
                for record in self.__new_records:
                    record._reset_updated()
                self.__records += self.__new_records
                self.__new_records = []
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

            for field in self.__fields:
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
            for question in self.__questions:
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

            for record in self.__new_records:
                record._reset_updated()
            self.__records += self.__new_records
            self.__new_records = []

    @classmethod
    def from_argilla(
        cls,
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

    @requires_version("datasets")
    def format_as(self, format: Literal["datasets"]) -> "Dataset":
        """Formats the `FeedbackDataset` as a `datasets.Dataset` object.

        Args:
            format: the format to use to format the `FeedbackDataset`. Currently supported formats are:
                `datasets`.

        Returns:
            The `FeedbackDataset.records` formatted as a `datasets.Dataset` object.

        Raises:
            ValueError: if the provided format is not supported.

        Examples:
            >>> import argilla as rg
            >>> rg.init(...)
            >>> dataset = rg.FeedbackDataset.from_argilla(name="my-dataset")
            >>> huggingface_dataset = dataset.format_as("datasets")
        """
        if format == "datasets":
            return self._huggingface_format(self)
        raise ValueError(f"Unsupported format '{format}'.")

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
            else:
                raise ValueError(f"Question {question} is not supported yet")

        strategy.unify_responses(self.records, question)

    def prepare_for_training(
        self,
        framework: Union[Framework, str],
        task_mapping: TrainingTaskMappingForTextClassification,
        train_size: Optional[float] = 1,
        test_size: Optional[float] = None,
        seed: Optional[int] = None,
        fetch_records: bool = True,
        lang: Optional[str] = None,
    ):
        if isinstance(framework, str):
            framework = Framework(framework)

        # validate train and test sizes
        if train_size is None:
            train_size = 1
        if test_size is None:
            test_size = 1 - train_size

        # check if all numbers are larger than 0
        if not [abs(train_size), abs(test_size)] == [train_size, test_size]:
            raise ValueError("`train_size` and `test_size` must be larger than 0.")
        # check if train sizes sum up to 1
        if not (train_size + test_size) == 1:
            raise ValueError("`train_size` and `test_size` must sum to 1.")

        if test_size == 0:
            test_size = None

        if fetch_records:
            self.fetch_records()

        if isinstance(task_mapping, TrainingTaskMappingForTextClassification):
            self.unify_responses(question=task_mapping.label.question, strategy=task_mapping.label.strategy)
        else:
            raise ValueError(f"Training data {type(task_mapping)} is not supported yet")

        data = task_mapping._format_data(self.records)
        if framework in [
            Framework.TRANSFORMERS,
            Framework.SETFIT,
            Framework.SPAN_MARKER,
            Framework.PEFT,
        ]:
            return task_mapping._prepare_for_training_with_transformers(
                data=data, train_size=train_size, seed=seed, framework=framework
            )
        elif framework is Framework.SPACY or framework is Framework.SPACY_TRANSFORMERS:
            require_version("spacy")
            import spacy

            if lang is None:
                _LOGGER.warning("spaCy `lang` is not provided. Using `en`(English) as default language.")
                lang = spacy.blank("en")
            elif lang.isinstance(str):
                if len(lang) == 2:
                    lang = spacy.blank(lang)
                else:
                    lang = spacy.load(lang)
            return task_mapping._prepare_for_training_with_spacy(data=data, train_size=train_size, seed=seed, lang=lang)
        elif framework is Framework.SPARK_NLP:
            return task_mapping._prepare_for_training_with_spark_nlp(data=data, train_size=train_size, seed=seed)
        elif framework is Framework.OPENAI:
            return task_mapping._prepare_for_training_with_openai(data=data, train_size=train_size, seed=seed)
        else:
            raise NotImplementedError(
                f"Framework {framework} is not supported. Choose from: {[e.value for e in Framework]}"
            )
