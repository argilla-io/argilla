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
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from pydantic import BaseModel, Field, StrictInt, StrictStr, create_model, validator
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


class ValueSchema(BaseModel):
    value: Union[StrictStr, StrictInt]


class ResponseSchema(BaseModel):
    values: Dict[str, ValueSchema]
    status: Literal["submitted", "missing", "discarded"]


class FeedbackRecord(BaseModel):
    fields: Dict[str, str]
    response: Optional[ResponseSchema] = None
    external_id: Optional[str] = None

    class Config:
        fields = {"response": {"exclude": True}, "external_id": {"exclude": True}}


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
    def __init__(
        self,
        name: Optional[str] = None,
        *,
        workspace: Optional[Union[rg.Workspace, str]] = None,
        id: Optional[str] = None,
    ) -> None:
        self.client: "Argilla" = rg.active_client()

        assert name or (name and workspace) or id, (
            "You must provide either the `name` and `workspace` (the latter just if applicable, if not the default"
            " `workspace` will be used) or the `id`, which is the Argilla ID of the `rg.FeedbackDataset`, which implies it must"
            " exist in advance."
        )

        if name or (name and workspace):
            if workspace is None or isinstance(workspace, str):
                workspace = rg.Workspace.from_name(workspace)

            if not isinstance(workspace, rg.Workspace):
                raise ValueError(f"Workspace must be a `rg.Workspace` instance or a string, got {type(workspace)}")

            for dataset in self.client.list_datasets():
                if dataset.name == name and dataset.workspace_id == workspace.id:
                    self.id = dataset.id

            if not hasattr(self, "id"):
                raise ValueError(f"Dataset with name {name} not found in workspace {workspace}")

        existing_dataset: FeedbackDatasetModel = self.client.get_dataset(id=id or self.id)

        self.id = existing_dataset.id
        self.name = existing_dataset.name
        self.workspace = existing_dataset.workspace_id
        self.guidelines = existing_dataset.guidelines

        self.schema = None

        self.__fields = None
        self.__questions = None
        self.__records = None

    def __repr__(self) -> str:
        return f"FeedbackDataset(name={self.name}, workspace={self.workspace}, id={self.id})"

    def __len__(self) -> int:
        if self.__records is None or len(self.__records) < 1:
            warnings.warn(
                "Since no records were provided, those will be fetched automatically from Argilla if available."
            )
            return len(self.records)
        return len(self.__records)

    def __getitem__(self, key: Union[slice, int]) -> Union["FeedbackItemModel", List["FeedbackItemModel"]]:
        return self.__records[key]

    def __del__(self) -> None:
        if hasattr(self, "__records"):
            del self.__records

    def __enter__(self) -> "FeedbackDataset":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.__del__()

    @property
    def fields(self) -> List[FeedbackFieldModel]:
        if self.__fields is None or len(self.__fields) < 1:
            self.__fields = self.client.get_fields(id=self.id)
        return self.__fields

    @property
    def questions(self) -> List[FeedbackQuestionModel]:
        if self.__questions is None or len(self.__questions) < 1:
            self.__questions = self.client.get_questions(id=self.id)
        return self.__questions

    @property
    def records(self) -> List["FeedbackItemModel"]:
        # TODO: we can use a cache to store the results to `.cache/argilla/datasets/{dataset_id}/records`
        if self.__records is None or len(self.__records) < 1:
            response = self.client.get_records(id=self.id, offset=0, limit=1)
            self.__records = response.items
            total_records = response.total
            if total_records > 1:
                prev_limit = 0
                with tqdm(
                    initial=len(self.__records), total=total_records, desc="Fetching records from Argilla"
                ) as pbar:
                    while prev_limit < total_records:
                        prev_limit += 1
                        self.__records += self.client.get_records(id=self.id, offset=prev_limit, limit=1).items
                        pbar.update(1)
        return self.__records

    def add_records(
        self,
        records: Union[FeedbackRecord, Dict[str, Any], List[Union[FeedbackRecord, Dict[str, Any]]]],
    ) -> None:
        if isinstance(records, list):
            records = [FeedbackRecord(**record) if isinstance(record, dict) else record for record in records]
        if isinstance(records, dict):
            records = [FeedbackRecord(**records)]
        if isinstance(records, FeedbackRecord):
            records = [records]

        if self.schema is None:
            warnings.warn("Since the `schema` hasn't been defined during the dataset creation, it will be inferred.")
            self.schema = generate_pydantic_schema(records[0].fields)

        for record in records:
            record.fields = self.schema.parse_obj(record.fields)

        # # If there are records already logged to Argilla, fetch one and get the schema
        # self.schema = generate_pydantic_schema(self.fetch_one())
        # # If there are no records logged to Argilla, check if `self.schema` has been set
        # ...
        # # If `self.schema` has not been set, just infer the schema based on the record
        # ...
        # record = record.dict() if isinstance(record, BaseModel) else record
        self.client.add_records(
            id=self.id,
            records=[record.dict() for record in records],
        )
        # if self.__records is not None and isinstance(self.__records, list) and len(self.__records) > 0:
        #     self.__records.append(record)

    def fetch_one(self) -> "FeedbackItemModel":
        if self.__records is None or len(self.__records) < 1:
            return self.client.get_records(id=self.id, offset=0, limit=1).items[0]
        return self.__records[0]

    def iter(self, batch_size: int = 32) -> List["FeedbackItemModel"]:
        if self.__records is None or len(self.__records) < 1:
            first_batch = self.client.get_records(id=self.id, offset=0, limit=batch_size)
            self.__records = first_batch.items
            yield batch
            total_batches = first_batch.total // batch_size
            current_batch = 1
            with tqdm(initial=current_batch, total=total_batches, desc="Fetching records from Argilla") as pbar:
                while current_batch <= total_batches:
                    batch = self.client.get_records(id=self.id, offset=batch_size, limit=batch_size)
                    self.__records += batch.items
                    yield batch
                    current_batch += 1
                    pbar.update(1)
        else:
            for batch in self.records[0::batch_size]:
                yield batch


