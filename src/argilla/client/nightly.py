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

import warnings
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypeVar, Union

from pydantic import BaseModel, Field, create_model, validator
from tqdm import tqdm

import argilla as rg

if TYPE_CHECKING:
    from argilla.client.api import Argilla
    from argilla.client.sdk.datasets.v1.models import FeedbackDataset

RecordFieldSchema = TypeVar("RecordFieldSchema", bound=BaseModel)


class RecordSchema(BaseModel):
    fields: RecordFieldSchema
    response: Optional[Dict[str, Any]] = {"values": {}, "status": "submitted"}
    external_id: Optional[str] = None


class OnlineRecordSchema(RecordSchema):
    id: str
    inserted_at: Optional[str] = None
    updated_at: Optional[str] = None


class FieldSchema(BaseModel):
    name: str
    title: str
    required: bool
    settings: Dict[str, Any]


class OnlineFieldSchema(FieldSchema):
    id: str
    inserted_at: Optional[str] = None
    updated_at: Optional[str] = None


class QuestionSchema(BaseModel):
    name: str
    title: str
    required: bool
    settings: Dict[str, Any]


class OnlineQuestionSchema(FieldSchema):
    id: str
    inserted_at: Optional[str] = None
    updated_at: Optional[str] = None


class CustomField(BaseModel):
    name: str
    title: Optional[str] = None
    required: Optional[bool] = True
    settings: Dict[str, Any]

    @validator("title", always=True)
    def title_must_have_value(cls, v, values):
        if not v:
            return values["name"].capitalize()
        return v


class TextField(CustomField):
    settings: Dict[str, Any] = Field({"type": "text"}, const=True)


class Question(BaseModel):
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


class TextQuestion(Question):
    settings: Dict[str, Any] = Field({"type": "text"}, const=True)


class RatingQuestion(Question):
    settings: Dict[str, Any] = Field({"type": "rating"})
    values: List[int]

    @validator("values", always=True)
    def update_settings_with_values(cls, v, values):
        if v:
            values["settings"]["options"] = [{"value": value} for value in v]
        return v


class DatasetStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"


class QuestionSchema(BaseModel):
    name: str
    title: str
    required: bool
    settings: Dict[str, Any]


def create_feedback_dataset(
    name: str,
    workspace_id: Optional[str] = None,
    guidelines: Optional[str] = None,
    fields: Optional[List[BaseModel]] = None,
    questions: Optional[List[QuestionSchema]] = None,
) -> "FeedbackDataset":
    client = rg.active_client()

    for dataset in client.list_datasets().parsed:
        if dataset.name == name and dataset.workspace_id == workspace_id:
            warnings.warn(f"Dataset with name '{name}' already exists, skipping creation.")
            return FeedbackDataset(id=dataset.id)

    new_dataset = client.create_dataset(name=name, workspace_id=workspace_id, guidelines=guidelines).parsed

    for field in fields:
        if isinstance(field, dict):
            field = FieldSchema(**field)
        client.add_field(id=new_dataset.id, field=field.dict())

    for question in questions:
        if isinstance(question, dict):
            question = QuestionSchema(**question)
        client.add_question(id=new_dataset.id, question=question.dict())

    client.publish_dataset(id=new_dataset.id)

    return FeedbackDataset(id=new_dataset.id)


