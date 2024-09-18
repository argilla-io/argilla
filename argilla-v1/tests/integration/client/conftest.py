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
import random
from typing import TYPE_CHECKING, Generator, List

import pytest
from argilla_server.models import User
from argilla_v1 import SpanQuestion
from argilla_v1.client.api import log
from argilla_v1.client.datasets import read_datasets
from argilla_v1.client.feedback.dataset.local.dataset import FeedbackDataset
from argilla_v1.client.feedback.schemas import (
    FeedbackRecord,
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RankingValueSchema,
    RatingQuestion,
    TextField,
    TextQuestion,
)
from argilla_v1.client.feedback.schemas.metadata import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
)
from argilla_v1.client.feedback.schemas.vector_settings import VectorSettings
from argilla_v1.client.models import (
    Text2TextRecord,
    TextClassificationRecord,
    TokenAttributions,
    TokenClassificationRecord,
)
from argilla_v1.client.sdk.datasets.models import TaskType
from argilla_v1.client.sdk.text2text.models import (
    CreationText2TextRecord,
    Text2TextBulkData,
)
from argilla_v1.client.sdk.text_classification.models import (
    CreationTextClassificationRecord,
    TextClassificationBulkData,
)
from argilla_v1.client.sdk.token_classification.models import (
    CreationTokenClassificationRecord,
    TokenClassificationBulkData,
)
from argilla_v1.client.singleton import init
from datasets import Dataset

from tests.integration.utils import delete_ignoring_errors

if TYPE_CHECKING:
    from argilla_v1.client.feedback.schemas.types import (
        AllowedFieldTypes,
        AllowedMetadataPropertyTypes,
        AllowedQuestionTypes,
    )

random.seed(42)


@pytest.fixture
def gutenberg_spacy_ner(argilla_user: User) -> Generator[str, None, None]:
    from datasets import load_dataset

    dataset = "gutenberg_spacy_ner"
    dataset_ds = load_dataset(
        "argilla/gutenberg_spacy-ner",
        split="train",
        # This revision does not includes the vectors info, so tests will pass
        revision="fff5f572e4cc3127f196f46ba3f9914c6fd0d763",
    )

    dataset_rb = read_datasets(dataset_ds, task="TokenClassification")

    init(api_key=argilla_user.api_key, workspace=argilla_user.username)

    delete_ignoring_errors(dataset)
    log(name=dataset, records=dataset_rb)

    yield dataset

    delete_ignoring_errors(dataset, workspace=argilla_user.username)


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
        RatingQuestion(name="question-2", values=[1, 2], required=True),
        LabelQuestion(name="question-3", labels=["a", "b", "c"], required=True),
        MultiLabelQuestion(name="question-4", labels=["a", "b", "c"], required=True),
        RankingQuestion(name="question-5", values=["a", "b"], required=True),
        SpanQuestion(name="question-6", field="text", labels=["a", "b"], required=False),
    ]


@pytest.fixture
def feedback_dataset_metadata_properties() -> List["AllowedMetadataPropertyTypes"]:
    return [
        TermsMetadataProperty(name="metadata-property-1", values=["a", "b", "c"]),
        IntegerMetadataProperty(name="metadata-property-2", min=0, max=10),
        FloatMetadataProperty(name="metadata-property-3", min=0, max=10),
    ]


@pytest.fixture
def feedback_dataset_vectors_settings() -> List["VectorSettings"]:
    return [VectorSettings(name="vector-settings-1", dimensions=5)]


@pytest.fixture
def feedback_dataset(
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_metadata_properties: List["AllowedMetadataPropertyTypes"],
    feedback_dataset_vectors_settings: List["VectorSettings"],
) -> "FeedbackDataset":
    return FeedbackDataset(
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
        metadata_properties=feedback_dataset_metadata_properties,
        vectors_settings=feedback_dataset_vectors_settings,
    )


