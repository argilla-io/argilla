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

import json

from argilla.utils.dependency import requires_version


class ArgillaSetFitTrainer(object):
    @requires_version("setfit", "0.6")
    @requires_version("torch")
    def __init__(self, logger, dataset, device, multi_label: bool = False, split_applied=False):
        self.model_name = "all-MiniLM-L6-v2"
        self.num_epoch = 1
        self.device = device
        self.setfit_kwargs = {}

        self._logger = logger
        if split_applied:
            self._train_dataset = dataset["train"]
            self._test_dataset = dataset["test"]
        else:
            self._train_dataset = dataset["train"]
            self._test_dataset = dataset["test"]
        if multi_label:
            self._multi_target_strategy = "one-vs-rest"
            self._column_mapping = {"text": "text", "label": "label"}
        else:
            self._multi_target_strategy = "one-vs-one"
            self._column_mapping = {"text": "text", "binarized_label": "label"}

    def update_config(
        self,
        model_name: str = None,
        num_epoch: int = None,
        device: str = None,
        multi_target_strategy: str = None,
        **setfit_kwargs,
    ):
        if model_name:
            self.model_name = model_name
        if num_epoch:
            self.num_epoch = num_epoch
        if device:
            self.device = device
        if multi_target_strategy:
            self._multi_target_strategy = multi_target_strategy
        self.setfit_kwargs.update(setfit_kwargs)

    @requires_version("setfit", "0.6")
    def train(self):
        from setfit import SetFitModel, SetFitTrainer

        self._model = SetFitModel.from_pretrained(
            pretrained_model_name_or_path=self.model_name,
            multi_target_strategy=self._multi_target_strategy,
            device=self._device,
        )
        self.__trainer = SetFitTrainer(
            self._model,
            train_dataset=self._train_dataset,
            test_dataset=self._test_dataset,
            num_epochs=self._num_epoch,
            use_amp=True,
            column_mapping=self._column_mapping,
            **self.setfit_kwargs,
        )
        self.__trainer.train()
        self.metrics = self.__trainer.evaluate()

    def save(self, path: str):
        """
        The function saves the model to the path specified, and also saves the label2id and id2label
        dictionaries to the same path

        Args:
          path (str): the path to save the model to
        """

        self._model.save_pretrained(path)

        id2label = dict(enumerate(self.dataset.features["label"][0].names))
        label2id = {v: k for k, v in id2label.items()}

        # store dict as json
        with open(path + "/label2id.json", "w") as f:
            json.dump(label2id, f)
        with open(path + "/id2label.json", "w") as f:
            json.dump(id2label, f)