class FeedbackDataset:
    def __init__(
        self,
        name: Optional[str] = None,
        *,
        workspace: Optional[Union[Workspace, str]] = None,
        id: Optional[str] = None,
    ) -> None:
        self.client: "Argilla" = rg.active_client()

        assert name or (name and workspace) or id, (
            "You must provide either the `name` and `workspace` (the latter just if applicable, if not the default"
            " `workspace` will be used) or the `id`, which is the Argilla ID of the `Dataset`, which implies it must"
            " exist in advance."
        )

        self.id = id
        dataset = self.client.get_dataset(id=self.id).parsed

        self.name = dataset.name
        self.workspace = dataset.workspace_id
        self.guidelines = dataset.guidelines

        self.schema = None
        self.__fields = None
        self.__questions = None
        self.__records = None

    def __repr__(self) -> str:
        return f"Dataset(name={self.name}, workspace={self.workspace}, id={self.id})"

    def __len__(self) -> int:
        if self.__records is None or len(self.__records) < 1:
            warnings.warn(
                "Since no records were provided, those will be fetched automatically from Argilla if available."
            )
            return len(self.records)
        return len(self.__records)

    def __getitem__(self, key: Union[slice, int]) -> Union[OnlineRecordSchema, List[OnlineRecordSchema]]:
        return self.__records[key]

    def __del__(self) -> None:
        if hasattr(self, "__records"):
            del self.__records

    def __enter__(self) -> "FeedbackDataset":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.__del__()

    @property
    def fields(self) -> List[OnlineFieldSchema]:
        if self.__fields is None or len(self.__fields) < 1:
            self.__fields = [OnlineFieldSchema(**field) for field in self.client.get_fields(id=self.id).parsed["items"]]
        return self.__fields

    @property
    def questions(self) -> List[OnlineQuestionSchema]:
        if self.__questions is None or len(self.__questions) < 1:
            self.__questions = [
                OnlineQuestionSchema(**question) for question in self.client.get_questions(id=self.id).parsed["items"]
            ]
        return self.__questions

    @property
    def records(self) -> List[RecordFieldSchema]:
        if self.__records is None or len(self.__records) < 1:
            response = self.client.get_records(id=self.id, offset=0, limit=1).parsed
            if self.schema is None:
                self.schema = generate_pydantic_schema(response["items"][0]["fields"])
                RecordFieldSchema.__bound__ = self.schema
            # TODO: we can use a cache to store the results to `.cache/argilla/datasets/{dataset_id}/records`
            self.__records = [
                OnlineRecordSchema(
                    id=record["id"],
                    fields=self.schema(**record["fields"]),
                    response=record["response"] if "response" in record else {},
                    external_id=record["external_id"],
                    inserted_at=record["inserted_at"],
                    updated_at=record["inserted_at"],
                )
                for record in response["items"]
            ]
            total_records = response["total"]
            if total_records > 1:
                prev_limit = 0
                with tqdm(
                    initial=len(self.__records), total=total_records, desc="Fetching records from Argilla"
                ) as pbar:
                    while prev_limit < total_records:
                        prev_limit += 1
                        self.__records += [
                            OnlineRecordSchema(
                                id=record["id"],
                                fields=self.schema(**record["fields"]),
                                response=record["response"] if "response" in record else {"values": {}},
                                external_id=record["external_id"],
                                inserted_at=record["inserted_at"],
                                updated_at=record["inserted_at"],
                            )
                            for record in self.client.get_records(id=self.id, offset=prev_limit, limit=1).parsed[
                                "items"
                            ]
                        ]
                        pbar.update(1)
        return self.__records

    def add_record(
        self,
        record: Union[RecordFieldSchema, Dict[str, Any]],
        response: Optional[Dict[str, Any]] = {"values": {}, "status": "submitted"},
        external_id: Optional[str] = None,
    ) -> None:
        if self.schema is None:
            warnings.warn("Since the `schema` hasn't been defined during the dataset creation, it will be inferred.")
            self.schema = generate_pydantic_schema(record)
        # # If there are records already logged to Argilla, fetch one and get the schema
        # self.schema = generate_pydantic_schema(self.fetch_one())
        # # If there are no records logged to Argilla, check if `self.schema` has been set
        # ...
        # # If `self.schema` has not been set, just infer the schema based on the record
        # ...
        # record = record.dict() if isinstance(record, RecordFieldSchema) else record
        self.client.add_record(
            id=self.id,
            record=RecordSchema(fields=self.schema(**record), external_id=external_id, response=response).dict(),
        )
        if self.__records is not None and isinstance(self.__records, list) and len(self.__records) > 0:
            self.records.append(self.schema(**record))

    def fetch_one(self) -> Union[Dict[str, Any], List[str, Any]]:
        if self.__records is None or len(self.__records) < 1:
            # TODO: handle exception if there are no records
            return self.client.get_records(id=self.id, offset=0, limit=1).parsed["items"][0]
        return self.__records[0]

    # TODO: we could fetch those on iter, maybe we can create an `streaming` flag or something similar
    def iter(self, batch_size: int = 32) -> List[BaseModel]:
        if self.__records is None or len(self.__records) < 1:
            first_batch = self.client.get_records(id=self.id, offset=0, limit=batch_size).parsed
            if self.schema is None:
                self.schema = generate_pydantic_schema(first_batch["items"][0]["fields"])
                RecordFieldSchema.__bound__ = self.schema
            batch = [
                OnlineRecordSchema(
                    id=record["id"],
                    fields=self.schema(**record["fields"]),
                    response=record["response"] if "response" in record else {},
                    external_id=record["external_id"],
                    inserted_at=record["inserted_at"],
                    updated_at=record["inserted_at"],
                )
                for record in first_batch["items"]
            ]
            self.__records = batch
            yield batch
            total_batches = first_batch["total"] // batch_size
            current_batch = 1
            with tqdm(initial=current_batch, total=total_batches, desc="Fetching records from Argilla") as pbar:
                while current_batch <= total_batches:
                    batch = [
                        OnlineRecordSchema(
                            id=record["id"],
                            fields=self.schema(**record["fields"]),
                            response=record["response"] if "response" in record else {},
                            external_id=record["external_id"],
                            inserted_at=record["inserted_at"],
                            updated_at=record["inserted_at"],
                        )
                        for record in first_batch["items"]
                    ]
                    self.__records += batch
                    yield batch
                    current_batch += 1
                    pbar.update(1)
        else:
            for batch in self.records[0::batch_size]:
                yield batch


def generate_pydantic_schema(record: Dict[str, Any]) -> BaseModel:
    record_schema = {key: (type(value), ...) for key, value in record.items()}
    return create_model("RecordFieldSchema", **record_schema)
