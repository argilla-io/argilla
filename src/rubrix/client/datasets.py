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
from typing import Dict, List, Optional, Tuple, Type, Union

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


class DatasetBase:
    """The Dataset classes are containers for Rubrix records.

    This is the base class to facilitate the implementation for each record type.

    Args:
        record_type: Type of the records.
        records: A list of Rubrix records.

    Raises:
        WrongRecordTypeError: When the record type in the provided
            list does not correspond to the dataset type.
    """

    def __init__(
        self, record_type: Type[Record], records: Optional[List[Record]] = None
    ):
        self._record_type = record_type
        self._records = records or []
        if self._records:
            self._validate_record_type()

    def _validate_record_type(self):
        """Validates the record type.

        Raises:
            WrongRecordTypeError: When the record type in the provided
                list does not correspond to the dataset type.
        """
        record_types = {type(rec): None for rec in self._records}
        if len(record_types) > 1:
            raise WrongRecordTypeError(
                f"A {type(self).__name__} must only contain {self._record_type.__name__}s, "
                f"but you provided various types: {[rt.__name__ for rt in record_types.keys()]}"
            )
        elif next(iter(record_types)) is not self._record_type:
            raise WrongRecordTypeError(
                f"A {type(self).__name__} must only contain {self._record_type.__name__}s, "
                f"but you provided {list(record_types.keys())[0].__name__}s."
            )

    def __iter__(self):
        return self._records.__iter__()

    def __getitem__(self, key):
        return self._records[key]

    def __setitem__(self, key, value):
        if type(value) is not self._record_type:
            raise WrongRecordTypeError(
                f"You are only allowed to set a record of type {self._record_type} in this dataset, but you provided {type(value)}"
            )
        self._records[key] = value

    def __delitem__(self, key):
        del self._records[key]

    def __len__(self) -> int:
        return len(self._records)

    def append(self, record: Record):
        """Appends a record to the dataset.

        Args:
            record: The record to be added to the dataset.

        Raises:
            WrongRecordTypeError: When the type of the record does not correspond to the dataset type.
        """
        if type(record) is not self._record_type:
            raise WrongRecordTypeError(
                f"You are only allowed to append a record of type {self._record_type} to this dataset, but you provided {type(record)}"
            )
        self._records.append(record)

    def to_datasets(self) -> "datasets.Dataset":
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
            raise ModuleNotFoundError(
                "Version >1.17.0 of 'datasets' must be installed to use `to_datasets`! "
                "You can update 'datasets' with the command: `pip install -U datasets>1.17.0`"
            )

        ds_dict = self._to_datasets_dict()

        return self._dict_to_datasets(ds_dict)

    def _to_datasets_dict(self) -> Dict:
        """Helper method to transform a Rubrix dataset into a dict that is compatible with `datasets.Dataset`"""
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

    @classmethod
    def from_datasets(cls, dataset: "datasets.Dataset") -> "Dataset":
        """Imports records from a `datasets.Dataset`.

        Args:
            dataset: A datasets Dataset from which to import the records.

        Returns:
            The imported records in a Rubrix Dataset.
        """
        raise NotImplementedError

    def to_pandas(self) -> pd.DataFrame:
        """Exports your records to a `pandas.DataFrame`.

        Returns:
            A `datasets.Dataset` containing your records.
        """
        return pd.DataFrame(map(dict, self._records))

    @classmethod
    def from_pandas(cls, dataframe: pd.DataFrame) -> "Dataset":
        """Imports records from a `pandas.DataFrame`.

        Args:
            dataframe: A pandas DataFrame from which to import the records.

        Returns:
            The imported records in a Rubrix Dataset.
        """
        raise NotImplementedError


def _prepend_docstring(record_type: Type[Record]):
    docstring = f"""This Dataset contains {record_type.__name__} records.

    It allows you to export/import records into/from different formats,
    append further records, loop over the records, and access them by index.

    Args:
        records: A list of `{record_type.__name__}`s.

    Raises:
        WrongRecordTypeError: When the record type in the provided
            list does not correspond to the dataset type.
    """

    def docstring_decorator(fn):
        fn.__doc__ = docstring + (fn.__doc__ or "")
        return fn

    return docstring_decorator


