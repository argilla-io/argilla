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

import datetime
from typing import TYPE_CHECKING, List

import argilla as rg
import pytest
from argilla.client.api import delete, log
from argilla.client.datasets import read_datasets
from argilla.client.models import (
    Text2TextRecord,
    TextClassificationRecord,
    TokenAttributions,
    TokenClassificationRecord,
)
from argilla.client.sdk.datasets.models import TaskType
from datasets import Dataset

if TYPE_CHECKING:
    from argilla.client.feedback.schemas import AllowedFieldTypes, AllowedQuestionTypes

from argilla.client.feedback.schemas import (
    FeedbackRecord,
    LabelQuestion,
    MultiLabelQuestion,
    RatingQuestion,
    TextField,
    TextQuestion,
)
from argilla.client.sdk.text2text.models import (
    CreationText2TextRecord,
    Text2TextBulkData,
)
from argilla.client.sdk.text_classification.models import (
    CreationTextClassificationRecord,
    TextClassificationBulkData,
)
from argilla.client.sdk.token_classification.models import (
    CreationTokenClassificationRecord,
    TokenClassificationBulkData,
)
from argilla.server.daos.backend.client_adapters.factory import ClientAdapterFactory
from argilla.server.settings import settings

try:
    client = ClientAdapterFactory.get(
        hosts=settings.elasticsearch,
        index_shards=settings.es_records_index_shards,
        ssl_verify=settings.elasticsearch_ssl_verify,
        ca_path=settings.elasticsearch_ca_path,
    )

    SUPPORTED_VECTOR_SEARCH = client.vector_search_supported
except Exception:
    SUPPORTED_VECTOR_SEARCH = False


@pytest.fixture(scope="session")
def supported_vector_search() -> bool:
    return SUPPORTED_VECTOR_SEARCH


@pytest.fixture
def gutenberg_spacy_ner(mocked_client):
    from datasets import load_dataset

    dataset = "gutenberg_spacy_ner"
    dataset_ds = load_dataset(
        "argilla/gutenberg_spacy-ner",
        split="train",
        # This revision does not includes the vectors info, so tests will pass
        revision="fff5f572e4cc3127f196f46ba3f9914c6fd0d763",
    )

    dataset_rb = read_datasets(dataset_ds, task="TokenClassification")

    delete(dataset)
    log(name=dataset, records=dataset_rb)

    return dataset


@pytest.fixture(scope="session")
def singlelabel_textclassification_records(
    request,
) -> List[TextClassificationRecord]:
    return [
        TextClassificationRecord(
            inputs={"text": "mock", "context": "mock"},
            prediction=[("a", 0.5), ("b", 0.5)],
            prediction_agent="mock_pagent",
            annotation="a",
            annotation_agent="mock_aagent",
            id=1,
            event_timestamp=datetime.datetime(2000, 1, 1),
            metadata={"mock_metadata": "mock"},
            explanation={"text": [TokenAttributions(token="mock", attributions={"a": 0.1, "b": 0.5})]},
            status="Validated",
        ),
        TextClassificationRecord(
            inputs={"text": "mock2", "context": "mock2"},
            prediction=[("a", 0.5), ("b", 0.2)],
            prediction_agent="mock2_pagent",
            id=2,
            event_timestamp=datetime.datetime(2000, 2, 1),
            metadata={"mock2_metadata": "mock2"},
            explanation={"text": [TokenAttributions(token="mock2", attributions={"a": 0.7, "b": 0.2})]},
            status="Default",
        ),
        TextClassificationRecord(
            inputs={"text": "mock2", "context": "mock2"},
            prediction=[("a", 0.5), ("b", 0.2)],
            prediction_agent="mock2_pagent",
            id=3,
            status="Discarded",
        ),
        TextClassificationRecord(
            inputs={"text": "mock3", "context": "mock3"},
            annotation="a",
            annotation_agent="mock_aagent",
            id="a",
            event_timestamp=datetime.datetime(2000, 3, 1),
            metadata={"mock_metadata": "mock"},
        ),
        TextClassificationRecord(
            text="mock",
            id="b",
            status="Default",
            metrics={"mock_metric": ["B", "I", "O"]},
        ),
    ]


