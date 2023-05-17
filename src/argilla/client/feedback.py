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
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional, Tuple, Union
from uuid import UUID

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from pydantic import (
    BaseModel,
    Extra,
    Field,
    StrictInt,
    StrictStr,
    ValidationError,
    create_model,
    validator,
)
from tqdm import tqdm

import argilla as rg

if TYPE_CHECKING:
    from argilla.client.api import Argilla
    from argilla.client.sdk.v1.datasets.models import (
        FeedbackDatasetModel,
        FeedbackFieldModel,
        FeedbackItemModel,
        FeedbackQuestionModel,
    )

FETCHING_BATCH_SIZE = 250


class ValueSchema(BaseModel):
    value: Union[StrictStr, StrictInt]


class ResponseSchema(BaseModel):
    values: Dict[str, ValueSchema]
    status: Literal["submitted", "missing", "discarded"]


class OfflineFeedbackResponse(ResponseSchema):
    user_id: Optional[UUID] = None

    @validator("user_id", always=True)
    def user_id_must_have_value(cls, v):
        if not v:
            warnings.warn(
                "`user_id` not provided for `OfflineFeedbackResponse`. So it will be"
                " set to `None`. Which is not an issue, even though if you're planning"
                " to log the record in Argilla, as it will be set automatically to the"
                " current user's id."
            )
        return v


class FeedbackRecord(BaseModel):
    fields: Dict[str, str]
    responses: Optional[Union[ResponseSchema, List[ResponseSchema]]] = None
    external_id: Optional[str] = None

    @validator("responses", always=True)
    def responses_must_be_a_list(cls, v):
        if not v:
            return []
        if isinstance(v, ResponseSchema):
            return [v]
        return v

    class Config:
        extra = Extra.forbid


class OfflineFeedbackRecord(BaseModel):
    id: Optional[str] = None
    fields: Dict[str, str]
    responses: List[OfflineFeedbackResponse] = []
    external_id: Optional[str] = None
    inserted_at: Optional[str] = None
    updated_at: Optional[str] = None


class FieldSchema(BaseModel):
    name: str
    title: Optional[str] = None
    required: Optional[bool] = True
    settings: Dict[str, Any]

    @validator("title", always=True)
    def title_must_have_value(cls, v, values):
        if not v:
            return values["name"].capitalize()
        return v


class TextField(FieldSchema):
    settings: Dict[str, Any] = Field({"type": "text"}, const=True)


FIELD_TYPE_TO_PYTHON_TYPE = {"text": str}


class QuestionSchema(BaseModel):
    name: str
    title: Optional[str] = None
    description: Optional[str] = None
    required: Optional[bool] = True
    settings: Dict[str, Any]

    @validator("title", always=True)
    def title_must_have_value(cls, v, values):
        if not v:
            return values["name"].capitalize()
        return v


# TODO(alvarobartt): add `TextResponse` and `RatingResponse` classes
class TextQuestion(QuestionSchema):
    settings: Dict[str, Any] = Field({"type": "text"}, const=True)


