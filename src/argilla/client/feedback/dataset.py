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

import json
import logging
import tempfile
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Literal, Optional, Union
from uuid import UUID

from pydantic import (
    ValidationError,
    parse_obj_as,
)
from tqdm import tqdm

import argilla as rg
from argilla.client.feedback.config import FeedbackDatasetConfig
from argilla.client.feedback.constants import (
    FETCHING_BATCH_SIZE,
    FIELD_TYPE_TO_PYTHON_TYPE,
    PUSHING_BATCH_SIZE,
)
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
from argilla.client.feedback.typing import AllowedFieldTypes, AllowedQuestionTypes
from argilla.client.feedback.unification import (
    LabelQuestionStrategy,
    MultiLabelQuestionStrategy,
    RatingQuestionStrategy,
)
from argilla.client.feedback.utils import (
    feedback_dataset_in_argilla,
    generate_pydantic_schema,
)
from argilla.client.models import Framework
from argilla.client.sdk.v1.datasets import api as datasets_api_v1
from argilla.utils.dependency import require_version, requires_version

if TYPE_CHECKING:
    import httpx
    from datasets import Dataset

    from argilla.client.client import Argilla as ArgillaClient
    from argilla.client.sdk.v1.datasets.models import (
        FeedbackDatasetModel,
        FeedbackFieldModel,
        FeedbackQuestionModel,
    )

_LOGGER = logging.getLogger(__name__)


