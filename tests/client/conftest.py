import datetime
from typing import List

import pytest

import rubrix as rb
from rubrix.client.sdk.datasets.models import TaskType
from rubrix.client.sdk.text_classification.models import (
    CreationTextClassificationRecord,
    TextClassificationBulkData,
)
from rubrix.client.sdk.token_classification.models import (
    CreationTokenClassificationRecord,
    TokenClassificationBulkData,
)
from tests.server.test_helpers import client


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
            id="one",
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
            metrics={},
        ),
        rb.TextClassificationRecord(
            inputs={"text": "mock2", "context": "mock2"},
            prediction=[("a", 0.5), ("b", 0.2)],
            prediction_agent="mock2_pagent",
            id="two",
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
            metrics={},
        ),
        rb.TextClassificationRecord(
            inputs={"text": "mock3", "context": "mock3"},
            annotation="a",
            annotation_agent="mock_aagent",
            id="three",
            event_timestamp=datetime.datetime(2000, 3, 1),
            metadata={"mock_metadata": "mock"},
            metrics={},
        ),
        rb.TextClassificationRecord(
            inputs="mock",
            id=4,
            status="Validated",
            metrics={"mock_metric": ["B", "I", "O"]},
        ),
    ]


@pytest.fixture(scope="session")
def log_singlelabel_textclassification_records(
    request,
    singlelabel_textclassification_records,
) -> str:
    dataset_name = "singlelabel_textclassification_records"
    client.delete(f"/api/datasets/{dataset_name}")

    client.post(
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
            id="one",
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
            metrics={},
        ),
        rb.TextClassificationRecord(
            inputs={"text": "mock2", "context": "mock2"},
            prediction=[("a", 0.5), ("b", 0.2)],
            prediction_agent="mock2_pagent",
            multi_label=True,
            id="two",
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
            metrics={},
        ),
        rb.TextClassificationRecord(
            inputs={"text": "mock3", "context": "mock3"},
            annotation=["a"],
            annotation_agent="mock_aagent",
            multi_label=True,
            id="three",
            event_timestamp=datetime.datetime(2000, 3, 1),
            metadata={"mock_metadata": "mock"},
            metrics={},
        ),
        rb.TextClassificationRecord(
            inputs="mock",
            multi_label=True,
            id=4,
            status="Validated",
            metrics={"mock_metric": ["B", "I", "O"]},
        ),
    ]


@pytest.fixture(scope="session")
def log_multilabel_textclassification_records(
    request,
    multilabel_textclassification_records,
) -> str:
    dataset_name = "multilabel_textclassification_records"
    client.delete(f"/api/datasets/{dataset_name}")

    client.post(
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
            id="one",
            event_timestamp=datetime.datetime(2000, 1, 1),
            metadata={"mock_metadata": "mock"},
            status="Validated",
            metrics={},
        ),
        rb.TokenClassificationRecord(
            text="This is a second example",
            tokens=["This", "is", "a", "second", "example"],
            prediction=[("a", 5, 7), ("b", 8, 9)],
            prediction_agent="mock_pagent",
            id="two",
            event_timestamp=datetime.datetime(2000, 1, 1),
            metadata={"mock_metadata": "mock"},
            metrics={},
        ),
        rb.TokenClassificationRecord(
            text="This is a third example",
            tokens=["This", "is", "a", "third", "example"],
            annotation=[("a", 0, 4), ("b", 16, 23)],
            annotation_agent="mock_pagent",
            id="three",
            event_timestamp=datetime.datetime(2000, 1, 1),
            metadata={"mock_metadata": "mock"},
            metrics={},
        ),
        rb.TokenClassificationRecord(
            text="This is a third example",
            tokens=["This", "is", "a", "third", "example"],
            id=4,
            status="Discarded",
            metrics={"mock_metric": ["B", "I", "O"]},
        ),
    ]


@pytest.fixture(scope="session")
def log_tokenclassification_records(
    request,
    tokenclassification_records,
) -> str:
    dataset_name = "tokenclassification_records"
    client.delete(f"/api/datasets/{dataset_name}")

    client.post(
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
