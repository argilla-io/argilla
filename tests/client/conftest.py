import datetime
from typing import List

import pytest

import rubrix as rb
from rubrix.client.sdk.datasets.models import TaskType
from rubrix.client.sdk.text2text.models import (
    CreationText2TextRecord,
    Text2TextBulkData,
)
from rubrix.client.sdk.text_classification.models import (
    CreationTextClassificationRecord,
    TextClassificationBulkData,
)
from rubrix.client.sdk.token_classification.models import (
    CreationTokenClassificationRecord,
    TokenClassificationBulkData,
)


@pytest.fixture(scope="session")
def singlelabel_textclassification_records(
    request,
) -> List[rb.TextClassificationRecord]:
    return [
        rb.TextClassificationRecord(
            inputs={"text": "mock", "context": "mock"},
            prediction=[("a", 0.5), ("b", 0.5)],
            prediction_agent="mock_pagent",
            annotation="a",
            annotation_agent="mock_aagent",
            id=1,
            event_timestamp=datetime.datetime(2000, 1, 1),
            metadata={"mock_metadata": "mock"},
            explanation={
                "text": [
                    rb.TokenAttributions(
                        token="mock", attributions={"a": 0.1, "b": 0.5}
                    )
                ]
            },
            status="Validated",
        ),
        rb.TextClassificationRecord(
            inputs={"text": "mock2", "context": "mock2"},
            prediction=[("a", 0.5), ("b", 0.2)],
            prediction_agent="mock2_pagent",
            id=2,
            event_timestamp=datetime.datetime(2000, 2, 1),
            metadata={"mock2_metadata": "mock2"},
            explanation={
                "text": [
                    rb.TokenAttributions(
                        token="mock2", attributions={"a": 0.7, "b": 0.2}
                    )
                ]
            },
            status="Default",
        ),
        rb.TextClassificationRecord(
            inputs={"text": "mock2", "context": "mock2"},
            prediction=[("a", 0.5), ("b", 0.2)],
            prediction_agent="mock2_pagent",
            id=3,
            status="Discarded",
        ),
        rb.TextClassificationRecord(
            inputs={"text": "mock3", "context": "mock3"},
            annotation="a",
            annotation_agent="mock_aagent",
            id="a",
            event_timestamp=datetime.datetime(2000, 3, 1),
            metadata={"mock_metadata": "mock"},
        ),
        rb.TextClassificationRecord(
            inputs="mock",
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
                CreationTextClassificationRecord.from_client(rec)
                for rec in singlelabel_textclassification_records
            ],
        ).dict(by_alias=True),
    )

    return dataset_name


@pytest.fixture(scope="session")
def multilabel_textclassification_records(request) -> List[rb.TextClassificationRecord]:
    return [
        rb.TextClassificationRecord(
            inputs={"text": "mock", "context": "mock"},
            prediction=[("a", 0.6), ("b", 0.4)],
            prediction_agent="mock_pagent",
            annotation=["a", "b"],
            annotation_agent="mock_aagent",
            multi_label=True,
            id=1,
            event_timestamp=datetime.datetime(2000, 1, 1),
            metadata={"mock_metadata": "mock"},
            explanation={
                "text": [
                    rb.TokenAttributions(
                        token="mock", attributions={"a": 0.1, "b": 0.5}
                    )
                ]
            },
            status="Validated",
        ),
        rb.TextClassificationRecord(
            inputs={"text": "mock2", "context": "mock2"},
            prediction=[("a", 0.5), ("b", 0.2)],
            prediction_agent="mock2_pagent",
            multi_label=True,
            id=2,
            event_timestamp=datetime.datetime(2000, 2, 1),
            metadata={"mock2_metadata": "mock2"},
            explanation={
                "text": [
                    rb.TokenAttributions(
                        token="mock2", attributions={"a": 0.7, "b": 0.2}
                    )
                ]
            },
            status="Default",
        ),
        rb.TextClassificationRecord(
            inputs={"text": "mock2", "context": "mock2"},
            prediction=[("a", 0.5), ("b", 0.2)],
            prediction_agent="mock2_pagent",
            multi_label=True,
            id=3,
            status="Discarded",
        ),
        rb.TextClassificationRecord(
            inputs={"text": "mock3", "context": "mock3"},
            annotation=["a"],
            annotation_agent="mock_aagent",
            multi_label=True,
            id="a",
            event_timestamp=datetime.datetime(2000, 3, 1),
            metadata={"mock_metadata": "mock"},
            metrics={},
        ),
        rb.TextClassificationRecord(
            inputs="mock",
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
                CreationTextClassificationRecord.from_client(rec)
                for rec in multilabel_textclassification_records
            ],
        ).dict(by_alias=True),
    )

    return dataset_name


@pytest.fixture(scope="session")
def tokenclassification_records(request) -> List[rb.TokenClassificationRecord]:
    return [
        rb.TokenClassificationRecord(
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
        rb.TokenClassificationRecord(
            text="This is a second example",
            tokens=["This", "is", "a", "second", "example"],
            prediction=[("a", 5, 7), ("b", 8, 9)],
            prediction_agent="mock_pagent",
            id=2,
            event_timestamp=datetime.datetime(2000, 1, 1),
            metadata={"mock_metadata": "mock"},
        ),
        rb.TokenClassificationRecord(
            text="This is a secondd example",
            tokens=["This", "is", "a", "secondd", "example"],
            prediction=[("a", 5, 7), ("b", 8, 9, 0.5)],
            prediction_agent="mock_pagent",
            id=3,
            status="Default",
        ),
        rb.TokenClassificationRecord(
            text="This is a third example",
            tokens=["This", "is", "a", "third", "example"],
            annotation=[("a", 0, 4), ("b", 16, 23)],
            annotation_agent="mock_pagent",
            id="a",
            event_timestamp=datetime.datetime(2000, 1, 1),
            metadata={"mock_metadata": "mock"},
            metrics={},
        ),
        rb.TokenClassificationRecord(
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
            records=[
                CreationTokenClassificationRecord.from_client(rec)
                for rec in tokenclassification_records
            ],
        ).dict(by_alias=True),
    )

    return dataset_name


@pytest.fixture(scope="session")
def text2text_records(request) -> List[rb.Text2TextRecord]:
    return [
        rb.Text2TextRecord(
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
        rb.Text2TextRecord(
            text="This is a one and a half example",
            prediction=[("Das ist ein Beispiell", 0.9), ("Esto es un ejemploo", 0.1)],
            prediction_agent="mock_pagent",
            id=2,
            event_timestamp=datetime.datetime(2000, 1, 1),
            metadata={"mock_metadata": "mock"},
        ),
        rb.Text2TextRecord(
            text="This is a second example",
            prediction=["Esto es un ejemplooo", ("Das ist ein Beispielll", 0.9)],
            prediction_agent="mock_pagent",
            id=3,
            event_timestamp=datetime.datetime(2000, 1, 1),
            metadata={"mock_metadata": "mock"},
            metrics={},
        ),
        rb.Text2TextRecord(
            text="This is a third example",
            annotation="C'est une très bonne baguette",
            annotation_agent="mock_pagent",
            id="a",
            event_timestamp=datetime.datetime(2000, 1, 1),
            metadata={"mock_metadata": "mock"},
            metrics={},
        ),
        rb.Text2TextRecord(
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
            records=[
                CreationText2TextRecord.from_client(rec) for rec in text2text_records
            ],
        ).dict(by_alias=True),
    )

    return dataset_name
