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
import tempfile
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
    parse_obj_as,
    validator,
)
from tqdm import tqdm

import argilla as rg
from argilla.client.sdk.v1.datasets import api as datasets_api_v1
from argilla.utils.dependency import requires_version

if TYPE_CHECKING:
    import httpx
    from datasets import Dataset

    from argilla.client.sdk.v1.datasets.models import (
        FeedbackDatasetModel,
        FeedbackFieldModel,
        FeedbackQuestionModel,
    )

FETCHING_BATCH_SIZE = 250
PUSHING_BATCH_SIZE = 32

_LOGGER = logging.getLogger(__name__)


class ValueSchema(BaseModel):
    value: Union[StrictStr, StrictInt]


class ResponseSchema(BaseModel):
    user_id: Optional[UUID] = None
    values: Dict[str, ValueSchema]
    status: Literal["submitted", "discarded"] = "submitted"

    @validator("user_id", always=True)
    def user_id_must_have_value(cls, v):
        if not v:
            warnings.warn(
                "`user_id` not provided, so it will be set to `None`. Which is not an"
                " issue, unless you're planning to log the response in Argilla, as "
                " it will be automatically set to the active `user_id`.",
                stacklevel=2,
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
        extra = Extra.ignore


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
    values: List[int] = Field(unique_items=True)

    @validator("values", always=True)
    def update_settings_with_values(cls, v, values):
        if v:
            values["settings"]["options"] = [{"value": value} for value in v]
        return v

    class Config:
        validate_assignment = True


AllowedQuestionTypes = Union[TextQuestion, RatingQuestion]


class FeedbackDatasetConfig(BaseModel):
    fields: List[FieldSchema]
    questions: List[AllowedQuestionTypes]
    guidelines: Optional[str] = None


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
        TypeError: if `questions` is not a list of `TextQuestion` and/or `RatingQuestion`.
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
        ...     ],
        ...     guidelines="These are the annotation guidelines.",
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
        ...             responses=[{"values": {"question-1": {"value": "This is the first answer"}, "question-2": {"value": 5}}}],
        ...             external_id="entry-1",
        ...         ),
        ...     ]
        ... )
        >>> dataset.records
        [FeedbackRecord(fields={"text": "This is the first record", "label": "positive"}, responses=[ResponseSchema(user_id=None, values={"question-1": ValueSchema(value="This is the first answer"), "question-2": ValueSchema(value=5)})])]
        >>> dataset.push_to_argilla(name="my-dataset", workspace="my-workspace")
        >>> dataset.argilla_id
        "..."
        >>> dataset = rg.FeedbackDataset.from_argilla(argilla_id="...")
        >>> dataset.records
        [FeedbackRecord(fields={"text": "This is the first record", "label": "positive"}, responses=[ResponseSchema(user_id=None, values={"question-1": ValueSchema(value="This is the first answer"), "question-2": ValueSchema(value=5)})])]
    """

    argilla_id: Optional[str] = None

    def __init__(
        self,
        *,
        fields: List[FieldSchema],
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
            TypeError: if `questions` is not a list of `TextQuestion` and/or `RatingQuestion`.
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
            ...     ],
            ...     guidelines="These are the annotation guidelines.",
            ... )
        """
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
            if not isinstance(question, (TextQuestion, RatingQuestion)):
                raise TypeError(
                    "Expected `questions` to be a list of `TextQuestion` and/or `RatingQuestion`, got a"
                    f" question in the list with type {type(question)} instead."
                )
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

    @property
    def questions(self) -> List["FeedbackQuestionModel"]:
        """Returns the questions that will be used to annotate the dataset."""
        return self.__questions

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
            httpx_client: "httpx.Client" = rg.active_client()._client.httpx
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
            ...     ],
            ...     guidelines="These are the annotation guidelines.",
            ... )
            >>> dataset.records
            []
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
            [FeedbackRecord(fields={"text": "This is the first record", "label": "positive"}, responses=[ResponseSchema(user_id=None, values={"question-1": ValueSchema(value="This is the first answer"), "question-2": ValueSchema(value=5)})])]
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

    def iter(self, batch_size: Optional[int] = FETCHING_BATCH_SIZE) -> Iterator[FeedbackRecord]:
        """Returns an iterator over the records in the dataset.

        Args:
            batch_size: the size of the batches to return. Defaults to 100.
        """
        for i in range(0, len(self.records), batch_size):
            yield self.records[i : i + batch_size]

    def push_to_argilla(self, name: Optional[str] = None, workspace: Optional[Union[str, rg.Workspace]] = None) -> None:
        """Pushes the `FeedbackDataset` to Argilla. If the dataset has been previously pushed to Argilla, it will be updated
        with the new records.

        Note that you may need to `rg.init(...)` with your Argilla credentials before calling this function, otherwise
        the default http://localhost:6900 will be used, which will fail if Argilla is not deployed locally.

        Args:
            name: the name of the dataset to push to Argilla. If not provided, the `argilla_id` will be used if the dataset
                has been previously pushed to Argilla.
            workspace: the workspace where to push the dataset to. If not provided, the active workspace will be used.
        """
        httpx_client: "httpx.Client" = rg.active_client()._client.httpx

        if not name or (not name and not workspace):
            if self.argilla_id is None:
                _LOGGER.warning(
                    "No `name` or `workspace` have been provided, and no dataset has"
                    " been pushed to Argilla yet, so no records will be pushed to"
                    " Argilla."
                )
                return

            if len(self.__new_records) < 1:
                _LOGGER.warning(
                    "No new records have been added to the current `FeedbackTask`"
                    " dataset, so no records will be pushed to Argilla."
                )
                return

            try:
                for i in range(0, len(self.__new_records), PUSHING_BATCH_SIZE):
                    datasets_api_v1.add_records(
                        client=httpx_client,
                        id=self.argilla_id,
                        records=[record.dict() for record in self.__new_records[i : i + PUSHING_BATCH_SIZE]],
                    )
                self.__records += self.__new_records
                self.__new_records = []
            except Exception as e:
                Exception(
                    "Failed while adding new records to the current `FeedbackTask`"
                    f" dataset in Argilla with exception: {e}"
                )
        elif name or (name and workspace):
            if workspace is None:
                workspace = rg.Workspace.from_name(rg.active_client().get_workspace())

            if isinstance(workspace, str):
                workspace = rg.Workspace.from_name(workspace)

            dataset_exists, _ = feedback_dataset_in_argilla(name=name, workspace=workspace)
            if dataset_exists:
                raise RuntimeError(
                    f"Dataset with name=`{name}` and workspace=`{workspace.name}`"
                    " already exists in Argilla, please choose another name and/or"
                    " workspace."
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

            def delete_and_raise_exception(dataset_id: str, exception: Exception) -> None:
                try:
                    datasets_api_v1.delete_dataset(client=httpx_client, id=dataset_id)
                except Exception as e:
                    raise Exception(
                        "Failed while deleting the `FeedbackTask` dataset with ID"
                        f" '{dataset_id}' from Argilla with exception: {e}"
                    )
                raise exception

            for field in self.fields:
                try:
                    datasets_api_v1.add_field(client=httpx_client, id=argilla_id, field=field.dict())
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
                    datasets_api_v1.add_question(client=httpx_client, id=argilla_id, question=question.dict())
                except Exception as e:
                    delete_and_raise_exception(
                        dataset_id=argilla_id,
                        exception=Exception(
                            f"Failed while adding the question '{question.name}' to the"
                            f" `FeedbackTask` dataset in Argilla with exception: {e}"
                        ),
                    )

            try:
                datasets_api_v1.publish_dataset(client=httpx_client, id=argilla_id)
            except Exception as e:
                delete_and_raise_exception(
                    dataset_id=argilla_id,
                    exception=Exception(
                        f"Failed while publishing the `FeedbackTask` dataset in Argilla with exception: {e}"
                    ),
                )

            for batch in self.iter():
                try:
                    datasets_api_v1.add_records(
                        client=httpx_client,
                        id=argilla_id,
                        records=[record.dict() for record in batch],
                    )
                except Exception as e:
                    delete_and_raise_exception(
                        dataset_id=argilla_id,
                        exception=Exception(
                            "Failed while adding the records to the `FeedbackTask`"
                            f" dataset in Argilla with exception: {e}"
                        ),
                    )

            self.__records += self.__new_records
            self.__new_records = []

            if self.argilla_id is not None:
                _LOGGER.warning(
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
        httpx_client: "httpx.Client" = rg.active_client()._client.httpx

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

        cls.argilla_id = existing_dataset.id
        fields = []
        for field in datasets_api_v1.get_fields(client=httpx_client, id=existing_dataset.id).parsed:
            if field.settings["type"] == "text":
                field = TextField.construct(**field.dict())
            else:
                raise ValueError(
                    f"Field '{field.name}' is not a supported field in the current Python package version,"
                    " supported field types are: `TextField`."
                )
            fields.append(field)
        questions = []
        for question in datasets_api_v1.get_questions(client=httpx_client, id=existing_dataset.id).parsed:
            if question.settings["type"] == "rating":
                question = RatingQuestion.construct(**question.dict())
            elif question.settings["type"] == "text":
                question = TextQuestion.construct(**question.dict())
            else:
                raise ValueError(
                    f"Question '{question.name}' is not a supported question in the current Python package"
                    " version, supported question types are: `RatingQuestion` and `TextQuestion`."
                )
            questions.append(question)
        self = cls(
            fields=fields,
            questions=questions,
            guidelines=existing_dataset.guidelines or None,
        )
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

            dataset = {}
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
                # TODO(alvarobartt): if we constraint ranges from 0 to N, then we can use `ClassLabel` for ratings
                features[question.name] = Sequence(
                    {
                        "user_id": Value(dtype="string"),
                        "value": Value(dtype="string" if question.settings["type"] == "text" else "int32"),
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
                    dataset[question.name].append(
                        [
                            {
                                "user_id": r.user_id,
                                "value": r.values[question.name].value,
                                "status": r.status,
                            }
                            for r in record.responses
                        ]
                        or None
                    )
                dataset["external_id"].append(record.external_id or None)

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
        from huggingface_hub import DatasetCard, HfApi
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
            explained_fields = "## Fields\n\n" + "".join(
                [
                    f"* `{field.name}` is of type {FIELD_TYPE_TO_PYTHON_TYPE[field.settings['type']]}\n"
                    for field in self.fields
                ]
            )
            explained_questions = "## Questions\n\n" + "".join(
                [
                    f"* `{question.name}` {': ' + question.description if question.description else None}\n"
                    for question in self.questions
                ]
            )
            loading_guide = (
                "## Load with Argilla\n\nTo load this dataset with Argilla, you'll just need to "
                "install Argilla as `pip install argilla --upgrade` and then use the following code:\n\n"
                "```python\n"
                "import argilla as rg\n\n"
                f"ds = rg.FeedbackDataset.from_huggingface({repo_id!r})\n"
                "```\n\n"
                "## Load with Datasets\n\nTo load this dataset with Datasets, you'll just need to "
                "install Datasets as `pip install datasets --upgrade` and then use the following code:\n\n"
                "```python\n"
                "from datasets import load_dataset\n\n"
                f"ds = load_dataset({repo_id!r})\n"
                "```"
            )
            card = DatasetCard(
                f"## Guidelines\n\n{self.guidelines}\n\n"
                f"{explained_fields}\n\n"
                f"{explained_questions}\n\n"
                f"{loading_guide}\n\n"
            )
            card.push_to_hub(repo_id, repo_type="dataset", token=kwargs.get("token"))

    @classmethod
    @requires_version("datasets")
    @requires_version("huggingface_hub")
    def from_huggingface(cls, repo_id: str, *args, **kwargs) -> "FeedbackDataset":
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
        with open(config_path, "rb") as f:
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
                    responses[user_id]["values"].update({question.name: {"value": value}})
            cls.__records.append(
                FeedbackRecord(
                    fields={field.name: hfds[index][field.name] for field in cls.fields},
                    responses=list(responses.values()) or None,
                    external_id=hfds[index]["external_id"],
                )
            )
        del hfds
        return cls


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
    fields: List[FieldSchema],
    questions: List[QuestionSchema],
    workspace: Union[str, rg.Workspace] = None,
    guidelines: Optional[str] = None,
) -> FeedbackDataset:
    """Creates a `FeedbackDataset` object and pushes it to Argilla.

    Args:
        name: the name of dataset in Argilla (must be unique per workspace).
        fields: the list of `FieldSchema` objects to define the schema of the records pushed to Argilla.
        questions: the list of `QuestionSchema` objects to define the questions to ask to the annotator.
        workspace: the name of the workspace in Argilla where to push the dataset. Defaults to the default workspace.
        guidelines: the annotation guidelines to help the annotator understand the dataset to annotate and how to annotate it.
            Defaults to `None`.

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
        ...     guidelines="These are the annotation guidelines.",
        ... )
    """
    fds = FeedbackDataset(
        fields=fields,
        questions=questions,
        guidelines=guidelines,
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

    httpx_client: "httpx.Client" = rg.active_client()._client.httpx

    if name or (name and workspace):
        if workspace is None:
            workspace = rg.Workspace.from_name(rg.active_client().get_workspace())

        if isinstance(workspace, str):
            workspace = rg.Workspace.from_name(workspace)

        if not isinstance(workspace, rg.Workspace):
            raise ValueError(f"Workspace must be a `rg.Workspace` instance or a string, got {type(workspace)}")

        try:
            datasets = datasets_api_v1.list_datasets(client=httpx_client).parsed
        except Exception as e:
            raise Exception(f"Failed while listing the `FeedbackTask` datasets from Argilla with exception: {e}")

        for dataset in datasets:
            if dataset.name == name and dataset.workspace_id == workspace.id:
                return (True, dataset)
        return (False, None)
    else:
        try:
            return (True, datasets_api_v1.get_dataset(client=httpx_client, id=id).parsed)
        except:
            return (False, None)
