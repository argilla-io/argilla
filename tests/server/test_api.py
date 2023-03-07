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

import os

from argilla.server.apis.v0.models.text_classification import (
    TextClassificationBulkRequest,
    TextClassificationRecord,
)
from argilla.server.commons.models import TaskStatus, TaskType
from starlette.testclient import TestClient


def create_some_data_for_text_classification(
    client,
    name: str,
    n: int,
    with_vectors: bool = True,
):
    n = n or 10

    records = [
        TextClassificationRecord(**data)
        for idx in range(0, n, 2)
        for data in [
            {
                "id": idx,
                "inputs": {"data": "my data"},
                "multi_label": True,
                "metadata": {"field_one": "value one", "field_two": "value 2"},
                "status": TaskStatus.validated,
                "annotation": {
                    "agent": "test",
                    "labels": [
                        {"class": "Test"},
                        {"class": "Mocking"},
                    ],
                },
            },
            {
                "id": idx + 1,
                "inputs": {"data": "my data"},
                "multi_label": True,
                "metadata": {"field_one": "another value one", "field_two": "value 2"},
                "status": TaskStatus.validated,
                "prediction": {
                    "agent": "test",
                    "labels": [
                        {"class": "NoClass"},
                    ],
                },
                "annotation": {
                    "agent": "test",
                    "labels": [
                        {"class": "Test"},
                    ],
                },
            },
        ]
    ]
    vectors = [
        {
            "bert_cased": {
                "record_properties": ["data"],
                "value": [1.2, 2.3, 3.4, 4.5],
            },
        },
        {
            "bert_cased": {
                "record_properties": ["data"],
                "value": [1.2, 2.3, 3.4, 4.5],
            },
        },
    ] * n

    if with_vectors:
        for record, record_vectors in zip(records, vectors):
            record.vectors = record_vectors

    client.post(
        f"/api/datasets/{name}/{TaskType.text_classification}:bulk",
        json=TextClassificationBulkRequest(
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=records,
        ).dict(by_alias=True),
    )

    data = {}
    for vector_cfg in vectors:
        data.update(vector_cfg)

    return data


def uri_2_path(uri: str):
    from urllib.parse import urlparse

    p = urlparse(uri)
    return os.path.abspath(os.path.join(p.netloc, p.path))


def test_docs_redirect(test_client: TestClient):
    response = test_client.get("/docs", follow_redirects=False)
    assert response.status_code == 307
    assert response.next_request.url.path == "/api/docs"

    response = test_client.get("/api", follow_redirects=False)
    assert response.status_code == 307
    assert response.next_request.url.path == "/api/docs"
