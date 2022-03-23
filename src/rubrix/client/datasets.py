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

    @classmethod
    def _record_init_args(cls) -> List[str]:
        """
        Helper the returns the field list available for creation of inner records.
        The ``_RECORD_TYPE.__fields__`` will be returned as default
        """
        return [field for field in cls._RECORD_TYPE.__fields__]

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
        # TODO: THIS FIELD IS ONLY AT CLIENT API LEVEL. NOT SENSE HERE FOR NOW
        if "search_keywords" in ds_dict:
            del ds_dict["search_keywords"]

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
    def from_datasets(
        cls,
        dataset: "datasets.Dataset",
        id: Optional[str] = None,
        text: Optional[str] = None,
        annotation: Optional[str] = None,
        metadata: Optional[Union[str, List[str]]] = None,
        **kwargs,
    ) -> "Dataset":
        """Imports records from a `datasets.Dataset`.

        Columns that are not supported are ignored.

        Args:
            dataset: A datasets Dataset from which to import the records.
            id: The field name used as record id. Default: `None`
            text: The field name used as record text. Default: `None`
            annotation: The field name used as record annotation. Default: `None`
            metadata: The field name used as record metadata. Default: `None`

        Returns:
            The imported records in a Rubrix Dataset.
        """
        import datasets

        assert not isinstance(dataset, datasets.DatasetDict), (
            "ERROR: `datasets.DatasetDict` are not supported. "
            "Please, select the dataset split before"
        )

        dataset = cls._prepare_hf_dataset(
            dataset,
            id=id,
            text=text,
            annotation=annotation,
            metadata=metadata,
            **kwargs,
        )

        not_supported_columns = [
            col for col in dataset.column_names if col not in cls._record_init_args()
        ]
        if not_supported_columns:
            _LOGGER.warning(
                f"Following columns are not supported by the {cls._RECORD_TYPE.__name__}"
                f" model and are ignored: {not_supported_columns}"
            )
            dataset = dataset.remove_columns(not_supported_columns)
        return cls._from_datasets(dataset)

    @classmethod
    def _prepare_hf_dataset(
        cls,
        dataset: "dataset.Dataset",
        id: Optional[str] = None,
        text: Optional[str] = None,
        annotation: Optional[str] = None,
        metadata: Optional[Union[str, List[str]]] = None,
    ) -> "dataclasses.Dataset":
        for field, parser in [
            (id, cls._parse_id_field),
            (text, cls._parse_text_field),
            (metadata, cls._parse_metadata_field),
            (annotation, cls._parse_annotation_field),
        ]:
            if field:
                dataset = parser(dataset, field)
        return dataset

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
            col for col in dataframe.columns if col not in cls._record_init_args()
        ]
        if not_supported_columns:
            _LOGGER.warning(
                f"Following columns are not supported by the {cls._RECORD_TYPE.__name__} model "
                f"and are ignored: {not_supported_columns}"
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

    @classmethod
    def _parse_id_field(
        cls, dataset: "datasets.Dataset", field: str
    ) -> "datasets.Dataset":
        return dataset.rename_column(field, "id")

    @classmethod
    def _parse_text_field(
        cls, dataset: "datasets.Dataset", field: str
    ) -> "datasets.Dataset":
        return dataset.rename_column(field, "text")

    @classmethod
    def _parse_metadata_field(
        cls, dataset: "datasets.Dataset", fields: Union[str, List[str]]
    ) -> "datasets.Dataset":

        if isinstance(fields, str):
            fields = [fields]

        def parse_metadata_from_dataset(example):
            return {"metadata": {k: example[k] for k in fields}}

        return dataset.map(
            parse_metadata_from_dataset, desc="Parsing metadata"
        ).remove_columns(fields)

    @classmethod
    def _parse_annotation_field(
        cls, dataset: "datasets.Dataset", field: str
    ) -> "datasets.Dataset":
        return dataset.rename_column(field, "annotation")


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
        ...     rb.TextClassificationRecord(text="example"),
        ...     rb.TextClassificationRecord(text="another example"),
        ... ]
        >>> dataset = rb.DatasetForTextClassification(records)
        >>> assert len(dataset) == 2
        >>>
        >>> # Indexing into the dataset:
        >>> dataset[0]
        ... rb.TextClassificationRecord(text="example")
        >>> dataset[0] = rb.TextClassificationRecord(text="replaced example")
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
        text: Optional[str] = None,
        id: Optional[str] = None,
        inputs: Optional[Union[str, List[str]]] = None,
        annotation: Optional[str] = None,
        metadata: Optional[Union[str, List[str]]] = None,
    ) -> "DatasetForTextClassification":
        """Imports records from a `datasets.Dataset`.

        Columns that are not supported are ignored.

        Args:
            dataset: A datasets Dataset from which to import the records.
            text: The field name used as record text. Default: `None`
            id: The field name used as record id. Default: `None`
            inputs: A list of field names used for record inputs. Default: `None`
            annotation: The field name used as record annotation. Default: `None`
            metadata: The field name used as record metadata. Default: `None`

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

        return super().from_datasets(
            dataset,
            text=text,
            id=id,
            annotation=annotation,
            metadata=metadata,
            inputs=inputs,
        )

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
    def _parse_annotation_field(
        cls, dataset: "datasets.Dataset", field: str
    ) -> "datasets.Dataset":
        import datasets

        labels = dataset.features[field]
        if isinstance(labels, datasets.Sequence):
            labels = labels.feature

        dataset = dataset.rename_column(field, "annotation")

        if not isinstance(labels, datasets.ClassLabel):
            return dataset

        def int2str_for_annotation(example):
            try:
                return {"annotation": labels.int2str(example["annotation"])}
            # integers don't have to map to the names ...
            # it seems that sometimes -1 is used to denote "no label"
            except ValueError:
                return {"annotation": None}

        return dataset.map(int2str_for_annotation, desc="Parsing annotation")

    @classmethod
    def _prepare_hf_dataset(
        cls,
        dataset: "dataset.Dataset",
        inputs: Optional[Union[str, List[str]]] = None,
        **kwargs,
    ) -> "dataclasses.Dataset":
        dataset = super()._prepare_hf_dataset(dataset, **kwargs)
        if inputs:
            dataset = cls._parse_inputs_field(dataset, fields=inputs)
        return dataset

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

            records.append(TextClassificationRecord.parse_obj(row))
        return cls(records)

    @classmethod
    def _parse_inputs_field(
        cls, dataset: "datasets.Dataset", fields: Optional[Union[str, List[str]]]
    ) -> "datasets.Dataset":
        if isinstance(fields, str):
            fields = [fields]

        return dataset.map(
            lambda example: {"inputs": {k: example[k] for k in fields}},
            desc="Parsing inputs",
        )

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

        class_label = (
            datasets.ClassLabel(names=sorted(labels.keys()))
            if ds_dict["label"]
            # in case we don't have any labels, ClassLabel fails with Dataset.from_dict({"labels": []})
            else datasets.Value("string")
        )
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

    @classmethod
    def _record_init_args(cls) -> List[str]:
        """Adds the `tags` argument to default record init arguments"""
        parent_fields = super(DatasetForTokenClassification, cls)._record_init_args()
        return parent_fields + ["tags"]  # compute annotation from tags

    def __init__(self, records: Optional[List[TokenClassificationRecord]] = None):
        # we implement this to have more specific type hints
        super().__init__(records=records)

    @classmethod
    def from_datasets(
        cls,
        dataset: "datasets.Dataset",
        text: Optional[str] = None,
        tokens: Optional[str] = None,
        tags: Optional[str] = None,
        metadata: Optional[Union[str, List[str]]] = None,
    ) -> "DatasetForTokenClassification":
        """Imports records from a `datasets.Dataset`.

        Columns that are not supported are ignored.

        Args:
            dataset: A datasets Dataset from which to import the records.
            text: The field name used as record text. Default: `None`
            tokens: The field name used as record tokens. Default: `None`
            tags: The field name used as record tags. Default: `None`
            metadata: The field name used as record metadata. Default: `None`

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
        return super().from_datasets(
            dataset, text=text, tokens=tokens, tags=tags, metadata=metadata
        )

    @classmethod
    def from_pandas(
        # we implement this to have more specific type hints
        cls,
        dataframe: pd.DataFrame,
    ) -> "DatasetForTokenClassification":
        return super().from_pandas(dataframe)

    @_requires_datasets
    def prepare_for_training(self) -> "datasets.Dataset":
        """Prepares the dataset for training.

        This will return a ``datasets.Dataset`` with all columns returned by ``to_datasets`` method
        and an additional  *ner_tags* column:
            - Records without an annotation are removed.
            - The *ner_tags* column corresponds to the iob tags sequences for annotations of the records
            - The iob tags are transformed to integers.

        Returns:
            A datasets Dataset with a *ner_tags* column and all columns returned by ``to_datasets``.

        Examples:
            >>> import rubrix as rb
            >>> rb_dataset = rb.DatasetForTokenClassification([
            ...     rb.TokenClassificationRecord(
            ...         text="The text",
            ...         tokens=["The", "text"],
            ...         annotation=[("TAG", 0, 2)],
            ...     )
            ... ])
            >>> rb_dataset.prepare_for_training().features
            {'text': Value(dtype='string'),
             'tokens': Sequence(feature=Value(dtype='string'), length=-1),
             'prediction': Value(dtype='null'),
             'prediction_agent': Value(dtype='null'),
             'annotation': [{'end': Value(dtype='int64'),
               'label': Value(dtype='string'),
               'start': Value(dtype='int64')}],
             'annotation_agent': Value(dtype='null'),
             'id': Value(dtype='null'),
             'metadata': Value(dtype='null'),
             'status': Value(dtype='string'),
             'event_timestamp': Value(dtype='null'),
             'metrics': Value(dtype='null'),
             'ner_tags': [ClassLabel(num_classes=3, names=['O', 'B-TAG', 'I-TAG'])]}


        """
        import datasets

        has_annotations = False
        for rec in self._records:
            if rec.annotation is not None:
                has_annotations = True
                break

        if not has_annotations:
            return datasets.Dataset.from_dict({})

        class_tags = ["O"]
        class_tags.extend(
            [
                f"{pre}-{label}"
                for label in sorted(self.__all_labels__())
                for pre in ["B", "I"]
            ]
        )
        class_tags = datasets.ClassLabel(names=class_tags)

        def spans2iob(example):
            r = TokenClassificationRecord(
                text=example["text"],
                tokens=example["tokens"],
                annotation=self.__entities_to_tuple__(example["annotation"]),
            )
            return class_tags.str2int(r.spans2iob(r.annotation))

        ds = (
            self.to_datasets()
            .filter(self.__only_annotations__)
            .map(lambda example: {"ner_tags": spans2iob(example)})
        )
        new_features = ds.features.copy()
        new_features["ner_tags"] = [class_tags]

        return ds.cast(new_features)

    def __all_labels__(self):
        all_labels = set()
        for record in self._records:
            if record.annotation:
                all_labels.update([label for label, _, _ in record.annotation])

        return list(all_labels)

    def __only_annotations__(self, data) -> bool:
        return data["annotation"] is not None

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

    @staticmethod
    def __entities_to_tuple__(
        entities,
    ) -> List[Union[Tuple[str, int, int], Tuple[str, int, int, float]]]:
        return [
            (ent["label"], ent["start"], ent["end"])
            if len(ent) == 3
            else (ent["label"], ent["start"], ent["end"], ent["score"] or 1.0)
            for ent in entities
        ]

    @classmethod
    def _prepare_hf_dataset(
        cls,
        dataset: "dataset.Dataset",
        tokens: Optional[str] = None,
        tags: Optional[str] = None,
        **kwargs,
    ) -> "dataclasses.Dataset":
        dataset = super()._prepare_hf_dataset(dataset, **kwargs)
        if tokens:
            dataset = cls._parse_tokens_field(dataset, field=tokens)
        if tags:
            dataset = cls._parse_tags_field(dataset, field=tags)
        return dataset

    @classmethod
    def _from_datasets(
        cls,
        dataset: "datasets.Dataset",
    ) -> "DatasetForTokenClassification":

        records = []
        for row in dataset:
            if row.get("prediction"):
                row["prediction"] = cls.__entities_to_tuple__(row["prediction"])
            if row.get("annotation"):
                row["annotation"] = cls.__entities_to_tuple__(row["annotation"])
            if not row["tokens"]:
                _LOGGER.warning(f"Ignoring row with no tokens.")
                continue
            records.append(TokenClassificationRecord.parse_obj(row))
        return cls(records)

    @classmethod
    def _parse_tokens_field(
        cls, dataset: "datasets.Dataset", field: str
    ) -> "datasets.Dataset":
        def parse_tokens_from_example(example):
            tokens: List[str] = example[field]
            data = {"tokens": tokens}

            if "text" not in example:
                data["text"] = " ".join(tokens)
            return data

        return dataset.map(parse_tokens_from_example, desc="Parsing tokens")

    @classmethod
    def _parse_tags_field(
        cls, dataset: "datasets.Dataset", field: str = str
    ) -> "datasets.Dataset":
        import datasets

        labels = dataset.features[field]
        if isinstance(labels, datasets.Sequence):
            labels = labels.feature
        int2str = (
            labels.int2str if isinstance(labels, datasets.ClassLabel) else lambda x: x
        )

        def parse_tags_from_example(example):
            return {"tags": [int2str(t) for t in example[field] or []]}

        return dataset.map(parse_tags_from_example, desc="Parsing tags")

    @classmethod
    def _from_pandas(cls, dataframe: pd.DataFrame) -> "DatasetForTokenClassification":
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
    def from_datasets(
        cls,
        dataset: "datasets.Dataset",
        text: Optional[str] = None,
        annotation: Optional[str] = None,
        metadata: Optional[Union[str, List[str]]] = None,
    ) -> "DatasetForText2Text":
        """Imports records from a `datasets.Dataset`.

        Columns that are not supported are ignored.

        Args:
            dataset: A datasets Dataset from which to import the records.
            text: The field name used as record text. Default: `None`
            annotation: The field name used as record annotation. Default: `None`
            metadata: The field name used as record metadata. Default: `None`

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
        return super().from_datasets(
            dataset, text=text, annotation=annotation, metadata=metadata
        )

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


def read_datasets(
    dataset: "datasets.Dataset", task: Union[str, TaskType], **kwargs
) -> Dataset:
    """Reads a datasets Dataset and returns a Rubrix Dataset

    Args:
        dataset: Dataset to be read in.
        task: Task for the dataset, one of: ["TextClassification", "TokenClassification", "Text2Text"].
        **kwargs: Passed on to the task-specific ``DatasetFor*.from_datasets()`` method.

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
        return DatasetForTextClassification.from_datasets(dataset, **kwargs)
    if task is TaskType.token_classification:
        return DatasetForTokenClassification.from_datasets(dataset, **kwargs)
    if task is TaskType.text2text:
        return DatasetForText2Text.from_datasets(dataset, **kwargs)
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
