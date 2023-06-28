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
from argilla.client.models import TextClassificationRecord, TokenClassificationRecord
from argilla.training import ArgillaTrainer

from .helpers import cleanup_spacy_config, train_with_cleanup

FRAMEWORK = "spacy"
MODEL = "en_core_web_sm"


def test_update_config(dataset_text_classification):
    trainer = ArgillaTrainer(name=dataset_text_classification, model=MODEL, framework=FRAMEWORK)
    trainer.update_config(max_steps=15000)
    assert trainer._trainer.config["training"]["max_steps"] == 15000
    trainer.update_config(num_epochs=1000)
    assert trainer._trainer.config["training"]["num_epochs"] == 1000


def test_train_textcat(dataset_text_classification):
    trainer = ArgillaTrainer(name=dataset_text_classification, model=MODEL, framework=FRAMEWORK)
    trainer.update_config(max_steps=1)
    output_dir = "tmp_spacy_train_textcat"
    train_with_cleanup(trainer, output_dir)
    record = trainer.predict("This is a text", as_argilla_records=True)
    assert isinstance(record, TextClassificationRecord)
    assert record.multi_label is False
    not_record = trainer.predict("This is a text", as_argilla_records=False)
    assert isinstance(not_record.cats, dict)
    train_with_cleanup(trainer, output_dir, train=False)
    cleanup_spacy_config(trainer)


def test_train_textcat_multi_label(dataset_text_classification_multi_label):
    trainer = ArgillaTrainer(
        name=dataset_text_classification_multi_label, model=MODEL, train_size=0.5, framework=FRAMEWORK
    )
    output_dir = "tmp_spacy_train_multi_label"
    trainer.update_config(max_steps=1)
    train_with_cleanup(trainer, output_dir)
    record = trainer.predict("This is a text", as_argilla_records=True)
    assert isinstance(record, TextClassificationRecord)
    assert record.multi_label is True
    not_record = trainer.predict("This is a text", as_argilla_records=False)
    assert isinstance(not_record.cats, dict)
    train_with_cleanup(trainer, output_dir, train=False)
    cleanup_spacy_config(trainer)


def test_train_tokencat(dataset_token_classification):
    trainer = ArgillaTrainer(name=dataset_token_classification, model=MODEL, framework=FRAMEWORK)
    trainer.update_config(max_steps=1)
    output_dir = "tmp_spacy_train_tokencat"
    train_with_cleanup(trainer, output_dir)
    record = trainer.predict("This is a text", as_argilla_records=True)
    assert isinstance(record, TokenClassificationRecord)
    not_record = trainer.predict("This is a text", as_argilla_records=False)
    assert not isinstance(not_record, TokenClassificationRecord)
    train_with_cleanup(trainer, output_dir, train=False)
    cleanup_spacy_config(trainer)


def test_init_with_gpu_id(dataset_text_classification):
    trainer = ArgillaTrainer(name=dataset_text_classification, model=MODEL, framework=FRAMEWORK, gpu_id=0)
    try:
        import torch  # noqa

        has_torch = True
    except ImportError:
        has_torch = False

    try:
        import tensorflow  # noqa

        has_tensorflow = True
    except ImportError:
        has_tensorflow = False

    import spacy

    if not has_torch and not has_tensorflow:
        assert trainer._trainer.gpu_id == -1
    else:
        assert trainer._trainer.use_gpu == spacy.prefer_gpu(0)


def test_predict_wo_training(dataset_text_classification):
    trainer = ArgillaTrainer(name=dataset_text_classification, framework=FRAMEWORK, model=MODEL)
    trainer._trainer.predict("This is a text")