@pytest.fixture
def log_singlelabel_textclassification_records(
    mocked_client,
    singlelabel_textclassification_records,
) -> str:
    dataset_name = "singlelabel_textclassification_records"
    mocked_client.delete(f"/api/datasets/{dataset_name}")
    mocked_client.post(
        f"/api/datasets/{dataset_name}/{TaskType.text_classification}:bulk",
        json=TextClassificationBulkData(
            tags={
                "env": "test",
                "task": TaskType.text_classification,
                "multi_label": False,
            },
            records=[
                CreationTextClassificationRecord.from_client(rec) for rec in singlelabel_textclassification_records
            ],
        ).dict(by_alias=True),
    )

    return dataset_name


@pytest.fixture(scope="session")
def multilabel_textclassification_records(request) -> List[TextClassificationRecord]:
    return [
        TextClassificationRecord(
            inputs={"text": "mock", "context": "mock"},
            prediction=[("a", 0.6), ("b", 0.4)],
            prediction_agent="mock_pagent",
            annotation=["a", "b"],
            annotation_agent="mock_aagent",
            multi_label=True,
            id=1,
            event_timestamp=datetime.datetime(2000, 1, 1),
            metadata={"mock_metadata": "mock"},
            explanation={"text": [TokenAttributions(token="mock", attributions={"a": 0.1, "b": 0.5})]},
            status="Validated",
        ),
        TextClassificationRecord(
            inputs={"text": "mock2", "context": "mock2"},
            prediction=[("a", 0.5), ("b", 0.2)],
            prediction_agent="mock2_pagent",
            multi_label=True,
            id=2,
            event_timestamp=datetime.datetime(2000, 2, 1),
            metadata={"mock2_metadata": "mock2"},
            explanation={"text": [TokenAttributions(token="mock2", attributions={"a": 0.7, "b": 0.2})]},
            status="Default",
        ),
        TextClassificationRecord(
            inputs={"text": "mock2", "context": "mock2"},
            prediction=[("a", 0.5), ("b", 0.2)],
            prediction_agent="mock2_pagent",
            multi_label=True,
            id=3,
            status="Discarded",
        ),
        TextClassificationRecord(
            inputs={"text": "mock3", "context": "mock3"},
            annotation=["a"],
            annotation_agent="mock_aagent",
            multi_label=True,
            id="a",
            event_timestamp=datetime.datetime(2000, 3, 1),
            metadata={"mock_metadata": "mock"},
            metrics={},
        ),
        TextClassificationRecord(
            text="mock",
            multi_label=True,
            id="b",
            status="Validated",
            metrics={"mock_metric": ["B", "I", "O"]},
        ),
    ]


@pytest.fixture
def log_multilabel_textclassification_records(
    mocked_client,
    multilabel_textclassification_records,
) -> str:
    dataset_name = "multilabel_textclassification_records"
    mocked_client.delete(f"/api/datasets/{dataset_name}")

    mocked_client.post(
        f"/api/datasets/{dataset_name}/{TaskType.text_classification}:bulk",
        json=TextClassificationBulkData(
            tags={
                "env": "test",
                "task": TaskType.text_classification,
                "multi_label": True,
            },
            records=[
                CreationTextClassificationRecord.from_client(rec) for rec in multilabel_textclassification_records
            ],
        ).dict(by_alias=True),
    )

    return dataset_name


