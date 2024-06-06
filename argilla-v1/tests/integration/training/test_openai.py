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

import pytest
from argilla_v1.training import ArgillaTrainer

FRAMEWORK = "openai"
MODEL = "curie"

os.environ["OPENAI_API_KEY"] = "1234"


def test_update_config(dataset_text_classification):
    trainer = ArgillaTrainer(name=dataset_text_classification, model=MODEL, framework=FRAMEWORK)
    trainer.update_config(model=3)
    assert trainer._trainer.trainer_kwargs["model"] == 3
    trainer.update_config(prompt_loss_weight=1)
    assert trainer._trainer.trainer_kwargs["prompt_loss_weight"] == 1


def test_openai_train(dataset_text_classification, mocked_openai):
    trainer = ArgillaTrainer(name=dataset_text_classification, model=MODEL, framework=FRAMEWORK)
    trainer.train("model")


def test_openai_train_multi_label(dataset_text_classification_multi_label):
    with pytest.raises(
        NotImplementedError, match="OpenAI does not support `multi-label=True` TextClassification tasks."
    ):
        ArgillaTrainer(name=dataset_text_classification_multi_label, model=MODEL, train_size=0.5, framework=FRAMEWORK)


def test_openai_train_token(dataset_token_classification):
    with pytest.raises(NotImplementedError, match="OpenAI does not support `TokenClassification` tasks."):
        ArgillaTrainer(name=dataset_token_classification, model=MODEL, train_size=0.5, framework=FRAMEWORK)


def test_openai_train_text2text(dataset_text2text, mocked_openai):
    trainer = ArgillaTrainer(name=dataset_text2text, model=MODEL, framework=FRAMEWORK)
    trainer.train("model")
