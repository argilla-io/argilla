#  coding=utf-8
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
from typing import List, Optional

from rubrix.client.models import Record


class Dataset:
    """Dataset is a container class for Rubrix records.

    Args:
        records: A list of Rubrix records

    Raises:
        MixedRecordTypesError: When the provided list contains more than one type of record.
    """

    def __init__(self, records: Optional[List[Record]] = None):
        self._records = records or []
        self._record_type = None

        record_types = {type(rec): None for rec in self._records}

        if len(record_types) > 1:
            raise MixedRecordTypesError(
                f"A Dataset must only contain one type of record, but you provided more than one: {list(record_types.keys())}"
            )

        if record_types:
            self._record_type = next(iter(record_types))

    def __iter__(self):
        return self._records.__iter__()

    def __getitem__(self, key):
        return self._records[key]

    def __setitem__(self, key, value):
        if self._record_type and type(value) is not self._record_type:
            raise WrongRecordTypeError(
                f"You are only allowed to set a record of type {self._record_type} in this dataset, but you provided {type(value)}"
            )
        self._records[key] = value

    def __len__(self) -> int:
        return len(self._records)

    def append(self, record: Record):
        """Appends a record to the dataset

        Args:
            record: The record to be added to the dataset
        """
        if self._record_type and type(record) is not self._record_type:
            raise WrongRecordTypeError(
                f"You are only allowed to append a record of type {self._record_type} to this dataset, but you provided {type(record)}"
            )
        self._record_type = type(record)

        self._records.append(record)


class DatasetError(Exception):
    pass


class MixedRecordTypesError(DatasetError):
    pass


class WrongRecordTypeError(DatasetError):
    pass
