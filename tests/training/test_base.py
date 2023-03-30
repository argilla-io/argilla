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

import argilla as rg
import pytest
from argilla.training import ArgillaTrainer


def test_wrong_framework(dataset_text_classification):
    framework = "mock"
    with pytest.raises(NotImplementedError, match=f"Framework {framework} is not supported."):
        ArgillaTrainer(dataset=dataset_text_classification, framework=framework)


@pytest.mark.parameterize(["spacy", "transformers", "setfit"])
def test_base_text_classification_without_split(framework, dataset_text_classification):
    trainer = ArgillaTrainer(dataset=dataset_text_classification, framework=framework)
    assert trainer._split_applied is False
    assert trainer._multi_label is False
    assert trainer._trainer._eval_dataset is None
    assert trainer._required_fields == ["id", "text", "inputs", "annotation", "multi_label"]
    assert trainer._rg_dataset_type == rg.DatasetForTextClassification
    assert trainer._trainer.record_class == rg.TextClassificationRecord


@pytest.mark.parameterize(["spacy", "transformers", "setfit"])
def test_base_text_classification_with_split(framework, dataset_text_classification):
    trainer = ArgillaTrainer(dataset=dataset_text_classification, framework=framework, train_size=0.8)
    assert trainer._split_applied is True
    assert trainer._multi_label is False
    assert trainer._trainer._eval_dataset is not None
    assert trainer._required_fields == ["id", "text", "inputs", "annotation", "multi_label"]
    assert trainer._rg_dataset_type == rg.DatasetForTextClassification
    assert trainer._trainer.record_class == rg.TextClassificationRecord


@pytest.mark.parameterize(["spacy", "transformers", "setfit"])
def test_base_token_classification(framework, dataset_text_classification):
    def _init_trainer(_framework):
        trainer = ArgillaTrainer(dataset=dataset_text_classification, framework=_framework)
        assert trainer._split_applied is False
        assert trainer._multi_label is False
        assert trainer._trainer._eval_dataset is None
        assert trainer._required_fields == ["id", "text", "tokens", "annotation", "ner_tags"]
        assert trainer._rg_dataset_type == rg.DatasetForTokenClassification()
        assert trainer._trainer.record_class == rg.TokenClassificationRecord()

    if framework == "setfit":
        with pytest.raises(NotImplementedError, match=f"{framework} only support `TextClassification` tasks."):
            _init_trainer(framework)
    else:
        _init_trainer(framework)


@pytest.mark.parameterize(["spacy", "transformers", "setfit"])
def test_base_text2text(framework, dataset_text2text):
    with pytest.raises(NotImplementedError, match="`argilla.training` does not support `Text2Text` tasks yet."):
        ArgillaTrainer(dataset=dataset_text2text, framework=framework)
