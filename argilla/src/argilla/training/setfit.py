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

from argilla.client.models import TextClassificationRecord
from argilla.training.transformers import ArgillaTransformersTrainer
from argilla.training.utils import get_default_args
from argilla.utils.dependency import require_dependencies


class ArgillaSetFitTrainer(ArgillaTransformersTrainer):
    _logger = logging.getLogger("ArgillaSetFitTrainer")
    _logger.setLevel(logging.INFO)

    def __init__(self, *args, **kwargs):
        require_dependencies(["torch", "datasets", "transformers", "setfit>=1.0.0"])
        if kwargs.get("model") is None and "model" in kwargs:
            kwargs["model"] = "all-MiniLM-L6-v2"
            self._logger.warning(f"No model defined. Using the default model {kwargs['model']}.")
        self.multi_target_strategy = None
        self._column_mapping = None
        super().__init__(*args, **kwargs)

        if self._record_class is not TextClassificationRecord:
            raise NotImplementedError("SetFit only supports the `TextClassification` task.")

        if self._multi_label:
            # We shall rename binarized_label as label, we need to remove the column that was previously called label.
            # This change is due to SetFit version >=1.0.0
            self._dataset = self._dataset.remove_columns("label")
            self._eval_dataset = self._eval_dataset.remove_columns("label")
            self._train_dataset = self._train_dataset.remove_columns("label")
            self._column_mapping = {"text": "text", "binarized_label": "label"}
            self.multi_target_strategy = "one-vs-rest"
        else:
            self.multi_target_strategy = None
            self._column_mapping = {"text": "text", "label": "label"}
        self.init_training_args()

    def init_training_args(self) -> None:
        from setfit import SetFitModel, SetFitTrainer

        # SetFit only: we get both the HuggingFace Hub args and the SetFit-specific args
        # We get the default args for `_from_pretrained` first to override the shared args
        # with the HuggingFace Hub specific args
        self.model_kwargs = get_default_args(SetFitModel._from_pretrained)
        self.model_kwargs.update(get_default_args(SetFitModel.from_pretrained))

        # Due to an inconsistency between `pretrained_model_name_or_path` with both `model_id` and `revision`
        # we pop both `model_id` and `revision`
        self.model_kwargs.pop("model_id", None)
        self.model_kwargs.pop("revision", None)

        self.model_kwargs["pretrained_model_name_or_path"] = self._model
        self.model_kwargs["multi_target_strategy"] = self.multi_target_strategy
        self.model_kwargs["device"] = self.device

        self.trainer_kwargs = get_default_args(SetFitTrainer.__init__)
        self.trainer_kwargs["column_mapping"] = self._column_mapping
        self.trainer_kwargs["train_dataset"] = self._train_dataset
        self.trainer_kwargs["eval_dataset"] = self._eval_dataset
        self.trainer_kwargs["seed"] = self._seed

        self.trainer_model = None

    def update_config(
        self,
        **kwargs,
    ) -> None:
        """
        Updates the `model_kwargs` and `trainer_kwargs` dictionaries with the keyword
        arguments passed to the `update_config` function.
        """
        self.model_kwargs.update((k, v) for k, v in kwargs.items() if k in self.model_kwargs)
        self.trainer_kwargs.update((k, v) for k, v in kwargs.items() if k in self.trainer_kwargs)

    def __repr__(self):
        formatted_string = []
        arg_dict = {
            "'SetFitModel'": self.model_kwargs,
            "'SetFitTrainer'": self.trainer_kwargs,
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

        self.trainer_model = SetFitModel.from_pretrained(**self.model_kwargs)
        self.trainer_kwargs["model"] = self.trainer_model
        self._trainer = SetFitTrainer(**self.trainer_kwargs)
        self._trainer.train()
        if self._eval_dataset:
            self._metrics = self._trainer.evaluate()
            self._logger.info(self._metrics)
        else:
            self._metrics = None

        if output_dir is not None:
            self.save(output_dir)

    def init_model(self):
        from setfit import SetFitModel

        self.trainer_model = SetFitModel.from_pretrained(**self.model_kwargs)

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
        if self.trainer_model is None:
            self._logger.warning("Using model without fine-tuning.")
            self.init_model()

        str_input = False
        if isinstance(text, str):
            text = [text]
            str_input = True

        predictions = self.trainer_model.predict_proba(text, **kwargs)

        formatted_prediction = []
        for val, pred in zip(text, predictions):
            pred = {self._id2label[idx]: float(p) for idx, p in enumerate(pred)}
            if as_argilla_records:
                pred = self._record_class(
                    text=val, prediction=[(k, v) for k, v in pred.items()], multi_label=self._multi_label
                )
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
        self.trainer_model.save_pretrained(output_dir)

        # store dict as json
        with open(output_dir + "/label2id.json", "w") as f:
            json.dump(self._label2id, f)
        with open(output_dir + "/id2label.json", "w") as f:
            json.dump(self._id2label, f)
