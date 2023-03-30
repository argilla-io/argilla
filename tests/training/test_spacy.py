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

FRAMEWORK = "spacy"
MODEL = "en-core-web-sm"


def test_update_config(dataset_text_classification):
    trainer = ArgillaTrainer(dataset=dataset_text_classification, model=MODEL, framework=FRAMEWORK)
    trainer.update_config(max_steps=15000)
    assert trainer._trainer.trainer_kwargs["num_epochs"] == 15000
    trainer.update_config(max_steps=1000)
    assert trainer._trainer.trainer_kwargs["num_epochs"] == 1000


def test_train_textcat(dataset_text_classification):
    trainer = ArgillaTrainer(dataset=dataset_text_classification, model=MODEL, framework=FRAMEWORK)
    trainer.update_config(max_steps=1000)
    trainer.train(f"tmp/{FRAMEWORK}_train")
    record = trainer.predict("This is a text", as_records=True)
    assert isinstance(record, rg.TextClassificationRecord)
    assert record.multi_label is False
    not_record = trainer.predict("This is a text", as_records=False)
    assert isinstance(not_record.textcat, str)
    trainer.save(f"tmp/{FRAMEWORK}_train")


def test_train_textcat_multi_label(dataset_text_classification_multi_label):
    trainer = ArgillaTrainer(
        dataset=dataset_text_classification_multi_label, model=MODEL, train_size=0.5, framework=FRAMEWORK
    )
    trainer.update_config(max_steps=1000)
    trainer.train(f"tmp/{FRAMEWORK}_train")
    record = trainer.predict("This is a text", as_records=True)
    assert isinstance(record, rg.TextClassificationRecord)
    assert record.multi_label is True
    not_record = trainer.predict("This is a text", as_records=False)
    assert isinstance(not_record.textcat, list)
    trainer.save(f"tmp/{FRAMEWORK}_train")


def test_train_tokencat(dataset_text_classification):
    trainer = ArgillaTrainer(dataset=dataset_text_classification, model=MODEL, framework=FRAMEWORK)
    trainer.update_config(max_steps=1000)
    trainer.train(f"tmp/{FRAMEWORK}_train")
    record = trainer.predict("This is a text", as_records=True)
    assert isinstance(record, rg.TokenClassificationRecord)
    not_record = trainer.predict("This is a text", as_records=False)
    assert not isinstance(not_record, rg.TokenClassificationRecord)
    trainer.save(f"tmp/{FRAMEWORK}_train")
