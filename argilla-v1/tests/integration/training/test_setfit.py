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

from argilla_v1.client.models import TextClassificationRecord
from argilla_v1.training import ArgillaTrainer

from .helpers import train_with_cleanup

FRAMEWORK = "setfit"
MODEL = "all-MiniLM-L6-v2"


def test_update_config(dataset_text_classification):
    trainer = ArgillaTrainer(name=dataset_text_classification, model=MODEL, framework=FRAMEWORK)
    trainer.update_config(num_epochs=3)
    assert trainer._trainer.trainer_kwargs["num_epochs"] == 3
    trainer.update_config(num_epochs=1)
    assert trainer._trainer.trainer_kwargs["num_epochs"] == 1


def test_setfit_train(dataset_text_classification):
    trainer = ArgillaTrainer(name=dataset_text_classification, model=MODEL, framework=FRAMEWORK)
    output_dir = "tmp_setfit_train"
    trainer.update_config(num_epochs=1, num_iterations=1)
    train_with_cleanup(trainer, output_dir)
    record = trainer.predict("This is a text", as_argilla_records=True)
    assert isinstance(record, TextClassificationRecord)
    assert record.multi_label is False
    not_record = trainer.predict("This is a text", as_argilla_records=False)
    assert not isinstance(not_record, TextClassificationRecord)
    train_with_cleanup(trainer, output_dir, train=False)


def test_setfit_train_multi_label(dataset_text_classification_multi_label):
    trainer = ArgillaTrainer(
        name=dataset_text_classification_multi_label, model=MODEL, train_size=0.5, framework=FRAMEWORK
    )
    output_dir = "tmp_setfit_train_multi_label"
    trainer.update_config(num_epochs=1, num_iterations=1)
    train_with_cleanup(trainer, output_dir)
    record = trainer.predict("This is a text", as_argilla_records=True)
    assert isinstance(record, TextClassificationRecord)
    assert record.multi_label is True
    not_record = trainer.predict("This is a text", as_argilla_records=False)
    assert not isinstance(not_record, TextClassificationRecord)
    train_with_cleanup(trainer, output_dir, train=False)
