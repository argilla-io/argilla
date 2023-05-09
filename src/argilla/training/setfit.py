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
import logging
from typing import List, Union

from argilla.training.transformers import ArgillaTransformersTrainer
from argilla.training.utils import filter_allowed_args, get_default_args
from argilla.utils.dependency import require_version


class ArgillaSetFitTrainer(ArgillaTransformersTrainer):
    _logger = logging.getLogger("ArgillaSetFitTrainer")
    _logger.setLevel(logging.INFO)

    require_version("torch")
    require_version("datasets")
    require_version("transformers")
    require_version("setfit>=0.6")

    def __init__(self, *args, **kwargs):
        if kwargs.get("model") is None and "model" in kwargs:
            kwargs["model"] = "all-MiniLM-L6-v2"
        self.multi_target_strategy = None
        self._column_mapping = None
        super().__init__(*args, **kwargs)
        if self._multi_label:
            self._column_mapping = {"text": "text", "binarized_label": "label"}
            self.multi_target_strategy = "one-vs-rest"
        else:
            self.multi_target_strategy = None
            self._column_mapping = {"text": "text", "label": "label"}
        self.init_training_args()

    def init_training_args(self):
        from setfit import SetFitModel, SetFitTrainer

        self.setfit_model_kwargs = get_default_args(SetFitModel.from_pretrained)
        self.setfit_model_kwargs["pretrained_model_name_or_path"] = self._model
        self.setfit_model_kwargs["multi_target_strategy"] = self.multi_target_strategy
        self.setfit_model_kwargs["device"] = self.device

        self.setfit_trainer_kwargs = get_default_args(SetFitTrainer.__init__)
        self.setfit_trainer_kwargs["column_mapping"] = self._column_mapping
        self.setfit_trainer_kwargs["train_dataset"] = self._train_dataset
        self.setfit_trainer_kwargs["eval_dataset"] = self._eval_dataset
        self.setfit_trainer_kwargs["seed"] = self._seed

        self._setfit_model = None

    def update_config(
        self,
        **setfit_kwargs,
    ):
        """
        Updates the `setfit_model_kwargs` and `setfit_trainer_kwargs` dictionaries with the keyword
        arguments passed to the `update_config` function.
        """
        from setfit import SetFitTrainer

        self.setfit_model_kwargs.update(setfit_kwargs)

        self.setfit_trainer_kwargs.update(setfit_kwargs)
        self.setfit_trainer_kwargs = filter_allowed_args(SetFitTrainer.__init__, **self.setfit_trainer_kwargs)

    def __repr__(self):
        formatted_string = []
        arg_dict = {
            "'SetFitModel'": self.setfit_model_kwargs,
            "'SetFitTrainer'": self.setfit_trainer_kwargs,
        }
        for arg_dict_key, arg_dict_single in arg_dict.items():
            formatted_string.append(arg_dict_key)
            for key, val in arg_dict_single.items():
                formatted_string.append(f"{key}: {val}")
        return "\n".join(formatted_string)

    def train(self, output_dir: str = None):
        """
        We create a SetFitModel object from a pretrained model, then create a SetFitTrainer object with
        the model, and then train the model
        """
        from setfit import SetFitModel, SetFitTrainer

        self._setfit_model = SetFitModel.from_pretrained(**self.setfit_model_kwargs)
        self.setfit_trainer_kwargs["model"] = self._setfit_model
        self.__trainer = SetFitTrainer(**self.setfit_trainer_kwargs)
        self.__trainer.train()
        if self._eval_dataset:
            self._metrics = self.__trainer.evaluate()
            self._logger.info(self._metrics)
        else:
            self._metrics = None

        if output_dir is not None:
            self.save(output_dir)

    def init_model(self):
        from setfit import SetFitModel

        self._setfit_model = SetFitModel.from_pretrained(**self.setfit_model_kwargs)

    def predict(self, text: Union[List[str], str], as_argilla_records: bool = True, **kwargs):
        """
        The function takes in a list of strings and returns a list of predictions

        Args:
          text (Union[List[str], str]): The text to be classified.
          as_argilla_records (bool): If True, the prediction will be returned as an Argilla record. If
        False, the prediction will be returned as a string. Defaults to True

        Returns:
          A list of predictions
        """
        if self._setfit_model is None:
            self._logger.warn("Using model without fine-tuning.")
            self.init_model()

        str_input = False
        if isinstance(text, str):
            text = [text]
            str_input = True

        predictions = self._setfit_model(text, **kwargs)

        formatted_prediction = []
        for val, pred in zip(text, predictions):
            if self._multi_label:
                pred = [self._id2label[idx] for idx, p in enumerate(pred) if p == 1]
                if as_argilla_records:
                    pred = self._record_class(
                        text=val, prediction=[(p, 1) for p in pred], multi_label=self._multi_label
                    )
            else:
                pred = self._id2label[int(pred)]
                if as_argilla_records:
                    pred = self._record_class(text=val, prediction=[(pred, 1)])
            formatted_prediction.append(pred)

        if str_input:
            formatted_prediction = formatted_prediction[0]
        return formatted_prediction

    def save(self, output_dir: str):
        """
        The function saves the model to the path specified, and also saves the label2id and id2label
        dictionaries to the same path

        Args:
          path (str): the path to save the model to
        """
        if not isinstance(output_dir, str):
            output_dir = str(output_dir)
        self._setfit_model.save_pretrained(output_dir)

        # store dict as json
        with open(output_dir + "/label2id.json", "w") as f:
            json.dump(self._label2id, f)
        with open(output_dir + "/id2label.json", "w") as f:
            json.dump(self._id2label, f)
