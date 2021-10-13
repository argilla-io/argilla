#  coding=utf-8
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

from rubrix.server.metrics.model import (
    DatasetMetric,
    DatasetMetricCreation,
)
from rubrix.server.tasks.text_classification import (
    TextClassificationBulkData,
    TextClassificationRecord,
)

from tests.server.test_helpers import client


def test_dataset_metrics():
    records = [
        TextClassificationRecord.parse_obj(data)
        for data in [
            {
                "id": 0,
                "inputs": {"text": "Some test data"},
                "multi_label": False,
                "metadata": {"textLength": len("Some test data")},
            },
            {
                "id": 1,
                "inputs": {"text": "Another data with different length"},
                "multi_label": False,
                "metadata": {"textLength": len("Another data with different length")},
            },
        ]
    ]
    request = TextClassificationBulkData(records=records)
    dataset = "test_get_dataset_metrics"

    assert client.delete(f"/api/datasets/{dataset}").status_code == 200

    assert (
        client.post(
            f"/api/datasets/{dataset}/TextClassification:bulk",
            json=request.dict(by_alias=True),
        ).status_code
        == 200
    )

    metric_id = "test-metric-001"
    assert (
        client.post(
            f"/api/datasets/{dataset}/metrics",
            json=DatasetMetricCreation(
                id=metric_id,
                name="A simple test metric",
                description="Large description for a test metric",
                field="metadata.textLength",
            ).dict(),
        ).status_code
        == 200
    )
    metrics = client.get(f"/api/datasets/{dataset}/metrics").json()

    assert len(metrics) == 1

    metrics = [DatasetMetric.parse_obj(m) for m in metrics]
    assert metrics[0].id == metric_id

    assert (
        client.delete(f"/api/datasets/{dataset}/metrics/{metric_id}").status_code == 200
    )
    assert (
        client.delete(f"/api/datasets/{dataset}/metrics/{metric_id}").status_code == 404
    )
