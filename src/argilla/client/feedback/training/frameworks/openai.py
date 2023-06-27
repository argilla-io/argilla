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

from argilla.client.feedback.training.base import ArgillaTrainerSkeleton
from argilla.client.models import TextClassificationRecord, TokenClassificationRecord
from argilla.training.openai import ArgillaOpenAITrainer as ArgillaOpenAITrainerV1


class ArgillaOpenAITrainer(ArgillaOpenAITrainerV1, ArgillaTrainerSkeleton):
    def __init__(self, *args, **kwargs):
        ArgillaTrainerSkeleton.__init__(self, *args, **kwargs)

        if self._record_class is TokenClassificationRecord:
            raise NotImplementedError("OpenAI does not support `TokenClassification` tasks.")
        elif self._record_class is TextClassificationRecord and self._multi_label:
            raise NotImplementedError("OpenAI does not support multi-label TextClassification tasks.")

        self.sleep_timer = 10
        self.device = None
        self.finetune_id = None

        if self._seed is not None:
            self._logger.warning("Seed is not supported for OpenAI. Ignoring seed for training.")

        if self._model is None:
            self._model = "curie"

        if isinstance(self._dataset, tuple):
            self._train_dataset = self._dataset[0]
            self._eval_dataset = self._dataset[1]
        else:
            self._train_dataset = self._dataset
            self._eval_dataset = None

        self.init_training_args(model=self._model)
