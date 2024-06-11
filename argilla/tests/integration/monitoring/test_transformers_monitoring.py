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
from time import sleep
from typing import List, Union

import argilla_v1
import pytest
from argilla_v1.client.models import TextClassificationRecord

from tests.integration.utils import delete_ignoring_errors


def test_classifier_monitoring_with_all_scores(
    mocked_client,
    classifier_monitor_all_scores,
    classifier_dataset,
):
    delete_ignoring_errors(classifier_dataset)

    expected_text = "This is a text, yeah"
    classifier_monitor_all_scores(expected_text)

    sleep(1)  # wait for the consumer time
    ds = argilla_v1.load(classifier_dataset)
    df = ds.to_pandas()
    assert len(df) == 1
    record = TextClassificationRecord.parse_obj(df.to_dict(orient="records")[0])
    assert record.inputs == {"text": expected_text}
    assert len(record.prediction) > 1


def test_classifier_monitoring(mocked_client, classifier_monitor, classifier_dataset):
    delete_ignoring_errors(classifier_dataset)

    expected_text = "This is a text, yeah"
    classifier_monitor(expected_text)

    sleep(1)  # wait for the consumer time
    ds = argilla_v1.load(classifier_dataset)
    df = ds.to_pandas()
    assert len(df) == 1
    record = TextClassificationRecord.parse_obj(df.to_dict(orient="records")[0])
    assert record.inputs == {"text": expected_text}
    assert len(record.prediction) == 1

    delete_ignoring_errors(classifier_dataset)
    texts = ["This is a text", "And another text here"]
    classifier_monitor(texts)

    sleep(1)  # wait for the consumer time
    ds = argilla_v1.load(classifier_dataset)
    df = ds.to_pandas()
    assert len(df) == 2
    assert set([r["text"] for r in df.inputs.values.tolist()]) == set(texts)

    delete_ignoring_errors(classifier_dataset)
    classifier_monitor(expected_text, metadata={"some": "metadata"})

    sleep(1)  # wait for the consumer time
    ds = argilla_v1.load(classifier_dataset)
    df = ds.to_pandas()
    assert len(df) == 1
    assert df.metadata.values.tolist()[0] == {"some": "metadata"}


@pytest.fixture
def classifier_dataset():
    return "classifier_dataset"


@pytest.fixture
def classifier_monitor_all_scores(
    sentiment_classifier_all_scores,
    classifier_dataset,
    monkeypatch,
):
    monitor = argilla_v1.monitor(
        sentiment_classifier_all_scores,
        dataset=classifier_dataset,
        sample_rate=1.0,
        log_interval=0.5,
    )

    return monitor


@pytest.fixture
def classifier_monitor(
    sentiment_classifier,
    classifier_dataset,
    monkeypatch,
):
    monitor = argilla_v1.monitor(
        sentiment_classifier,
        dataset=classifier_dataset,
        sample_rate=1.0,
        log_interval=0.5,
    )
    return monitor


@pytest.fixture(scope="session")
def sentiment_classifier():
    from transformers import pipeline

    return pipeline(
        model="distilbert-base-uncased-finetuned-sst-2-english",
        task="sentiment-analysis",
        return_all_scores=False,
    )


@pytest.fixture(scope="session")
def sentiment_classifier_all_scores():
    from transformers import pipeline

    return pipeline(
        model="distilbert-base-uncased-finetuned-sst-2-english",
        task="sentiment-analysis",
        return_all_scores=True,
    )


@pytest.fixture(scope="session")
def zero_shot_classifier():
    from transformers import pipeline

    return pipeline(
        "zero-shot-classification",
        model="Recognai/bert-base-spanish-wwm-cased-xnli",
    )


def zero_shot_inputs():
    return [
        (
            "El autor se perfila, a los 50 años de su muerte, como uno de los grandes de su siglo",
            ["cultura", "sociedad", "economia", "salud", "deportes"],
            "Este ejemplo es {}.",
        )
    ]


@pytest.fixture()
def dataset():
    return "zero_shot_dataset"


@pytest.fixture
def mocked_monitor(dataset, monkeypatch, zero_shot_classifier):
    monitor = argilla_v1.monitor(
        zero_shot_classifier,
        dataset=dataset,
        sample_rate=1.0,
        log_interval=0.5,
    )

    return monitor


