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

from datasets import DatasetDict

import argilla as rg
from argilla.client.feedback.training.base import ArgillaTrainerSkeleton
from argilla.training.span_marker import (
    ArgillaSpanMarkerTrainer as ArgillaSpanMarkerTrainerV1,
)


class ArgillaSpanMarkerTrainer(ArgillaSpanMarkerTrainerV1, ArgillaTrainerSkeleton):
    def __init__(self, *args, **kwargs) -> None:
        ArgillaTrainerSkeleton.__init__(*args, **kwargs)

        import torch
        from span_marker import SpanMarkerModel

        self._span_marker_model = None

        self.device = "cpu"
        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"

        if self._seed is None:
            self._seed = 42

        if self._model is None:
            self._model = "bert-base-cased"

        if isinstance(self._dataset, DatasetDict):
            self._train_dataset = self._dataset["train"]
            self._eval_dataset = self._dataset["test"]
        else:
            self._train_dataset = self._dataset
            self._eval_dataset = None

        if self._record_class == rg.TokenClassificationRecord:
            self._column_mapping = {"text": "text", "token": "tokens", "ner_tags": "ner_tags"}
            self._label_list = self._train_dataset.features["ner_tags"].feature.names

            self._model_class = SpanMarkerModel
        else:
            raise NotImplementedError("rg.Text2TextRecord and rg.TextClassification are not supported.")

        self.init_training_args()
