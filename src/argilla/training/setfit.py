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
from typing import List, Union

from datasets import DatasetDict


class ArgillaSetFitTrainer(object):
    # @require_version("setfit", "0.6")
    def __init__(self, dataset, device, record_class, multi_label: bool = False):
        self._record_class = record_class
        if isinstance(dataset, DatasetDict):
            self._train_dataset = dataset["train"]
            self._eval_dataset = dataset["test"]
        else:
            self._train_dataset = dataset
            self._eval_dataset = None
        if multi_label:
            self.multi_target_strategy = "one-vs-rest"
            self._column_mapping = {"text": "text", "binarized_label": "label"}
        else:
            self.multi_target_strategy = None
            self._column_mapping = {"text": "text", "label": "label"}

        self._id2label = dict(enumerate(self._train_dataset.features["label"].names))
        self._label2id = {v: k for k, v in self._id2label.items()}

        self.setfit_kwargs = {
            "pretrained_model_name_or_path": "all-MiniLM-L6-v2",
            "num_epochs": 1,
            "device": device,
            "multi_target_strategy": self.multi_target_strategy,
        }

    def update_config(
        self,
        **setfit_kwargs,
    ):
        """These configs correspond to `SetFitTrainer.__init__` and `SetFitModel.from_pretrained`"""
        self.setfit_kwargs.update(setfit_kwargs)

    # @require_version("setfit", "0.6")
    def train(self, path: str = None):
        from setfit import SetFitModel, SetFitTrainer

        self._model = SetFitModel.from_pretrained(
            **self.setfit_kwargs,
        )
        self.__trainer = SetFitTrainer(
            model=self._model,
            train_dataset=self._train_dataset,
            eval_dataset=self._eval_dataset,
            column_mapping=self._column_mapping,
            **{
                key: val
                for key, val in self.setfit_kwargs.items()
                if key in SetFitTrainer.__init__.__code__.co_varnames
            },
        )
        self.__trainer.train()
        self._metrics = self.__trainer.evaluate()

    def predict(self, text: Union[List[str], str], as_argilla_records: bool = True):
        str_input = False
        if isinstance(text, str):
            text = [text]
            str_input = True

        predictions = self._model(text)

        formatted_prediction = []
        for val, pred in zip(text, predictions):
            pred = self._id2label[int(pred)]
            if as_argilla_records:
                pred = self._record_class(text=val, prediction=[(pred, 1)])
            formatted_prediction.append(pred)

        if str_input:
            formatted_prediction = formatted_prediction[0]
        return formatted_prediction

    def save(self, path: str):
        """
        The function saves the model to the path specified, and also saves the label2id and id2label
        dictionaries to the same path

        Args:
          path (str): the path to save the model to
        """

        self._model.save_pretrained(path)

        # store dict as json
        with open(path + "/label2id.json", "w") as f:
            json.dump(self._label2id, f)
        with open(path + "/id2label.json", "w") as f:
            json.dump(self._id2label, f)

    def get_relevant_args():
        from setfit import SetFitTrainer

        SetFitTrainer.__init__.func_code.co_varnames
