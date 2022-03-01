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
import functools
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


def _requires_datasets(func):
    @functools.wraps(func)
    def check_if_datasets_installed(*args, **kwargs):
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
        return func(*args, **kwargs)

    return check_if_datasets_installed


class DatasetBase:
    """The Dataset classes are containers for Rubrix records.

    This is the base class to facilitate the implementation for each record type.

    Args:
        records: A list of Rubrix records.

    Raises:
        WrongRecordTypeError: When the record type in the provided
            list does not correspond to the dataset type.
    """

    _RECORD_TYPE = None

    def __init__(self, records: Optional[List[Record]] = None):
        if self._RECORD_TYPE is None:
            raise NotImplementedError(
                "A Dataset implementation has to define a `_RECORD_TYPE`!"
            )

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
                f"A {type(self).__name__} must only contain {self._RECORD_TYPE.__name__}s, "
                f"but you provided various types: {[rt.__name__ for rt in record_types.keys()]}"
            )
        elif next(iter(record_types)) is not self._RECORD_TYPE:
            raise WrongRecordTypeError(
                f"A {type(self).__name__} must only contain {self._RECORD_TYPE.__name__}s, "
                f"but you provided {list(record_types.keys())[0].__name__}s."
            )

    def __iter__(self):
        return self._records.__iter__()

    def __getitem__(self, key):
        return self._records[key]

    def __setitem__(self, key, value):
        if type(value) is not self._RECORD_TYPE:
            raise WrongRecordTypeError(
                f"You are only allowed to set a record of type {self._RECORD_TYPE} in this dataset, but you provided {type(value)}"
            )
        self._records[key] = value

    def __delitem__(self, key):
        del self._records[key]

    def __len__(self) -> int:
        return len(self._records)

    @_requires_datasets
    def to_datasets(self) -> "datasets.Dataset":
        """Exports your records to a `datasets.Dataset`.

        Returns:
            A `datasets.Dataset` containing your records.
        """
        import datasets

        ds_dict = self._to_datasets_dict()

        try:
            dataset = datasets.Dataset.from_dict(ds_dict)
        # try without metadata, since it is more prone to incompatible structures
        except Exception:
            del ds_dict["metadata"]
            dataset = datasets.Dataset.from_dict(ds_dict)
            _LOGGER.warning(
                "The 'metadata' of the records were removed, since it was incompatible with the 'datasets' format."
            )

        return dataset

    def _to_datasets_dict(self) -> Dict:
        """Helper method to transform a Rubrix dataset into a dict that is compatible with `datasets.Dataset`"""
        raise NotImplementedError

    @classmethod
    def from_datasets(cls, dataset: "datasets.Dataset") -> "Dataset":
        """Imports records from a `datasets.Dataset`.

        Columns that are not supported are ignored.

        Args:
            dataset: A datasets Dataset from which to import the records.

        Returns:
            The imported records in a Rubrix Dataset.
        """

        not_supported_columns = [
            col
            for col in dataset.column_names
            if col not in cls._RECORD_TYPE.__fields__
        ]
        if not_supported_columns:
            _LOGGER.warning(
                f"Following columns are not supported by the {cls._RECORD_TYPE.__name__} model and are ignored: {not_supported_columns}"
            )
            dataset = dataset.remove_columns(not_supported_columns)

        return cls._from_datasets(dataset)

    @classmethod
    def _from_datasets(cls, dataset: "datasets.Dataset") -> "Dataset":
        """Helper method to create a Rubrix Dataset from a datasets Dataset.

        Must be implemented by the child class.

        Args:
            dataset: A datasets Dataset

        Returns:
            A Rubrix Dataset
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

        Columns that are not supported are ignored.

        Args:
            dataframe: A pandas DataFrame from which to import the records.

        Returns:
            The imported records in a Rubrix Dataset.
        """
        not_supported_columns = [
            col for col in dataframe.columns if col not in cls._RECORD_TYPE.__fields__
        ]
        if not_supported_columns:
            _LOGGER.warning(
                f"Following columns are not supported by the {cls._RECORD_TYPE.__name__} model and are ignored: {not_supported_columns}"
            )
            dataframe = dataframe.drop(columns=not_supported_columns)

        return cls._from_pandas(dataframe)

    @classmethod
    def _from_pandas(cls, dataframe: pd.DataFrame) -> "Dataset":
        """Helper method to create a Rubrix Dataset from a pandas DataFrame.

        Must be implemented by the child class.

        Args:
            dataframe: A pandas DataFrame

        Returns:
            A Rubrix Dataset
        """
        raise NotImplementedError

    @_requires_datasets
    def prepare_for_training(self, **kwargs) -> "datasets.Dataset":
        """Prepares the dataset for training.

        Args:
            **kwargs: Specific to the task of the dataset.

        Returns:
            A datasets Dataset.
        """
        raise NotImplementedError


