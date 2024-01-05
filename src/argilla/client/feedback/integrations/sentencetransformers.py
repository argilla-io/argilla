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

from sentence_transformers import SentenceTransformer

from argilla.client.feedback.dataset.local.dataset import FeedbackDataset
from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
from argilla.client.feedback.schemas.records import FeedbackRecord
from argilla.client.feedback.schemas.remote.records import RemoteFeedbackRecord
from argilla.client.feedback.schemas.vector_settings import VectorSettings
from argilla.utils.dependency import require_dependencies


class SentenceTransformersExtractor:
    """This class extracts a number of basic text descriptives from FeedbackDataset
    records using the TextDescriptives library and adds them as record metadata."""

    def __init__(
        self,
        model: Optional[Union[SentenceTransformer, str]] = "TaylorAI/bge-micro-v2",
        fields: Optional[List[str]] = None,
        show_progress: Optional[bool] = True,
        **kwargs,
    ):
        require_dependencies("sentence_transformers")
        self.fields = fields
        self.show_progress = show_progress
        if isinstance(model, str):
            self.model = SentenceTransformer(model, **kwargs)
        else:
            if kwargs:
                warnings.warn(
                    "kwargs for initializing SentenceTransformer are ignored when passing a SentenceTransformer instance"
                )
            self.model = model
        self.embedding_dim = self.model.encode(["sample sentence"])[0].shape[0]

    def _create_vector_settings(
        self, dataset: Union[FeedbackDataset, RemoteFeedbackDataset], overwrite: bool = False
    ) -> Union[FeedbackDataset, RemoteFeedbackDataset]:
        for field in self.fields:
            if dataset.vector_settings_by_name(field):
                if overwrite:
                    if dataset.vectors_settings[field].dimensions != self.embedding_dim:
                        dataset.delete_vectors_settings(field)
                        dataset.add_vector_settings(
                            VectorSettings(
                                name=field,
                                dimensions=self.embedding_dim,
                            )
                        )
                else:
                    setting = dataset.vector_settings_by_name(field)
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
        fields: List[str],
        overwrite: Optional[bool] = None,
        **kwargs,
    ) -> List[Union[FeedbackRecord, RemoteFeedbackRecord]]:
        self.fields = fields
        # unwrap potential records from RemoteFeedbackDataset
        modified_records = []
        for record in records:
            modified_records.append(record)
        # encode fields
        for field in fields:
            modified_records = self._encode_single_field(modified_records, field, overwrite, **kwargs)
        return modified_records

    def update_dataset(
        self,
        dataset: Union[FeedbackDataset, RemoteFeedbackDataset],
        fields: Optional[List[str]] = None,
        include_records: bool = True,
        overwrite: bool = False,
        **kwargs,
    ) -> Union[FeedbackDataset, RemoteFeedbackDataset]:
        if overwrite and not include_records:
            raise ValueError("Cannot overwrite metadata properties without including records.")
        if not isinstance(dataset, (FeedbackDataset, RemoteFeedbackDataset)):
            raise ValueError(
                f"Provided object is of `type={type(dataset)}` while only `type=FeedbackDataset` or `type=RemoteFeedbackDataset` are allowed."
            )
        # If fields is None, use all fields
        if fields:
            self.fields = fields
        if not self.fields:
            self.fields = [field.name for field in dataset.fields]
        else:
            for field in self.fields:
                if field not in [field.name for field in dataset.fields]:
                    raise ValueError(f"Field {field} is not present in the dataset.")

        dataset = self._create_vector_settings(dataset=dataset, overwrite=overwrite)

        if include_records:
            records = self.update_records(records=dataset.records, fields=self.fields, overwrite=overwrite, **kwargs)
            if isinstance(dataset, RemoteFeedbackDataset):
                print(records[0].vectors)
                dataset.update_records(records)
        return dataset