def check_zero_shot_results(
    predictions,
    zero_shot_classifier,
    dataset: str,
    text: Union[str, List[str]],
    labels: List[str],
    hypothesis: str,
    multi_label: bool = False,
):
    assert predictions == zero_shot_classifier(
        text,
        candidate_labels=labels,
        hypothesis_template=hypothesis,
        multi_label=multi_label,
    )

    if isinstance(text, list):
        text = text[0]
    try:
        predictions = predictions[0]
    except KeyError:
        pass

    sleep(1)  # wait for the consumer time
    ds = argilla_v1.load(dataset)
    df = ds.to_pandas()
    assert len(df) == 1
    record = TextClassificationRecord.parse_obj(df.to_dict(orient="records")[0])
    assert record.inputs["text"] == text
    assert record.metadata == {"labels": labels, "hypothesis_template": hypothesis}
    assert record.prediction_agent == zero_shot_classifier.model.config.name_or_path
    assert record.prediction == [(label, score) for label, score in zip(predictions["labels"], predictions["scores"])]


@pytest.mark.parametrize(
    ("text", "labels", "hypothesis"),
    zero_shot_inputs(),
)
def test_monitor_zero_short_passing_labels_as_args(
    text,
    labels,
    hypothesis,
    mocked_client,
    mocked_monitor,
    dataset,
):
    delete_ignoring_errors(dataset)
    predictions = mocked_monitor(text, labels, hypothesis_template=hypothesis)

    check_zero_shot_results(
        predictions,
        zero_shot_classifier=mocked_monitor.__model__,
        dataset=dataset,
        text=text,
        labels=labels,
        hypothesis=hypothesis,
    )


@pytest.mark.parametrize(
    ("text", "labels", "hypothesis"),
    zero_shot_inputs(),
)
def test_monitor_zero_short_passing_labels_keyword_arg(
    text,
    labels,
    hypothesis,
    mocked_client,
    mocked_monitor,
    dataset,
):
    delete_ignoring_errors(dataset)
    predictions = mocked_monitor(
        text,
        candidate_labels=labels,
        hypothesis_template=hypothesis,
    )

    check_zero_shot_results(
        predictions,
        zero_shot_classifier=mocked_monitor.__model__,
        dataset=dataset,
        text=text,
        labels=labels,
        hypothesis=hypothesis,
    )


@pytest.mark.parametrize(
    ("text", "labels", "hypothesis"),
    zero_shot_inputs(),
)
def test_monitor_zero_shot_with_multilabel(
    text,
    labels,
    hypothesis,
    mocked_client,
    mocked_monitor,
    dataset,
):
    delete_ignoring_errors(dataset)
    delete_ignoring_errors(dataset + "_multi")
    predictions = mocked_monitor(
        text,
        candidate_labels=labels,
        hypothesis_template=hypothesis,
        multi_label=True,
    )

    with pytest.raises(Exception):
        argilla_v1.load(dataset)

    check_zero_shot_results(
        predictions,
        zero_shot_classifier=mocked_monitor.__model__,
        dataset=dataset + "_multi",
        text=text,
        labels=labels,
        hypothesis=hypothesis,
        multi_label=True,
    )


@pytest.mark.parametrize(
    ("text", "labels", "hypothesis"),
    zero_shot_inputs(),
)
def test_monitor_zero_shot_with_text_array(
    text,
    labels,
    hypothesis,
    mocked_client,
    mocked_monitor,
    dataset,
):
    delete_ignoring_errors(dataset)
    predictions = mocked_monitor([text], candidate_labels=labels, hypothesis_template=hypothesis)

    check_zero_shot_results(
        predictions,
        zero_shot_classifier=mocked_monitor.__model__,
        dataset=dataset,
        text=[text],
        labels=labels,
        hypothesis=hypothesis,
    )


@pytest.mark.parametrize(
    ("text", "labels", "hypothesis"),
    zero_shot_inputs(),
)
def test_monitor_zero_shot_passing_metadata(
    text,
    labels,
    hypothesis,
    mocked_client,
    mocked_monitor,
    dataset,
):
    delete_ignoring_errors(dataset)
    expected_metadata = {"type": "test"}
    mocked_monitor(
        text,
        candidate_labels=labels,
        hypothesis_template=hypothesis,
        metadata=expected_metadata,
    )

    sleep(1)  # wait for the consumer time
    ds = argilla_v1.load(dataset)
    df = ds.to_pandas()
    assert len(df) == 1

    record = TextClassificationRecord.parse_obj(df.to_dict(orient="records")[0])
    assert record.metadata == {
        **expected_metadata,
        "labels": labels,
        "hypothesis_template": hypothesis,
    }