def generate_pydantic_schema(
    fields: Union[BaseModel, Dict[str, Any]], name: Optional[str] = "FieldsSchema"
) -> BaseModel:
    fields_schema = {key: (type(value), ...) for key, value in fields.items()}
    return create_model(name, **fields_schema)


def create_feedback_dataset(
    name: str,
    workspace: Optional[Union[str, rg.Workspace]] = None,
    guidelines: Optional[str] = None,
    fields: Optional[List[FieldSchema]] = None,
    questions: Optional[List[QuestionSchema]] = None,
) -> FeedbackDataset:
    client = rg.active_client()

    if workspace is None or isinstance(workspace, str):
        try:
            workspace = rg.Workspace.from_name(workspace)
        except ValueError as e:
            raise e

    if not isinstance(workspace, rg.Workspace):
        raise ValueError(f"Workspace must be a `rg.Workspace` instance or a string, got {type(workspace)}")
    else:
        if workspace.id is None:
            raise ValueError(
                "`rg.Workspace` must have an ID, which means that it exists in Argilla, if you don't know the ID but know the name and that it exists in Argilla, then use `rg.Workspace.from_name` instead."
            )

    try:
        datasets = client.list_datasets()
    except Exception as e:
        raise Exception(f"Failed while listing the `FeedbackTask` datasets from Argilla with exception: {e}")

    for dataset in datasets:
        if dataset.name == name and dataset.workspace_id == workspace.id:
            warnings.warn(
                f"`rg.FeedbackDataset` with name '{name}' in workspace {workspace.id} already exists, skipping creation."
            )
            return FeedbackDataset(id=dataset.id)

    def delete_and_raise_exception(dataset_id: str, exception: Exception) -> None:
        try:
            client.delete_dataset(id=dataset_id)
        except Exception as e:
            raise Exception(
                f"Failed while deleting the `FeedbackTask` dataset with ID '{dataset_id}' from Argilla with exception: {e}"
            )
        raise exception

    try:
        new_dataset: FeedbackDatasetModel = client.create_dataset(
            name=name, workspace_id=workspace.id, guidelines=guidelines
        )
    except Exception as e:
        raise Exception(f"Failed while creating the `FeedbackTask` dataset in Argilla with exception: {e}")

    for field in fields:
        if isinstance(field, dict):
            try:
                field = FieldSchema(**field)
            except Exception as e:
                delete_and_raise_exception(
                    dataset_id=new_dataset.id,
                    exception=Exception(
                        f"Failed while parsing the field '{field}' to a `FieldSchema` instance with exception: {e}"
                    ),
                )
        try:
            client.add_field(id=new_dataset.id, field=field.dict())
        except Exception as e:
            delete_and_raise_exception(
                dataset_id=new_dataset.id,
                exception=Exception(
                    f"Failed while adding the field '{field.name}' to the `FeedbackTask` dataset in Argilla with exception: {e}"
                ),
            )

    for question in questions:
        if isinstance(question, dict):
            try:
                question = QuestionSchema(**question)
            except Exception as e:
                delete_and_raise_exception(
                    dataset_id=new_dataset.id,
                    exception=Exception(
                        f"Failed while parsing the question '{question}' to a `QuestionSchema` instance with exception: {e}"
                    ),
                )
        try:
            client.add_question(id=new_dataset.id, question=question.dict())
        except Exception as e:
            delete_and_raise_exception(
                dataset_id=new_dataset.id,
                exception=Exception(
                    f"Failed while adding the question '{question.name}' to the `FeedbackTask` dataset in Argilla with exception: {e}"
                ),
            )

    try:
        client.publish_dataset(id=new_dataset.id)
    except Exception as e:
        delete_and_raise_exception(
            dataset_id=new_dataset.id,
            exception=Exception(f"Failed while publishing the `FeedbackTask` dataset in Argilla with exception: {e}"),
        )

    return FeedbackDataset(id=new_dataset.id)