@_prepend_docstring(TextClassificationRecord)
class DatasetForTextClassification(DatasetBase):
    """
    Examples:
        Import/export records:
        >>> dataset = {record_type.__name__}.from_pandas(my_dataframe)
        >>> dataset.to_datasets()  # returns a datasets.Dataset

        Looping over the dataset:
        >>> assert len(dataset) == 2
        >>> for record in dataset:
        ...     print(record)

        Passing in a list of records:
        >>> import rubrix as rb
        >>> records = [
        ...     rb.TextClassificationRecord(inputs="example"),
        ...     rb.TextClassificationRecord(inputs="another example"),
        ... ]
        >>> dataset = rb.DatasetForTextClassification(records)

        Appending records to the dataset:
        >>> for text in ["example", "another example"]:
        ...     dataset.append(rb.TextClassificationRecord(inputs=text))

        Indexing into the dataset:
        >>> dataset[0]
        ... rb.TextClassificationRecord(inputs={"text": "example"})
        >>> dataset[0] = rb.TextClassificationRecord(inputs="replaced example")
    """

    def __init__(self, records: Optional[List[TextClassificationRecord]] = None):
        # we implement this to have more specific type hints
        super().__init__(record_type=TextClassificationRecord, records=records)

    def append(self, record: TextClassificationRecord):
        # we implement this to have more specific type hints
        super().append(record)

    def _to_datasets_dict(self) -> Dict:
        # create a dict first, where we make the necessary transformations
        ds_dict = {}
        for key in self._record_type.__fields__:
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

        return ds_dict

    @classmethod
    def from_datasets(
        cls, dataset: "datasets.Dataset"
    ) -> "DatasetForTextClassification":
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

    @classmethod
    def from_pandas(cls, dataframe: pd.DataFrame) -> "DatasetForTextClassification":
        return cls(
            [TextClassificationRecord(**row) for row in dataframe.to_dict("records")]
        )


@_prepend_docstring(TokenClassificationRecord)
class DatasetForTokenClassification(DatasetBase):
    """
    Examples:
        Import/export records:
        >>> dataset = DatasetForTokenClassification.from_pandas(my_dataframe)
        >>> dataset.to_datasets()  # returns a datasets.Dataset

        Looping over the dataset:
        >>> assert len(dataset) == 2
        >>> for record in dataset:
        ...     print(record)

        Passing in a list of records:
        >>> import rubrix as rb
        >>> records = [
        ...     rb.TokenClassificationRecord(text="example", tokens=["example"]),
        ...     rb.TokenClassificationRecord(text="another example", tokens=["another", "example"]),
        ... ]
        >>> dataset = rb.DatasetForTokenClassification(records)

        Appending records to the dataset:
        >>> for text in ["example", "another example"]:
        ...     dataset.append(rb.TokenClassificationRecord(text=text, tokens=text.split()))

        Indexing into the dataset:
        >>> dataset[0]
        ... rb.TokenClassificationRecord(text="example", tokens=["example"])
        >>> dataset[0] = rb.TokenClassificationRecord(text="replace example", tokens=["replace", "example"])
    """

    def __init__(self, records: Optional[List[TokenClassificationRecord]] = None):
        # we implement this to have more specific type hints
        super().__init__(record_type=TokenClassificationRecord, records=records)

    def append(self, record: TokenClassificationRecord):
        # we implement this to have more specific type hints
        super().append(record)

    def _to_datasets_dict(self) -> Dict:
        """Helper method to put token classification records in a `datasets.Dataset`"""
        # create a dict first, where we make the necessary transformations
        def entities_to_dict(annotation_or_prediction: str):
            return [
                [
                    {"label": ent[0], "start": ent[1], "end": ent[2]}
                    for ent in getattr(rec, annotation_or_prediction)
                ]
                if getattr(rec, annotation_or_prediction) is not None
                else None
                for rec in self._records
            ]

        ds_dict = {}
        for key in self._record_type.__fields__:
            if key == "prediction":
                ds_dict[key] = entities_to_dict(key)
            elif key == "annotation":
                ds_dict[key] = entities_to_dict(key)
            elif key == "id":
                ds_dict[key] = [str(rec.id) for rec in self._records]
            else:
                ds_dict[key] = [getattr(rec, key) for rec in self._records]

        return ds_dict

    @classmethod
    def from_datasets(
        cls, dataset: "datasets.Dataset"
    ) -> "DatasetForTokenClassification":
        def entities_to_tuple(entities):
            return [(ent["label"], ent["start"], ent["end"]) for ent in entities]

        records = []
        for row in dataset:
            if row["prediction"] is not None:
                row["prediction"] = entities_to_tuple(row["prediction"])
            if row["annotation"] is not None:
                row["annotation"] = entities_to_tuple(row["annotation"])
            records.append(TokenClassificationRecord(**row))

        return cls(records)

    @classmethod
    def from_pandas(cls, dataframe: pd.DataFrame) -> "DatasetForTextClassification":
        return cls(
            [TokenClassificationRecord(**row) for row in dataframe.to_dict("records")]
        )


