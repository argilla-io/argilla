from typing import List, Union

import pytest

import rubrix
from rubrix import TextClassificationRecord
from tests.monitoring.helpers import mock_monitor


def test_classifier_monitoring_with_all_scores(
    mocked_client, classifier_monitor_all_scores, classifier_dataset
):
    rubrix.delete(classifier_dataset)

    expected_text = "This is a text, yeah"
    classifier_monitor_all_scores(expected_text)

    df = rubrix.load(classifier_dataset)
    assert len(df) == 1
    record = TextClassificationRecord.parse_obj(df.to_dict(orient="records")[0])
    assert record.inputs == {"text": expected_text}
    assert len(record.prediction) > 1


def test_classifier_monitoring(mocked_client, classifier_monitor, classifier_dataset):
    rubrix.delete(classifier_dataset)

    expected_text = "This is a text, yeah"
    classifier_monitor(expected_text)

    df = rubrix.load(classifier_dataset)
    assert len(df) == 1
    record = TextClassificationRecord.parse_obj(df.to_dict(orient="records")[0])
    assert record.inputs == {"text": expected_text}
    assert len(record.prediction) == 1

    rubrix.delete(classifier_dataset)
    texts = ["This is a text", "And another text here"]
    classifier_monitor(texts)
    df = rubrix.load(classifier_dataset)
    assert len(df) == 2
    assert set([r["text"] for r in df.inputs.values.tolist()]) == set(texts)

    rubrix.delete(classifier_dataset)
    classifier_monitor(expected_text, metadata={"some": "metadata"})
    df = rubrix.load(classifier_dataset)
    assert len(df) == 1
    assert df.metadata.values.tolist()[0] == {"some": "metadata"}


@pytest.fixture
def classifier_dataset():
    return "classifier_dataset"


@pytest.fixture
def classifier_monitor_all_scores(
    sentiment_classifier_all_scores, classifier_dataset, monkeypatch
):
    monitor = rubrix.monitor(
        sentiment_classifier_all_scores, dataset=classifier_dataset, sample_rate=1.0
    )
    mock_monitor(monitor, monkeypatch)
    return monitor


@pytest.fixture
def classifier_monitor(sentiment_classifier, classifier_dataset, monkeypatch):
    monitor = rubrix.monitor(
        sentiment_classifier, dataset=classifier_dataset, sample_rate=1.0
    )
    mock_monitor(monitor, monkeypatch)
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
        "zero-shot-classification", model="Recognai/bert-base-spanish-wwm-cased-xnli"
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
    monitor = rubrix.monitor(zero_shot_classifier, dataset=dataset, sample_rate=1.0)
    mock_monitor(monitor, monkeypatch)

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

    df = rubrix.load(dataset)
    assert len(df) == 1
    record = TextClassificationRecord.parse_obj(df.to_dict(orient="records")[0])
    assert record.inputs["text"] == text
    assert record.metadata == {"labels": labels, "hypothesis_template": hypothesis}
    assert record.prediction_agent == zero_shot_classifier.model.config.name_or_path
    assert record.prediction == [
        (label, score)
        for label, score in zip(predictions["labels"], predictions["scores"])
    ]


@pytest.mark.parametrize(
    ("text", "labels", "hypothesis"),
    zero_shot_inputs(),
)
def test_monitor_zero_short_passing_labels_as_args(
    text, labels, hypothesis, mocked_client, mocked_monitor, dataset
):
    rubrix.delete(dataset)
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
    text, labels, hypothesis, mocked_client, mocked_monitor, dataset
):

    rubrix.delete(dataset)
    predictions = mocked_monitor(
        text, candidate_labels=labels, hypothesis_template=hypothesis
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
    text, labels, hypothesis, mocked_client, mocked_monitor, dataset
):
    rubrix.delete(dataset)
    rubrix.delete(dataset + "_multi")
    predictions = mocked_monitor(
        text, candidate_labels=labels, hypothesis_template=hypothesis, multi_label=True
    )

    with pytest.raises(Exception):
        rubrix.load(dataset)

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
    text, labels, hypothesis, mocked_client, mocked_monitor, dataset
):

    rubrix.delete(dataset)
    predictions = mocked_monitor(
        [text], candidate_labels=labels, hypothesis_template=hypothesis
    )

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
    text, labels, hypothesis, mocked_client, mocked_monitor, dataset
):
    rubrix.delete(dataset)
    expected_metadata = {"type": "test"}
    mocked_monitor(
        text,
        candidate_labels=labels,
        hypothesis_template=hypothesis,
        metadata=expected_metadata,
    )

    df = rubrix.load(dataset)
    assert len(df) == 1

    record = TextClassificationRecord.parse_obj(df.to_dict(orient="records")[0])
    assert record.metadata == {
        **expected_metadata,
        "labels": labels,
        "hypothesis_template": hypothesis,
    }
