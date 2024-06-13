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

import argilla_v1
from argilla_server.models import User


class MockModel:
    pass


def test_monitor_with_non_supported_model(argilla_user: User):
    with warnings.catch_warnings(record=True) as warning_list:
        model = MockModel()

        maybe_monitored = argilla_v1.monitor(model, dataset="mock")
        assert model == maybe_monitored

        assert any(
            [
                warning.message.args[0] == "The provided task model is not supported by monitoring module. "
                "Predictions won't be logged into argilla."
                for warning in warning_list
            ]
        )


def test_monitor_non_supported_huggingface_model(argilla_user: User):
    with warnings.catch_warnings(record=True) as warning_list:
        from transformers import (
            AutoModelForTokenClassification,
            AutoTokenizer,
            pipeline,
        )

        tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
        model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")

        nlp = pipeline("ner", model=model, tokenizer=tokenizer)
        maybe_monitored = argilla_v1.monitor(nlp, dataset="ds")
        assert nlp == maybe_monitored
        assert any(
            [
                warning.message.args[0] == "The provided task model is not supported by monitoring module. "
                "Predictions won't be logged into argilla."
                for warning in warning_list
            ]
        )
