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
import json
from pathlib import Path
from typing import List, Union

from argilla.records._resource import Record
from argilla.records._io import GenericIO


class JsonIO:
    @staticmethod
    def to_json(records: List["Record"], path: Union[Path, str]) -> Path:
        """
        Export the records to a file on disk. This is a convenient shortcut for dataset.records(...).to_disk().

        Parameters:
            path (str): The path to the file to save the records.
            orient (str): The structure of the exported dictionary.

        Returns:
            The path to the file where the records were saved.

        """
        if isinstance(path, str):
            path = Path(path)
        if path.exists():
            raise FileExistsError(f"File {path} already exists.")
        record_dicts = GenericIO.to_list(records, flatten=False)
        with open(path, "w") as f:
            json.dump(record_dicts, f)
        return path

    @staticmethod
    def _records_from_json(path: Union[Path, str]) -> List["Record"]:
        """Creates a DatasetRecords object from a disk path.

        Parameters:
            path (str): The path to the file containing the records.

        Returns:
            DatasetRecords: The DatasetRecords object created from the disk path.

        """
        with open(path, "r") as f:
            record_dicts = json.load(f)
        records = [Record.from_dict(record_dict) for record_dict in record_dicts]
        return records
