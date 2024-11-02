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

import warnings
from typing import List, Optional, Union

from argilla_v1.client.feedback.dataset.local.dataset import FeedbackDataset
from argilla_v1.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
from argilla_v1.client.feedback.schemas.records import FeedbackRecord
from argilla_v1.client.feedback.schemas.remote.records import RemoteFeedbackRecord
from argilla_v1.client.feedback.schemas.vector_settings import VectorSettings
from argilla_v1.utils.dependency import require_dependencies


class SentenceTransformersExtractor:
    """This class extracts a number of basic text descriptives from FeedbackDataset
    records using the TextDescriptives library and adds them as record metadata."""

    def __init__(
        self,
        model: Union["SentenceTransformer", str] = "TaylorAI/bge-micro-v2",
        show_progress: Optional[bool] = True,
        **kwargs,
    ):
        """
        Initialize the SentenceTransformersExtractor.

        Args:
            model (Optional[Union["SentenceTransformer", str]]): The SentenceTransformer model to use.
                Defaults to "TaylorAI/bge-micro-v2".
            show_progress (Optional[bool]): Whether to show the progress bar during encoding.
                Defaults to True.
            **kwargs: Additional keyword arguments to pass to the init of the SentenceTransformer model.

        Examples:
        >>> import argilla_v1 as rg
        >>> from argilla_v1.client.feedback.integrations.textdescriptives import SentenceTransformersExtractor
        >>> ds = rg.FeedbackDataset(...)
        >>> tde = SentenceTransformersExtractor()
        >>> updated_ds = tde.update_dataset(ds)
        >>> updated_records = tde.update_records(ds.records)
        """
        require_dependencies("sentence_transformers")
        from sentence_transformers import SentenceTransformer

        self.show_progress = show_progress
        if isinstance(model, str):
            self.model = SentenceTransformer(model, **kwargs)
        else:
            if kwargs:
                warnings.warn(
                    "kwargs for initializing SentenceTransformer are ignored when passing a SentenceTransformer instance."
                )
            self.model = model
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

    def _create_vector_settings(
        self,
        dataset: Union[FeedbackDataset, RemoteFeedbackDataset],
        fields: List[str],
        overwrite: bool = False,
    ) -> Union[FeedbackDataset, RemoteFeedbackDataset]:
        """
        Create or update vector settings for the given dataset.

        Args:
            dataset (Union[FeedbackDataset, RemoteFeedbackDataset]): The dataset to create or update vector settings for.
            fields (List[str]): The list of fields to create or update vector settings for.
            overwrite (bool, optional): Whether to overwrite existing vector settings if they have different dimensions. Defaults to False.

        Returns:
            Union[FeedbackDataset, RemoteFeedbackDataset]: The dataset with updated vector settings.
        """
        available_vector_settings = [setting.name for setting in dataset.vectors_settings]
        for field in fields:
            if field in available_vector_settings:
                setting = dataset.vector_settings_by_name(field)
                if overwrite:
                    if setting.dimensions != self.embedding_dim:
                        dataset.delete_vectors_settings(field)
                        dataset.add_vector_settings(
                            VectorSettings(
                                name=field,
                                dimensions=self.embedding_dim,
                            )
                        )
                else:
                    if setting.dimensions != self.embedding_dim:
                        raise ValueError(
                            f"Field {field} has a different embedding dimension ({dataset.vectors_settings[field].dimensions}) than the provided model ({self.embedding_dim})."
                        )
            else:
                dataset.add_vector_settings(
                    VectorSettings(
                        name=field,
                        dimensions=self.embedding_dim,
                    )
                )
        return dataset

    def _encode_single_field(
        self, records: List[Union[RemoteFeedbackRecord, FeedbackRecord]], field: str, overwrite: bool, **kwargs
    ) -> List[Union[FeedbackRecord, RemoteFeedbackRecord]]:
        """
        Encode a single field in the records with vectors.

        Args:
            records (List[Union[RemoteFeedbackRecord, FeedbackRecord]]): The list of records to encode.
            field (str): The field to encode.
            overwrite (bool): Whether to overwrite existing vectors for the field.
            **kwargs: Additional keyword arguments.

        Returns:
            List[Union[FeedbackRecord, RemoteFeedbackRecord]]: The updated list of records.
        """
        texts = []
        idxs = []
        # only
        for idx, record in enumerate(records):
            text = record.fields.get(field)
            if text:
                if field in record.vectors:
                    if overwrite:
                        texts.append(text)
                        idxs.append(idx)
                    else:
                        continue
                else:
                    texts.append(text)
                    idxs.append(idx)
        vectors = self.model.encode(texts, show_progress_bar=self.show_progress, **kwargs)
        for idx, vector in zip(idxs, vectors):
            records[idx].vectors[field] = vector.tolist()
        return records

    def update_records(
        self,
        records: List[Union[FeedbackRecord, RemoteFeedbackRecord]],
        fields: Optional[List[str]] = None,
        overwrite: Optional[bool] = False,
        **kwargs,
    ) -> List[Union[FeedbackRecord, RemoteFeedbackRecord]]:
        """
        Update the records by encoding fields with vectors.

        Args:
            records (List[Union[FeedbackRecord, RemoteFeedbackRecord]]): The records to update.
            fields (Optional[List[str]]): The fields to update. If None, use all available fields.
            overwrite (Optional[bool]): Whether to overwrite existing vectors. If None, use the value from
                the parent method. Defaults to None.
            **kwargs: Additional keyword arguments for encoding with sentence-transformers.

        Returns:
            List[Union[FeedbackRecord, RemoteFeedbackRecord]]: The updated records.

        Examples:
        >>> from argilla_v1.client.feedback.integrations.sentencetransformers import SentenceTransformersExtractor
        >>> records = [rg.FeedbackRecord(fields={"text": "This is a test."})]
        >>> tde = SentenceTransformersExtractor()
        >>> updated_records = tde.update_records(records)
        """
        available_fields = set()
        # unwrap potential records from RemoteFeedbackDataset
        modified_records = []
        for rec in records:
            modified_records.append(rec)
            for key in rec.fields:
                available_fields.add(key)
        if fields is None:
            fields = list(available_fields)
        # encode fields
        for field in fields:
            modified_records = self._encode_single_field(modified_records, field, overwrite, **kwargs)
        return modified_records

    def update_dataset(
        self,
        dataset: Union[FeedbackDataset, RemoteFeedbackDataset],
        fields: Optional[List[str]] = None,
        update_records: Optional[bool] = True,
        overwrite: Optional[bool] = False,
        **kwargs,
    ) -> Union[FeedbackDataset, RemoteFeedbackDataset]:
        """
        Update the dataset by encoding fields with vectors.

        Args:
            dataset (Union[FeedbackDataset, RemoteFeedbackDataset]): The dataset to update.
            fields (Optional[List[str]]): The fields to update. If None, use all available fields.
            update_records (bool): Whether to update the records with vectors. Defaults to True.
            overwrite (bool): Whether to overwrite existing vectors. Defaults to False.
            **kwargs: Additional keyword arguments for encoding with sentence-transformers.

        Returns:
            Union[FeedbackDataset, RemoteFeedbackDataset]: The updated dataset.

        Examples:
        >>> import argilla_v1 as rg
        >>> from argilla_v1.client.feedback.integrations.sentencetransformers import SentenceTransformersExtractor
        >>> dataset = rg.FeedbackDataset(...)
        >>> tde = SentenceTransformersExtractor()
        >>> updated_dataset = tde.update_dataset(dataset)
        """
        # If fields is None, use all fields
        if fields is None:
            fields = [field.name for field in dataset.fields]
        available_fields = [field.name for field in dataset.fields]
        if not all([field in available_fields for field in fields]):
            raise ValueError(f"Fields {fields} are not present in the dataset.")

        dataset = self._create_vector_settings(dataset=dataset, fields=fields, overwrite=overwrite)

        if update_records:
            records = self.update_records(records=dataset.records, fields=fields, overwrite=overwrite, **kwargs)
            if isinstance(dataset, RemoteFeedbackDataset):
                dataset.update_records(records)
        return dataset
