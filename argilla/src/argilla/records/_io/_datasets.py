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

import warnings
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Dict, List, Union

from datasets import Dataset as HFDataset
from datasets import IterableDataset, Image, ClassLabel, Value

from argilla.records._io._generic import GenericIO
from argilla._helpers._media import pil_to_data_uri, uncast_image

if TYPE_CHECKING:
    from argilla.records import Record
    from argilla.datasets import Dataset


def _cast_images_as_urls(hf_dataset: "HFDataset", columns: List[str]) -> "HFDataset":
    """Cast the image features in the Hugging Face dataset as URLs.

    Parameters:
        hf_dataset (HFDataset): The Hugging Face dataset to cast.
        repo_id (str): The ID of the Hugging Face Hub repo.

    Returns:
        HFDataset: The Hugging Face dataset with image features cast as URLs.
    """

    for column in columns:
        # make an updated features object with the new column type
        features = hf_dataset.features.copy()
        features[column] = Value("string")
        # cast the column in batches
        hf_dataset = hf_dataset.map(
            function=lambda batch: {column: [pil_to_data_uri(sample) for sample in batch]},
            with_indices=False,
            batched=True,
            input_columns=[column],
            remove_columns=[column],
            features=features,
        )

    return hf_dataset


def _cast_classlabels_as_strings(hf_dataset: "HFDataset", columns: List[str]) -> "HFDataset":
    """Cast the class label features in the Hugging Face dataset as strings.

    Parameters:
        hf_dataset (HFDataset): The Hugging Face dataset to cast.
        columns (List[str]): The names of the columns containing the class label features.

    Returns:
        HFDataset: The Hugging Face dataset with class label features cast as strings.
    """
    for column in columns:
        features = hf_dataset.features.copy()
        features[column] = Value("string")
        hf_dataset = hf_dataset.map(
            lambda x: {column: hf_dataset.features[column].int2str(x[column])}, features=features
        )
    return hf_dataset


FEATURE_CASTERS = {
    Image: _cast_images_as_urls,
    ClassLabel: _cast_classlabels_as_strings,
}


def _uncast_uris_as_images(hf_dataset: "HFDataset", columns: List[str]) -> "HFDataset":
    """Cast the image features in the Hugging Face dataset as PIL images.

    Parameters:
        hf_dataset (HFDataset): The Hugging Face dataset to cast.
        columns (List[str]): The names of the columns containing the image features.

    Returns:
        HFDataset: The Hugging Face dataset with image features cast as PIL images.
    """

    for column in columns:
        features = hf_dataset.features.copy()
        features[column] = Image()
        casted_hf_dataset = hf_dataset.map(
            function=lambda batch: {column: [uncast_image(sample) for sample in batch]},
            with_indices=False,
            batched=True,
            input_columns=[column],
            remove_columns=[column],
            features=features,
        )
        try:
            casted_hf_dataset[0]
        except FileNotFoundError:
            warnings.warn(
                f"Image file not found for column {column}. Image will be persisted as string (URL, path, or base64)."
            )
            casted_hf_dataset = hf_dataset
    return casted_hf_dataset


def _uncast_label_questions_as_classlabels(hf_dataset: "HFDataset", columns: List[str]) -> "HFDataset":
    """Cast the class label features in the Hugging Face dataset as strings.

    Parameters:
        hf_dataset (HFDataset): The Hugging Face dataset to cast.
        columns (List[str]): The names of the columns containing the class label features.

    Returns:
        HFDataset: The Hugging Face dataset with class label features cast as strings.
    """
    for column in columns:
        column = f"{column}.suggestion"
        if column not in hf_dataset.column_names:
            continue
        values = list(hf_dataset.unique(column))
        features = hf_dataset.features.copy()
        features[column] = ClassLabel(names=values)
        hf_dataset = hf_dataset.map(
            function=lambda batch: {column: [values.index(sample) for sample in batch]},
            with_indices=False,
            batched=True,
            input_columns=[column],
            remove_columns=[column],
            features=features,
        )
    return hf_dataset


ATTRIBUTE_UNCASTERS = {
    "image": _uncast_uris_as_images,
    "label_selection": _uncast_label_questions_as_classlabels,
}


class HFDatasetsIO:
    @staticmethod
    def _is_hf_dataset(dataset: Any) -> bool:
        """Check if the object is a Hugging Face dataset.

        Parameters:
            dataset (Dataset): The object to check.

        Returns:
            bool: True if the object is a Hugging Face dataset, False otherwise.
        """
        return isinstance(dataset, HFDataset)

    @staticmethod
    def to_datasets(records: List["Record"], dataset: "Dataset") -> HFDataset:
        """
        Export the records to a Hugging Face dataset.

        Returns:
            The dataset containing the records.
        """
        record_dicts = GenericIO.to_dict(records, flatten=True)
        hf_dataset = HFDataset.from_dict(record_dicts)
        hf_dataset = HFDatasetsIO._uncast_argilla_attributes_to_datasets(hf_dataset, dataset.schema)
        return hf_dataset

    @staticmethod
    def _record_dicts_from_datasets(dataset: HFDataset) -> List[Dict[str, Union[str, float, int, list]]]:
        """Creates a dictionaries from a HF dataset that can be passed to DatasetRecords.add or DatasetRecords.update.

        Parameters:
            dataset (Dataset): The dataset containing the records.

        Returns:
            Generator[Dict[str, Union[str, float, int, list]], None, None]: A generator of dictionaries to be passed to DatasetRecords.add or DatasetRecords.update.
        """
        dataset = HFDatasetsIO._cast_datasets_features_to_argilla(hf_dataset=dataset)
        try:
            dataset: IterableDataset = dataset.to_iterable_dataset()
        except AttributeError:
            pass
        record_dicts = []
        for example in dataset:
            record_dicts.append(example)
        return record_dicts

    @staticmethod
    def _uncast_argilla_attributes_to_datasets(hf_dataset: "HFDataset", schema: Dict) -> List[str]:
        """Get the names of the Argilla fields that contain image data.

        Parameters:
            dataset (Dataset): The dataset to check.

        Returns:
            List[str]: The names of the Argilla fields that contain image data.
        """

        for attribute_type, uncaster in ATTRIBUTE_UNCASTERS.items():
            attributes = []
            for attribute_name, attribute_schema in schema.items():
                if hasattr(attribute_schema, "type") and attribute_schema.type == attribute_type:
                    attributes.append(attribute_name)
            if attributes:
                hf_dataset = uncaster(hf_dataset, attributes)
        return hf_dataset

    @staticmethod
    def _cast_datasets_features_to_argilla(hf_dataset: "HFDataset") -> List[str]:
        """Check if the Hugging Face dataset contains image features.

        Parameters:
            hf_dataset (HFDataset): The Hugging Face dataset to check.

        Returns:
            bool: True if the Hugging Face dataset contains image features, False otherwise.
        """
        casted_features = defaultdict(list)

        for name, feature in hf_dataset.features.items():
            if isinstance(feature, Image):
                casted_features[Image].append(name)
            if isinstance(feature, ClassLabel):
                casted_features[ClassLabel].append(name)

        for feature_type, columns in casted_features.items():
            hf_dataset = FEATURE_CASTERS[feature_type](hf_dataset, columns)

        return hf_dataset
