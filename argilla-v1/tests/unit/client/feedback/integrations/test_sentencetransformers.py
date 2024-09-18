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

from typing import List
from unittest.mock import MagicMock

import numpy as np
import pytest
from argilla_v1.client.feedback.dataset.local.dataset import FeedbackDataset
from argilla_v1.client.feedback.integrations.sentencetransformers import SentenceTransformersExtractor
from argilla_v1.client.feedback.schemas.fields import TextField
from argilla_v1.client.feedback.schemas.questions import TextQuestion
from argilla_v1.client.feedback.schemas.records import FeedbackRecord
from argilla_v1.client.feedback.schemas.vector_settings import VectorSettings
from sentence_transformers import SentenceTransformer


@pytest.fixture(scope="function")
def records() -> List[FeedbackRecord]:
    return [
        FeedbackRecord(fields={"field_1": "This is a test", "field_2": "This is a test"}),
        FeedbackRecord(
            fields={
                "field_1": "This is a test",
            }
        ),
        FeedbackRecord(
            fields={"field_1": "This is a test", "field_2": "This is a test"},
        ),
    ]


@pytest.fixture(scope="function")
def dataset() -> FeedbackDataset:
    ds = FeedbackDataset(
        fields=[
            TextField(name="field_1"),
            TextField(name="field_2", required=False),
        ],
        questions=[
            TextQuestion(name="question_1"),
        ],
    )
    return ds


@pytest.fixture(scope="session")
def st_extractor() -> SentenceTransformersExtractor:
    model = SentenceTransformer("TaylorAI/bge-micro-v2")
    model.get_sentence_embedding_dimension = MagicMock(return_value=1)
    model.encode = MagicMock(return_value=np.array([1]))
    return SentenceTransformersExtractor(model=model)


@pytest.mark.usefixtures("st_extractor", "dataset", "records")
def test_st_extractor(
    st_extractor: SentenceTransformersExtractor, dataset: FeedbackDataset, records: List[FeedbackRecord]
):
    dataset.add_records(records)
    st_extractor = SentenceTransformersExtractor()
    assert isinstance(st_extractor.model, SentenceTransformer)
    assert st_extractor.embedding_dim == st_extractor.model.get_sentence_embedding_dimension()
    assert st_extractor.show_progress
    new_dataset = FeedbackDataset(
        fields=dataset.fields,
        questions=dataset.questions,
        vectors_settings=[VectorSettings(name="field_1", dimensions=st_extractor.embedding_dim)],
    )
    st_extractor._create_vector_settings = MagicMock(return_value=new_dataset)
    new_records = []
    for record in records:
        new_records.append(FeedbackRecord(fields=record.fields, vectors={"field_1": np.array([1]).tolist()}))
    st_extractor._encode_single_field = MagicMock(return_value=records)
    st_extractor.update_records(records, fields=["field_1"])
    st_extractor._encode_single_field.assert_called_once_with(records, "field_1", False)
    st_extractor.update_dataset(dataset, update_records=True)
    st_extractor._encode_single_field.call_count == len(dataset.fields) + 1
    st_extractor._create_vector_settings.call_count == len(dataset.fields)


@pytest.mark.fixtures("st_extractor", "dataset")
def test_create_vector_settings(st_extractor: SentenceTransformersExtractor, dataset: FeedbackDataset):
    dataset = st_extractor._create_vector_settings(dataset, fields=["field_1"])
    assert dataset.vectors_settings == [VectorSettings(name="field_1", dimensions=st_extractor.embedding_dim)]


@pytest.mark.fixtures("st_extractor", "records")
def test_encode_single_field(st_extractor: SentenceTransformersExtractor, records: List[FeedbackRecord]):
    records = st_extractor._encode_single_field(records=records, field="field_1", overwrite=False)
    assert records[0].vectors["field_1"] == np.array([1])


@pytest.mark.fixtures("st_extractor")
def test_update_dataset_with_invalid_fields(st_extractor: SentenceTransformersExtractor):
    dataset = FeedbackDataset(
        fields=[TextField(name="text")],
        questions=[TextQuestion(name="question")],
    )
    with pytest.raises(ValueError):
        st_extractor.update_dataset(dataset, fields=["my_fake_field"])