@pytest.fixture
def feedback_dataset_records() -> List[FeedbackRecord]:
    return [
        FeedbackRecord(
            fields={"text": "This is a positive example", "label": "positive"},
            responses=[
                {
                    "values": {
                        "question-1": {"value": "positive example"},
                        "question-2": {"value": 1},
                        "question-3": {"value": "a"},
                        "question-4": {"value": ["a", "b"]},
                        "question-5": {"value": [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}]},
                        "question-6": {"value": [{"start": 0, "end": 4, "label": "a"}]},
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
                        "question-1": {"value": "negative example"},
                        "question-2": {"value": 2},
                        "question-3": {"value": "b"},
                        "question-4": {"value": ["b", "c"]},
                        "question-5": {
                            "value": [RankingValueSchema(rank=1, value="a"), RankingValueSchema(rank=2, value="b")]
                        },
                        "question-6": {"value": [{"start": 0, "end": 4, "label": "a"}]},
                    },
                    "status": "submitted",
                }
            ],
            suggestions=[
                {
                    "question_name": "question-1",
                    "value": "This is a suggestion to question 1",
                    "type": "human",
                    "score": 0.0,
                    "agent": "agent-1",
                },
                {
                    "question_name": "question-2",
                    "value": 1,
                    "type": "human",
                    "score": 0.0,
                    "agent": "agent-1",
                },
                {
                    "question_name": "question-3",
                    "value": "a",
                    "type": "human",
                    "score": 0.0,
                    "agent": "agent-1",
                },
                {
                    "question_name": "question-4",
                    "value": ["a", "b"],
                    "type": "human",
                    "score": [0.0, 0.0],
                    "agent": "agent-1",
                },
                {
                    "question_name": "question-5",
                    "value": [RankingValueSchema(rank=1, value="a"), RankingValueSchema(rank=2, value="b")],
                    "type": "human",
                    "score": [0.0, 0.0],
                    "agent": "agent-1",
                },
                {
                    "question_name": "question-6",
                    "value": [{"start": 0, "end": 4, "label": "a"}],
                    "type": "human",
                    "score": [0.0],
                    "agent": "agent-1",
                },
            ],
            external_id="3",
        ),
        FeedbackRecord(
            fields={"text": "This is a negative example", "label": "negative"},
            responses=[
                {
                    "values": {
                        "question-1": {"value": "negative example"},
                        "question-2": {"value": 2},
                        "question-3": {"value": "c"},
                        "question-4": {"value": ["a", "c"]},
                        "question-5": {"value": [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}]},
                        "question-6": {"value": [{"start": 0, "end": 4, "label": "a"}]},
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
                        "question-1": {"value": "negative example"},
                        "question-2": {"value": 1},
                        "question-3": {"value": "a"},
                        "question-4": {"value": ["a"]},
                        "question-5": {"value": [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}]},
                    },
                    "status": "submitted",
                }
            ],
            external_id="5",
        ),
    ]