@pytest.fixture(scope="session")
def tokenclassification_records(request) -> List[TokenClassificationRecord]:
    return [
        TokenClassificationRecord(
            text="This is an example",
            tokens=["This", "is", "an", "example"],
            prediction=[("a", 5, 7), ("b", 11, 18)],
            prediction_agent="mock_pagent",
            annotation=[("a", 5, 7)],
            annotation_agent="mock_aagent",
            id=1,
            event_timestamp=datetime.datetime(2000, 1, 1),
            metadata={"mock_metadata": "mock"},
            status="Validated",
        ),
        TokenClassificationRecord(
            text="This is a second example",
            tokens=["This", "is", "a", "second", "example"],
            prediction=[("a", 5, 7), ("b", 8, 9)],
            prediction_agent="mock_pagent",
            id=2,
            event_timestamp=datetime.datetime(2000, 1, 1),
            metadata={"mock_metadata": "mock"},
        ),
        TokenClassificationRecord(
            text="This is a secondd example",
            tokens=["This", "is", "a", "secondd", "example"],
            prediction=[("a", 5, 7), ("b", 8, 9, 0.5)],
            prediction_agent="mock_pagent",
            id=3,
            status="Default",
        ),
        TokenClassificationRecord(
            text="This is a third example",
            tokens=["This", "is", "a", "third", "example"],
            annotation=[("a", 0, 4), ("b", 16, 23)],
            annotation_agent="mock_pagent",
            id="a",
            event_timestamp=datetime.datetime(2000, 1, 1),
            metadata={"mock_metadata": "mock"},
            metrics={},
        ),
        TokenClassificationRecord(
            text="This is a third example",
            tokens=["This", "is", "a", "third", "example"],
            id="b",
            status="Discarded",
            metrics={"mock_metric": ["B", "I", "O"]},
        ),
    ]


@pytest.fixture
def log_tokenclassification_records(
    mocked_client,
    tokenclassification_records,
) -> str:
    dataset_name = "tokenclassification_records"
    mocked_client.delete(f"/api/datasets/{dataset_name}")

    mocked_client.post(
        f"/api/datasets/{dataset_name}/{TaskType.token_classification}:bulk",
        json=TokenClassificationBulkData(
            tags={
                "env": "test",
                "task": TaskType.token_classification,
            },
            records=[CreationTokenClassificationRecord.from_client(rec) for rec in tokenclassification_records],
        ).dict(by_alias=True),
    )

    return dataset_name


@pytest.fixture(scope="session")
def text2text_records(request) -> List[Text2TextRecord]:
    return [
        Text2TextRecord(
            text="This is an example",
            prediction=["Das ist ein Beispiel", "Esto es un ejemplo"],
            prediction_agent="mock_pagent",
            annotation="C'est une baguette",
            annotation_agent="mock_aagent",
            id=1,
            event_timestamp=datetime.datetime(2000, 1, 1),
            metadata={"mock_metadata": "mock"},
            status="Validated",
        ),
        Text2TextRecord(
            text="This is a one and a half example",
            prediction=[("Das ist ein Beispiell", 0.9), ("Esto es un ejemploo", 0.1)],
            prediction_agent="mock_pagent",
            id=2,
            event_timestamp=datetime.datetime(2000, 1, 1),
            metadata={"mock_metadata": "mock"},
        ),
        Text2TextRecord(
            text="This is a second example",
            prediction=["Esto es un ejemplooo", ("Das ist ein Beispielll", 0.9)],
            prediction_agent="mock_pagent",
            id=3,
            event_timestamp=datetime.datetime(2000, 1, 1),
            metadata={"mock_metadata": "mock"},
            metrics={},
        ),
        Text2TextRecord(
            text="This is a third example",
            annotation="C'est une très bonne baguette",
            annotation_agent="mock_pagent",
            id="a",
            event_timestamp=datetime.datetime(2000, 1, 1),
            metadata={"mock_metadata": "mock"},
            metrics={},
        ),
        Text2TextRecord(
            text="This is a forth example",
            id="b",
            status="Discarded",
            metrics={"mock_metric": ["B", "I", "O"]},
        ),
    ]


