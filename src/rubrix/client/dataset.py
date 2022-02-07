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
import logging
from typing import Dict, List, Optional, Union

import pandas as pd
from pkg_resources import parse_version

from rubrix.client.models import (
    Record,
    Text2TextRecord,
    TextClassificationRecord,
    TokenAttributions,
    TokenClassificationRecord,
)
from rubrix.client.sdk.datasets.models import TaskType

_LOGGER = logging.getLogger(__name__)


class Dataset:
    """Dataset is a container class for Rubrix records.

    Args:
        records: A list of Rubrix records

    Raises:
        MixedRecordTypesError: When the provided list contains more than one type of record.

    Examples:
        Pass in a list of records:
        >>> import rubrix as rb
        >>> records = [
        ...     rb.TextClassificationRecord(inputs="example"),
        ...     rb.TextClassificationRecord(inputs="another example"),
        ... ]
        >>> dataset = rb.Dataset(records)

        Append records to an empty dataset:
        >>> import rubrix as rb
        >>> dataset = Dataset()
        >>> for text in ["example", "another example"]:
        ...     datasets.append(rb.TextClassificationRecord(inputs=text))

        Index into the dataset:
        >>> dataset[0]
        ... rb.TextClassificationRecord(inputs={"text": "example"})
        >>> dataset[0] = rb.TextClassificationRecord(inputs="replaced example")

        Loop over the dataset:
        >>> assert len(dataset) == 2
        >>> for record in dataset:
        ...     print(record)
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

    def to_datasets(self) -> Optional["datasets.Dataset"]:
        """Exports your records to a `datasets.Dataset`.

        Returns:
            A `datasets.Dataset` containing your records.
        """
        try:
            import datasets
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "'datasets' must be installed to use `to_datasets`! "
                "You can install 'datasets' with the command: `pip install datasets>1.17.0`"
            )
        if not (parse_version(datasets.__version__) > parse_version("1.17.0")):
            raise ImportError(
                "Version >1.17.0 of 'datasets' must be installed to use `to_datasets`! "
                "You can update 'datasets' with the command: `pip install -U datasets>1.17.0`"
            )

        if self._record_type is TextClassificationRecord:
            return self._textclassification_to_datasets()
        if self._record_type is TokenClassificationRecord:
            return self._tokenclassification_to_datasets()
        if self._record_type is Text2TextRecord:
            return self._text2text_to_datasets()

    @classmethod
    def from_datasets(
        cls,
        dataset: "datasets.Dataset",
        task: Union[str, TaskType] = "TextClassification",
    ) -> "Dataset":
        """Imports records from a `datasets.Dataset`.

        Args:
            dataset: A datasets Dataset from which to import the records.
            task: The task defines the record type.

        Returns:
            The imported records in a Rubrix Dataset.
        """
        if isinstance(task, str):
            task = TaskType(task)

        if task is TaskType.text_classification:
            return cls._datasets_to_textclassification(dataset)
        if task is TaskType.token_classification:
            raise NotImplementedError(f"{task} is still not implemented.")
        if task is TaskType.text2text:
            raise NotImplementedError(f"{task} is still not implemented.")
        raise ValueError(f"Provided task {task} is not supported!")

    def _textclassification_to_datasets(self) -> "datasets.Dataset":
        """Helper method to put text classification records in a `datasets.Dataset`"""
        # create a dict first, where we make the necessary transformations
        ds_dict = {}
        for key in self._records[0].__fields__:
            if key == "prediction":
                ds_dict[key] = [
                    [{"label": pred[0], "score": pred[1]} for pred in rec.prediction]
                    if rec.prediction is not None
                    else None
                    for rec in self._records
                ]
            elif key == "explanation":
                ds_dict[key] = [
                    {
                        key: list(map(dict, tokattrs))
                        for key, tokattrs in rec.explanation.items()
                    }
                    if rec.explanation is not None
                    else None
                    for rec in self._records
                ]
            elif key == "id":
                ds_dict[key] = [str(rec.id) for rec in self._records]
            else:
                ds_dict[key] = [getattr(rec, key) for rec in self._records]

        return self._dict_to_datasets(ds_dict)

    @classmethod
    def _datasets_to_textclassification(
        cls,
        dataset: "datasets.Dataset",
    ) -> "Dataset":
        """Helper method to import text classification records from a `datasets.Dataset`.

        Args:
            dataset: A datasets Dataset

        Returns:
            A Dataset.
        """
        records = []
        for row in dataset:
            row["inputs"] = {
                key: val for key, val in row["inputs"].items() if val is not None
            }
            row["prediction"] = (
                [
                    (
                        pred["label"],
                        pred["score"],
                    )
                    for pred in row["prediction"]
                ]
                if row["prediction"] is not None
                else None
            )
            row["explanation"] = (
                {
                    key: [TokenAttributions(**tokattr_kwargs) for tokattr_kwargs in val]
                    for key, val in row["explanation"].items()
                }
                if row["explanation"] is not None
                else None
            )

            records.append(TextClassificationRecord(**row))

        return cls(records)

    def _tokenclassification_to_datasets(self):
        raise NotImplementedError

    def _text2text_to_datasets(self):
        raise NotImplementedError

    def _dict_to_datasets(self, records_dict: Dict) -> "datasets.Dataset":
        """Helper method to create a datasets Dataset from a dict, removing the 'metadata' key from the dict if necessary.

        Args:
            records_dict: A dict containing dataset records.

        Returns:
            A datasets Dataset object, without the metadata, if it is incompatible with the Dataset format.
        """
        from datasets import Dataset

        try:
            dataset = Dataset.from_dict(records_dict)
        # try without metadata
        except Exception:
            del records_dict["metadata"]
            dataset = Dataset.from_dict(records_dict)
            _LOGGER.warning(
                "The 'metadata' of the records were removed, since it was incompatible with the 'datasets' format."
            )

        return dataset

    def to_pandas(self) -> pd.DataFrame:
        """Exports your records to a `pandas.DataFrame`.

        Returns:
            A `datasets.Dataset` containing your records.
        """
        return pd.DataFrame(map(dict, self._records))

    def from_pandas(
        cls, dataframe: pd.DataFrame, task: Union[str, TaskType] = "TextClassification"
    ) -> "Dataset":
        if isinstance(task, str):
            task = TaskType(task)

        if task is TaskType.text_classification:
            return cls(
                [TextClassificationRecord(**row) for row in dataframe.itertuples()]
            )
        if task is TaskType.token_classification:
            raise NotImplementedError(f"{task} is still not implemented.")
        if task is TaskType.text2text:
            raise NotImplementedError(f"{task} is still not implemented.")

        raise ValueError(f"Provided task {task} is not supported!")


class DatasetError(Exception):
    pass


class MixedRecordTypesError(DatasetError):
    pass


class WrongRecordTypeError(DatasetError):
    pass