@pytest.fixture
def feedback_dataset_records_with_paired_suggestions() -> List[FeedbackRecord]:
    # This fixture contains the same records as `feedback_dataset_records` but with suggestions
    # for each question so that we can test the annotator metrics.
    # Generates 4 records from 3 annotators.

    import random
    import uuid

    q1_options = ["positive", "negative"]
    q2_options = [1, 2]
    q3_options = ["a", "b", "c"]
    q4_options = [["a", "b"], ["b", "c"], ["a", "c"]]
    q5_options = [
        [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}],
        [{"rank": 2, "value": "a"}, {"rank": 1, "value": "b"}],
        [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}],
    ]

    records = []

    for record_id in range(1, 5):
        responses = []
        for annotator_id in range(1, 4):
            # Make the random seed depend on the record_id and annotator_id for reproducibility.
            random.seed(123 + record_id + annotator_id)
            idx1 = random.randint(0, len(q1_options) - 1)
            random.seed(123 + record_id + annotator_id + 1)
            idx2 = random.randint(0, len(q2_options) - 1)
            random.seed(123 + record_id + annotator_id + 2)
            idx3 = random.randint(0, len(q3_options) - 1)
            random.seed(123 + record_id + annotator_id + 3)
            idx4 = random.randint(0, len(q4_options) - 1)
            random.seed(123 + record_id + annotator_id + 4)
            idx5 = random.randint(0, len(q5_options) - 1)

            response_q1 = q1_options[idx1]
            response_q2 = q2_options[idx2]
            response_q3 = q3_options[idx3]
            response_q4 = q4_options[idx4]
            response_q5 = q5_options[idx5]

            if annotator_id == 1:
                # Always answer like the suggestion
                suggestion_q1 = response_q1
                suggestion_q2 = response_q2
                suggestion_q3 = response_q3
                suggestion_q4 = response_q4
                suggestion_q5 = response_q5
            elif annotator_id == 2:
                # Never answer like the suggestion
                suggestion_q1 = q1_options[idx1 - 1]
                suggestion_q2 = q2_options[idx2 - 1]
                suggestion_q3 = q3_options[idx3 - 1]
                suggestion_q4 = q4_options[idx4 - 1]
                suggestion_q5 = q5_options[idx5 - 1]
            elif annotator_id == 3:
                # Sometimes answer like the suggestion
                if record_id % 2 == 0:
                    suggestion_q1 = response_q1
                    suggestion_q2 = response_q2
                    suggestion_q3 = response_q3
                    suggestion_q4 = response_q4
                    suggestion_q5 = response_q5
                else:
                    suggestion_q1 = q1_options[idx1 - 1]
                    suggestion_q2 = q2_options[idx2 - 1]
                    suggestion_q3 = q3_options[idx3 - 1]
                    suggestion_q4 = q4_options[idx4 - 1]
                    suggestion_q5 = q5_options[idx5 - 1]

            score_q1 = 0.0 if not isinstance(suggestion_q1, list) else [0.0] * len(suggestion_q1)
            score_q2 = 0.0 if not isinstance(suggestion_q2, list) else [0.0] * len(suggestion_q2)
            score_q3 = 0.0 if not isinstance(suggestion_q3, list) else [0.0] * len(suggestion_q3)
            score_q4 = 0.0 if not isinstance(suggestion_q4, list) else [0.0] * len(suggestion_q4)
            score_q5 = 0.0 if not isinstance(suggestion_q5, list) else [0.0] * len(suggestion_q5)

            responses.append(
                {
                    "values": {
                        "question-1": {"value": f"{response_q1} example"},
                        "question-2": {"value": response_q2},
                        "question-3": {"value": response_q3},
                        "question-4": {"value": response_q4},
                        "question-5": {"value": response_q5},
                    },
                    "status": "submitted",
                    "user_id": uuid.UUID(int=annotator_id),
                },
            )

        records.append(
            FeedbackRecord(
                fields={"text": f"This is a {response_q1} example", "label": f"{response_q1}"},
                responses=responses,
                suggestions=[
                    {
                        "question_name": "question-1",
                        "value": suggestion_q1,
                        "type": "human",
                        "score": score_q1,
                        "agent": f"agent-{annotator_id}",
                    },
                    {
                        "question_name": "question-2",
                        "value": suggestion_q2,
                        "type": "human",
                        "score": score_q2,
                        "agent": f"agent-{annotator_id}",
                    },
                    {
                        "question_name": "question-3",
                        "value": suggestion_q3,
                        "type": "human",
                        "score": score_q3,
                        "agent": f"agent-{annotator_id}",
                    },
                    {
                        "question_name": "question-4",
                        "value": suggestion_q4,
                        "type": "human",
                        "score": score_q4,
                        "agent": f"agent-{annotator_id}",
                    },
                    {
                        "question_name": "question-5",
                        "value": suggestion_q5,
                        "type": "human",
                        "score": score_q5,
                        "agent": f"agent-{annotator_id}",
                    },
                ],
                metadata={"unit": "test"},
                external_id=str(annotator_id + record_id),
            )
        )

    return records


