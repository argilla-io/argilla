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


from datasets import Dataset, DatasetDict

from argilla.client.feedback.training.base import ArgillaTrainerSkeleton
from argilla.client.feedback.training.schemas import (
    TrainingTaskMappingForTextClassification,
)
from argilla.training.transformers import (
    ArgillaTransformersTrainer as ArgillaTransformersTrainerV1,
)


class ArgillaTransformersTrainer(ArgillaTransformersTrainerV1, ArgillaTrainerSkeleton):
    def __init__(self, *args, **kwargs):
        # init ArgillaTrainerSkeleton
        ArgillaTrainerSkeleton.__init__(self, *args, **kwargs)

        import torch
        from transformers import (
            AutoModelForSequenceClassification,
            set_seed,
        )

        self._transformers_model = None
        self._transformers_tokenizer = None
        self._pipeline = None

        self.device = "cpu"
        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"

        if self._seed is None:
            self._seed = 42
        set_seed(self._seed)

        if self._model is None:
            self._model = "bert-base-cased"

        if isinstance(self._dataset, DatasetDict):
            self._train_dataset = self._dataset["train"]
            self._eval_dataset = self._dataset["test"]
        elif isinstance(self._dataset, Dataset):
            self._train_dataset = self._dataset
            self._eval_dataset = None
        else:
            raise NotImplementedError(f"We do not support {type(self._dataset)} yet.")

        if isinstance(self._task_mapping, TrainingTaskMappingForTextClassification):
            self._model_class = AutoModelForSequenceClassification
        else:
            raise NotImplementedError(f"ArgillaTransformersTrainer does not support {type(self._task_mapping)} yet.")

        self.init_training_args()