def _prepend_docstring(record_type: Type[Record]):
    docstring = f"""This Dataset contains {record_type.__name__} records.

    It allows you to export/import records into/from different formats,
    loop over the records, and access them by index.

    Args:
        records: A list of `{record_type.__name__}`s.

    Raises:
        WrongRecordTypeError: When the record type in the provided
            list does not correspond to the dataset type.
    """

    def docstring_decorator(cls):
        cls.__doc__ = docstring + (cls.__doc__ or "")
        return cls

    return docstring_decorator


@_prepend_docstring(TextClassificationRecord)
class DatasetForTextClassification(DatasetBase):
    """
    Examples:
        >>> # Import/export records:
        >>> import rubrix as rb
        >>> dataset = rb.DatasetForTextClassification.from_pandas(my_dataframe)
        >>> dataset.to_datasets()
        >>>
        >>> # Looping over the dataset:
        >>> for record in dataset:
        ...     print(record)
        >>>
        >>> # Passing in a list of records:
        >>> records = [
        ...     rb.TextClassificationRecord(inputs="example"),
        ...     rb.TextClassificationRecord(inputs="another example"),
        ... ]
        >>> dataset = rb.DatasetForTextClassification(records)
        >>> assert len(dataset) == 2
        >>>
        >>> # Indexing into the dataset:
        >>> dataset[0]
        ... rb.TextClassificationRecord(inputs={"text": "example"})
        >>> dataset[0] = rb.TextClassificationRecord(inputs="replaced example")
    """

    _RECORD_TYPE = TextClassificationRecord

    def __init__(self, records: Optional[List[TextClassificationRecord]] = None):
        # we implement this to have more specific type hints
        super().__init__(records=records)

    @classmethod
    def from_datasets(
        # we implement this to have more specific type hints
        cls,
        dataset: "datasets.Dataset",
    ) -> "DatasetForTextClassification":
        """Imports records from a `datasets.Dataset`.

        Columns that are not supported are ignored.

        Args:
            dataset: A datasets Dataset from which to import the records.

        Returns:
            The imported records in a Rubrix Dataset.

        Examples:
            >>> import datasets
            >>> ds = datasets.Dataset.from_dict({
            ...     "inputs": ["example"],
            ...     "prediction": [
            ...         [{"label": "LABEL1", "score": 0.9}, {"label": "LABEL2", "score": 0.1}]
            ...     ]
            ... })
            >>> DatasetForTextClassification.from_datasets(ds)
        """
        return super().from_datasets(dataset)

    @classmethod
    def from_pandas(
        # we implement this to have more specific type hints
        cls,
        dataframe: pd.DataFrame,
    ) -> "DatasetForTextClassification":
        return super().from_pandas(dataframe)

    def _to_datasets_dict(self) -> Dict:
        # create a dict first, where we make the necessary transformations
        ds_dict = {}
        for key in self._RECORD_TYPE.__fields__:
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
                ds_dict[key] = [
                    None if rec.id is None else str(rec.id) for rec in self._records
                ]
            elif key == "metadata":
                ds_dict[key] = [getattr(rec, key) or None for rec in self._records]
            else:
                ds_dict[key] = [getattr(rec, key) for rec in self._records]

        return ds_dict

    @classmethod
    def _from_datasets(
        cls, dataset: "datasets.Dataset"
    ) -> "DatasetForTextClassification":
        records = []
        for row in dataset:
            if row.get("inputs") and isinstance(row["inputs"], dict):
                row["inputs"] = {
                    key: val for key, val in row["inputs"].items() if val is not None
                }
            if row.get("prediction"):
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
            if row.get("explanation"):
                row["explanation"] = (
                    {
                        key: [
                            TokenAttributions(**tokattr_kwargs)
                            for tokattr_kwargs in val
                        ]
                        for key, val in row["explanation"].items()
                    }
                    if row["explanation"] is not None
                    else None
                )

            records.append(TextClassificationRecord(**row))

        return cls(records)

    @classmethod
    def _from_pandas(cls, dataframe: pd.DataFrame) -> "DatasetForTextClassification":
        return cls(
            [TextClassificationRecord(**row) for row in dataframe.to_dict("records")]
        )

    @_requires_datasets
    def prepare_for_training(self) -> "datasets.Dataset":
        """Prepares the dataset for training.

        This will return a ``datasets.Dataset`` with a *label* column,
        and one column for each key in the *inputs* dictionary of the records:
            - Records without an annotation are removed.
            - The *label* column corresponds to the annotations of the records.
            - Labels are transformed to integers.

        Returns:
            A datasets Dataset with a *label* column and several *inputs* columns.

        Examples:
            >>> import rubrix as rb
            >>> rb_dataset = rb.DatasetForTextClassification([
            ...     rb.TextClassificationRecord(
            ...         inputs={"header": "my header", "content": "my content"},
            ...         annotation="SPAM",
            ...     )
            ... ])
            >>> rb_dataset.prepare_for_training().features
            {'header': Value(dtype='string'),
             'content': Value(dtype='string'),
             'label': ClassLabel(num_classes=1, names=['SPAM'])}

        """
        import datasets

        inputs_keys = {
            key: None
            for rec in self._records
            for key in rec.inputs
            if rec.annotation is not None
        }.keys()
        ds_dict = {**{key: [] for key in inputs_keys}, "label": []}
        for rec in self._records:
            if rec.annotation is None:
                continue
            for key in inputs_keys:
                ds_dict[key].append(rec.inputs.get(key))
            ds_dict["label"].append(rec.annotation)

        if self._records[0].multi_label:
            labels = {label: None for labels in ds_dict["label"] for label in labels}
        else:
            labels = {label: None for label in ds_dict["label"]}

        class_label = datasets.ClassLabel(names=sorted(labels.keys()))
        feature_dict = {
            **{key: datasets.Value("string") for key in inputs_keys},
            "label": [class_label] if self._records[0].multi_label else class_label,
        }

        return datasets.Dataset.from_dict(
            ds_dict, features=datasets.Features(feature_dict)
        )


