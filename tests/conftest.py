import datetime
from typing import List

import pytest

import rubrix as rb
from rubrix.client.sdk.datasets.models import TaskType
from rubrix.client.sdk.text_classification.models import (
    CreationTextClassificationRecord,
    TextClassificationBulkData,
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
