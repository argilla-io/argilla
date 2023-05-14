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

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, List, Optional, Union

import argilla as rg
from argilla.training.base import ArgillaTrainerSkeleton
from argilla.utils.dependency import require_version

if TYPE_CHECKING:
    import tensorflow as tf


class ArgillaKerasNLPTrainer(ArgillaTrainerSkeleton):
    _logger = logging.getLogger("ArgillaKerasNLPTrainer")
    _logger.setLevel(logging.INFO)

    require_version("keras-nlp")
    require_version("tensorflow")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if isinstance(self._dataset, tuple):
            self._train_dataset: "tf.data.Dataset" = self._dataset[0]
            self._eval_dataset: "tf.data.Dataset" = self._dataset[1]
        else:
            self._train_dataset: "tf.data.Dataset" = self._dataset
            self._eval_dataset = None

        if self._record_class == rg.TextClassificationRecord:
            if self._multi_label:
                raise NotImplementedError("`rg.TextClassificationRecord` with multi_label is not supported yet.")

            import tensorflow as tf

            all_labels = [y.numpy().decode("utf-8") for _, y in self._train_dataset]
            unique_labels = list(set(all_labels))
            self.num_classes = len(unique_labels)

            self.idx2label = {idx: label for idx, label in enumerate(unique_labels)}
            self.label2idx = {label: idx for idx, label in self.idx2label.items()}

            def str_to_int(t: tf.Tensor):
                return self.label2idx[t.numpy().decode("utf-8")]

            self._train_dataset = self._train_dataset.map(
                lambda x, y: (x, tf.py_function(func=str_to_int, inp=[y], Tout=tf.int32))
            )
            if self._eval_dataset:
                self._eval_dataset = self._eval_dataset.map(
                    lambda x, y: (x, tf.py_function(func=str_to_int, inp=[y], Tout=tf.int32))
                )
        else:
            raise NotImplementedError("`rg.TokenClassificationRecord` and `rg.Text2TextRecord` are not supported yet.")

        self._train_batch_size = 16
        self._eval_batch_size = 8
        self.n_epochs = 5

        self.init_training_args()

    def init_training_args(self) -> None:
        pass

    def init_model(self) -> None:
        pass

    def __repr__(self) -> str:
        return ""

    def update_config(self) -> None:
        pass

    def train(self, output_dir: Optional[str] = None) -> None:
        # from keras_nlp.models import (BertClassifier, FNetClassifier, AlbertClassifier, RobertaClassifier, DebertaV3Classifier, DistilBertClassifier, XLMRobertaClassifier)
        from keras_nlp.models import BertClassifier

        self.classifier = BertClassifier.from_preset(self._model, num_classes=self.num_classes)
        self.classifier.fit(
            self._train_dataset.batch(self._train_batch_size),
            validation_data=self._eval_dataset.batch(self._eval_batch_size) if self._eval_dataset else None,
            epochs=self.n_epochs,
        )
        if output_dir:
            self.save(output_dir)

    def save(self, output_dir: Union[str, Path]) -> None:
        output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir
        if output_dir and not output_dir.exists():
            output_dir.mkdir(parents=True)
        self.classifier.save(output_dir)  # To be loaded as `tf.keras.models.load_model(output_dir)`

    require_version("numpy")

    def predict(self, text: Union[List[str], str], as_argilla_records: bool = True, **kwargs) -> Any:
        import numpy as np

        prediction = self.classifier.predict([text] if isinstance(text, str) else text)
        prediction = np.argmax(prediction, axis=1)
        return prediction
