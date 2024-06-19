# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import warnings
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Sequence, Union
from uuid import UUID

from tqdm import tqdm

from argilla._api import RecordsAPI
from argilla._helpers import LoggingMixin
from argilla._models import RecordModel, MetadataValue, VectorValue, FieldValue
from argilla.client import Argilla
from argilla.records._io import GenericIO, HFDataset, HFDatasetsIO, JsonIO
from argilla.records._resource import Record
from argilla.records._search import Query
from argilla.responses import Response
from argilla.settings import TextField, VectorField
from argilla.settings._metadata import MetadataPropertyBase
from argilla.settings._question import QuestionPropertyBase
from argilla.suggestions import Suggestion
from argilla.vectors import Vector

if TYPE_CHECKING:
    from argilla.datasets import Dataset


class DatasetRecordsIterator:
    """This class is used to iterate over records in a dataset"""

    def __init__(
        self,
        dataset: "Dataset",
        client: "Argilla",
        query: Optional[Query] = None,
        start_offset: int = 0,
        batch_size: Optional[int] = None,
        with_suggestions: bool = False,
        with_responses: bool = False,
        with_vectors: Optional[Union[str, List[str], bool]] = None,
    ):
        self.__dataset = dataset
        self.__client = client
        self.__query = query or Query()
        self.__offset = start_offset or 0
        self.__batch_size = batch_size or 100
        self.__with_suggestions = with_suggestions
        self.__with_responses = with_responses
        self.__with_vectors = with_vectors
        self.__records_batch = []

    def __iter__(self):
        return self

    def __next__(self) -> Record:
        if not self._has_local_records():
            self._fetch_next_batch()
            if not self._has_local_records():
                raise StopIteration()
        return self._next_record()

    def _next_record(self) -> Record:
        return self.__records_batch.pop(0)

    def _has_local_records(self) -> bool:
        return len(self.__records_batch) > 0

    def _fetch_next_batch(self) -> None:
        self.__records_batch = list(self._list())
        self.__offset += len(self.__records_batch)

    def _list(self) -> Sequence[Record]:
        for record_model in self._fetch_from_server():
            yield Record.from_model(model=record_model, dataset=self.__dataset)

    def _fetch_from_server(self) -> List[RecordModel]:
        if not self.__dataset.exists():
            raise ValueError(f"Dataset {self.__dataset.name} does not exist on the server.")
        if self._is_search_query():
            return self._fetch_from_server_with_search()
        return self._fetch_from_server_with_list()

    def _fetch_from_server_with_list(self) -> List[RecordModel]:
        return self.__client.api.records.list(
            dataset_id=self.__dataset.id,
            limit=self.__batch_size,
            offset=self.__offset,
            with_responses=self.__with_responses,
            with_suggestions=self.__with_suggestions,
            with_vectors=self.__with_vectors,
        )

    def _fetch_from_server_with_search(self) -> List[RecordModel]:
        search_items, total = self.__client.api.records.search(
            dataset_id=self.__dataset.id,
            query=self.__query.model,
            limit=self.__batch_size,
            offset=self.__offset,
            with_responses=self.__with_responses,
            with_suggestions=self.__with_suggestions,
        )
        return [record_model for record_model, _ in search_items]

    def _is_search_query(self) -> bool:
        return bool(self.__query and (self.__query.query or self.__query.filter))

    def to_list(self, flatten: bool) -> List[Dict[str, Any]]:
        return GenericIO.to_list(records=list(self), flatten=flatten)

    def to_dict(self, flatten: bool, orient: str) -> Dict[str, Any]:
        data = GenericIO.to_dict(records=list(self), flatten=flatten, orient=orient)
        return data

    def to_json(self, path: Union[Path, str]) -> Path:
        return JsonIO.to_json(records=list(self), path=path)

    def to_datasets(self) -> "HFDataset":
        return HFDatasetsIO.to_datasets(records=list(self))


