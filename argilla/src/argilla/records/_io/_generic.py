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

from collections import defaultdict
from typing import Any, Dict, List, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from argilla import Record


class GenericIO:
    """This is a mixin class for DatasetRecords and Export classes.
    It handles methods for exporting records to generic python formats."""

    @staticmethod
    def to_list(records: List["Record"], flatten: bool = False) -> List[Dict[str, Union[str, float, int, list]]]:
        """Export records to a list of dictionaries with either names or record index as keys.
        Args:
            flatten (bool): The structure of the exported dictionary.
                - True: The record fields, metadata, suggestions and responses will be flattened.
                - False: The record fields, metadata, suggestions and responses will be nested.
        Returns:
            dataset_records (List[Dict[str, Union[str, float, int, list]]]): The exported records in a list of dictionaries format.
        """
        dataset_records: list = []
        for record in records:
            dataset_records.append(GenericIO._record_to_dict(record=record, flatten=flatten))
        return dataset_records

    @staticmethod
    def to_dict(
        records: List["Record"], flatten: bool = False, orient: str = "names"
    ) -> Dict[str, Union[str, float, int, list]]:
        """Export records to a dictionary with either names or record index as keys.
        Args:
            flatten (bool): The structure of the exported dictionary.
                - True: The record fields, metadata, suggestions and responses will be flattened.
                - False: The record fields, metadata, suggestions and responses will be nested.
            orient (str): The orientation of the exported dictionary.
                - "names": The keys of the dictionary will be the names of the fields, metadata, suggestions and responses.
                - "index": The keys of the dictionary will be the id of the records.
        Returns:
            dataset_records (Dict[str, Union[str, float, int, list]]): The exported records in a dictionary format.
        """
        if orient == "names":
            dataset_records: dict = defaultdict(list)
            for record in records:
                for key, value in GenericIO._record_to_dict(record=record, flatten=flatten).items():
                    dataset_records[key].append(value)
        elif orient == "index":
            dataset_records: dict = {}
            for record in records:
                dataset_records[record.id] = GenericIO._record_to_dict(record=record, flatten=flatten)
        else:
            raise ValueError(f"Invalid value for orient parameter: {orient}")
        return dict(dataset_records)

    ############################
    # Private methods
    ############################

    @staticmethod
    def _record_to_dict(record: "Record", flatten=False) -> Dict[str, Any]:
        """Converts a Record object to a dictionary for export.
        Args:
            record (Record): The Record object to convert.
            flatten (bool): The structure of the exported dictionary.
                - True: The record fields, metadata, suggestions and responses will be flattened
                        so that their keys becomes the keys of the record dictionary, using
                        dot notation for nested keys. i.e. `label.suggestion` and `label.response`
                - False: The record fields, metadata, suggestions and responses will be nested as
                        dictionaries within the record dictionary. i.e. `label: {suggestion: ..., response: ...}`
        Returns:
            A dictionary representing the record.
        """
        record_dict = record.to_dict()
        if flatten:
            responses: dict = record_dict.pop("responses")
            suggestions: dict = record_dict.pop("suggestions")
            fields: dict = record_dict.pop("fields")
            metadata: dict = record_dict.pop("metadata")
            record_dict.update(fields)
            record_dict.update(metadata)
            question_names = set(suggestions.keys()).union(responses.keys())
            for question_name in question_names:
                _suggestion: Union[Dict, None] = suggestions.get(question_name)
                if _suggestion:
                    record_dict[f"{question_name}.suggestion"] = _suggestion.pop("value")
                    record_dict.update(
                        {f"{question_name}.suggestion.{key}": value for key, value in _suggestion.items()}
                    )
                for _response in responses.get(question_name, []):
                    user_id = _response.pop("user_id")
                    record_dict[f"{question_name}.response.{user_id}"] = _response.pop("value")
                    record_dict.update(
                        {f"{question_name}.response.{user_id}.{key}": value for key, value in _response.items()}
                    )
        return record_dict