@_prepend_docstring(Text2TextRecord)
class DatasetForText2Text(DatasetBase):
    """
    Examples:
        Import/export records:
        >>> dataset = DatasetForText2Text.from_pandas(my_dataframe)
        >>> dataset.to_datasets()  # returns a datasets.Dataset

        Looping over the dataset:
        >>> assert len(dataset) == 2
        >>> for record in dataset:
        ...     print(record)

        Passing in a list of records:
        >>> import rubrix as rb
        >>> records = [
        ...     rb.Text2TextRecord(text="example"),
        ...     rb.Text2TextRecord(text="another example"),
        ... ]
        >>> dataset = rb.DatasetForText2Text(records)

        Appending records to the dataset:
        >>> for text in ["example", "another example"]:
        ...     dataset.append(rb.Text2TextRecord(text=text))

        Indexing into the dataset:
        >>> dataset[0]
        ... rb.Text2TextRecord(text="example"})
        >>> dataset[0] = rb.Text2TextRecord(text="replaced example")
    """

    def __init__(self, records: Optional[List[Text2TextRecord]] = None):
        # we implement this to have more specific type hints
        super().__init__(record_type=Text2TextRecord, records=records)

    def append(self, record: Text2TextRecord):
        # we implement this to have more specific type hints
        super().append(record)

    def _to_datasets_dict(self) -> Dict:
        # create a dict first, where we make the necessary transformations
        def pred_to_dict(pred: Union[str, Tuple[str, float]]):
            if isinstance(pred, str):
                return {"text": pred, "score": None}
            return {"text": pred[0], "score": pred[1]}

        ds_dict = {}
        for key in self._record_type.__fields__:
            if key == "prediction":
                ds_dict[key] = [
                    [pred_to_dict(pred) for pred in rec.prediction]
                    if rec.prediction is not None
                    else None
                    for rec in self._records
                ]
            elif key == "id":
                ds_dict[key] = [str(rec.id) for rec in self._records]
            else:
                ds_dict[key] = [getattr(rec, key) for rec in self._records]

        return ds_dict

    @classmethod
    def from_datasets(cls, dataset: "datasets.Dataset") -> "DatasetForText2Text":
        records = []
        for row in dataset:
            if row["prediction"] is not None:
                row["prediction"] = [
                    pred["text"]
                    if pred["score"] is None
                    else (pred["text"], pred["score"])
                    for pred in row["prediction"]
                ]
            records.append(Text2TextRecord(**row))

        return cls(records)

    @classmethod
    def from_pandas(cls, dataframe: pd.DataFrame) -> "DatasetForText2Text":
        return cls([Text2TextRecord(**row) for row in dataframe.to_dict("records")])


Dataset = Union[
    DatasetForTextClassification, DatasetForTokenClassification, DatasetForText2Text
]


def read_datasets(dataset: "datasets.Dataset", task: Union[str, TaskType]) -> Dataset:
    """Reads a datasets Dataset and returns a Rubrix Dataset

    Args:
        dataset: Dataset to be read in.
        task: Task for the dataset, one of: ["TextClassification", "TokenClassification", "Text2Text"]

    Returns:
        A Rubrix dataset for the given task.
    """
    if isinstance(task, str):
        task = TaskType(task)

    if task is TaskType.text_classification:
        return DatasetForTextClassification.from_datasets(dataset)
    if task is TaskType.token_classification:
        return DatasetForTokenClassification.from_datasets(dataset)
    if task is TaskType.text2text:
        return DatasetForText2Text.from_datasets(dataset)
    raise NotImplementedError(
        "Reading a datasets Dataset is not implemented for the given task!"
    )


def read_pandas(dataframe: pd.DataFrame, task: Union[str, TaskType]) -> Dataset:
    """Reads a pandas DataFrame and returns a Rubrix Dataset

    Args:
        dataframe: Dataframe to be read in.
        task: Task for the dataset, one of: ["TextClassification", "TokenClassification", "Text2Text"]

    Returns:
        A Rubrix dataset for the given task.
    """
    if isinstance(task, str):
        task = TaskType(task)

    if task is TaskType.text_classification:
        return DatasetForTextClassification.from_pandas(dataframe)
    if task is TaskType.token_classification:
        return DatasetForTokenClassification.from_pandas(dataframe)
    if task is TaskType.text2text:
        return DatasetForText2Text.from_pandas(dataframe)
    raise NotImplementedError(
        "Reading a pandas DataFrame is not implemented for the given task!"
    )


class WrongRecordTypeError(Exception):
    pass
