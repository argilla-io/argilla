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
from cProfile import label
import warnings
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Sequence, Union
from uuid import UUID

from tqdm import tqdm

from argilla._api import RecordsAPI
from argilla._helpers import LoggingMixin
from argilla._models import RecordModel, MetadataValue
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
        return DatasetRecordsIterator(self.__dataset, self.__client)

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
        records = list(self(with_suggestions=True, with_responses=True))
        data = GenericIO.to_dict(records=records, flatten=flatten, orient=orient)
        return data

    def to_list(self, flatten: bool = False) -> List[Dict[str, Any]]:
        """
        Return the records as a list of dictionaries. This is a convenient shortcut for dataset.records(...).to_list().

        Parameters:
            flatten (bool): Whether to flatten the dictionary and use dot notation for nested keys like suggestions and responses.

        Returns:
            A list of dictionaries of records.
        """
        records = list(self(with_suggestions=True, with_responses=True))
        data = GenericIO.to_list(records=records, flatten=flatten)
        return data

    def to_json(self, path: Union[Path, str]) -> Path:
        """
        Export the records to a file on disk.

        Parameters:
            path (str): The path to the file to save the records.

        Returns:
            The path to the file where the records were saved.

        """
        records = list(self(with_suggestions=True, with_responses=True))
        return JsonIO.to_json(records=records, path=path)

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
        records = list(self(with_suggestions=True, with_responses=True))
        return HFDatasetsIO.to_datasets(records=records)

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
            keys = list(dict(next(iter(records))).keys())
            mapping = self._reverse_parse_mapping(keys=keys, mapping=mapping)
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

    def _reverse_parse_mapping(self, keys: List[str], mapping: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        schema = self.__dataset.schema

        reverse_mapping = {}
        mapping = mapping or {}

        unknown_src_keys = [key for key in keys if key not in mapping.values() or key not in schema]

        warnings.warn(message=f"Record keys {unknown_src_keys} are not in the schema or mapping so skipping.")

        for _attribute_mapping, src_key in mapping.items():
            if src_key not in keys:
                raise ValueError(
                    f"Record key in mapping {src_key} not found in first row of provided records. \
                        Records should be a list of dictionaries with keys matching the mapping."
                )

            _attribute_mapping = _attribute_mapping.split(".")
            attribute_name = _attribute_mapping[0]
            attribute_type = None if len(_attribute_mapping) == 1 else _attribute_mapping[1]
            sub_attribute = None if len(_attribute_mapping) < 3 else _attribute_mapping[2]

            if attribute_name not in schema:
                raise ValueError(f"Record attribute {attribute_name} not found in the schema.")

            schema_attribute = schema[attribute_name]

            if attribute_type == "suggestion" and sub_attribute is None:
                raise ValueError(
                    f"Record attribute {attribute_name} is a suggestion so sub_attribute is required. \
                        To assign the value to the suggestion value, use the format '<question_name>.suggestion.value' or <question_name>"
                )

            # Assign the value to question, field, or response based on schema item
            if isinstance(schema_attribute, TextField):
                attribute_type = "field"
            elif isinstance(schema_attribute, QuestionPropertyBase) and attribute_type == "response":
                attribute_type = "response"
            elif (
                isinstance(schema_attribute, QuestionPropertyBase)
                and attribute_type is None
                or attribute_type == "suggestion"
            ):
                attribute_type = "suggestion"
                sub_attribute = sub_attribute or "value"
            elif isinstance(schema_attribute, VectorField):
                attribute_type = "vector"
            elif isinstance(schema_attribute, MetadataPropertyBase):
                attribute_type = "metadata"
            else:
                # warnings.warn(message=f"Record attribute {attribute} is not in the schema or mapping so skipping.")
                continue

            reverse_mapping[src_key] = (attribute_name, attribute_type, sub_attribute, schema_attribute.id)
            
            self._log_message(
                message=f"Reverse mapping: {src_key} -> {attribute_name} ({attribute_type})",
                level="debug",
            )

        for key in keys:
            if key in reverse_mapping:
                continue
            schema_item = schema.get(key)
            if not schema_item:
                continue
            if isinstance(schema_item, TextField):
                attribute_type = "field"
            elif isinstance(schema_item, QuestionPropertyBase):
                attribute_type = "suggestion"
            elif isinstance(schema_item, VectorField):
                attribute_type = "vector"
            elif isinstance(schema_item, MetadataPropertyBase):
                attribute_type = "metadata"
            reverse_mapping[key] = (key, attribute_type, None, schema_item.id)

        return reverse_mapping

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
        fields: Dict[str, str] = {}
        responses: List[Response] = []
        record_id: Optional[str] = None
        suggestion_values = defaultdict(dict)
        vectors: List[Vector] = []
        metadata: Dict[str, MetadataValue] = {}

        for src_key, value in data.items():
            attribute_name, attribute_type, sub_attribute, schema_item_id = mapping.get(
                src_key, (None, None, None, None)
            )

            if attribute_name == "id":
                record_id = value
                continue

            # Add suggestion values to the suggestions
            if attribute_type == "suggestion":
                sub_attribute = sub_attribute or "value"
                suggestion_values[attribute_name][sub_attribute] = value
                suggestion_values[attribute_name]["question_id"] = schema_item_id

            # Assign the value to question, field, or response based on schema item
            if attribute_type == "field":
                fields[attribute_name] = value
            elif attribute_type == "response":
                responses.append(Response(question_name=attribute_name, value=value, user_id=user_id))
            elif attribute_type is "suggestion":
                suggestion_values[attribute_name].update(
                    {"value": value, "question_name": attribute_name, "question_id": schema_item_id}
                )
            elif attribute_type == "vector":
                vectors.append(Vector(name=attribute_name, values=value))
            elif attribute_type == "metadata":
                metadata[attribute_name] = value
            else:
                warnings.warn(message=f"Record attribute {attribute_name} is not in the schema or mapping so skipping.")
                continue

        suggestions = [Suggestion(**suggestion_dict) for suggestion_dict in suggestion_values.values()]

        return Record(
            id=record_id,
            fields=fields,
            suggestions=suggestions,
            responses=responses,
            vectors=vectors,
            metadata=metadata,
            _dataset=self.__dataset,
        )
