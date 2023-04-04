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
from argilla.training import ArgillaTrainer

from .helpers import cleanup, cleanup_spacy_config

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
    cleanup(trainer, output_dir)
    record = trainer.predict("This is a text", as_argilla_records=True)
    assert isinstance(record, rg.TextClassificationRecord)
    assert record.multi_label is False
    not_record = trainer.predict("This is a text", as_argilla_records=False)
    assert isinstance(not_record.cats, dict)
    cleanup(trainer, output_dir, train=False)
    cleanup_spacy_config(trainer)


def test_train_textcat_multi_label(dataset_text_classification_multi_label):
    trainer = ArgillaTrainer(
        name=dataset_text_classification_multi_label, model=MODEL, train_size=0.5, framework=FRAMEWORK
    )
    output_dir = "tmp_spacy_train_multi_label"
    trainer.update_config(max_steps=1)
    cleanup(trainer, output_dir)
    record = trainer.predict("This is a text", as_argilla_records=True)
    assert isinstance(record, rg.TextClassificationRecord)
    assert record.multi_label is True
    not_record = trainer.predict("This is a text", as_argilla_records=False)
    assert isinstance(not_record.cats, dict)
    cleanup(trainer, output_dir, train=False)
    cleanup_spacy_config(trainer)


def test_train_tokencat(dataset_token_classification):
    trainer = ArgillaTrainer(name=dataset_token_classification, model=MODEL, framework=FRAMEWORK)
    trainer.update_config(max_steps=1)
    output_dir = "tmp_spacy_train_tokencat"
    cleanup(trainer, output_dir)
    record = trainer.predict("This is a text", as_argilla_records=True)
    assert isinstance(record, rg.TokenClassificationRecord)
    not_record = trainer.predict("This is a text", as_argilla_records=False)
    assert not isinstance(not_record, rg.TokenClassificationRecord)
    cleanup(trainer, output_dir, train=False)
    cleanup_spacy_config(trainer)
