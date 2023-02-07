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

import warnings

import argilla


class MockModel:
    pass


def test_monitor_with_non_supported_model():
    with warnings.catch_warnings(record=True) as warning_list:
        model = MockModel()

        maybe_monitored = argilla.monitor(model, dataset="mock")
        assert model == maybe_monitored
        assert len(warning_list) == 1
        warn_text = warning_list[0].message.args[0]
        assert (
            warn_text
            == "The provided task model is not supported by monitoring module. "
            "Predictions won't be logged into argilla"
        )


def test_monitor_non_supported_huggingface_model():
    with warnings.catch_warnings(record=True) as warning_list:
        from transformers import (
            AutoModelForTokenClassification,
            AutoTokenizer,
            pipeline,
        )

        tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
        model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")

        nlp = pipeline("ner", model=model, tokenizer=tokenizer)
        maybe_monitored = argilla.monitor(nlp, dataset="ds")
        assert nlp == maybe_monitored
        assert len(warning_list) == 1
        warn_text = warning_list[0].message.args[0]
        assert (
            warn_text
            == "The provided task model is not supported by monitoring module. "
            "Predictions won't be logged into argilla"
        )