@_prepend_docstring(TokenClassificationRecord)
class DatasetForTokenClassification(DatasetBase):
    """
    Examples:
        >>> # Import/export records:
        >>> import rubrix as rb
        >>> dataset = rb.DatasetForTokenClassification.from_pandas(my_dataframe)
        >>> dataset.to_datasets()
        >>>
        >>> # Looping over the dataset:
        >>> assert len(dataset) == 2
        >>> for record in dataset:
        ...     print(record)
        >>>
        >>> # Passing in a list of records:
        >>> import rubrix as rb
        >>> records = [
        ...     rb.TokenClassificationRecord(text="example", tokens=["example"]),
        ...     rb.TokenClassificationRecord(text="another example", tokens=["another", "example"]),
        ... ]
        >>> dataset = rb.DatasetForTokenClassification(records)
        >>>
        >>> # Indexing into the dataset:
        >>> dataset[0]
        ... rb.TokenClassificationRecord(text="example", tokens=["example"])
        >>> dataset[0] = rb.TokenClassificationRecord(text="replace example", tokens=["replace", "example"])
    """

    _RECORD_TYPE = TokenClassificationRecord

    def __init__(self, records: Optional[List[TokenClassificationRecord]] = None):
        # we implement this to have more specific type hints
        super().__init__(records=records)

    @classmethod
    def from_datasets(
        cls, dataset: "datasets.Dataset"
    ) -> "DatasetForTokenClassification":
        """Imports records from a `datasets.Dataset`.

        Columns that are not supported are ignored.

        Args:
            dataset: A datasets Dataset from which to import the records.

        Returns:
            The imported records in a Rubrix Dataset.

        Examples:
            >>> import datasets
            >>> ds = datasets.Dataset.from_dict({
            ...     "text": ["my example"],
            ...     "tokens": [["my", "example"]],
            ...     "prediction": [
            ...         [{"label": "LABEL1", "start": 3, "end": 10, "score": 1.0}]
            ...     ]
            ... })
            >>> DatasetForTokenClassification.from_datasets(ds)
        """
        # we implement this to have more specific type hints
        return super().from_datasets(dataset)

    @classmethod
    def from_pandas(
        # we implement this to have more specific type hints
        cls,
        dataframe: pd.DataFrame,
    ) -> "DatasetForTokenClassification":
        return super().from_pandas(dataframe)

    def _to_datasets_dict(self) -> Dict:
        """Helper method to put token classification records in a `datasets.Dataset`"""
        # create a dict first, where we make the necessary transformations
        def entities_to_dict(
            entities: Optional[
                List[Union[Tuple[str, int, int, float], Tuple[str, int, int]]]
            ]
        ) -> Optional[List[Dict[str, Union[str, int, float]]]]:
            if entities is None:
                return None
            return [
                {"label": ent[0], "start": ent[1], "end": ent[2]}
                if len(ent) == 3
                else {"label": ent[0], "start": ent[1], "end": ent[2], "score": ent[3]}
                for ent in entities
            ]

        ds_dict = {}
        for key in self._RECORD_TYPE.__fields__:
            if key == "prediction":
                ds_dict[key] = [
                    entities_to_dict(rec.prediction) for rec in self._records
                ]
            elif key == "annotation":
                ds_dict[key] = [
                    entities_to_dict(rec.annotation) for rec in self._records
                ]
            elif key == "id":
                ds_dict[key] = [
                    None if rec.id is None else str(rec.id) for rec in self._records
                ]
            elif key == "metadata":
                ds_dict[key] = [getattr(rec, key) or None for rec in self._records]
            else:
                ds_dict[key] = [getattr(rec, key) for rec in self._records]

        return ds_dict

    @classmethod
    def _from_datasets(
        cls, dataset: "datasets.Dataset"
    ) -> "DatasetForTokenClassification":
        def entities_to_tuple(entities):
            return [
                (ent["label"], ent["start"], ent["end"])
                if len(ent) == 3
                else (ent["label"], ent["start"], ent["end"], ent["score"] or 1.0)
                for ent in entities
            ]

        records = []
        for row in dataset:
            if row.get("prediction"):
                row["prediction"] = entities_to_tuple(row["prediction"])
            if row.get("annotation"):
                row["annotation"] = entities_to_tuple(row["annotation"])

            records.append(TokenClassificationRecord(**row))

        return cls(records)

    @classmethod
    def _from_pandas(cls, dataframe: pd.DataFrame) -> "DatasetForTextClassification":
        return cls(
            [TokenClassificationRecord(**row) for row in dataframe.to_dict("records")]
        )