class RatingQuestion(QuestionSchema):
    settings: Dict[str, Any] = Field({"type": "rating"})
    values: List[int]

    @validator("values", always=True)
    def update_settings_with_values(cls, v, values):
        if v:
            values["settings"]["options"] = [{"value": value} for value in v]
        return v


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
        TypeError: if `questions` is not a list of `QuestionSchema`.
        ValueError: if `questions` does not contain at least one required question.

    Examples:
        >>> import argilla as rg
        >>> rg.init(api_url="...", api_key="...")
        >>> dataset = rg.FeedbackDataset(
        ...     guidelines="These are the annotation guidelines.",
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
        ...     ],
        ... )
        >>> dataset.guidelines
        "These are the annotation guidelines."
        >>> dataset.fields
        [TextField(name="text", title="Text", required=True, settings={"type": "text"}), TextField(name="label", title="Label", required=True, settings={"type": "text"})]
        >>> dataset.questions
        [TextQuestion(name="question-1", title="Question 1", description="This is the first question", required=True, settings={"type": "text"}), RatingQuestion(name="question-2", title="Question 2", description="This is the second question", required=True, settings={"type": "rating"}, values=[1, 2, 3, 4, 5])]
        >>> dataset.records
        []
        >>> dataset.add_records(
        ...     [
        ...         rg.FeedbackRecord(
        ...             fields={"text": "This is the first record", "label": "positive"},
        ...             response={"question-1": "This is the first answer", "question-2": 5},
        ...             external_id="entry-1",
        ...         ),
        ...     ]
        ... )
        >>> dataset.records
        [FeedbackRecord(fields={"text": "This is the first record", "label": "positive"}, response={"question-1": "This is the first answer", "question-2": 5}, external_id="entry-1")]
        >>> dataset.push_to_argilla(name="my-dataset", workspace="my-workspace")
        >>> dataset.argilla_id
        "..."
        >>> dataset = rg.FeedbackDataset.from_argilla(argilla_id="...")
        >>> dataset.records
        [FeedbackRecord(fields={"text": "This is the first record", "label": "positive"}, response={"question-1": "This is the first answer", "question-2": 5}, external_id="entry-1")]
    """

    argilla_id: Optional[str] = None

    def __init__(
        self,
        *,
        guidelines: str,
        fields: List[FieldSchema],
        questions: List[QuestionSchema],
    ) -> None:
        """Initializes a `FeedbackDataset` instance locally.

        Args:
            guidelines: contains the guidelines for annotating the dataset.
            fields: contains the fields that will define the schema of the records in the dataset.
            questions: contains the questions that will be used to annotate the dataset.

        Raises:
            TypeError: if `guidelines` is not a string.
            TypeError: if `fields` is not a list of `FieldSchema`.
            ValueError: if `fields` does not contain at least one required field.
            TypeError: if `questions` is not a list of `QuestionSchema`.
            ValueError: if `questions` does not contain at least one required question.

        Examples:
            >>> import argilla as rg
            >>> rg.init(api_url="...", api_key="...")
            >>> dataset = rg.FeedbackDataset(
            ...     guidelines="These are the annotation guidelines.",
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
            ...     ],
            ... )
        """
        if not isinstance(guidelines, str):
            raise TypeError(f"Expected `guidelines` to be a string, got {type(guidelines)} instead.")
        self.__guidelines = guidelines

        if not isinstance(fields, list):
            raise TypeError(f"Expected `fields` to be a list, got {type(fields)} instead.")
        any_required = False
        for field in fields:
            if not isinstance(field, FieldSchema):
                raise TypeError(f"Expected `fields` to be a list of `FieldSchema`, got {type(field)} instead.")
            if not any_required and field.required:
                any_required = True
        if not any_required:
            raise ValueError("At least one `FieldSchema` in `fields` must be required (`required=True`).")
        self.__fields = fields
        self.__fields_schema = None

        if not isinstance(questions, list):
            raise TypeError(f"Expected `questions` to be a list, got {type(questions)} instead.")
        any_required = False
        for question in questions:
            if not isinstance(question, QuestionSchema):
                raise TypeError(f"Expected `questions` to be a list of `QuestionSchema`, got {type(question)} instead.")
            if not any_required and question.required:
                any_required = True
        if not any_required:
            raise ValueError("At least one `QuestionSchema` in `questions` must be required (`required=True`).")
        self.__questions = questions

        self.__records = []
        self.__new_records = []

    def __len__(self) -> int:
        """Returns the number of records in the dataset."""
        return len(self.records)

    def __getitem__(self, key: Union[slice, int]) -> Union["FeedbackItemModel", List["FeedbackItemModel"]]:
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

    @property
    def questions(self) -> List["FeedbackQuestionModel"]:
        """Returns the questions that will be used to annotate the dataset."""
        return self.__questions

    @property
    def records(self) -> List["FeedbackItemModel"]:
        """Returns the all the records in the dataset."""
        return self.__records + self.__new_records

    def fetch_records(self) -> None:
        """Fetches the records from Argilla or HuggingFace and stores them locally.

        If the dataset has not been saved in Argilla or HuggingFace, a warning will be
        raised and the current records will be returned instead.
        """
        if not self.argilla_id:
            warnings.warn(
                "No records have been logged into neither Argilla nor HuggingFace, so"
                " no records will be fetched. The current records will be returned"
                " instead."
            )
            return self.records

        # TODO(alvarobartt): create `ArgillaMixIn` and `HuggingFaceMixIn` classes to inherit their specific methods
        if self.argilla_id:
            client = rg.active_client()
            first_batch = client.get_records(id=self.argilla_id, offset=0, limit=FETCHING_BATCH_SIZE)
            self.__records = first_batch.items
            total_batches = first_batch.total // FETCHING_BATCH_SIZE
            current_batch = 1
            with tqdm(
                initial=current_batch,
                total=total_batches,
                desc="Fetching records from Argilla",
            ) as pbar:
                while current_batch <= total_batches:
                    batch = client.get_records(
                        id=self.argilla_id,
                        offset=FETCHING_BATCH_SIZE * current_batch,
                        limit=FETCHING_BATCH_SIZE,
                    )
                    self.__records += batch.items
                    current_batch += 1
                    pbar.update(1)

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
            ValueError: if the given records do not match the expected schema.
        """
        if isinstance(records, list):
            records = [FeedbackRecord(**record) if isinstance(record, dict) else record for record in records]
        if isinstance(records, dict):
            records = [FeedbackRecord(**records)]
        if isinstance(records, FeedbackRecord):
            records = [records]

        if self.__fields_schema is None:
            self.__fields_schema = generate_pydantic_schema(self.fields)

        for record in records:
            try:
                record.fields = self.__fields_schema.parse_obj(record.fields)
            except ValidationError as e:
                raise ValueError(
                    f"`rg.FeedbackRecord.fields` does not match the expected schema, with exception: {e}"
                ) from e

        if len(self.__new_records) > 0:
            self.__new_records += [OfflineFeedbackRecord.construct(**record.dict()).dict() for record in records]
        else:
            self.__new_records = [OfflineFeedbackRecord.construct(**record.dict()).dict() for record in records]

    def iter(
        self, batch_size: Optional[int] = FETCHING_BATCH_SIZE
    ) -> Iterator[Union["FeedbackItemModel", OfflineFeedbackRecord]]:
        """Returns an iterator over the records in the dataset.

        Args:
            batch_size: the size of the batches to return. Defaults to 100.
        """
        for i in range(0, len(self.records), batch_size):
            yield self.records[i : i + batch_size]

    def push_to_argilla(self, name: Optional[str] = None, workspace: Optional[Union[str, rg.Workspace]] = None) -> None:
        """Pushes the dataset to Argilla. If the dataset has been previously pushed to Argilla, it will be updated
        with the new records.

        Note that you may need to `rg.init(...)` with your Argilla credentials before calling this function, otherwise
        the default http://localhost:6900 will be used, which will fail if Argilla is not deployed locally.

        Args:
            name: the name of the dataset to push to Argilla. If not provided, the `argilla_id` will be used if the dataset
                has been previously pushed to Argilla.
            workspace: the workspace where to push the dataset to. If not provided, the active workspace will be used.
        """
        if not name or (not name and not workspace):
            if self.argilla_id is None:
                warnings.warn(
                    "No `name` or `workspace` have been provided, and no dataset has"
                    " been pushed to Argilla yet, so no records will be pushed to"
                    " Argilla."
                )
                return

            if len(self.__new_records) < 1:
                warnings.warn(
                    "No new records have been added to the current `FeedbackTask`"
                    " dataset, so no records will be pushed to Argilla."
                )
                return

            try:
                client: "Argilla" = rg.active_client()
                for i in range(0, len(self.__new_records), 32):
                    client.add_records(
                        id=self.argilla_id,
                        records=self.__new_records[i : i + 32],
                    )
                self.__records += self.__new_records
                self.__new_records = []
            except Exception as e:
                Exception(
                    "Failed while adding new records to the current `FeedbackTask`"
                    f" dataset in Argilla with exception: {e}"
                )
        elif name or (name and workspace):
            client: "Argilla" = rg.active_client()
            if workspace is None:
                workspace = rg.Workspace.from_name(client.get_workspace())

            if isinstance(workspace, str):
                workspace = rg.Workspace.from_name(workspace)

            dataset_exists, _ = feedback_dataset_in_argilla(name=name, workspace=workspace)
            if dataset_exists:
                raise RuntimeError(
                    f"Dataset with name=`{name}` and workspace=`{workspace.name}`"
                    " already exists in Argilla, please choose another name and/or"
                    " workspace."
                )

            client: "Argilla" = rg.active_client()

            try:
                new_dataset: "FeedbackDatasetModel" = client.create_dataset(
                    name=name, workspace_id=workspace.id, guidelines=self.guidelines
                )
                argilla_id = new_dataset.id
            except Exception as e:
                raise Exception(
                    f"Failed while creating the `FeedbackTask` dataset in Argilla with exception: {e}"
                ) from e

            def delete_and_raise_exception(dataset_id: str, exception: Exception) -> None:
                try:
                    client.delete_dataset(id=dataset_id)
                except Exception as e:
                    raise Exception(
                        "Failed while deleting the `FeedbackTask` dataset with ID"
                        f" '{dataset_id}' from Argilla with exception: {e}"
                    )
                raise exception

            for field in self.fields:
                try:
                    client.add_field(id=argilla_id, field=field.dict())
                except Exception as e:
                    delete_and_raise_exception(
                        dataset_id=argilla_id,
                        exception=Exception(
                            f"Failed while adding the field '{field.name}' to the"
                            f" `FeedbackTask` dataset in Argilla with exception: {e}"
                        ),
                    )

            for question in self.questions:
                try:
                    client.add_question(id=argilla_id, question=question.dict())
                except Exception as e:
                    delete_and_raise_exception(
                        dataset_id=argilla_id,
                        exception=Exception(
                            f"Failed while adding the question '{question.name}' to the"
                            f" `FeedbackTask` dataset in Argilla with exception: {e}"
                        ),
                    )

            try:
                client.publish_dataset(id=argilla_id)
            except Exception as e:
                delete_and_raise_exception(
                    dataset_id=argilla_id,
                    exception=Exception(
                        f"Failed while publishing the `FeedbackTask` dataset in Argilla with exception: {e}"
                    ),
                )

            for batch in self.iter():
                try:
                    client.add_records(
                        id=argilla_id,
                        records=batch,
                    )
                except Exception as e:
                    delete_and_raise_exception(
                        dataset_id=argilla_id,
                        exception=Exception(
                            "Failed while adding the records to the `FeedbackTask`"
                            f" dataset in Argilla with exception: {e}"
                        ),
                    )

            if self.argilla_id is not None:
                warnings.warn(
                    "Since the current object is already a `FeedbackDataset` pushed to"
                    " Argilla, you'll keep on interacting with the same dataset in"
                    " Argilla, even though the one you just pushed holds a different"
                    f" ID ({argilla_id}). So on, if you want to switch to the newly"
                    " pushed `FeedbackDataset` instead, please use"
                    f" `FeedbackDataset.from_argilla(id='{argilla_id}')`."
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
        dataset_exists, existing_dataset = feedback_dataset_in_argilla(name=name, workspace=workspace, id=id)
        if not dataset_exists:
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

        client: "Argilla" = rg.active_client()

        cls.argilla_id = existing_dataset.id
        self = cls(
            guidelines=existing_dataset.guidelines,
            fields=[FieldSchema.construct(**field.dict()) for field in client.get_fields(id=existing_dataset.id)],
            questions=[
                QuestionSchema.construct(**question.dict()) for question in client.get_questions(id=existing_dataset.id)
            ],
        )
        if with_records:
            self.fetch_records()
        return self


def generate_pydantic_schema(fields: List[FieldSchema], name: Optional[str] = "FieldsSchema") -> BaseModel:
    """Generates a `pydantic.BaseModel` schema from a list of `FieldSchema` objects to validate
    the fields of a `FeedbackDataset` object before inserting them.

    Args:
        fields: the list of `FieldSchema` objects to generate the schema from.
        name: the name of the `pydantic.BaseModel` schema to generate. Defaults to "FieldsSchema".

    Returns:
        A `pydantic.BaseModel` schema to validate the fields of a `FeedbackDataset` object before
        inserting them.

    Raises:
        ValueError: if one of the fields has an unsupported type.

    Examples:
        >>> from argilla.client.feedback import TextField, generate_pydantic_schema
        >>> fields = [
        ...     TextField(name="text", required=True),
        ...     TextField(name="label", required=True),
        ... ]
        >>> FieldsSchema = generate_pydantic_schema(fields)
        >>> FieldsSchema(text="Hello", label="World")
        FieldsSchema(text='Hello', label='World')
    """
    fields_schema = {}
    for field in fields:
        if field.settings["type"] not in FIELD_TYPE_TO_PYTHON_TYPE.keys():
            raise ValueError(
                f"Field {field.name} has an unsupported type: {field.settings['type']}, for the moment only the"
                f" following types are supported: {list(FIELD_TYPE_TO_PYTHON_TYPE.keys())}"
            )
        fields_schema.update(
            {field.name: (FIELD_TYPE_TO_PYTHON_TYPE[field.settings["type"]], ... if field.required else None)}
        )
    return create_model(name, **fields_schema)


def create_feedback_dataset(
    name: str,
    guidelines: str,
    fields: List[FieldSchema],
    questions: List[QuestionSchema],
    workspace: Union[str, rg.Workspace] = None,
) -> FeedbackDataset:
    """Creates a `FeedbackDataset` object and pushes it to Argilla.

    Args:
        name: the name of dataset in Argilla (must be unique per workspace).
        guidelines: the annotation guidelines to help the annotator understand the dataset to annotate and how to annotate it.
        fields: the list of `FieldSchema` objects to define the schema of the records pushed to Argilla.
        questions: the list of `QuestionSchema` objects to define the questions to ask to the annotator.
        workspace: the name of the workspace in Argilla where to push the dataset. Defaults to the default workspace.

    Returns:
        The `FeedbackDataset` object created and pushed to Argilla.

    Raises:
        ValueError: if one of the fields has an unsupported type.
        Exception: if the dataset could not be pushed to Argilla.

    Examples:
        >>> import argilla as rg
        >>> rg.init(api_url="...", api_key="...")
        >>> fds = rg.create_feedback_dataset(
        ...     name="my-dataset",
        ...     guidelines="These are the annotation guidelines.",
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
        ...     ],
        ... )
    """
    fds = FeedbackDataset(
        guidelines=guidelines,
        fields=fields,
        questions=questions,
    )
    fds.push_to_argilla(name=name, workspace=workspace)
    return fds


def feedback_dataset_in_argilla(
    name: Optional[str] = None,
    *,
    workspace: Optional[Union[str, rg.Workspace]] = None,
    id: Optional[str] = None,
) -> Tuple[bool, Optional[FeedbackDataset]]:
    """Checks whether a `FeedbackDataset` exists in Argilla or not, based on the `name`, `id`, or the combination of
    `name` and `workspace`.

    Args:
        name: the name of the `FeedbackDataset` in Argilla.
        workspace: the name of the workspace in Argilla where the `FeedbackDataset` is located.
        id: the Argilla ID of the `FeedbackDataset`.

    Returns:
        A tuple with a boolean indicating whether the `FeedbackDataset` exists in Argilla or not, and the `FeedbackDataset`
        object if it exists, `None` otherwise.

    Raises:
        ValueError: if the `workspace` is not a `rg.Workspace` instance or a string.
        Exception: if the `FeedbackDataset` could not be listed from Argilla.

    Examples:
        >>> import argilla as rg
        >>> rg.init(api_url="...", api_key="...")
        >>> from argilla.client.feedback import feedback_dataset_in_argilla
        >>> fds_exists, fds_cls = feedback_dataset_in_argilla(name="my-dataset")
    """
    assert name or (name and workspace) or id, (
        "You must provide either the `name` and `workspace` (the latter just if"
        " applicable, if not the default `workspace` will be used) or the `id`, which"
        " is the Argilla ID of the `rg.FeedbackDataset`."
    )

    client: "Argilla" = rg.active_client()

    if name or (name and workspace):
        if workspace is None:
            workspace = rg.Workspace.from_name(client.get_workspace())

        if isinstance(workspace, str):
            workspace = rg.Workspace.from_name(workspace)

        if not isinstance(workspace, rg.Workspace):
            raise ValueError(f"Workspace must be a `rg.Workspace` instance or a string, got {type(workspace)}")

        try:
            datasets = client.list_datasets()
        except Exception as e:
            raise Exception(f"Failed while listing the `FeedbackTask` datasets from Argilla with exception: {e}")

        for dataset in datasets:
            if dataset.name == name and dataset.workspace_id == workspace.id:
                return (True, dataset)
        return (False, None)
    else:
        try:
            return (True, client.get_dataset(id=id))
        except Exception as e:
            return (False, None)
