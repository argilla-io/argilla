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
from argilla_v1.client import singleton
from argilla_v1.client.api import log
from argilla_v1.client.models import TextClassificationRecord
from argilla_v1.metrics.text_classification import f1, f1_multilabel


def test_metrics_for_text_classification(mocked_client):
    dataset = "test_metrics_for_text_classification"

    log(
        [
            TextClassificationRecord(
                id=1,
                text="my first argilla example",
                prediction=[("spam", 0.8), ("ham", 0.2)],
                annotation=["spam"],
            ),
            TextClassificationRecord(
                id=2,
                inputs={"text": "my first argilla example"},
                prediction=[("ham", 0.8), ("spam", 0.2)],
                annotation=["ham"],
            ),
        ],
        name=dataset,
    )

    results = f1(dataset)
    assert results and results.data == {
        "f1_macro": 1.0,
        "f1_micro": 1.0,
        "ham_f1": 1.0,
        "ham_precision": 1.0,
        "ham_recall": 1.0,
        "ham_support": 1,
        "precision_macro": 1.0,
        "precision_micro": 1.0,
        "recall_macro": 1.0,
        "recall_micro": 1.0,
        "spam_f1": 1.0,
        "spam_precision": 1.0,
        "spam_recall": 1.0,
        "spam_support": 1,
    }
    results.visualize()

    results = f1_multilabel(dataset)
    assert results and results.data == {
        "f1_macro": 1.0,
        "f1_micro": 1.0,
        "ham_f1": 1.0,
        "ham_precision": 1.0,
        "ham_recall": 1.0,
        "ham_support": 1,
        "precision_macro": 1.0,
        "precision_micro": 1.0,
        "recall_macro": 1.0,
        "recall_micro": 1.0,
        "spam_f1": 1.0,
        "spam_precision": 1.0,
        "spam_recall": 1.0,
        "spam_support": 1,
    }
    results.visualize()


def test_f1_without_results(mocked_client):
    dataset = "test_f1_without_results"

    log(
        [
            TextClassificationRecord(
                id=1,
                text="my first argilla example",
            ),
            TextClassificationRecord(
                id=2,
                inputs={"text": "my first argilla example"},
            ),
        ],
        name=dataset,
    )

    results = f1(dataset)
    assert results
    assert results.data == {}
    results.visualize()


def test_dataset_labels_metric(mocked_client):
    dataset = "test_dataset_labels_metric"
    records = [
        TextClassificationRecord(
            id=i,
            text="aa" * i,
            prediction=[("A", 0.3)],
        )
        for i in range(0, 1000)
    ]

    records.extend(
        [
            TextClassificationRecord(
                id=i,
                text="aa" * i,
                annotation="B",
            )
            for i in range(1000, 2000)
        ]
    )
    records.extend(
        [
            TextClassificationRecord(
                id=i,
                text="aa" * i,
                prediction=[("C", 0.3)],
                annotation=["D"],
            )
            for i in range(2000, 3000)
        ]
    )
    log(
        name=dataset,
        records=records,
    )

    metric = singleton.active_api().compute_metric(
        dataset,
        metric="dataset_labels",
    )
    assert set(metric.results["labels"]) == {"C", "A", "B", "D"}
