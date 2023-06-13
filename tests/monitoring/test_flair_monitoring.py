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

from argilla.server.models import User


def test_flair_monitoring(monkeypatch, argilla_user: User):
    import argilla as rg
    from flair.data import Sentence
    from flair.models import SequenceTagger

    dataset = "test_flair_monitoring"
    model = "flair/ner-english"

    rg.delete(dataset)

    # load tagger
    tagger = SequenceTagger.load(model)
    tagger = rg.monitor(
        tagger,
        dataset=dataset,
        sample_rate=1.0,
        agent=model,
        log_interval=0.5,
    )

    # make example sentence
    expected_text = "George Washington went to Washington"
    sentence = Sentence(expected_text)
    # predict NER tags
    tagger.predict(sentence)

    sleep(1)  # wait for the consumer time
    detected_labels = sentence.get_labels("ner")
    detected_spans = sentence.get_spans("ner")
    records = rg.load(dataset)
    assert len(records) == 1

    record = records[0]
    assert record.text == expected_text
    assert record.tokens == [token.text for token in sentence.tokens]

    assert len(record.prediction) == len(detected_labels)
    assert len(record.prediction) == len(detected_spans)
    for (label, start, end, score), detected_label, detected_span in zip(
        record.prediction, detected_labels, detected_spans
    ):
        assert label == detected_label.value
        assert start == detected_span.start_position
        assert end == detected_span.end_position
        assert score == detected_label.score
