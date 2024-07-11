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
import argilla_v1
import argilla_v1.client.singleton
import pytest
from argilla_v1.client.api import log
from argilla_v1.client.models import TextClassificationRecord
from argilla_v1.metrics.commons import keywords, records_status, text_length

from tests.integration.utils import delete_ignoring_errors


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

    dataset_rb = argilla_v1.read_datasets(dataset_ds, task="TokenClassification")

    delete_ignoring_errors(dataset)

    argilla_v1.log(name=dataset, records=dataset_rb)

    return dataset


def test_status_distribution(mocked_client):
    dataset = "test_status_distribution"

    delete_ignoring_errors(dataset)

    log(
        [
            TextClassificationRecord(
                id=1,
                inputs={"text": "my first example"},
                prediction=[("spam", 0.8), ("ham", 0.2)],
                annotation=["spam"],
            ),
            TextClassificationRecord(
                id=2,
                inputs={"text": "my second example"},
                prediction=[("ham", 0.8), ("spam", 0.2)],
                annotation=["ham"],
                status="Default",
            ),
        ],
        name=dataset,
    )

    results = records_status(dataset)
    assert results
    assert results.data == {"Default": 1, "Validated": 1}
    results.visualize()


def test_text_length(mocked_client):
    dataset = "test_text_length"

    delete_ignoring_errors(dataset)

    log(
        [
            TextClassificationRecord(
                id=1,
                inputs={"text": "my first example"},
                prediction=[("spam", 0.8), ("ham", 0.2)],
                annotation=["spam"],
            ),
            TextClassificationRecord(
                id=2,
                inputs={"text": "my second example"},
                prediction=[("ham", 0.8), ("spam", 0.2)],
                annotation=["ham"],
                status="Default",
            ),
            TextClassificationRecord(
                id=3,
                inputs={"text": "simple text"},
                prediction=[("ham", 0.8), ("spam", 0.2)],
                annotation=["ham"],
            ),
        ],
        name=dataset,
    )

    results = text_length(dataset)
    assert results
    assert results.data == {
        "11.0": 1,
        "12.0": 0,
        "13.0": 0,
        "14.0": 0,
        "15.0": 0,
        "16.0": 1,
        "17.0": 1,
    }
    results.visualize()


def test_keywords_metrics(mocked_client, gutenberg_spacy_ner):
    results = keywords(name=gutenberg_spacy_ner)

    assert results.data == {
        "clock": 46,
        "come": 20,
        "day": 18,
        "even": 18,
        "four": 18,
        "go": 24,
        "little": 26,
        "make": 22,
        "midnight": 24,
        "morning": 20,
        "must": 20,
        "night": 20,
        "now": 26,
        "one": 32,
        "roger": 18,
        "said": 38,
        "take": 18,
        "three": 20,
        "time": 34,
        "two": 18,
    }

    assert keywords(name=gutenberg_spacy_ner) == keywords(name=gutenberg_spacy_ner, query="")

    with pytest.raises(AssertionError, match="size must be greater than 0"):
        keywords(name=gutenberg_spacy_ner, size=0)


def test_failing_metrics(argilla_user: "User"):
    argilla_v1.client.singleton.init(api_key=argilla_user.api_key, workspace=argilla_user.username)
    dataset_name = "test_failing_metrics"

    delete_ignoring_errors(dataset_name)

    argilla_v1.log(argilla_v1.TextClassificationRecord(text="This is a text, yeah!"), name=dataset_name)

    with pytest.raises(AssertionError, match="Metric missing-metric not found"):
        argilla_v1.client.singleton.active_client().compute_metric(name=dataset_name, metric="missing-metric")
