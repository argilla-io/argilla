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
        records_schema = set()
        dataset_records: list = []
        for record in records:
            record_dict = GenericIO._record_to_dict(record=record, flatten=flatten)
            records_schema.update([k for k in record_dict])
            dataset_records.append(record_dict)

        # normalize records structure
        for record_dict in dataset_records:
            record_dict.update({k: None for k in records_schema if k not in record_dict})

        return dataset_records

    @classmethod
    def to_dict(
        cls, records: List["Record"], flatten: bool = False, orient: str = "names"
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
            for record in cls.to_list(records, flatten=flatten):
                for key, value in record.items():
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
            record_dict.update(
                **record_dict.pop("fields", {}),
                **record_dict.pop("metadata", {}),
                **record_dict.pop("vectors", {}),
            )

            record_dict.pop("responses")
            record_dict.pop("suggestions")

            responses_dict = defaultdict(list)
            for response in record.responses:
                responses_key = f"{response.question_name}.responses"
                responses_users_key = f"{responses_key}.users"
                responses_status_key = f"{responses_key}.status"

                responses_dict[responses_key].append(response.value)
                responses_dict[responses_users_key].append(str(response.user_id))
                responses_dict[responses_status_key].append(response.status.value if response.status else None)

            suggestions_dict = {}
            for suggestion in record.suggestions:
                suggestion_key = f"{suggestion.question_name}.suggestion"
                suggestion_agent_key = f"{suggestion_key}.agent"
                suggestion_score_key = f"{suggestion_key}.score"

                suggestions_dict.update(
                    {
                        suggestion_key: suggestion.value,
                        suggestion_score_key: suggestion.score,
                        suggestion_agent_key: suggestion.agent,
                    }
                )

            record_dict.update({**responses_dict, **suggestions_dict})
        return record_dict
