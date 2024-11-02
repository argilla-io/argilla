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

import pytest
from argilla_v1.client.datasets import (
    DatasetForTextClassification,
    DatasetForTokenClassification,
)
from argilla_v1.client.models import TextClassificationRecord, TokenClassificationRecord
from argilla_v1.training import ArgillaTrainer


def test_wrong_framework(dataset_text_classification):
    framework = "mock"
    with pytest.raises(ValueError, match=f"{framework!r} is not a valid framework."):
        ArgillaTrainer(dataset_text_classification, framework=framework)


@pytest.mark.parametrize("framework", ["spacy", "transformers", "setfit"])
def test_base_text_classification_without_split(framework, dataset_text_classification):
    trainer = ArgillaTrainer(dataset_text_classification, framework=framework)
    assert trainer._split_applied is False
    assert trainer._multi_label is False
    assert trainer._trainer._eval_dataset is None
    assert trainer._rg_dataset_type == DatasetForTextClassification
    assert trainer._trainer._record_class == TextClassificationRecord


@pytest.mark.parametrize("framework", ["spacy", "transformers", "setfit"])
def test_base_text_classification_with_split(framework, dataset_text_classification):
    trainer = ArgillaTrainer(dataset_text_classification, framework=framework, train_size=0.8)
    assert trainer._split_applied is True
    assert trainer._multi_label is False
    assert trainer._trainer._eval_dataset is not None
    assert trainer._rg_dataset_type == DatasetForTextClassification
    assert trainer._trainer._record_class == TextClassificationRecord


@pytest.mark.parametrize("framework", ["spacy", "transformers", "setfit"])
def test_base_token_classification(framework, dataset_token_classification):
    def _init_trainer(_framework) -> None:
        trainer = ArgillaTrainer(dataset_token_classification, framework=_framework)
        assert trainer._split_applied is False
        assert trainer._multi_label is False
        assert trainer._trainer._eval_dataset is None
        assert trainer._rg_dataset_type is DatasetForTokenClassification
        assert trainer._trainer._record_class is TokenClassificationRecord

    if framework == "setfit":
        with pytest.raises(NotImplementedError, match="SetFit only supports the `TextClassification` task."):
            _init_trainer(framework)
    else:
        _init_trainer(framework)
