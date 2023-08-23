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

from argilla.client.feedback.training.base import ArgillaTrainerSkeleton
from argilla.client.models import TextClassificationRecord, TokenClassificationRecord
from argilla.training.autotrain_advanced import ArgillaAutoTrainTrainer as ArgillaAutoTrainTrainerV1


class ArgillaAutoTrainTrainer(ArgillaAutoTrainTrainerV1, ArgillaTrainerSkeleton):
    def __init__(self, *args, **kwargs):
        # init ArgillaTrainerSkeleton
        ArgillaTrainerSkeleton.__init__(self, *args, **kwargs)

        self.project_name = f"{self._workspace}_{self._name}_{str(uuid4())[:8]}"

        if self._seed:
            self._logger.warning("Setting a seed is not supported by `autotrain-advanced`.")
            self._seed = 42

        if self._model is None:
            self._model = "bert-base-uncased"

        data_dict = {}
        self._num_samples = 0
        if isinstance(self._dataset, DatasetDict):
            self._train_dataset = self._dataset["train"]
            self._eval_dataset = self._dataset["test"]
            data_dict["valid_data"] = [self._eval_dataset.to_pandas()]
            self._num_samples += len(self._eval_dataset)
        else:
            self._train_dataset = self._dataset
            self._eval_dataset = None
            data_dict["valid_data"] = []
        data_dict["train_data"] = [self._train_dataset.to_pandas()]
        self._num_samples += len(self._train_dataset)

        if self._record_class == TextClassificationRecord:
            if self._multi_label:
                raise NotImplementedError(
                    "TextClassificaiton `multi_label=True` is not supported by `autotrain-advanced`."
                )
            elif self._multi_label is False:
                n_classes = len(self._train_dataset.features["label"].names)
                self.task = "text_multi_class_classification" if n_classes > 2 else "text_binary_classification"
                self._id2label = dict(enumerate(self._train_dataset.features["label"].names))
                self._label_list = self._train_dataset.features["label"].names
            self._label2id = {v: k for k, v in self._id2label.items()}
        elif self._record_class == TokenClassificationRecord:
            raise NotImplementedError(
                "`Text2Text` and `TokenClassification` tasks are not supported by `autotrain-advanced`."
            )

        self.init_training_args()

        self.prepare_dataset(data_dict=data_dict)
        self.initialize_project()