@pytest.fixture
def log_text2text_records(
    mocked_client,
    text2text_records,
) -> str:
    dataset_name = "text2text_records"
    mocked_client.delete(f"/api/datasets/{dataset_name}")

    mocked_client.post(
        f"/api/datasets/{dataset_name}/{TaskType.text2text}:bulk",
        json=Text2TextBulkData(
            tags={
                "env": "test",
                "task": TaskType.text2text,
            },
            records=[CreationText2TextRecord.from_client(rec) for rec in text2text_records],
        ).dict(by_alias=True),
    )

    return dataset_name


@pytest.fixture
def feedback_dataset_guidelines() -> str:
    return "These are the annotation guidelines."


@pytest.fixture
def feedback_dataset_fields() -> List["AllowedFieldTypes"]:
    return [
        TextField(name="text", required=True),
        TextField(name="label", required=True),
    ]


@pytest.fixture
def feedback_dataset_questions() -> List["AllowedQuestionTypes"]:
    return [
        TextQuestion(name="question-1", required=True),
        RatingQuestion(name="question-2", values=[0, 1], required=True),
        LabelQuestion(name="question-3", labels=["a", "b", "c"], required=True),
        MultiLabelQuestion(name="question-4", labels=["a", "b", "c"], required=True),
    ]


@pytest.fixture
def feedback_dataset_records() -> List[FeedbackRecord]:
    return [
        FeedbackRecord(
            fields={"text": "This is a positive example", "label": "positive"},
            responses=[
                {
                    "values": {
                        "question-1": {"value": "This is a response to question 1"},
                        "question-2": {"value": 1},
                        "question-3": {"value": "a"},
                        "question-4": {"value": ["a", "b"]},
                    },
                    "status": "submitted",
                },
            ],
            metadata={"unit": "test"},
            external_id="1",
        ),
        FeedbackRecord(
            fields={"text": "This is a negative example", "label": "negative"},
            metadata={"another unit": "test"},
            external_id="2",
        ),
        FeedbackRecord(
            fields={"text": "This is a negative example", "label": "negative"},
            responses=[
                {
                    "values": {
                        "question-1": {"value": "This is a response to question 1"},
                        "question-2": {"value": 0},
                        "question-3": {"value": "b"},
                        "question-4": {"value": ["b", "c"]},
                    },
                    "status": "submitted",
                }
            ],
            external_id="3",
        ),
        FeedbackRecord(
            fields={"text": "This is a negative example", "label": "negative"},
            responses=[
                {
                    "values": {
                        "question-1": {"value": "This is a response to question 1"},
                        "question-2": {"value": 0},
                        "question-3": {"value": "c"},
                        "question-4": {"value": ["a", "c"]},
                    },
                    "status": "submitted",
                }
            ],
            external_id="4",
        ),
        FeedbackRecord(
            fields={"text": "This is a negative example", "label": "negative"},
            responses=[
                {
                    "values": {
                        "question-1": {"value": "This is a response to question 1"},
                        "question-2": {"value": 1},
                        "question-3": {"value": "a"},
                        "question-4": {"value": ["a"]},
                    },
                    "status": "submitted",
                }
            ],
            external_id="5",
        ),
    ]


@pytest.fixture
def feedback_dataset_huggingface() -> Dataset:
    return Dataset.from_dict(
        {
            "text": ["This is a positive example"],
            "label": ["positive"],
            "question-1": [{"user_id": [None], "value": ["This is a response to question 1"], "status": ["submitted"]}],
            "question-2": [{"user_id": [None], "value": [1], "status": ["submitted"]}],
            "question-3": [{"user_id": [None], "value": ["a"], "status": ["submitted"]}],
            "question-4": [{"user_id": [None], "value": [["a", "b"]], "status": ["submitted"]}],
            "external_id": ["1"],
        }
    )