class DatasetRecords(Iterable[Record], LoggingMixin):
    """This class is used to work with records from a dataset and is accessed via `Dataset.records`.
    The responsibility of this class is to provide an interface to interact with records in a dataset,
    by adding, updating, fetching, querying, deleting, and exporting records.

    Attributes:
        client (Argilla): The Argilla client object.
        dataset (Dataset): The dataset object.
    """

    _api: RecordsAPI

    DEFAULT_BATCH_SIZE = 256

    def __init__(self, client: "Argilla", dataset: "Dataset"):
        """Initializes a DatasetRecords object with a client and a dataset.
        Args:
            client: An Argilla client object.
            dataset: A Dataset object.
        """
        self.__client = client
        self.__dataset = dataset
        self._api = self.__client.api.records

    def __iter__(self):
        return DatasetRecordsIterator(self.__dataset, self.__client, with_suggestions=True, with_responses=True)

    def __call__(
        self,
        query: Optional[Union[str, Query]] = None,
        batch_size: Optional[int] = DEFAULT_BATCH_SIZE,
        start_offset: int = 0,
        with_suggestions: bool = True,
        with_responses: bool = True,
        with_vectors: Optional[Union[List, bool, str]] = None,
    ) -> DatasetRecordsIterator:
        """Returns an iterator over the records in the dataset on the server.

        Parameters:
            query: A string or a Query object to filter the records.
            batch_size: The number of records to fetch in each batch. The default is 256.
            start_offset: The offset from which to start fetching records. The default is 0.
            with_suggestions: Whether to include suggestions in the records. The default is True.
            with_responses: Whether to include responses in the records. The default is True.
            with_vectors: A list of vector names to include in the records. The default is None.
                If a list is provided, only the specified vectors will be included.
                If True is provided, all vectors will be included.

        Returns:
            An iterator over the records in the dataset on the server.

        """
        if query and isinstance(query, str):
            query = Query(query=query)

        if with_vectors:
            self._validate_vector_names(vector_names=with_vectors)

        return DatasetRecordsIterator(
            self.__dataset,
            self.__client,
            query=query,
            batch_size=batch_size,
            start_offset=start_offset,
            with_suggestions=with_suggestions,
            with_responses=with_responses,
            with_vectors=with_vectors,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dataset})"

    ############################
    # Public methods
    ############################

    def log(
        self,
        records: Union[List[dict], List[Record], HFDataset],
        mapping: Optional[Dict[str, str]] = None,
        user_id: Optional[UUID] = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> List[Record]:
        """Add or update records in a dataset on the server using the provided records.
        If the record includes a known `id` field, the record will be updated.
        If the record does not include a known `id` field, the record will be added as a new record.
        See `rg.Record` for more information on the record definition.

        Parameters:
            records: A list of `Record` objects, a Hugging Face Dataset, or a list of dictionaries representing the records.
                     If records are defined as a dictionaries or a dataset, the keys/ column names should correspond to the
                     fields in the Argilla dataset's fields and questions. `id` should be provided to identify the records when updating.
            mapping: A dictionary that maps the keys/ column names in the records to the fields or questions in the Argilla dataset.
            user_id: The user id to be associated with the records' response. If not provided, the current user id is used.
            batch_size: The number of records to send in each batch. The default is 256.

        Returns:
            A list of Record objects representing the updated records.

        """
        record_models = self._ingest_records(records=records, mapping=mapping, user_id=user_id or self.__client.me.id)
        batch_size = self._normalize_batch_size(
            batch_size=batch_size,
            records_length=len(record_models),
            max_value=self._api.MAX_RECORDS_PER_UPSERT_BULK,
        )

        created_or_updated = []
        records_updated = 0
        for batch in tqdm(
            iterable=range(0, len(records), batch_size), desc="Adding and updating records", unit="batch"
        ):
            self._log_message(message=f"Sending records from {batch} to {batch + batch_size}.")
            batch_records = record_models[batch : batch + batch_size]
            models, updated = self._api.bulk_upsert(dataset_id=self.__dataset.id, records=batch_records)
            created_or_updated.extend([Record.from_model(model=model, dataset=self.__dataset) for model in models])
            records_updated += updated

        records_created = len(created_or_updated) - records_updated
        self._log_message(
            message=f"Updated {records_updated} records and added {records_created} records to dataset {self.__dataset.name}",
            level="info",
        )

        return created_or_updated

    def delete(
        self,
        records: List[Record],
    ) -> List[Record]:
        """Delete records in a dataset on the server using the provided records
            and matching based on the id.

        Parameters:
            records: A list of `Record` objects representing the records to be deleted.

        Returns:
            A list of Record objects representing the deleted records.

        """
        mapping = None
        user_id = self.__client.me.id

        record_models = self._ingest_records(records=records, mapping=mapping, user_id=user_id)

        self._api.delete_many(dataset_id=self.__dataset.id, records=record_models)

        self._log_message(
            message=f"Deleted {len(record_models)} records from dataset {self.__dataset.name}",
            level="info",
        )

        return record_models

    def to_dict(self, flatten: bool = False, orient: str = "names") -> Dict[str, Any]:
        """
        Return the records as a dictionary. This is a convenient shortcut for dataset.records(...).to_dict().

        Parameters:
            flatten (bool): The structure of the exported dictionary.
                - True: The record fields, metadata, suggestions and responses will be flattened.
                - False: The record fields, metadata, suggestions and responses will be nested.
            orient (str): The orientation of the exported dictionary.
                - "names": The keys of the dictionary will be the names of the fields, metadata, suggestions and responses.
                - "index": The keys of the dictionary will be the id of the records.
        Returns:
            A dictionary of records.

        """
        return self().to_dict(flatten=flatten, orient=orient)

    def to_list(self, flatten: bool = False) -> List[Dict[str, Any]]:
        """
        Return the records as a list of dictionaries. This is a convenient shortcut for dataset.records(...).to_list().

        Parameters:
            flatten (bool): Whether to flatten the dictionary and use dot notation for nested keys like suggestions and responses.

        Returns:
            A list of dictionaries of records.
        """
        data = self().to_list(flatten=flatten)
        return data

    def to_json(self, path: Union[Path, str]) -> Path:
        """
        Export the records to a file on disk.

        Parameters:
            path (str): The path to the file to save the records.

        Returns:
            The path to the file where the records were saved.

        """
        return self().to_json(path=path)

    def from_json(self, path: Union[Path, str]) -> List[Record]:
        """Creates a DatasetRecords object from a disk path to a JSON file.
            The JSON file should be defined by `DatasetRecords.to_json`.

        Args:
            path (str): The path to the file containing the records.

        Returns:
            DatasetRecords: The DatasetRecords object created from the disk path.

        """
        records = JsonIO._records_from_json(path=path)
        return self.log(records=records)

    def to_datasets(self) -> HFDataset:
        """
        Export the records to a HFDataset.

        Returns:
            The dataset containing the records.

        """

        return self().to_datasets()

    ############################
    # Private methods
    ############################

    def _ingest_records(
        self,
        records: Union[List[Dict[str, Any]], Dict[str, Any], List[Record], Record, HFDataset],
        mapping: Optional[Dict[str, str]] = None,
        user_id: Optional[UUID] = None,
    ) -> List[RecordModel]:
        if len(records) == 0:
            raise ValueError("No records provided to ingest.")
        if HFDatasetsIO._is_hf_dataset(dataset=records):
            records = HFDatasetsIO._record_dicts_from_datasets(dataset=records)
        if all(map(lambda r: isinstance(r, dict), records)):
            # Records as flat dicts of values to be matched to questions as suggestion or response
            records = [self._infer_record_from_mapping(data=r, mapping=mapping, user_id=user_id) for r in records]  # type: ignore
        elif all(map(lambda r: isinstance(r, Record), records)):
            for record in records:
                record.dataset = self.__dataset
        else:
            raise ValueError(
                "Records should be a a list Record instances, "
                "a Hugging Face Dataset, or a list of dictionaries representing the records."
            )
        return [record.api_model() for record in records]

    def _normalize_batch_size(self, batch_size: int, records_length, max_value: int):
        norm_batch_size = min(batch_size, records_length, max_value)

        if batch_size != norm_batch_size:
            self._log_message(
                message=f"The provided batch size {batch_size} was normalized. Using value {norm_batch_size}.",
                level="warning",
            )

        return norm_batch_size

    def _validate_vector_names(self, vector_names: Union[List[str], str]) -> None:
        if not isinstance(vector_names, list):
            vector_names = [vector_names]
        for vector_name in vector_names:
            if isinstance(vector_name, bool):
                continue
            if vector_name not in self.__dataset.schema:
                raise ValueError(f"Vector field {vector_name} not found in dataset schema.")

    def _infer_record_from_mapping(
        self,
        data: dict,
        mapping: Optional[Dict[str, str]] = None,
        user_id: Optional[UUID] = None,
    ) -> "Record":
        """Converts a mapped record dictionary to a Record object for use by the add or update methods.
        Args:
            dataset: The dataset object to which the record belongs.
            data: A dictionary representing the record.
            mapping: A dictionary mapping source data keys to Argilla fields, questions, and ids.
            user_id: The user id to associate with the record responses.
        Returns:
            A Record object.
        """
        record_id: Optional[str] = None

        fields: Dict[str, FieldValue] = {}
        vectors: Dict[str, VectorValue] = {}
        metadata: Dict[str, MetadataValue] = {}

        responses: List[Response] = []
        suggestion_values: Dict[str, dict] = defaultdict(dict)

        schema = self.__dataset.schema

        for attribute, value in data.items():
            schema_item = schema.get(attribute)
            attribute_type = None
            sub_attribute = None

            # Map source data keys using the mapping
            if mapping and attribute in mapping:
                attribute_mapping = mapping.get(attribute)
                attribute_mapping = attribute_mapping.split(".")
                attribute = attribute_mapping[0]
                schema_item = schema.get(attribute)
                if len(attribute_mapping) > 1:
                    attribute_type = attribute_mapping[1]
                if len(attribute_mapping) > 2:
                    sub_attribute = attribute_mapping[2]
            elif schema_item is mapping is None and attribute != "id":
                warnings.warn(
                    message=f"""Record attribute {attribute} is not in the schema so skipping.
                        Define a mapping to map source data fields to Argilla Fields, Questions, and ids
                        """
                )
                continue

            if attribute == "id":
                record_id = value
                continue

            # Add suggestion values to the suggestions
            if attribute_type == "suggestion":
                if sub_attribute in ["score", "agent"]:
                    suggestion_values[attribute][sub_attribute] = value

                elif sub_attribute is None:
                    suggestion_values[attribute].update(
                        {"value": value, "question_name": attribute, "question_id": schema_item.id}
                    )
                else:
                    warnings.warn(
                        message=f"Record attribute {sub_attribute} is not a valid suggestion sub_attribute so skipping."
                    )
                continue

            # Assign the value to question, field, or response based on schema item
            if isinstance(schema_item, TextField):
                fields[attribute] = value
            elif isinstance(schema_item, QuestionPropertyBase) and attribute_type == "response":
                responses.append(Response(question_name=attribute, value=value, user_id=user_id))
            elif isinstance(schema_item, QuestionPropertyBase) and attribute_type is None:
                suggestion_values[attribute].update(
                    {"value": value, "question_name": attribute, "question_id": schema_item.id}
                )
            elif isinstance(schema_item, VectorField):
                vectors[attribute] = value
            elif isinstance(schema_item, MetadataPropertyBase):
                metadata[attribute] = value
            else:
                warnings.warn(message=f"Record attribute {attribute} is not in the schema or mapping so skipping.")
                continue

        suggestions = [Suggestion(**suggestion_dict) for suggestion_dict in suggestion_values.values()]

        return Record(
            id=record_id,
            fields=fields,
            vectors=vectors,
            metadata=metadata,
            suggestions=suggestions,
            responses=responses,
            _dataset=self.__dataset,
        )
