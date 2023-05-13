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
from typing import Any, List, Optional, Union

import argilla as rg
from argilla.training.base import ArgillaTrainerSkeleton
from argilla.utils.dependency import require_version


class ArgillaKerasNLPTrainer(ArgillaTrainerSkeleton):
    _logger = logging.getLogger("ArgillaKerasNLPTrainer")
    _logger.setLevel(logging.INFO)

    require_version("keras-nlp")
    require_version("tensorflow")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if isinstance(self._dataset, tuple):
            self._train_dataset, self._eval_dataset = self._dataset
        else:
            self._train_dataset = self._dataset
            self._eval_dataset = None

        if self._record_class == rg.TextClassificationRecord:
            if self._multi_label:
                self._column_mapping = {"text": "text", "binarized_label": "label"}
                self._pipeline = ["textcat_multilabel"]
            else:
                self._column_mapping = {"text": "text", "label": "label"}
                self._pipeline = ["textcat"]
        else:
            raise NotImplementedError("`rg.TokenClassificationRecord` and `rg.Text2TextRecord` are not supported yet.")

        self.init_training_args()

    def init_training_args(self) -> None:
        pass

    def init_model(self) -> None:
        pass

    def __repr__(self) -> str:
        pass

    def update_config(self) -> None:
        pass

    def train(self, output_dir: Optional[str] = None) -> None:
        # from keras_nlp.models import (BertClassifier, FNetClassifier, AlbertClassifier, RobertaClassifier, DebertaV3Classifier, DistilBertClassifier, XLMRobertaClassifier)
        from keras_nlp.models import BertClassifier

        self.classifier = BertClassifier.from_preset(self._model, num_classes=2)
        self.classifier.fit(
            self._train_dataset,
            validation_data=self._eval_dataset,
            epochs=1,
        )
        if output_dir:
            self.save(output_dir)

    def save(self, output_dir: Union[str, Path]) -> None:
        output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir
        if output_dir and not output_dir.exists():
            output_dir.mkdir(parents=True)
        self.classifier.save(output_dir)  # To be loaded as `tf.keras.models.load_model(output_dir)`

    def predict(self, text: Union[List[str], str], as_argilla_records: bool = True, **kwargs) -> Any:
        import numpy as np

        prediction = self.classifier.predict([text] if isinstance(text, str) else text)
        prediction = np.argmax(prediction, axis=1)
        return prediction
