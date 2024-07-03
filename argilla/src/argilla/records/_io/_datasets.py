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

from typing import Dict, List, Union, Optional, Type, TYPE_CHECKING, Any

from argilla.records._io._generic import GenericIO

if TYPE_CHECKING:
    from argilla.records import Record


def _resolve_hf_datasets_type() -> Optional[Type["HFDataset"]]:
    """This function resolves the `datasets.Dataset` type safely in case the datasets package is not installed.

    Returns:
        Optional[Type]: The Dataset class definition in case the datasets package is installed. Otherwise, None.
    """
    try:
        from datasets import Dataset

        return Dataset
    except ImportError:
        return None


HFDataset = _resolve_hf_datasets_type()


class HFDatasetsIO:
    @staticmethod
    def _is_hf_dataset(dataset: Any) -> bool:
        """Check if the object is a Hugging Face dataset.

        Parameters:
            dataset (Dataset): The object to check.

        Returns:
            bool: True if the object is a Hugging Face dataset, False otherwise.
        """
        datasets_class = _resolve_hf_datasets_type()
        if datasets_class is None:
            return False
        return isinstance(dataset, datasets_class)

    @staticmethod
    def to_datasets(records: List["Record"]) -> "HFDataset":
        """
        Export the records to a Hugging Face dataset.

        Returns:
            The dataset containing the records.
        """
        dataset_class = _resolve_hf_datasets_type()
        if dataset_class is None:
            raise ImportError("Hugging Face datasets is not installed. Please install it using `pip install datasets`.")
        record_dicts = GenericIO.to_list(records, flatten=True)
        dataset = dataset_class.from_list(record_dicts)
        return dataset

    @staticmethod
    def _record_dicts_from_datasets(dataset: "HFDataset") -> List[Dict[str, Union[str, float, int, list]]]:
        """Creates a dictionaries from a HF dataset that can be passed to DatasetRecords.add or DatasetRecords.update.

        Parameters:
            dataset (Dataset): The dataset containing the records.

        Returns:
            Generator[Dict[str, Union[str, float, int, list]], None, None]: A generator of dictionaries to be passed to DatasetRecords.add or DatasetRecords.update.
        """
        record_dicts = []
        for example in dataset.to_iterable_dataset():
            record_dicts.append(example)
        return record_dicts
