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
import random
import uuid
import warnings
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type, Union

import pandas as pd

from argilla._constants import OPENAI_END_TOKEN, OPENAI_SEPARATOR, OPENAI_WHITESPACE
from argilla.client.apis.datasets import TextClassificationSettings, TokenClassificationSettings
from argilla.client.models import (
    Framework,
    Record,
    Text2TextRecord,
    TextClassificationRecord,
    TokenAttributions,
    TokenClassificationRecord,
)
from argilla.client.sdk.datasets.models import TaskType
from argilla.utils.dependency import require_dependencies, requires_dependencies
from argilla.utils.span_utils import SpanUtils

if TYPE_CHECKING:
    import datasets
    import pandas
    import spacy


class DatasetBase:
    """The Dataset classes are containers for argilla records.

    This is the base class to facilitate the implementation for each record type.

    Args:
        records: A list of argilla records.

    Raises:
        WrongRecordTypeError: When the record type in the provided
            list does not correspond to the dataset type.
    """

    _RECORD_TYPE = None
    # record fields that can hold multiple input columns from a datasets.Dataset or a pandas.DataFrame
    _RECORD_FIELDS_WITH_MULTIPLE_INPUT_COLUMNS = ["inputs", "metadata"]
    _SETTINGS = None

    @classmethod
    def _record_init_args(cls) -> List[str]:
        """
        Helper the returns the field list available for creation of inner records.
        The ``_RECORD_TYPE.__fields__`` will be returned as default
        """
        return [field for field in cls._RECORD_TYPE.__fields__]

    def __init__(self, records: Optional[List[Record]] = None):
        if self._RECORD_TYPE is None:
            raise NotImplementedError("A Dataset implementation has to define a `_RECORD_TYPE`!")

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
                f"A {type(self).__name__} must only contain"
                f" {self._RECORD_TYPE.__name__}s, but you provided various types:"
                f" {[rt.__name__ for rt in record_types.keys()]}"
            )
        elif next(iter(record_types)) is not self._RECORD_TYPE:
            raise WrongRecordTypeError(
                f"A {type(self).__name__} must only contain"
                f" {self._RECORD_TYPE.__name__}s, but you provided"
                f" {list(record_types.keys())[0].__name__}s."
            )

    def __iter__(self):
        return self._records.__iter__()

    def __getitem__(self, key):
        return self._records[key]

    def __setitem__(self, key, value):
        if type(value) is not self._RECORD_TYPE:
            raise WrongRecordTypeError(
                f"You are only allowed to set a record of type {self._RECORD_TYPE} in"
                f" this dataset, but you provided {type(value)}"
            )
        self._records[key] = value

    def __delitem__(self, key):
        del self._records[key]

    def __len__(self) -> int:
        return len(self._records)

    def __repr__(self):
        return repr(self.to_pandas())

    def __str__(self):
        return repr(self)

    @requires_dependencies("datasets>1.17.0")
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
            warnings.warn(
                "The 'metadata' of the records were removed, since it was incompatible with the 'datasets' format."
            )

        return dataset

    def _to_datasets_dict(self) -> Dict:
        raise NotImplementedError

    @classmethod
    def from_datasets(cls, dataset: "datasets.Dataset", **kwargs) -> "Dataset":
        """Imports records from a `datasets.Dataset`.

        Columns that are not supported are ignored.

        Args:
            dataset: A datasets Dataset from which to import the records.

        Returns:
            The imported records in a argilla Dataset.
        """
        raise NotImplementedError

    @classmethod
    def _prepare_dataset_and_column_mapping(
        cls,
        dataset: "datasets.Dataset",
        column_mapping: Dict[str, Union[str, List[str]]],
    ) -> Tuple["datasets.Dataset", Dict[str, List[str]]]:
        """Renames and removes columns, and extracts the mapping of the columns to be joined.

        Args:
            dataset: A datasets Dataset from which to import the records.
            column_mapping: Mappings from record fields to column names.

        Returns:
            The prepared dataset and a mapping for the columns to be joined
        """
        import datasets

        if isinstance(dataset, datasets.DatasetDict):
            raise ValueError("`datasets.DatasetDict` are not supported. Please, select the dataset split before.")

        # clean column mappings
        column_mapping = {key: val for key, val in column_mapping.items() if val is not None}

        cols_to_be_renamed, cols_to_be_joined = {}, {}
        for field, col in column_mapping.items():
            if field in cls._RECORD_FIELDS_WITH_MULTIPLE_INPUT_COLUMNS:
                cols_to_be_joined[field] = [col] if isinstance(col, str) else col
            else:
                cols_to_be_renamed[col] = field

        dataset = dataset.rename_columns(cols_to_be_renamed)

        dataset = cls._remove_unsupported_columns(
            dataset,
            extra_columns=[col for cols in cols_to_be_joined.values() for col in cols],
        )

        return dataset, cols_to_be_joined

    @classmethod
    def _remove_unsupported_columns(
        cls,
        dataset: "datasets.Dataset",
        extra_columns: List[str],
    ) -> "datasets.Dataset":
        """Helper function to remove unsupported columns from the `datasets.Dataset` following the record type.

        Args:
            dataset: The dataset.
            extra_columns: Extra columns to be kept.

        Returns:
            The dataset with unsupported columns removed.
        """
        not_supported_columns = [
            col for col in dataset.column_names if col not in cls._record_init_args() + extra_columns
        ]

        if not_supported_columns:
            warnings.warn(
                "Following columns are not supported by the"
                f" {cls._RECORD_TYPE.__name__} model and are ignored:"
                f" {not_supported_columns}"
            )
            dataset = dataset.remove_columns(not_supported_columns)

        return dataset

    @staticmethod
    def _join_datasets_columns_and_delete(row: Dict[str, Any], columns: List[str]) -> Dict[str, Any]:
        """Joins columns of a `datasets.Dataset` row into a dict, and deletes the single columns.

        Updates the ``row`` dictionary!

        Args:
            row: A row of a `datasets.Dataset`
            columns: Name of the columns to be joined and deleted from the row.

        Returns:
            A dict containing the columns and its values.
        """
        joined_cols = {}
        for col in columns:
            joined_cols[col] = row[col]
            del row[col]

        return joined_cols

    @staticmethod
    def _parse_datasets_column_with_classlabel(
        column_value: Union[str, List[str], int, List[int]],
        feature: Optional[Any],
    ) -> Optional[Union[str, List[str], int, List[int]]]:
        """Helper function to parse a datasets.Dataset column with a potential ClassLabel feature.

        Args:
            column_value: The value from the datasets Dataset column.
            feature: The feature of the annotation column to optionally convert ints to strs.

        Returns:
            The column value optionally converted to str, or None if the conversion fails.
        """
        import datasets

        # extract ClassLabel feature
        if isinstance(feature, list):
            feature = feature[0]
        if isinstance(feature, datasets.Sequence):
            feature = feature.feature
        if not isinstance(feature, datasets.ClassLabel):
            feature = None

        if feature is None:
            return column_value

        try:
            return feature.int2str(column_value)
        # integers don't have to map to the names ...
        # it seems that sometimes -1 is used to denote "no label"
        except ValueError:
            return None

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
            The imported records in a argilla Dataset.
        """
        not_supported_columns = [col for col in dataframe.columns if col not in cls._record_init_args()]
        if not_supported_columns:
            warnings.warn(
                "Following columns are not supported by the"
                f" {cls._RECORD_TYPE.__name__} model and are ignored:"
                f" {not_supported_columns}"
            )
            dataframe = dataframe.drop(columns=not_supported_columns)

        return cls._from_pandas(dataframe)

    @classmethod
    def _from_pandas(cls, dataframe: pd.DataFrame) -> "Dataset":
        """Helper method to create a argilla Dataset from a pandas DataFrame.

        Must be implemented by the child class.

        Args:
            dataframe: A pandas DataFrame

        Returns:
            A argilla Dataset
        """
        raise NotImplementedError

    def prepare_for_training(
        self,
        framework: Union[Framework, str] = "transformers",
        settings: Union[TextClassificationSettings, TokenClassificationSettings] = None,
        lang: Optional["spacy.Language"] = None,
        train_size: Optional[float] = 1,
        test_size: Optional[float] = None,
        seed: Optional[int] = None,
    ) -> Union[
        "datasets.Dataset",
        "spacy.tokens.DocBin",
        Tuple["spacy.tokens.DocBin", "spacy.tokens.DocBin"],
        Tuple["pandas.DataFrame", "pandas.DataFrame"],
    ]:
        """Prepares the dataset for training.

        This will return a ``datasets.Dataset`` with all columns returned by ``to_datasets`` method
        and an additional  *ner_tags* column:
            - Records without an annotation are removed.
            - The *ner_tags* column corresponds to the iob tags sequences for annotations of the records
            - The iob tags are transformed to integers.

        Args:
            framework: A string|enum specifying the framework for the training.
                "transformers" and "spacy" are currently supported. Default: `transformers`
            lang: The spacy nlp Language pipeline used to process the dataset. (Only for spacy framework)
            train_size: The size of the training set. If float, should be between 0.0 and 1.0 and represent the
                proportion of the dataset to include in the train split.
            test_size: The size of the test set. If float, should be between 0.0 and 1.0 and represent the
                proportion of the dataset to include in the test split.
            seed: Random state.

        Returns:
            A datasets Dataset with a *ner_tags* or a *label* column and and several *inputs* columns.
            returned by ``to_datasets`` for "transformers" framework or a spaCy DocBin for "spacy" framework.

        Examples:
            >>> import argilla as rg
            >>> rb_dataset = rg.DatasetForTokenClassification([
            ...     rg.TokenClassificationRecord(
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

            >>> import argilla as rg
            >>> rb_dataset = rg.DatasetForTextClassification([
            ...     rg.TextClassificationRecord(
            ...         inputs={"header": "my header", "content": "my content"},
            ...         annotation="SPAM",
            ...     )
            ... ])
            >>> rb_dataset.prepare_for_training().features
            {'header': Value(dtype='string'),
             'content': Value(dtype='string'),
             'label': ClassLabel(num_classes=1, names=['SPAM'])}

        """
        if self._RECORD_TYPE == TextClassificationRecord:
            if settings is None:
                self._SETTINGS = self._infer_settings_from_records()
            elif isinstance(settings, TextClassificationSettings):
                self._SETTINGS = settings
            else:
                raise ValueError("settings must be TextClassificationSettings for TextClassificationRecord")
        elif self._RECORD_TYPE == TokenClassificationRecord:
            if settings is None:
                self._SETTINGS = self._infer_settings_from_records()
            elif isinstance(settings, TokenClassificationSettings):
                self._SETTINGS = settings
            else:
                raise ValueError("settings must be TokenClassificationSettings for TokenClassificationRecord")
        else:
            self._SETTINGS = settings

        if train_size is None:
            train_size = 1
        if test_size is None:
            test_size = 1 - train_size

        # check if all numbers are larger than 0
        assert [abs(train_size), abs(test_size)] == [train_size, test_size], ValueError(
            "`train_size` and `test_size` must be larger than 0."
        )

        # check if train sizes sum up to 1
        assert (train_size + test_size) == 1, ValueError("`train_size` and `test_size` must sum to 1.")

        # check for annotations
        assert any([rec.annotation for rec in self._records]), ValueError("Dataset has no annotations.")

        if test_size == 0:
            test_size = None

        # shuffle records
        shuffled_records = self._records.copy()
        seed = seed or random.randint(42, 1984)
        random.Random(seed).shuffle(shuffled_records)

        # turn the string into a Framework instance and trigger error if str is not valid
        if isinstance(framework, str):
            framework = Framework(framework)

        # prepare for training for the right method
        if framework in [
            Framework.TRANSFORMERS,
            Framework.SETFIT,
            Framework.SPAN_MARKER,
            Framework.PEFT,
        ]:
            return self._prepare_for_training_with_transformers(train_size=train_size, test_size=test_size, seed=seed)
        elif framework in [Framework.SPACY, Framework.SPACY_TRANSFORMERS] and lang is None:
            raise ValueError(
                "Please provide a `spaCy` language model to prepare the dataset for"
                " training with the `spaCy`/`spaCy-transformers` framework."
            )
        elif framework in [Framework.SPACY, Framework.SPACY_TRANSFORMERS, Framework.SPARK_NLP, Framework.OPENAI]:
            if train_size and test_size:
                require_dependencies("scikit-learn")
                from sklearn.model_selection import train_test_split

                records_train, records_test = train_test_split(
                    shuffled_records,
                    train_size=train_size,
                    shuffle=False,
                    random_state=seed,
                )
                if framework in [Framework.SPACY, Framework.SPACY_TRANSFORMERS]:
                    train_docbin = self._prepare_for_training_with_spacy(nlp=lang, records=records_train)
                    test_docbin = self._prepare_for_training_with_spacy(nlp=lang, records=records_test)
                    return train_docbin, test_docbin
                elif framework is Framework.SPARK_NLP:
                    train_df = self._prepare_for_training_with_spark_nlp(records_train)
                    test_df = self._prepare_for_training_with_spark_nlp(records_test)
                    return train_df, test_df
                else:
                    train_jsonl = self._prepare_for_training_with_openai(records=records_train)
                    test_jsonl = self._prepare_for_training_with_openai(records=records_test)
                    return train_jsonl, test_jsonl
            else:
                if framework in [Framework.SPACY, Framework.SPACY_TRANSFORMERS]:
                    return self._prepare_for_training_with_spacy(nlp=lang, records=shuffled_records)
                elif framework is Framework.SPARK_NLP:
                    return self._prepare_for_training_with_spark_nlp(records=shuffled_records)
                elif framework is Framework.OPENAI:
                    return self._prepare_for_training_with_openai(records=shuffled_records)
                else:
                    raise NotImplementedError(
                        f"Framework {framework} is not supported. Choose from: {[e.value for e in Framework]}"
                    )
        else:
            raise NotImplementedError(
                f"Framework {framework} is not supported. Choose from: {[e.value for e in Framework]}"
            )

    @requires_dependencies("spacy")
    def _prepare_for_training_with_spacy(
        self, **kwargs
    ) -> Union["spacy.token.DocBin", Tuple["spacy.token.DocBin", "spacy.token.DocBin"]]:
        """Prepares the dataset for training using the "spacy" framework.

        Args:
            **kwargs: Specific to the task of the dataset.

        Returns:
            A spacy.token.DocBin.
        """

        raise NotImplementedError

    @requires_dependencies("datasets>1.17.0")
    def _prepare_for_training_with_transformers(self, **kwargs) -> "datasets.Dataset":
        """Prepares the dataset for training using the "transformers" framework.

        Args:
            **kwargs: Specific to the task of the dataset.

        Returns:
            A datasets Dataset.
        """

        raise NotImplementedError

    def _prepare_for_training_with_spark_nlp(self, **kwargs) -> "datasets.Dataset":
        """Prepares the dataset for training using the "spark-nlp" framework.

        Args:
            **kwargs: Specific to the task of the dataset.

        Returns:
            A pd.DataFrame.
        """

        raise NotImplementedError

    def _prepare_for_training_with_openai(self, **kwargs) -> "dict":
        """Prepares the dataset for training using the "openai" framework.

        Args:
            **kwargs: Specific to the task of the dataset.

        Returns:
            A pd.DataFrame.
        """

        raise NotImplementedError

    def _infer_settings_from_records(self) -> Union[TokenClassificationSettings, TextClassificationSettings]:
        """Infer the settings from the records.

        Returns:
            A Settings object.
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
        >>> import argilla as rg
        >>> dataset = rg.DatasetForTextClassification.from_pandas(my_dataframe)
        >>> dataset.to_datasets()
        >>>
        >>> # Looping over the dataset:
        >>> for record in dataset:
        ...     print(record)
        >>>
        >>> # Passing in a list of records:
        >>> records = [
        ...     rg.TextClassificationRecord(text="example"),
        ...     rg.TextClassificationRecord(text="another example"),
        ... ]
        >>> dataset = rg.DatasetForTextClassification(records)
        >>> assert len(dataset) == 2
        >>>
        >>> # Indexing into the dataset:
        >>> dataset[0]
        ... rg.TextClassificationRecord(text="example")
        >>> dataset[0] = rg.TextClassificationRecord(text="replaced example")
    """

    _RECORD_TYPE = TextClassificationRecord

    def __init__(self, records: Optional[List[TextClassificationRecord]] = None):
        # we implement this to have more specific type hints
        super().__init__(records=records)

    @classmethod
    @requires_dependencies("datasets>1.17.0")
    def from_datasets(
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
            The imported records in a argilla Dataset.

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
        dataset, cols_to_be_joined = cls._prepare_dataset_and_column_mapping(
            dataset,
            dict(
                text=text,
                id=id,
                inputs=inputs,
                annotation=annotation,
                metadata=metadata,
            ),
        )

        records = []
        for row in dataset:
            row["inputs"] = cls._parse_inputs_field(row, cols_to_be_joined.get("inputs"))
            if row.get("inputs") is not None and row.get("text") is not None:
                del row["text"]

            if row.get("annotation") is not None:
                row["annotation"] = cls._parse_datasets_column_with_classlabel(
                    row["annotation"], dataset.features["annotation"]
                )

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
                        key: [TokenAttributions(**tokattr_kwargs) for tokattr_kwargs in val]
                        for key, val in row["explanation"].items()
                    }
                    if row["explanation"] is not None
                    else None
                )

            if cols_to_be_joined.get("metadata"):
                row["metadata"] = cls._join_datasets_columns_and_delete(row, cols_to_be_joined["metadata"])

            records.append(TextClassificationRecord.parse_obj(row))

        return cls(records)

    @classmethod
    def _parse_inputs_field(
        cls,
        row: Dict[str, Any],
        columns: Optional[List[str]],
    ) -> Optional[Union[Dict[str, str], str]]:
        """Helper function to parse the inputs field.

        Args:
            row: A row of the dataset.Datasets
            columns: A list of columns to be joined for the inputs field, optional.

        Returns:
            None, a dictionary or a string as input for the inputs field.
        """
        inputs = row.get("inputs")

        if columns is not None:
            inputs = cls._join_datasets_columns_and_delete(row, columns)

        if isinstance(inputs, dict):
            inputs = {key: val for key, val in inputs.items() if val is not None}

        return inputs

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
                    {key: list(map(dict, tokattrs)) for key, tokattrs in rec.explanation.items()}
                    if rec.explanation is not None
                    else None
                    for rec in self._records
                ]
            elif key == "id":
                ds_dict[key] = [None if rec.id is None else str(rec.id) for rec in self._records]
            elif key == "metadata":
                ds_dict[key] = [getattr(rec, key) or None for rec in self._records]
            else:
                ds_dict[key] = [getattr(rec, key) for rec in self._records]

        return ds_dict

    @classmethod
    def _from_pandas(cls, dataframe: pd.DataFrame) -> "DatasetForTextClassification":
        return cls([TextClassificationRecord(**row) for row in dataframe.to_dict("records")])

    @requires_dependencies("datasets>1.17.0")
    def _prepare_for_training_with_transformers(
        self,
        train_size: Optional[float] = None,
        test_size: Optional[float] = None,
        seed: Optional[int] = None,
    ):
        import datasets

        ds_dict = {"id": [], "text": [], "label": []}
        for rec in self._records:
            if rec.annotation is None:
                continue

            if rec.text is not None:
                text = rec.text
            elif rec.text is None and "text" in rec.inputs:
                text = rec.inputs["text"]
            else:
                text = " ".join(rec.inputs.values())

            ds_dict["text"].append(text)
            ds_dict["label"].append(rec.annotation)
            ds_dict["id"].append(str(rec.id))

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
            "id": datasets.Value("string"),
            "text": datasets.Value("string"),
            "label": [class_label] if self._records[0].multi_label else class_label,
        }

        ds = datasets.Dataset.from_dict(ds_dict, features=datasets.Features(feature_dict))

        if self._records[0].multi_label:
            require_dependencies("scikit-learn")
            from sklearn.preprocessing import MultiLabelBinarizer

            labels = [rec["label"] for rec in ds]
            mlb = MultiLabelBinarizer()
            binarized_labels = mlb.fit_transform(labels)
            feature_dict["binarized_label"] = feature_dict["label"]
            ds = datasets.Dataset.from_dict(
                {
                    "id": ds["id"],
                    "text": ds["text"],
                    "label": labels,
                    "binarized_label": binarized_labels,
                },
                features=datasets.Features(feature_dict),
            )
        if test_size is not None and test_size != 0:
            ds = ds.train_test_split(train_size=train_size, test_size=test_size, seed=seed)

        return ds

    @requires_dependencies("spacy")
    def _prepare_for_training_with_spacy(self, nlp: "spacy.Language", records: List[Record]) -> "spacy.tokens.DocBin":
        from spacy.tokens import DocBin

        db = DocBin(store_user_data=True)
        all_labels = self._verify_all_labels()

        # Creating the DocBin object as in https://spacy.io/usage/training#training-data

        for record in records:
            if record.annotation is None:
                continue

            if record.text is not None:
                text = record.text
            elif record.text is None and "text" in record.inputs:
                text = record.inputs["text"]
            else:
                text = ", ".join(f"{key}: {value}" for key, value in record.inputs.items())
            doc = nlp.make_doc(text)
            doc.user_data["id"] = record.id

            cats = dict.fromkeys(all_labels, 0)

            if isinstance(record.annotation, list):
                for anno in record.annotation:
                    cats[anno] = 1
            else:
                cats[record.annotation] = 1

            doc.cats = cats
            db.add(doc)

        return db

    def _prepare_for_training_with_spark_nlp(self, records: List[Record]) -> "pandas.DataFrame":
        if records[0].multi_label:
            label_name = "labels"
        else:
            label_name = "label"

        spark_nlp_data = []
        for record in records:
            if record.annotation is None:
                continue
            if record.id is None:
                record.id = str(uuid.uuid4())
            if record.text is not None:
                text = record.text
            elif record.text is None and "text" in record.inputs:
                text = record.inputs["text"]
            else:
                text = ", ".join(f"{key}: {value}" for key, value in record.inputs.items())

            spark_nlp_data.append([record.id, text, record.annotation])

        return pd.DataFrame(spark_nlp_data, columns=["id", "text", label_name])

    def _prepare_for_training_with_openai(self, **kwargs) -> "datasets.Dataset":
        """Prepares the dataset for training using the "openai" framework.

        Args:
            **kwargs: Specific to the task of the dataset.

        Returns:
            A pd.DataFrame.
        """
        separator = OPENAI_SEPARATOR
        whitespace = OPENAI_WHITESPACE
        self._verify_all_labels()  # verify that all labels are strings

        if len(self._records) <= len(self._SETTINGS.label_schema) * 100:
            warnings.warn("OpenAI recommends at least 100 examples per class for training a classification model.")

        jsonl = []
        for rec in self._records:
            if rec.annotation is None:
                continue

            if rec.text is not None:
                prompt = rec.text
            elif rec.text is None and "text" in rec.inputs:
                prompt = rec.inputs["text"]
            else:
                prompt = ", ".join(f"{key}: {value}" for key, value in rec.inputs.items())
            prompt += separator  # needed for better performance

            if self._records[0].multi_label:
                completion = " ".join([str(self._SETTINGS.label2id[annotation]) for annotation in rec.annotation])
            else:
                completion = str(self._SETTINGS.label2id[rec.annotation])

            jsonl.append({"id": rec.id, "prompt": prompt, "completion": whitespace + completion})

        return jsonl

    def _infer_settings_from_records(self) -> TextClassificationSettings:
        all_labels = set()
        for record in self._records:
            if record.annotation is None:
                continue
            elif isinstance(record.annotation, str):
                all_labels.add(record.annotation)
            elif isinstance(record.annotation, list):
                for label in record.annotation:
                    all_labels.add(label)
            else:
                # this is highly unlikely
                raise TypeError("Record.annotation contains an unsupported type: {}".format(type(record.annotation)))
        all_labels = list(all_labels)
        all_labels.sort()

        warnings.warn(
            f"No label schema provided. Using all_labels: TextClassificationSettings({all_labels}). "
            "We recommend providing a `TextClassificationSettings()` or setting "
            "`rg.configure_dataset_settings()`/`rg.load_dataset_settings()` to ensure reproducibility."
        )
        return TextClassificationSettings(all_labels)

    def _verify_all_labels(self):
        all_labels = self._SETTINGS.label_schema
        for record in self._records:
            if record.annotation is None:
                continue
            elif isinstance(record.annotation, str):
                if record.annotation not in all_labels:
                    raise ValueError(f"Label {record.annotation} is not in the settings.label_schema: {all_labels}.")
            elif isinstance(record.annotation, list):
                for label in record.annotation:
                    if label not in all_labels:
                        raise ValueError(f"Label {label} is not in the settings.label_schema: {all_labels}.")
            else:
                # this is highly unlikely
                raise TypeError("Record.annotation contains an unsupported type: {}".format(type(record.annotation)))

        return all_labels


@_prepend_docstring(TokenClassificationRecord)
class DatasetForTokenClassification(DatasetBase):
    """
    Examples:
        >>> # Import/export records:
        >>> import argilla as rg
        >>> dataset = rg.DatasetForTokenClassification.from_pandas(my_dataframe)
        >>> dataset.to_datasets()
        >>>
        >>> # Looping over the dataset:
        >>> assert len(dataset) == 2
        >>> for record in dataset:
        ...     print(record)
        >>>
        >>> # Passing in a list of records:
        >>> import argilla as rg
        >>> records = [
        ...     rg.TokenClassificationRecord(text="example", tokens=["example"]),
        ...     rg.TokenClassificationRecord(text="another example", tokens=["another", "example"]),
        ... ]
        >>> dataset = rg.DatasetForTokenClassification(records)
        >>>
        >>> # Indexing into the dataset:
        >>> dataset[0]
        ... rg.TokenClassificationRecord(text="example", tokens=["example"])
        >>> dataset[0] = rg.TokenClassificationRecord(text="replace example", tokens=["replace", "example"])
    """

    _RECORD_TYPE = TokenClassificationRecord

    def __init__(self, records: Optional[List[TokenClassificationRecord]] = None):
        # we implement this to have more specific type hints
        super().__init__(records=records)

    @classmethod
    def _record_init_args(cls) -> List[str]:
        """Adds the `tags` argument to default record init arguments"""
        parent_fields = super(DatasetForTokenClassification, cls)._record_init_args()
        return parent_fields + ["tags"]  # compute annotation from tags

    @classmethod
    @requires_dependencies("datasets>1.17.0")
    def from_datasets(
        cls,
        dataset: "datasets.Dataset",
        text: Optional[str] = None,
        id: Optional[str] = None,
        tokens: Optional[str] = None,
        tags: Optional[str] = None,
        metadata: Optional[Union[str, List[str]]] = None,
    ) -> "DatasetForTokenClassification":
        """Imports records from a `datasets.Dataset`.

        Columns that are not supported are ignored.

        Args:
            dataset: A datasets Dataset from which to import the records.
            text: The field name used as record text. Default: `None`
            id: The field name used as record id. Default: `None`
            tokens: The field name used as record tokens. Default: `None`
            tags: The field name used as record tags. Default: `None`
            metadata: The field name used as record metadata. Default: `None`

        Returns:
            The imported records in a argilla Dataset.

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
        dataset, cols_to_be_joined = cls._prepare_dataset_and_column_mapping(
            dataset,
            dict(
                text=text,
                tokens=tokens,
                tags=tags,
                id=id,
                metadata=metadata,
            ),
        )

        records = []
        for row in dataset:
            # TODO: fails with a KeyError if no tokens column is present and no mapping is indicated
            if not row["tokens"]:
                warnings.warn("Ignoring row with no tokens.")
                continue

            if row.get("tags"):
                row["tags"] = cls._parse_datasets_column_with_classlabel(row["tags"], dataset.features["tags"])

            if row.get("prediction"):
                row["prediction"] = cls.__entities_to_tuple__(row["prediction"])

            if row.get("annotation"):
                row["annotation"] = cls.__entities_to_tuple__(row["annotation"])

            if cols_to_be_joined.get("metadata"):
                row["metadata"] = cls._join_datasets_columns_and_delete(row, cols_to_be_joined["metadata"])

            records.append(TokenClassificationRecord.parse_obj(row))

        return cls(records)

    @classmethod
    def from_pandas(
        # we implement this to have more specific type hints
        cls,
        dataframe: pd.DataFrame,
    ) -> "DatasetForTokenClassification":
        return super().from_pandas(dataframe)

    @requires_dependencies("datasets>1.17.0")
    def _prepare_for_training_with_transformers(
        self,
        train_size: Optional[float] = None,
        test_size: Optional[float] = None,
        seed: Optional[int] = None,
    ):
        import datasets

        has_annotations = False
        for rec in self._records:
            if rec.annotation is not None:
                has_annotations = True
                break

        if not has_annotations:
            return datasets.Dataset.from_dict({})

        class_tags = ["O"]
        class_tags.extend([f"{pre}-{label}" for label in sorted(self._verify_all_labels()) for pre in ["B", "I"]])
        class_tags = datasets.ClassLabel(names=class_tags)

        def spans2iob(example):
            span_utils = SpanUtils(example["text"], example["tokens"])
            entity_spans = self.__entities_to_tuple__(example["annotation"])
            tags = span_utils.to_tags(entity_spans)

            return class_tags.str2int(tags)

        ds = self.to_datasets().filter(self.__only_annotations__).map(lambda example: {"ner_tags": spans2iob(example)})
        new_features = ds.features.copy()
        new_features["ner_tags"] = datasets.Sequence(feature=class_tags)
        ds = ds.cast(new_features)
        ds = ds.remove_columns(set(ds.column_names) - set(["id", "tokens", "ner_tags"]))

        if test_size is not None and test_size != 0:
            ds = ds.train_test_split(train_size=train_size, test_size=test_size, seed=seed)

        return ds

    @requires_dependencies("spacy")
    def _prepare_for_training_with_spacy(self, nlp: "spacy.Language", records: List[Record]) -> "spacy.tokens.DocBin":
        from spacy.tokens import DocBin

        db = DocBin(store_user_data=True)

        # Creating the DocBin object as in https://spacy.io/usage/training#training-data
        for record in records:
            if record.annotation is None:
                continue

            doc = nlp.make_doc(record.text)
            doc.user_data["id"] = record.id
            entities = []

            for anno in record.annotation:
                span = doc.char_span(anno[1], anno[2], label=anno[0])
                # There is a misalignment between record tokenization and spaCy tokenization
                if span is None:
                    # TODO(@dcfidalgo): Do we want to warn and continue or should we stop the training set generation?
                    raise ValueError(
                        "The following annotation does not align with the tokens"
                        " produced by the provided spacy language model:"
                        f" {(anno[0], record.text[anno[1]:anno[2]])}, {list(doc)}"
                    )
                else:
                    entities.append(span)

            doc.ents = entities
            db.add(doc)

        return db

    def _prepare_for_training_with_spark_nlp(self, records: List[Record]) -> "pandas.DataFrame":
        for record in records:
            if record.id is None:
                record.id = str(uuid.uuid4())
        iob_doc_data = [
            [
                record.id,
                record.text,
                record.tokens,
                [token["tag"] for token in record.metrics["tokens"]],
            ]
            for record in records
            if record.annotation is not None
        ]

        return pd.DataFrame(iob_doc_data, columns=["id", "text", "token", "label"])

    def _prepare_for_training_with_openai(self, **kwargs) -> "datasets.Dataset":
        """Prepares the dataset for training using the "openai" framework.

        Args:
            **kwargs: Specific to the task of the dataset.

        Returns:
            A pd.DataFrame.
        """
        separator = OPENAI_SEPARATOR
        end_token = OPENAI_END_TOKEN
        whitespace = OPENAI_WHITESPACE
        self._verify_all_labels()

        if len(self._records) <= 500:
            warnings.warn("OpenAI recommends at least 500 examples for training a conditional generation model.")

        jsonl = []
        for rec in self._records:
            if rec.annotation is None:
                continue

            prompt = rec.text + separator  # needed for better performance

            completion = {}
            for label, start, end in rec.annotation:
                completion[rec.text[start:end]] = self._SETTINGS.label2id[label]

            completion = "\n".join([f"- {k} {v}" for k, v in completion.items()])
            completion = completion + end_token
            jsonl.append({"id": rec.id, "prompt": prompt, "completion": whitespace + completion})

        return jsonl

    def _infer_settings_from_records(self) -> TokenClassificationSettings:
        all_labels = set()
        for record in self._records:
            if record.annotation:
                for label, _, _ in record.annotation:
                    all_labels.add(label)
        all_labels = list(all_labels)
        all_labels.sort()
        warnings.warn(
            f"No label schema provided. Using all_labels: TokenClassificationSettings({all_labels}). "
            "We recommend providing a `TokenClassificationSettings()` or setting "
            "`rg.configure_dataset_settings()`/`rg.load_dataset_settings()` to ensure reproducibility."
        )
        return TokenClassificationSettings(all_labels)

    def _verify_all_labels(self) -> List[str]:
        all_labels = self._SETTINGS.label_schema
        for record in self._records:
            if record.annotation:
                for label, _, _ in record.annotation:
                    if label not in all_labels:
                        raise ValueError(f"Label {label} is not in the settings.label_schema: {all_labels}.")

        return all_labels

    def __only_annotations__(self, data) -> bool:
        return data["annotation"] is not None

    def _to_datasets_dict(self) -> Dict:
        """Helper method to put token classification records in a `datasets.Dataset`"""

        # create a dict first, where we make the necessary transformations
        def entities_to_dict(
            entities: Optional[List[Union[Tuple[str, int, int, float], Tuple[str, int, int]]]]
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
                ds_dict[key] = [entities_to_dict(rec.prediction) for rec in self._records]
            elif key == "annotation":
                ds_dict[key] = [entities_to_dict(rec.annotation) for rec in self._records]
            elif key == "id":
                ds_dict[key] = [None if rec.id is None else str(rec.id) for rec in self._records]
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
            else (ent["label"], ent["start"], ent["end"], ent["score"] or 0.0)
            for ent in entities
        ]

    @classmethod
    def _from_pandas(cls, dataframe: pd.DataFrame) -> "DatasetForTokenClassification":
        return cls([TokenClassificationRecord(**row) for row in dataframe.to_dict("records")])


@_prepend_docstring(Text2TextRecord)
class DatasetForText2Text(DatasetBase):
    """
    Examples:
        >>> # Import/export records:
        >>> import argilla as rg
        >>> dataset = rg.DatasetForText2Text.from_pandas(my_dataframe)
        >>> dataset.to_datasets()
        >>>
        >>> # Passing in a list of records:
        >>> records = [
        ...     rg.Text2TextRecord(text="example"),
        ...     rg.Text2TextRecord(text="another example"),
        ... ]
        >>> dataset = rg.DatasetForText2Text(records)
        >>> assert len(dataset) == 2
        >>>
        >>> # Looping over the dataset:
        >>> for record in dataset:
        ...     print(record)
        >>>
        >>> # Indexing into the dataset:
        >>> dataset[0]
        ... rg.Text2TextRecord(text="example"})
        >>> dataset[0] = rg.Text2TextRecord(text="replaced example")
    """

    _RECORD_TYPE = Text2TextRecord

    def __init__(self, records: Optional[List[Text2TextRecord]] = None):
        # we implement this to have more specific type hints
        super().__init__(records=records)

    @classmethod
    @requires_dependencies("datasets>1.17.0")
    def from_datasets(
        cls,
        dataset: "datasets.Dataset",
        text: Optional[str] = None,
        annotation: Optional[str] = None,
        metadata: Optional[Union[str, List[str]]] = None,
        id: Optional[str] = None,
    ) -> "DatasetForText2Text":
        """Imports records from a `datasets.Dataset`.

        Columns that are not supported are ignored.

        Args:
            dataset: A datasets Dataset from which to import the records.
            text: The field name used as record text. Default: `None`
            annotation: The field name used as record annotation. Default: `None`
            metadata: The field name used as record metadata. Default: `None`

        Returns:
            The imported records in a argilla Dataset.

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
        dataset, cols_to_be_joined = cls._prepare_dataset_and_column_mapping(
            dataset,
            dict(
                text=text,
                annotation=annotation,
                id=id,
                metadata=metadata,
            ),
        )

        records = []
        for row in dataset:
            if row.get("prediction"):
                row["prediction"] = cls._parse_prediction_field(row["prediction"])

            if cols_to_be_joined.get("metadata"):
                row["metadata"] = cls._join_datasets_columns_and_delete(row, cols_to_be_joined["metadata"])

            records.append(Text2TextRecord.parse_obj(row))

        return cls(records)

    @staticmethod
    def _parse_prediction_field(predictions: List[Union[str, Dict[str, str]]]):
        def extract_prediction(prediction: Union[str, Dict]):
            if isinstance(prediction, str):
                return prediction
            if prediction["score"] is None:
                return prediction["text"]
            return prediction["text"], prediction["score"]

        return [extract_prediction(pred) for pred in predictions]

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
                    [pred_to_dict(pred) for pred in rec.prediction] if rec.prediction is not None else None
                    for rec in self._records
                ]
            elif key == "id":
                ds_dict[key] = [None if rec.id is None else str(rec.id) for rec in self._records]
            elif key == "metadata":
                ds_dict[key] = [getattr(rec, key) or None for rec in self._records]
            else:
                ds_dict[key] = [getattr(rec, key) for rec in self._records]

        return ds_dict

    @classmethod
    def _from_pandas(cls, dataframe: pd.DataFrame) -> "DatasetForText2Text":
        return cls([Text2TextRecord(**row) for row in dataframe.to_dict("records")])

    @requires_dependencies("datasets>1.17.0")
    def _prepare_for_training_with_transformers(
        self,
        train_size: Optional[float] = None,
        test_size: Optional[float] = None,
        seed: Optional[int] = None,
    ):
        import datasets

        ds_dict = {"id": [], "text": [], "target": []}
        for rec in self._records:
            if rec.annotation is None:
                continue
            ds_dict["id"].append(rec.id)
            ds_dict["text"].append(rec.text)
            ds_dict["target"].append(rec.annotation)

        feature_dict = {
            "id": datasets.Value("string"),
            "text": datasets.Value("string"),
            "target": datasets.Value("string"),
        }

        ds = datasets.Dataset.from_dict(ds_dict, features=datasets.Features(feature_dict))

        if test_size is not None and test_size != 0:
            ds = ds.train_test_split(train_size=train_size, test_size=test_size, seed=seed)

        return ds

    def _prepare_for_training_with_spark_nlp(self, records: List[Record]) -> "pandas.DataFrame":
        spark_nlp_data = []
        for record in records:
            if record.annotation is None:
                continue
            if record.id is None:
                record.id = str(uuid.uuid4())
            text = record.text

            spark_nlp_data.append([record.id, text, record.annotation])

        return pd.DataFrame(spark_nlp_data, columns=["id", "text", "target"])

    def _prepare_for_training_with_openai(self, **kwargs) -> "datasets.Dataset":
        """Prepares the dataset for training using the "openai" framework.

        Args:
            **kwargs: Specific to the task of the dataset.

        Returns:
            A pd.DataFrame.
        """
        separator = OPENAI_SEPARATOR
        end_token = OPENAI_END_TOKEN
        whitespace = OPENAI_WHITESPACE
        if len(self._records) <= 500:
            warnings.warn("OpenAI recommends at least 500 examples for training a conditional generation model.")

        jsonl = []
        for rec in self._records:
            if rec.annotation is None:
                continue

            prompt = rec.text + separator  # needed for better performance
            completion = rec.annotation + end_token

            jsonl.append({"id": rec.id, "prompt": prompt, "completion": whitespace + completion})

        return jsonl


Dataset = Union[DatasetForTextClassification, DatasetForTokenClassification, DatasetForText2Text]


def read_datasets(dataset: "datasets.Dataset", task: Union[str, TaskType], **kwargs) -> Dataset:
    """Reads a datasets Dataset and returns a argilla Dataset

    Columns not supported by the :mod:`Record <argilla.client.models>` instance corresponding
    with the task are ignored.

    Args:
        dataset: Dataset to be read in.
        task: Task for the dataset, one of: ["TextClassification", "TokenClassification", "Text2Text"].
        **kwargs: Passed on to the task-specific ``DatasetFor*.from_datasets()`` method.

    Returns:
        A argilla dataset for the given task.

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

    raise NotImplementedError("Reading a datasets Dataset is not implemented for the given task!")


def read_pandas(dataframe: pd.DataFrame, task: Union[str, TaskType]) -> Dataset:
    """Reads a pandas DataFrame and returns a argilla Dataset

    Columns not supported by the :mod:`Record <argilla.client.models>` instance corresponding
    with the task are ignored.

    Args:
        dataframe: Dataframe to be read in.
        task: Task for the dataset, one of: ["TextClassification", "TokenClassification", "Text2Text"]

    Returns:
        A argilla dataset for the given task.

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
    raise NotImplementedError("Reading a pandas DataFrame is not implemented for the given task!")


class WrongRecordTypeError(Exception):
    pass
