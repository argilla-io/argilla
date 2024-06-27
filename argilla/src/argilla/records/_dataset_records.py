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
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union
from uuid import UUID

from tqdm import tqdm

from argilla._api import RecordsAPI
from argilla._helpers import LoggingMixin
from argilla._models import RecordModel
from argilla._exceptions import RecordsIngestionError
from argilla.client import Argilla
from argilla.records._io import GenericIO, HFDataset, HFDatasetsIO, JsonIO
from argilla.records._resource import Record
from argilla.records._search import Query
from argilla.responses import Response
from argilla.settings import TextField, VectorField
from argilla.settings._metadata import MetadataPropertyBase
from argilla.settings._question import QuestionPropertyBase
from argilla.suggestions import Suggestion

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
        mapping: Optional[Dict[str, Union[str, Sequence[str]]]] = None,
        user_id: Optional[UUID] = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> "DatasetRecords":
        """Add or update records in a dataset on the server using the provided records.
        If the record includes a known `id` field, the record will be updated.
        If the record does not include a known `id` field, the record will be added as a new record.
        See `rg.Record` for more information on the record definition.

        Parameters:
            records: A list of `Record` objects, a Hugging Face Dataset, or a list of dictionaries representing the records.
                     If records are defined as a dictionaries or a dataset, the keys/ column names should correspond to the
                     fields in the Argilla dataset's fields and questions. `id` should be provided to identify the records when updating.
            mapping: A dictionary that maps the keys/ column names in the records to the fields or questions in the Argilla dataset.
                     To assign an incoming key or column to multiple fields or questions, provide a list or tuple of field or question names.
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
            iterable=range(0, len(records), batch_size),
            desc="Sending records...",
            total=len(records) // batch_size,
            unit="batch",
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

        return self

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
        mapping: Optional[Dict[str, Union[str, Sequence[str]]]] = None,
        user_id: Optional[UUID] = None,
    ) -> List[RecordModel]:
        """Ingests records from a list of dictionaries, a Hugging Face Dataset, or a list of Record objects."""

        if len(records) == 0:
            raise ValueError("No records provided to ingest.")

        if HFDatasetsIO._is_hf_dataset(dataset=records):
            records = HFDatasetsIO._record_dicts_from_datasets(dataset=records)

        ingested_records = []

        for record in records:
            try:
                if not isinstance(record, Record):
                    record = self._infer_record_from_mapping(data=record, mapping=mapping, user_id=user_id)
                elif isinstance(record, Record):
                    record.dataset = self.__dataset
                else:
                    raise ValueError(
                        "Records should be a a list Record instances, "
                        "a Hugging Face Dataset, or a list of dictionaries representing the records."
                        f"Found a record of type {type(record)}: {record}."
                    )
            except Exception as e:
                raise RecordsIngestionError(f"Failed to ingest record from dict {record}: {e}")
            ingested_records.append(record.api_model())
        return ingested_records

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

    def _render_record_mapping(
        self,
        records: List[Dict[str, Any]],
        mapping: Optional[Dict[str, Union[str, Sequence[str]]]] = None,
    ) -> Dict[str, Tuple[Optional[str]]]:
        """Renders a mapping from a list of records and a mapping dictionary, to a singular mapping dictionary."""
        schema = self.__dataset.schema
        mapping = mapping or {}
        singular_mapping = defaultdict(dict)

        # update the mapping with unmapped columns
        for key, value in records[0].items():
            if key not in schema and key not in mapping:
                warnings.warn(
                    message=f"Record attribute {key} is not in the schema so skipping.",
                )
            if key not in mapping:
                mapping[key] = key

        # create a singular mapping with destinations from the schema
        for source_key, value in mapping.items():
            destinations = [value] if isinstance(value, str) else list(value)

            for attribute_mapping in destinations:
                attribute_mapping = attribute_mapping.split(".")

                attribute_name = attribute_mapping[0]
                schema_item = schema.get(attribute_name)
                attribute_type = attribute_mapping[1] if len(attribute_mapping) > 1 else None
                sub_attribute = attribute_mapping[2] if len(attribute_mapping) > 2 else None

                # Assign the value to question, field, or response based on schema item
                if attribute_name == "id":
                    attribute_type = "id"
                elif isinstance(schema_item, TextField):
                    attribute_type = "field"
                elif isinstance(schema_item, QuestionPropertyBase) and attribute_type == "response":
                    attribute_type = "response"
                elif (
                    isinstance(schema_item, QuestionPropertyBase)
                    and attribute_type is None
                    or attribute_type == "suggestion"
                ):
                    attribute_type = "suggestion"
                    sub_attribute = sub_attribute or "value"
                    attribute_name = (attribute_name, sub_attribute)
                elif isinstance(schema_item, VectorField):
                    attribute_type = "vector"
                elif isinstance(schema_item, MetadataPropertyBase):
                    attribute_type = "metadata"
                else:
                    warnings.warn(
                        message=f"Record attribute {attribute_name} is not in the schema or mapping so skipping."
                    )
                    continue

                singular_mapping[attribute_type][attribute_name] = source_key

        return singular_mapping

    def _infer_record_from_mapping(
        self,
        data: Dict[str, Any],
        mapping: Dict[str, Tuple[Optional[str]]],
        user_id: Optional[UUID] = None,
    ) -> "Record":
        """Converts a mapped record dictionary to a Record object for use by the add or update methods.
        Args:
            dataset: The dataset object to which the record belongs.
            data: A dictionary representing the record.
            mapping: A dictionary mapping from source data keys/ columns to Argilla fields, questions, ids, etc.
            user_id: The user id to associate with the record responses.
        Returns:
            A Record object.

        """

        mapping = self._render_record_mapping(records=records, mapping=mapping)
        id_mapping = mapping.get("id", {})
        suggestion_mapping = mapping.get("suggestion", {})
        response_mapping = mapping.get("response", {})
        field_mapping = mapping.get("field", {})
        metadata_mapping = mapping.get("metadata", {})
        vector_mapping = mapping.get("vector", {})

        if "id" in id_mapping:
            record_id = data.get(id_mapping["id"])
        else:
            record_id = None

        # Parse suggestions and responses into objects aligned with questions
        suggestions = self._parse_suggestion_from_mapping(data=data, mapping=suggestion_mapping)
        responses = self._parse_response_from_mapping(data=data, mapping=response_mapping, user_id=user_id)

        # Parse fields, metadata, and vectors into
        fields = {attribute_name: data.get(source_key) for attribute_name, source_key in field_mapping.items()}
        metadata = {attribute_name: data.get(source_key) for attribute_name, source_key in metadata_mapping.items()}
        vectors = {attribute_name: data.get(source_key) for attribute_name, source_key in vector_mapping.items()}

        return Record(
            id=record_id,
            fields=fields,
            vectors=vectors,
            metadata=metadata,
            suggestions=suggestions,
            responses=responses,
            _dataset=self.__dataset,
        )

    def _parse_suggestion_from_mapping(
        self, data: Dict[str, Any], mapping: Dict[str, Tuple[Optional[str]]]
    ) -> List[Suggestion]:
        """Converts a mapped suggestion dictionary to a Suggestion object for use by the add or update methods.
        Suggestions can be defined across multiple source values and mapped to single questions.
        Args:
            data: A dictionary representing the suggestion.
            mapping: A dictionary mapping from source data keys/ columns to Argilla fields, questions, ids, etc.
        Returns:
            A Suggestion object.

        """
        suggestion_values = defaultdict(dict)

        for (attribute_name, sub_attribute), source_key in mapping.items():
            value = data.get(source_key)
            schema_item = self.__dataset.schema.get(attribute_name)
            suggestion_values[attribute_name].update(
                {sub_attribute: value, "question_name": attribute_name, "question_id": schema_item.id}
            )

        suggestions = [Suggestion(**suggestion_dict) for suggestion_dict in suggestion_values.values()]

        return suggestions

    def _parse_response_from_mapping(
        self, data: Dict[str, Any], mapping: Dict[str, Tuple[Optional[str]]], user_id: UUID
    ) -> List[Response]:
        """Converts a mapped response dictionary to a Response object for use by the add or update methods.
        Args:
            data: A dictionary representing the response.
            mapping: A dictionary mapping from source data keys/ columns to Argilla fields, questions, ids, etc.
            user_id: The user id to associate with the record responses.
        Returns:
            A Response object.

        """
        responses = []

        for attribute_name, source_key in mapping.items():
            response = Response(
                value=data.get(source_key),
                question_name=attribute_name,
                user_id=user_id,
            )
            responses.append(response)

        return responses
