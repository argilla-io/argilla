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

from typing import TYPE_CHECKING, Any, Dict, List, Union
from uuid import uuid4

from datasets import Dataset as HFDataset
from datasets import IterableDataset, Image

from argilla.records._io._generic import GenericIO
from argilla._helpers._media import pil_to_data_uri, uncast_image

if TYPE_CHECKING:
    from argilla.records import Record
    from argilla.datasets import Dataset


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
        image_fields = HFDatasetsIO._get_image_fields(schema=dataset.schema)
        if image_fields:
            hf_dataset = HFDatasetsIO._cast_uris_as_images(hf_dataset=hf_dataset, columns=image_fields)
        return hf_dataset

    @staticmethod
    def _record_dicts_from_datasets(dataset: HFDataset) -> List[Dict[str, Union[str, float, int, list]]]:
        """Creates a dictionaries from a HF dataset that can be passed to DatasetRecords.add or DatasetRecords.update.

        Parameters:
            dataset (Dataset): The dataset containing the records.

        Returns:
            Generator[Dict[str, Union[str, float, int, list]], None, None]: A generator of dictionaries to be passed to DatasetRecords.add or DatasetRecords.update.
        """
        media_features = HFDatasetsIO._get_image_features(dataset)
        if media_features:
            dataset = HFDatasetsIO._cast_images_as_urls(hf_dataset=dataset, columns=media_features)
        try:
            dataset: IterableDataset = dataset.to_iterable_dataset()
        except AttributeError:
            pass
        record_dicts = []
        for example in dataset:
            record_dicts.append(example)
        return record_dicts

    @staticmethod
    def _get_image_fields(schema: Dict) -> List[str]:
        """Get the names of the Argilla fields that contain image data.

        Parameters:
            dataset (Dataset): The dataset to check.

        Returns:
            List[str]: The names of the Argilla fields that contain image data.
        """
        return [field_name for field_name, field in schema.items() if field.type == "image"]

    @staticmethod
    def _get_image_features(dataset: "HFDataset") -> List[str]:
        """Check if the Hugging Face dataset contains image features.

        Parameters:
            hf_dataset (HFDataset): The Hugging Face dataset to check.

        Returns:
            bool: True if the Hugging Face dataset contains image features, False otherwise.
        """
        media_features = [name for name, feature in dataset.features.items() if isinstance(feature, Image)]
        return media_features

    @staticmethod
    def _cast_images_as_urls(hf_dataset: "HFDataset", columns: List[str]) -> "HFDataset":
        """Cast the image features in the Hugging Face dataset as URLs.

        Parameters:
            hf_dataset (HFDataset): The Hugging Face dataset to cast.
            repo_id (str): The ID of the Hugging Face Hub repo.

        Returns:
            HFDataset: The Hugging Face dataset with image features cast as URLs.
        """

        unique_identifier = uuid4().hex

        def batch_fn(batch):
            data_uris = [pil_to_data_uri(sample) for sample in batch]
            return {unique_identifier: data_uris}

        for column in columns:
            hf_dataset = hf_dataset.map(
                function=batch_fn,
                with_indices=False,
                batched=True,
                input_columns=[column],
                remove_columns=[column],
            )
            hf_dataset = hf_dataset.rename_column(original_column_name=unique_identifier, new_column_name=column)

        return hf_dataset

    @staticmethod
    def _cast_uris_as_images(hf_dataset: "HFDataset", columns: List[str]) -> "HFDataset":
        """Cast the image features in the Hugging Face dataset as PIL images.

        Parameters:
            hf_dataset (HFDataset): The Hugging Face dataset to cast.
            columns (List[str]): The names of the columns containing the image features.

        Returns:
            HFDataset: The Hugging Face dataset with image features cast as PIL images.
        """
        unique_identifier = uuid4().hex

        def batch_fn(batch):
            images = [uncast_image(sample) for sample in batch]
            return {unique_identifier: images}

        for column in columns:
            hf_dataset = hf_dataset.map(
                function=batch_fn,
                with_indices=False,
                batched=True,
                input_columns=[column],
                remove_columns=[column],
            )
            hf_dataset = hf_dataset.rename_column(original_column_name=unique_identifier, new_column_name=column)

        return hf_dataset
