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

from pydantic import BaseModel, create_model
from tqdm import tqdm

import argilla as rg

if TYPE_CHECKING:
    from argilla.client.api import Argilla
    from argilla.client.sdk.datasets.v1.models import FeedbackDataset

FieldsSchema = TypeVar("FieldsSchema", bound=BaseModel)


class RecordSchema(BaseModel):
    fields: FieldsSchema
    response: Optional[Dict[str, Any]] = {"values": {}}
    external_id: Optional[str] = None


class OnlineRecordSchema(RecordSchema):
    id: str
    inserted_at: Optional[str] = None
    updated_at: Optional[str] = None


class DatasetStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"


class QuestionSchema(BaseModel):
    name: str
    title: str
    required: bool
    settings: Dict[str, Any]


class Dataset:
    client: "Argilla" = rg.active_client()

    def __init__(
        self,
        # name: str,
        # workspace: Optional[str] = None,
        id: str,
        schema: Optional[BaseModel] = None,
        description: Optional[str] = None,
        guidelines: Optional[str] = None,
        records: Optional[List[BaseModel]] = None,
        questions: Optional[List[QuestionSchema]] = None,
    ) -> None:
        # TODO: check if dataset with that name in that workspace exists,
        # and show info if the dataset doesn't exist to the user so as to
        # create the dataset.
        self.id = id
        dataset: "FeedbackDataset" = self.client.get_dataset(id=self.id).parsed

        self.name = dataset.name
        self.workspace = dataset.workspace_id

        self.schema = schema or None
        if self.schema:
            FieldsSchema.__bound__ = self.schema
        self.description = description or ""
        self.guidelines = dataset.guidelines or guidelines

        # TODO: create `ResponseSchema` based on `self.questions`
        self.__questions = questions or None
        self.__records = records or None

        self.__status = DatasetStatus(dataset.status) or DatasetStatus.DRAFT

    @property
    def status(self) -> DatasetStatus:
        return self.__status

    def publish(self) -> None:
        if self.__status == DatasetStatus.DRAFT:
            self.client.publish_dataset(id=self.id)
            self.__status = DatasetStatus.READY

    @property
    def records(self) -> List[FieldsSchema]:
        if self.__records is None or len(self.__records) < 1:
            response = self.client.get_records(id=self.id, offset=0, limit=1).parsed
            if self.schema is None:
                self.schema = generate_pydantic_schema(response["items"][0]["fields"])
                FieldsSchema.__bound__ = self.schema
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
                        increment = 1 if prev_limit + 1 < total_records else total_records - prev_limit
                        self.__records += [
                            OnlineRecordSchema(
                                id=record["id"],
                                fields=self.schema(**record["fields"]),
                                response=record["response"] if "response" in record else {"values": {}},
                                external_id=record["external_id"],
                                inserted_at=record["inserted_at"],
                                updated_at=record["inserted_at"],
                            )
                            for record in self.client.get_records(
                                id=self.id, offset=prev_limit, limit=prev_limit + increment
                            ).parsed["items"]
                        ]
                        pbar.update(increment)
        return self.__records

    @property
    def questions(self) -> List[QuestionSchema]:
        return self.__questions

    def __repr__(self) -> str:
        return (
            f"Dataset(name={self.name}, workspace={self.workspace}, schema={self.schema},"
            f" description={self.description}, guidelines={self.guidelines}, questions={self.questions},"
            f" status={self.status})"
        )

    def add_record(
        self,
        record: Union[FieldsSchema, Dict[str, Any]],
        response: Optional[Dict[str, Any]] = {"values": {}},
        external_id: Optional[str] = None,
    ) -> None:
        if self.status is DatasetStatus.DRAFT:
            raise ValueError("Cannot add records to a dataset that is in draft status, please publish it first.")
        if self.schema is None:
            warnings.warn("Since the `schema` hasn't been defined during the dataset creation, it will be inferred.")
            self.schema = generate_pydantic_schema(record)
        # # If there are records already logged to Argilla, fetch one and get the schema
        # self.schema = generate_pydantic_schema(self.fetch_one())
        # # If there are no records logged to Argilla, check if `self.schema` has been set
        # ...
        # # If `self.schema` has not been set, just infer the schema based on the record
        # ...
        # record = record.dict() if isinstance(record, FieldsSchema) else record
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
                FieldsSchema.__bound__ = self.schema
            yield [self.schema(**record) for record in first_batch["items"]]
            total_batches = first_batch["total"] // batch_size
            current_batch = 1
            with tqdm(initial=current_batch, total=total_batches, desc="Fetching records from Argilla") as pbar:
                while current_batch < total_batches:
                    yield [
                        OnlineRecordSchema(
                            id=record["id"],
                            fields=self.schema(**record["fields"]),
                            response=record["response"] if "response" in record else {},
                            external_id=record["external_id"],
                            inserted_at=record["inserted_at"],
                            updated_at=record["inserted_at"],
                        )
                        for record in self.client.get_records(
                            id=self.id, offset=current_batch * batch_size, limit=batch_size
                        ).parsed["items"]
                    ]
                    current_batch += 1
                    pbar.update(1)
        else:
            for batch in self.records[:, batch_size]:
                yield [
                    OnlineRecordSchema(
                        id=record["id"],
                        fields=self.schema(**record["fields"]),
                        response=record["response"] if "response" in record else {},
                        external_id=record["external_id"],
                        inserted_at=record["inserted_at"],
                        updated_at=record["inserted_at"],
                    )
                    for record in batch
                ]


def generate_pydantic_schema(record: Dict[str, Any]) -> BaseModel:
    record_schema = {key: (type(value), ...) for key, value in record.items()}
    return create_model("FieldsSchema", **record_schema)