class FeedbackDataset:
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

        self.__records = []
        self.__new_records = []

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
    def fields(self) -> List["FeedbackFieldModel"]:
        """Returns the fields that define the schema of the records in the dataset."""
        return self.__fields

    def field_by_name(self, name: str) -> Dict[str, FieldSchema]:
        for item in self.fields:
            if item.name == name:
                return item
        raise KeyError(f"Field with name '{name}' not found in self.fields")

    @property
    def questions(self) -> List["FeedbackQuestionModel"]:
        """Returns the questions that will be used to annotate the dataset."""
        return self.__questions

    def question_by_name(self, name: str) -> Dict[str, "FeedbackQuestionModel"]:
        for item in self.questions:
            if item.name == name:
                return item
        raise KeyError(f"Question with name '{name}' not found in self.questions")

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

        # TODO(alvarobartt): create `ArgillaMixIn` and `HuggingFaceMixIn` classes to inherit their specific methods
        if self.argilla_id:
            httpx_client: "httpx.Client" = rg.active_client().http_client.httpx
            first_batch = datasets_api_v1.get_records(
                client=httpx_client, id=self.argilla_id, offset=0, limit=FETCHING_BATCH_SIZE
            ).parsed
            self.__records = parse_obj_as(List[FeedbackRecord], first_batch.items)
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
                    records = parse_obj_as(List[FeedbackRecord], batch.items)
                    self.__records += records
                    current_batch += 1
                    pbar.update(1)

                    if len(records) < FETCHING_BATCH_SIZE:
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
            self.__fields_schema = generate_pydantic_schema(self.fields)

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
        workspace: Optional[Union[str, rg.Workspace]] = None,
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
        client: "ArgillaClient" = rg.active_client()
        httpx_client: "httpx.Client" = client.http_client.httpx

        if name is None:
            if self.argilla_id is None:
                _LOGGER.warning(
                    "No `name` has been provided, and no dataset has been pushed to Argilla yet, so no records will be"
                    " pushed to Argilla."
                )
                return

            if len(self.__new_records) < 1:
                _LOGGER.warning(
                    "No new records have been added to the current `FeedbackTask` dataset, so no records will be pushed"
                    " to Argilla."
                )
                return

            try:
                for i in range(0, len(self.__new_records), PUSHING_BATCH_SIZE):
                    datasets_api_v1.add_records(
                        client=httpx_client,
                        id=self.argilla_id,
                        records=[
                            record.dict()
                            for record in tqdm(
                                self.__new_records[i : i + PUSHING_BATCH_SIZE],
                                desc="Pushing records to Argilla...",
                                disable=show_progress,
                            )
                        ],
                    )
                self.__records += self.__new_records
                self.__new_records = []
            except Exception as e:
                raise Exception(
                    f"Failed while adding new records to the current `FeedbackTask` dataset in Argilla with exception: {e}"
                ) from e
        else:
            if workspace is None:
                workspace = rg.Workspace.from_name(client.get_workspace())

            if isinstance(workspace, str):
                workspace = rg.Workspace.from_name(workspace)

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
                raise Exception(
                    f"Failed while creating the `FeedbackTask` dataset in Argilla with exception: {e}"
                ) from e

            def delete_dataset(dataset_id: UUID) -> None:
                try:
                    datasets_api_v1.delete_dataset(client=httpx_client, id=dataset_id)
                except Exception as e:
                    raise Exception(
                        f"Failed while deleting the `FeedbackTask` dataset with ID '{dataset_id}' from Argilla with"
                        f" exception: {e}"
                    ) from e

            for field in self.fields:
                try:
                    datasets_api_v1.add_field(client=httpx_client, id=argilla_id, field=field.dict())
                except Exception as e:
                    delete_dataset(dataset_id=argilla_id)
                    raise Exception(
                        f"Failed while adding the field '{field.name}' to the `FeedbackTask` dataset in Argilla with"
                        f" exception: {e}"
                    ) from e

            for question in self.questions:
                try:
                    datasets_api_v1.add_question(client=httpx_client, id=argilla_id, question=question.dict())
                except Exception as e:
                    delete_dataset(dataset_id=argilla_id)
                    raise Exception(
                        f"Failed while adding the question '{question.name}' to the `FeedbackTask` dataset in Argilla"
                        f" with exception: {e}"
                    ) from e

            try:
                datasets_api_v1.publish_dataset(client=httpx_client, id=argilla_id)
            except Exception as e:
                delete_dataset(dataset_id=argilla_id)
                raise Exception(
                    f"Failed while publishing the `FeedbackTask` dataset in Argilla with exception: {e}"
                ) from e

            for batch in self.iter():
                try:
                    datasets_api_v1.add_records(
                        client=httpx_client,
                        id=argilla_id,
                        records=[
                            record.dict()
                            for record in tqdm(batch, desc="Pushing records to Argilla...", disable=show_progress)
                        ],
                    )
                except Exception as e:
                    delete_dataset(dataset_id=argilla_id)
                    raise Exception(
                        f"Failed while adding the records to the `FeedbackTask` dataset in Argilla with exception: {e}"
                    ) from e

            self.__records += self.__new_records
            self.__new_records = []

            if self.argilla_id is not None:
                _LOGGER.warning(
                    "Since the current object is already a `FeedbackDataset` pushed to Argilla, you'll keep on"
                    " interacting with the same dataset in Argilla, even though the one you just pushed holds a"
                    f" different ID ({argilla_id}). So on, if you want to switch to the newly pushed `FeedbackDataset`"
                    f" instead, please use `FeedbackDataset.from_argilla(id='{argilla_id}')`."
                )
                return
            self.argilla_id = argilla_id

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
        httpx_client: "httpx.Client" = rg.active_client().http_client.httpx

        existing_dataset = feedback_dataset_in_argilla(name=name, workspace=workspace, id=id)
        if existing_dataset is None:
            raise ValueError(
                f"Could not find a `FeedbackTask` dataset in Argilla with name='{name}'."
                if name and not workspace
                else (
                    "Could not find a `FeedbackTask` dataset in Argilla with"
                    f" name='{name}' and workspace='{workspace}'."
                    if name and workspace
                    else (f"Could not find a `FeedbackTask` dataset in Argilla with ID='{id}'.")
                )
            )

        fields = []
        for field in datasets_api_v1.get_fields(client=httpx_client, id=existing_dataset.id).parsed:
            base_field = field.dict(include={"name", "title", "required"})
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
            question_dict = question.dict(include={"name", "title", "description", "required"})
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
        self = cls(
            fields=fields,
            questions=questions,
            guidelines=existing_dataset.guidelines or None,
        )
        self.argilla_id = existing_dataset.id
        if with_records:
            self.fetch_records()
        return self

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
            from datasets import Dataset, Features, Sequence, Value

            dataset = {"metadata": []}
            features = {}
            for field in self.fields:
                if field.settings["type"] not in FIELD_TYPE_TO_PYTHON_TYPE.keys():
                    raise ValueError(
                        f"Field {field.name} has an unsupported type: {field.settings['type']}, for the moment"
                        f" only the following types are supported: {list(FIELD_TYPE_TO_PYTHON_TYPE.keys())}"
                    )
                features[field.name] = Value(dtype="string", id="field")
                if field.name not in dataset:
                    dataset[field.name] = []
            for question in self.questions:
                if question.settings["type"] in ["text", "label_selection"]:
                    value = Value(dtype="string")
                elif question.settings["type"] == "rating":
                    value = Value(dtype="int32")
                elif question.settings["type"] == "ranking":
                    value = Sequence({"rank": Value(dtype="uint8"), "value": Value(dtype="string")})
                elif question.settings["type"] in "multi_label_selection":
                    value = Sequence(Value(dtype="string"))
                else:
                    raise ValueError(
                        f"Question {question.name} has an unsupported type: {question.settings['type']}, for the"
                        " moment only the following types are supported: 'text', 'rating', 'label_selection',"
                        " 'multi_label_selection', and 'ranking'."
                    )
                # TODO(alvarobartt): if we constraint ranges from 0 to N, then we can use `ClassLabel` for ratings
                features[question.name] = Sequence(
                    {
                        "user_id": Value(dtype="string"),
                        "value": value,
                        "status": Value(dtype="string"),
                    },
                    id="question",
                )
                if question.name not in dataset:
                    dataset[question.name] = []
            features["external_id"] = Value(dtype="string", id="external_id")
            dataset["external_id"] = []

            for record in self.records:
                for field in self.fields:
                    dataset[field.name].append(record.fields[field.name])
                for question in self.questions:
                    if not record.responses:
                        dataset[question.name].append(None)
                        continue
                    responses = []
                    for response in record.responses:
                        if question.name not in response.values:
                            responses.append(None)
                            continue
                        if question.settings["type"] == "ranking":
                            responses.append([r.dict() for r in response.values[question.name].value])
                        else:
                            responses.append(response.values[question.name].value)
                    dataset[question.name].append(
                        {
                            "user_id": [r.user_id for r in record.responses],
                            "value": responses,
                            "status": [r.status for r in record.responses],
                        }
                    )
                dataset["metadata"].append(json.dumps(record.metadata) if record.metadata else None)
                dataset["external_id"].append(record.external_id or None)

            if len(dataset["metadata"]) > 0:
                features["metadata"] = Value(dtype="string")
            else:
                del dataset["metadata"]

            return Dataset.from_dict(
                dataset,
                features=Features(features),
            )
        raise ValueError(f"Unsupported format '{format}'.")

    @requires_version("huggingface_hub")
    def push_to_huggingface(self, repo_id: str, generate_card: Optional[bool] = True, *args, **kwargs) -> None:
        """Pushes the `FeedbackDataset` to the HuggingFace Hub. If the dataset has been previously pushed to the
        HuggingFace Hub, it will be updated instead. Note that some params as `private` have no effect at all
        when a dataset is previously uploaded to the HuggingFace Hub.

        Args:
            repo_id: the ID of the HuggingFace Hub repo to push the `FeedbackDataset` to.
            generate_card: whether to generate a dataset card for the `FeedbackDataset` in the HuggingFace Hub. Defaults
                to `True`.
            *args: the args to pass to `datasets.Dataset.push_to_hub`.
            **kwargs: the kwargs to pass to `datasets.Dataset.push_to_hub`.
        """
        import huggingface_hub
        from huggingface_hub import DatasetCardData, HfApi
        from packaging.version import parse as parse_version

        if parse_version(huggingface_hub.__version__) < parse_version("0.14.0"):
            _LOGGER.warning(
                "Recommended `huggingface_hub` version is 0.14.0 or higher, and you have"
                f" {huggingface_hub.__version__}, so in case you have any issue when pushing the dataset to the"
                " HuggingFace Hub upgrade it as `pip install huggingface_hub --upgrade`."
            )

        if len(self) < 1:
            raise ValueError(
                "Cannot push an empty `rg.FeedbackDataset` to the HuggingFace Hub, please make sure to add at"
                " least one record, via the method `add_records`."
            )

        hfds = self.format_as("datasets")
        hfds.push_to_hub(repo_id, *args, **kwargs)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".cfg", delete=False) as f:
            f.write(
                FeedbackDatasetConfig(fields=self.fields, questions=self.questions, guidelines=self.guidelines).json()
            )
            f.flush()

            HfApi().upload_file(
                path_or_fileobj=f.name,
                path_in_repo="argilla.cfg",
                repo_id=repo_id,
                repo_type="dataset",
                token=kwargs.get("token"),
            )

        if generate_card:
            from argilla.client.feedback.card import (
                ArgillaDatasetCard,
                size_categories_parser,
            )

            card = ArgillaDatasetCard.from_template(
                card_data=DatasetCardData(
                    size_categories=size_categories_parser(len(self.records)),
                    tags=["rlfh", "argilla", "human-feedback"],
                ),
                repo_id=repo_id,
                argilla_fields=self.fields,
                argilla_questions=self.questions,
                argilla_guidelines=self.guidelines,
                argilla_record=json.loads(self.records[0].json()),
                huggingface_record=hfds[0],
            )
            card.push_to_hub(repo_id, repo_type="dataset", token=kwargs.get("token"))

    @classmethod
    @requires_version("datasets")
    @requires_version("huggingface_hub")
    def from_huggingface(cls, repo_id: str, *args: Any, **kwargs: Any) -> "FeedbackDataset":
        """Loads a `FeedbackDataset` from the HuggingFace Hub.

        Args:
            repo_id: the ID of the HuggingFace Hub repo to load the `FeedbackDataset` from.
            *args: the args to pass to `datasets.Dataset.load_from_hub`.
            **kwargs: the kwargs to pass to `datasets.Dataset.load_from_hub`.

        Returns:
            A `FeedbackDataset` loaded from the HuggingFace Hub.
        """
        import huggingface_hub
        from datasets import DatasetDict, load_dataset
        from huggingface_hub import hf_hub_download
        from packaging.version import parse as parse_version

        if parse_version(huggingface_hub.__version__) < parse_version("0.14.0"):
            _LOGGER.warning(
                "Recommended `huggingface_hub` version is 0.14.0 or higher, and you have"
                f" {huggingface_hub.__version__}, so in case you have any issue when pushing the dataset to the"
                " HuggingFace Hub upgrade it as `pip install huggingface_hub --upgrade`."
            )

        if "token" in kwargs:
            auth = kwargs.pop("token")
        elif "use_auth_token" in kwargs:
            auth = kwargs.pop("use_auth_token")
        else:
            auth = None

        hub_auth = (
            {"use_auth_token": auth}
            if parse_version(huggingface_hub.__version__) < parse_version("0.11.0")
            else {"token": auth}
        )
        config_path = hf_hub_download(
            repo_id=repo_id,
            filename="argilla.cfg",
            repo_type="dataset",
            **hub_auth,
        )
        with open(config_path, "r") as f:
            config = FeedbackDatasetConfig.parse_raw(f.read())

        cls = cls(
            fields=config.fields,
            questions=config.questions,
            guidelines=config.guidelines,
        )

        hfds = load_dataset(repo_id, use_auth_token=auth, *args, **kwargs)
        if isinstance(hfds, DatasetDict) and "split" not in kwargs:
            if len(hfds.keys()) > 1:
                raise ValueError(
                    "Only one dataset can be loaded at a time, use `split` to select a split, available splits"
                    f" are: {', '.join(hfds.keys())}."
                )
            hfds = hfds[list(hfds.keys())[0]]

        for index in range(len(hfds)):
            responses = {}
            for question in cls.questions:
                if hfds[index][question.name] is None or len(hfds[index][question.name]) < 1:
                    continue
                for user_id, value, status in zip(
                    hfds[index][question.name]["user_id"],
                    hfds[index][question.name]["value"],
                    hfds[index][question.name]["status"],
                ):
                    if user_id not in responses:
                        responses[user_id] = {
                            "user_id": user_id,
                            "status": status,
                            "values": {},
                        }
                    if question.settings["type"] == "ranking":
                        value = [{"rank": r, "value": v} for r, v in zip(value["rank"], value["value"])]
                    responses[user_id]["values"].update({question.name: {"value": value}})

            metadata = None
            if "metadata" in hfds[index] and hfds[index]["metadata"] is not None:
                metadata = json.loads(hfds[index]["metadata"])

            cls.__records.append(
                FeedbackRecord(
                    fields={field.name: hfds[index][field.name] for field in cls.fields},
                    metadata=metadata,
                    responses=list(responses.values()) or None,
                    external_id=hfds[index]["external_id"],
                )
            )
        del hfds
        return cls

    def unify_responses(
        self,
        question: Union[str, LabelQuestion, MultiLabelQuestion, RatingQuestion],
        strategy: Union[str, LabelQuestionStrategy, MultiLabelQuestionStrategy, RatingQuestionStrategy],
    ) -> None:
        """Unify responses for a given question using a given strategy"""
        if isinstance(question, str):
            question = self.question_by_name(question)
        if isinstance(strategy, str):
            strategy = LabelQuestionStrategy(strategy)
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
