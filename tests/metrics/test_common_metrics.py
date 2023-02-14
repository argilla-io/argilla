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
import argilla
import argilla as ar
import pytest
from argilla.metrics.commons import keywords, records_status, text_length


@pytest.fixture
def gutenberg_spacy_ner(mocked_client):
    from datasets import load_dataset

    dataset = "gutenberg_spacy_ner"
    # TODO(@frascuchon): Move dataset to new organization
    dataset_ds = load_dataset(
        "rubrix/gutenberg_spacy-ner",
        split="train",
    )

    dataset_rb = argilla.read_datasets(dataset_ds, task="TokenClassification")

    argilla.delete(dataset)
    argilla.log(name=dataset, records=dataset_rb)

    return dataset


def test_status_distribution(mocked_client):
    dataset = "test_status_distribution"

    ar.delete(dataset)

    ar.log(
        [
            ar.TextClassificationRecord(
                id=1,
                inputs={"text": "my first example"},
                prediction=[("spam", 0.8), ("ham", 0.2)],
                annotation=["spam"],
            ),
            ar.TextClassificationRecord(
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

    ar.delete(dataset)

    ar.log(
        [
            ar.TextClassificationRecord(
                id=1,
                inputs={"text": "my first example"},
                prediction=[("spam", 0.8), ("ham", 0.2)],
                annotation=["spam"],
            ),
            ar.TextClassificationRecord(
                id=2,
                inputs={"text": "my second example"},
                prediction=[("ham", 0.8), ("spam", 0.2)],
                annotation=["ham"],
                status="Default",
            ),
            ar.TextClassificationRecord(
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

    assert keywords(name=gutenberg_spacy_ner) == keywords(
        name=gutenberg_spacy_ner, query=""
    )

    with pytest.raises(AssertionError, match="size must be greater than 0"):
        keywords(name=gutenberg_spacy_ner, size=0)
