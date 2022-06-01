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
import rubrix as rb
from rubrix.metrics.text_classification import f1, f1_multilabel


def test_metrics_for_text_classification(mocked_client):
    dataset = "test_metrics_for_text_classification"

    rb.log(
        [
            rb.TextClassificationRecord(
                id=1,
                text="my first rubrix example",
                prediction=[("spam", 0.8), ("ham", 0.2)],
                annotation=["spam"],
            ),
            rb.TextClassificationRecord(
                id=2,
                inputs={"text": "my first rubrix example"},
                prediction=[("ham", 0.8), ("spam", 0.2)],
                annotation=["ham"],
            ),
        ],
        name=dataset,
    )

    results = f1(dataset)
    assert results
    assert results.data == {
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
    assert results
    assert results.data == {
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

    rb.log(
        [
            rb.TextClassificationRecord(
                id=1,
                text="my first rubrix example",
            ),
            rb.TextClassificationRecord(
                id=2,
                inputs={"text": "my first rubrix example"},
            ),
        ],
        name=dataset,
    )

    results = f1(dataset)
    assert results
    assert results.data == {}
    results.visualize()