@pytest.fixture
def feedback_dataset_records_with_metadata() -> List[FeedbackRecord]:
    records = []
    external_id = 0
    for status in ["submitted", "discarded"]:
        records.extend(
            [
                FeedbackRecord(
                    fields={"text": "This is a positive example", "label": "positive"},
                    responses=[
                        {
                            "values": {
                                "question-1": {"value": "positive example"},
                                "question-2": {"value": 1},
                                "question-3": {"value": "a"},
                                "question-4": {"value": ["a", "b"]},
                                "question-5": {"value": [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}]},
                            },
                            "status": status,
                        },
                    ],
                    metadata={"terms-metadata": "a", "integer-metadata": 2, "float-metadata": 2.0},
                    external_id=str(external_id + 1),
                ),
                FeedbackRecord(
                    fields={"text": "This is a negative example", "label": "negative"},
                    metadata={"terms-metadata": "a", "integer-metadata": 4, "float-metadata": 4.0},
                    external_id=str(external_id + 2),
                ),
                FeedbackRecord(
                    fields={"text": "This is a negative example", "label": "negative"},
                    responses=[
                        {
                            "values": {
                                "question-1": {"value": "negative example"},
                                "question-2": {"value": 1},
                                "question-3": {"value": "b"},
                                "question-4": {"value": ["b", "c"]},
                                "question-5": {"value": [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}]},
                            },
                            "status": status,
                        }
                    ],
                    metadata={"terms-metadata": "b", "integer-metadata": 4, "float-metadata": 4.0},
                    suggestions=[
                        {
                            "question_name": "question-1",
                            "value": "This is a suggestion to question 1",
                            "type": "human",
                            "score": 0.0,
                            "agent": "agent-1",
                        },
                        {
                            "question_name": "question-2",
                            "value": 1,
                            "type": "human",
                            "score": 0.0,
                            "agent": "agent-1",
                        },
                        {
                            "question_name": "question-3",
                            "value": "a",
                            "type": "human",
                            "score": 0.0,
                            "agent": "agent-1",
                        },
                        {
                            "question_name": "question-4",
                            "value": ["a", "b"],
                            "type": "human",
                            "score": [0.0, 0.0],
                            "agent": "agent-1",
                        },
                        {
                            "question_name": "question-5",
                            "value": [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}],
                            "type": "human",
                            "score": [0.0, 0.0],
                            "agent": "agent-1",
                        },
                    ],
                    external_id=str(external_id + 3),
                ),
                FeedbackRecord(
                    fields={"text": "This is a negative example", "label": "negative"},
                    responses=[
                        {
                            "values": {
                                "question-1": {"value": "negative example"},
                                "question-2": {"value": 1},
                                "question-3": {"value": "c"},
                                "question-4": {"value": ["a", "c"]},
                                "question-5": {"value": [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}]},
                            },
                            "status": status,
                        }
                    ],
                    metadata={"terms-metadata": "b", "integer-metadata": 5, "float-metadata": 4.0},
                    external_id=str(external_id + 4),
                ),
                FeedbackRecord(
                    fields={"text": "This is a negative example", "label": "negative"},
                    responses=[
                        {
                            "values": {
                                "question-1": {"value": "negative example"},
                                "question-2": {"value": 1},
                                "question-3": {"value": "a"},
                                "question-4": {"value": ["a"]},
                                "question-5": {"value": [{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}]},
                            },
                            "status": status,
                        }
                    ],
                    metadata={"terms-metadata": "c", "integer-metadata": 6, "float-metadata": 6.0},
                    external_id=str(external_id + 5),
                ),
            ]
        )
        external_id += 5

    return records


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
            "question-5": [
                {
                    "user_id": [None],
                    "value": [[{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}]],
                    "status": ["submitted"],
                }
            ],
            "question-1-suggestion": ["This is a suggestion to question 1"],
            "question-1-suggestion-metadata": [{"type": None, "score": None, "agent": None}],
            "question-2-suggestion": [1],
            "question-2-suggestion-metadata": [{"type": None, "score": None, "agent": None}],
            "question-3-suggestion": ["a"],
            "question-3-suggestion-metadata": [{"type": None, "score": None, "agent": None}],
            "question-4-suggestion": [["a", "b"]],
            "question-4-suggestion-metadata": [{"type": None, "score": None, "agent": None}],
            "question-5-suggestion": [[{"rank": 1, "value": "a"}, {"rank": 2, "value": "b"}]],
            "question-5-suggestion-metadata": [{"type": None, "score": None, "agent": None}],
            "external_id": ["1"],
        }
    )
