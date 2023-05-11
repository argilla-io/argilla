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

from __future__ import annotations

import sys
import warnings
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional, Tuple, Union
from uuid import UUID

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from pydantic import (
    BaseModel,
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
                "`user_id` not provided for `OfflineFeedbackResponse`. So it will be set to `None`. Which "
                "is not an issue, even though if you're planning to log the record in Argilla, as it will be set "
                "automatically to the current user's id."
            )
        return v


class FeedbackRecord(BaseModel):
    fields: Dict[str, str]
    response: Optional[ResponseSchema] = None
    external_id: Optional[str] = None


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
    argilla_id: Optional[str] = None

    def __init__(
        self,
        *,
        guidelines: str,
        fields: List[FieldSchema],
        questions: List[QuestionSchema],
    ) -> None:
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

    def __len__(self) -> int:
        return len(self.__records)

    def __getitem__(self, key: Union[slice, int]) -> Union["FeedbackItemModel", List["FeedbackItemModel"]]:
        if len(self.__records) < 1:
            raise RuntimeError(
                "In order to get items from `rg.FeedbackDataset` you need to either add them first with `add_records` or fetch them from Argilla or HuggingFace with `fetch_records`."
            )
        if isinstance(key, int) and len(self.__records) < key:
            raise IndexError(f"This dataset contains {len(self)} records, so index {key} is out of range.")
        return self.__records[key]

    def __del__(self) -> None:
        if hasattr(self, "__records"):
            del self.__records

    def __enter__(self) -> "FeedbackDataset":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.__del__()

    @property
    def guidelines(self) -> str:
        return self.__guidelines

    @guidelines.setter
    def guidelines(self, guidelines: str) -> None:
        if not isinstance(guidelines, str):
            raise TypeError(f"Expected `guidelines` to be a string, got {type(guidelines)} instead.")
        self.__guidelines = guidelines

    @property
    def fields(self) -> List[FeedbackFieldModel]:
        return self.__fields

    @property
    def questions(self) -> List[FeedbackQuestionModel]:
        return self.__questions

    @property
    def records(self) -> List["FeedbackItemModel"]:
        return self.__records

    def fetch_records(self, overwrite: bool = False) -> List["FeedbackItemModel"]:
        if not self.argilla_id:
            warnings.warn(
                "No records have been logged into neither Argilla nor HuggingFace, so no records will be fetched. The current records will be returned instead."
            )
            return self.__records
        if len(self.__records) > 0 and not overwrite:
            warnings.warn(
                "The current `rg.FeedbackDataset` contains records, just the pushed records will be fetched, while the non-pushed records will be lost. To ignore this warning and fetch the pushed records use `overwrite=True`. The current records will be returned instead."
            )
            return self.__records

        if self.argilla_id:
            client = rg.active_client()
            first_batch = client.get_records(id=self.argilla_id, offset=0, limit=FETCHING_BATCH_SIZE)
            self.__records = first_batch.items
            total_batches = first_batch.total // FETCHING_BATCH_SIZE
            current_batch = 1
            with tqdm(initial=current_batch, total=total_batches, desc="Fetching records from Argilla") as pbar:
                while current_batch <= total_batches:
                    batch = client.get_records(
                        id=self.argilla_id, offset=FETCHING_BATCH_SIZE * current_batch, limit=FETCHING_BATCH_SIZE
                    )
                    self.__records += batch.items
                    current_batch += 1
                    pbar.update(1)

        return self.__records

    def add_records(
        self,
        records: Union[FeedbackRecord, Dict[str, Any], List[Union[FeedbackRecord, Dict[str, Any]]]],
        push: bool = False,
    ) -> None:
        if isinstance(records, list):
            records = [FeedbackRecord(**record) if isinstance(record, dict) else record for record in records]
        if isinstance(records, dict):
            records = [FeedbackRecord(**records)]
        if isinstance(records, FeedbackRecord):
            records = [records]

        if self.__fields_schema is None:
            warnings.warn("Since the `schema` hasn't been defined during the dataset creation, it will be inferred.")
            self.__fields_schema = generate_pydantic_schema(records[0].fields)

        for record in records:
            try:
                record.fields = self.__fields_schema.parse_obj(record.fields)
            except ValidationError as e:
                raise ValueError(
                    f"`rg.FeedbackRecord.fields` do not match the expected schema, with exception: {e}"
                ) from e

        if self.__records is not None and isinstance(self.__records, list) and len(self.__records) > 0:
            self.__records += [OfflineFeedbackRecord.construct(**record.dict()).dict() for record in records]
        else:
            self.__records = [OfflineFeedbackRecord.construct(**record.dict()).dict() for record in records]

    def iter(
        self, batch_size: Optional[int] = FETCHING_BATCH_SIZE
    ) -> Iterator[Union["FeedbackItemModel", OfflineFeedbackRecord]]:
        for i in range(0, len(self.__records), batch_size):
            yield self.__records[i : i + batch_size]

    def push_to_argilla(self, name: str, workspace: Optional[Union[str, rg.Workspace]] = None) -> None:
        dataset_exists, _ = feedback_dataset_in_argilla(name=name, workspace=workspace)
        if dataset_exists:
            raise RuntimeError(
                f"Dataset with name `{name}` and workspace `{workspace.name}` already exists in Argilla, please choose another name and/or workspace."
            )

        client: "Argilla" = rg.active_client()

        def delete_and_raise_exception(dataset_id: str, exception: Exception) -> None:
            try:
                client.delete_dataset(id=dataset_id)
            except Exception as e:
                raise Exception(
                    f"Failed while deleting the `FeedbackTask` dataset with ID '{dataset_id}' from Argilla with exception: {e}"
                )
            raise exception

        try:
            new_dataset: "FeedbackDatasetModel" = client.create_dataset(
                name=name, workspace_id=workspace.id, guidelines=self.guidelines
            )
            argilla_id = new_dataset.id
        except Exception as e:
            delete_and_raise_exception(
                dataset_id=argilla_id,
                exception=Exception(f"Failed while creating the `FeedbackTask` dataset in Argilla with exception: {e}"),
            )

        for field in self.fields:
            try:
                client.add_field(id=argilla_id, field=field.dict())
            except Exception as e:
                delete_and_raise_exception(
                    dataset_id=argilla_id,
                    exception=Exception(
                        f"Failed while adding the field '{field.name}' to the `FeedbackTask` dataset in Argilla with exception: {e}"
                    ),
                )

        for question in self.questions:
            try:
                client.add_question(id=argilla_id, question=question.dict())
            except Exception as e:
                delete_and_raise_exception(
                    dataset_id=argilla_id,
                    exception=Exception(
                        f"Failed while adding the question '{question.name}' to the `FeedbackTask` dataset in Argilla with exception: {e}"
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

        self.argilla_id = argilla_id

    @classmethod
    def from_argilla(
        cls, name: Optional[str] = None, *, workspace: Optional[str] = None, id: Optional[str] = None
    ) -> "FeedbackDataset":
        assert name or (name and workspace) or id, (
            "You must provide either the `name` and `workspace` (the latter just if applicable, if not the default"
            " `workspace` will be used) or the `id`, which is the Argilla ID of the `rg.FeedbackDataset`."
        )

        client: "Argilla" = rg.active_client()

        dataset_exists, existing_dataset = feedback_dataset_in_argilla(name=name, workspace=workspace, id=id)
        if not dataset_exists:
            raise ValueError(
                f"Could not find a `FeedbackTask` dataset in Argilla with name='{name}'."
                if name and not workspace
                else f"Could not find a `FeedbackTask` dataset in Argilla with name='{name}' and workspace='{workspace}'."
                if name and workspace
                else f"Could not find a `FeedbackTask` dataset in Argilla with ID='{id}'."
            )

        cls.argilla_id = existing_dataset.id
        self = cls(
            guidelines=existing_dataset.guidelines,
            fields=[FieldSchema.construct(field) for field in client.get_fields(id=existing_dataset.id)],
            questions=[QuestionSchema.construct(question) for question in client.get_questions(id=existing_dataset.id)],
        )
        self.fetch_records()
        return self


def generate_pydantic_schema(
    fields: Union[BaseModel, Dict[str, Any]], name: Optional[str] = "FieldsSchema"
) -> BaseModel:
    fields_schema = {key: (type(value), ...) for key, value in fields.items()}
    return create_model(name, **fields_schema)


def create_feedback_dataset(
    name: str,
    guidelines: str,
    fields: List[FieldSchema],
    questions: List[QuestionSchema],
    workspace: Union[str, rg.Workspace] = None,
) -> FeedbackDataset:
    fds = FeedbackDataset(
        guidelines=guidelines,
        fields=fields,
        questions=questions,
    )
    fds.push_to_argilla(name=name, workspace=workspace)
    return fds


def feedback_dataset_in_argilla(
    name: Optional[str] = None, *, workspace: Optional[str] = None, id: Optional[str] = None
) -> Tuple[bool, Optional[FeedbackDataset]]:
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