@_prepend_docstring(Text2TextRecord)
class DatasetForText2Text(DatasetBase):
    """
    Examples:
        >>> # Import/export records:
        >>> import rubrix as rb
        >>> dataset = rb.DatasetForText2Text.from_pandas(my_dataframe)
        >>> dataset.to_datasets()
        >>>
        >>> # Passing in a list of records:
        >>> records = [
        ...     rb.Text2TextRecord(text="example"),
        ...     rb.Text2TextRecord(text="another example"),
        ... ]
        >>> dataset = rb.DatasetForText2Text(records)
        >>> assert len(dataset) == 2
        >>>
        >>> # Looping over the dataset:
        >>> for record in dataset:
        ...     print(record)
        >>>
        >>> # Indexing into the dataset:
        >>> dataset[0]
        ... rb.Text2TextRecord(text="example"})
        >>> dataset[0] = rb.Text2TextRecord(text="replaced example")
    """

    _RECORD_TYPE = Text2TextRecord

    def __init__(self, records: Optional[List[Text2TextRecord]] = None):
        # we implement this to have more specific type hints
        super().__init__(records=records)

    @classmethod
    def from_datasets(cls, dataset: "datasets.Dataset") -> "DatasetForText2Text":
        """Imports records from a `datasets.Dataset`.

        Columns that are not supported are ignored.

        Args:
            dataset: A datasets Dataset from which to import the records.

        Returns:
            The imported records in a Rubrix Dataset.

        Examples:
            >>> import datasets
            >>> ds = datasets.Dataset.from_dict({
            ...     "text": ["my example"],
            ...     "prediction": [["mi ejemplo", "ejemplo mio"]]
            ... })
            >>> # or
            >>> ds = datasets.Dataset.from_dict({
            ...     "text": ["my example"],
            ...     "prediction": [[{"text": "mi ejemplo", "score": 0.9}]]
            ... })
            >>> DatasetForText2Text.from_datasets(ds)
        """
        # we implement this to have more specific type hints
        return super().from_datasets(dataset)

    @classmethod
    def from_pandas(
        # we implement this to have more specific type hints
        cls,
        dataframe: pd.DataFrame,
    ) -> "DatasetForText2Text":
        return super().from_pandas(dataframe)

    def _to_datasets_dict(self) -> Dict:
        # create a dict first, where we make the necessary transformations
        def pred_to_dict(pred: Union[str, Tuple[str, float]]):
            if isinstance(pred, str):
                return {"text": pred, "score": None}
            return {"text": pred[0], "score": pred[1]}

        ds_dict = {}
        for key in self._RECORD_TYPE.__fields__:
            if key == "prediction":
                ds_dict[key] = [
                    [pred_to_dict(pred) for pred in rec.prediction]
                    if rec.prediction is not None
                    else None
                    for rec in self._records
                ]
            elif key == "id":
                ds_dict[key] = [
                    None if rec.id is None else str(rec.id) for rec in self._records
                ]
            elif key == "metadata":
                ds_dict[key] = [getattr(rec, key) or None for rec in self._records]
            else:
                ds_dict[key] = [getattr(rec, key) for rec in self._records]

        return ds_dict

    @classmethod
    def _from_datasets(cls, dataset: "datasets.Dataset") -> "DatasetForText2Text":
        def extract_prediction(prediction: Union[str, Dict]):
            if isinstance(prediction, str):
                return prediction
            if prediction["score"] is None:
                return prediction["text"]
            return prediction["text"], prediction["score"]

        records = []
        for row in dataset:
            if row.get("prediction"):
                row["prediction"] = [
                    extract_prediction(pred) for pred in row["prediction"]
                ]

            records.append(Text2TextRecord(**row))

        return cls(records)

    @classmethod
    def _from_pandas(cls, dataframe: pd.DataFrame) -> "DatasetForText2Text":
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

    Examples:
        >>> # Read text classification records from a datasets Dataset
        >>> import datasets
        >>> ds = datasets.Dataset.from_dict({
        ...     "inputs": ["example"],
        ...     "prediction": [
        ...         [{"label": "LABEL1", "score": 0.9}, {"label": "LABEL2", "score": 0.1}]
        ...     ]
        ... })
        >>> read_datasets(ds, task="TextClassification")
        >>>
        >>> # Read token classification records from a datasets Dataset
        >>> ds = datasets.Dataset.from_dict({
        ...     "text": ["my example"],
        ...     "tokens": [["my", "example"]],
        ...     "prediction": [
        ...         [{"label": "LABEL1", "start": 3, "end": 10}]
        ...     ]
        ... })
        >>> read_datasets(ds, task="TokenClassification")
        >>>
        >>> # Read text2text records from a datasets Dataset
        >>> ds = datasets.Dataset.from_dict({
        ...     "text": ["my example"],
        ...     "prediction": [["mi ejemplo", "ejemplo mio"]]
        ... })
        >>> # or
        >>> ds = datasets.Dataset.from_dict({
        ...     "text": ["my example"],
        ...     "prediction": [[{"text": "mi ejemplo", "score": 0.9}]]
        ... })
        >>> read_datasets(ds, task="Text2Text")
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

    Examples:
        >>> # Read text classification records from a pandas DataFrame
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "inputs": ["example"],
        ...     "prediction": [
        ...         [("LABEL1", 0.9), ("LABEL2", 0.1)]
        ...     ]
        ... })
        >>> read_pandas(df, task="TextClassification")
        >>>
        >>> # Read token classification records from a datasets Dataset
        >>> df = pd.DataFrame({
        ...     "text": ["my example"],
        ...     "tokens": [["my", "example"]],
        ...     "prediction": [
        ...         [("LABEL1", 3, 10)]
        ...     ]
        ... })
        >>> read_pandas(df, task="TokenClassification")
        >>>
        >>> # Read text2text records from a datasets Dataset
        >>> df = pd.DataFrame({
        ...     "text": ["my example"],
        ...     "prediction": [["mi ejemplo", "ejemplo mio"]]
        ... })
        >>> # or
        >>> ds = pd.DataFrame({
        ...     "text": ["my example"],
        ...     "prediction": [[("mi ejemplo", 0.9)]]
        ... })
        >>> read_pandas(df, task="Text2Text")
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
