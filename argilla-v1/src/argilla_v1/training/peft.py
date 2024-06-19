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
from typing import List, Union

import numpy as np

from argilla_v1.client.models import TextClassificationRecord, TokenClassificationRecord
from argilla_v1.training.transformers import ArgillaTransformersTrainer
from argilla_v1.training.utils import filter_allowed_args
from argilla_v1.utils.dependency import require_dependencies


class ArgillaPeftTrainer(ArgillaTransformersTrainer):
    _logger = logging.getLogger("ArgillaTransformersPEFTTrainer")
    _logger.setLevel(logging.INFO)

    import sys

    if sys.version_info < (3, 9):
        raise Exception("Must be using Python 3.9 or higher or PEFT won't work.")

    def init_training_args(self):
        require_dependencies("peft")
        super().init_training_args()

        self.lora_kwargs = {
            "r": 8,
            "target_modules": None,
            "lora_alpha": 16,
            "lora_dropout": 0.1,
            "fan_in_fan_out": False,
            "bias": "none",
            "inference_mode": False,
            "modules_to_save": None,
            "init_lora_weights": True,
        }

    def init_model(self, new: bool = False):
        from peft import LoraConfig, PeftConfig, PeftModel, get_peft_model
        from transformers import AutoTokenizer

        if self._record_class == TextClassificationRecord:
            self.lora_kwargs["task_type"] = "SEQ_CLS"
        elif self._record_class == TokenClassificationRecord:
            self.lora_kwargs["task_type"] = "TOKEN_CLS"
        else:
            raise NotImplementedError("`rg.Text2TextRecord` is not supported yet.")

        try:
            config = PeftConfig.from_pretrained(self.model_kwargs["pretrained_model_name_or_path"])
            model = self._model_class.from_pretrained(
                config.base_model_name_or_path,
                return_dict=True,
                num_labels=len(self._id2label),
                id2label=self._id2label,
                label2id=self._label2id,
            )
            self._model_sub_class = model.__class__
            model = PeftModel.from_pretrained(model, self.model_kwargs["pretrained_model_name_or_path"])
        except Exception:
            config = LoraConfig(**self.lora_kwargs)
            model = self._model_class.from_pretrained(**self.model_kwargs, return_dict=True)
            self._model_sub_class = model.__class__
            model = get_peft_model(model, config)
        self.trainer_tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path, add_prefix_space=True)
        self.trainer_model = model.to(self.device)

    def init_pipeline(self):
        pass

    def update_config(self, **kwargs):
        """
        Updates the `model_kwargs` and `trainer_kwargs` dictionaries with the keyword
        arguments passed to the `update_config` function.
        """
        super().update_config(**kwargs)

        from peft import LoraConfig

        self.lora_kwargs.update(filter_allowed_args(LoraConfig.__init__, **kwargs))

    def __repr__(self):
        formatted_string = []
        arg_dict = {
            "'AutoModel'": self.model_kwargs,
            "'Trainer'": self.trainer_kwargs,
            "'LoraConfig'": self.lora_kwargs,
        }
        for arg_dict_key, arg_dict_single in arg_dict.items():
            formatted_string.append(arg_dict_key)
            for key, val in arg_dict_single.items():
                formatted_string.append(f"{key}: {val}")
        return "\n".join(formatted_string)

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
        import torch

        if self.trainer_model is None:
            self._logger.warning("Using model without fine-tuning.")
            self.init_model(new=False)

        str_input = False
        if isinstance(text, str):
            text = [text]
            str_input = True

        if self._record_class == TextClassificationRecord:
            inputs = self.trainer_tokenizer(text, truncation=True, padding="longest", return_tensors="pt")

            with torch.no_grad():
                logits = self.trainer_model(**inputs).logits

            if self._multi_label:
                probabilities = torch.sigmoid(logits)
            else:
                probabilities = torch.softmax(logits, dim=1)
            predictions = []
            for probability in probabilities:
                prediction = []
                for idx, score in enumerate(probability):
                    prediction.append({"label": self._id2label[idx], "score": score})
                predictions.append(prediction)
        else:
            # Tokenize the text
            inputs_with_offsets = self.trainer_tokenizer(
                text, truncation=True, padding="longest", return_offsets_mapping=True, return_tensors="pt"
            )
            inputs_with_offsets = {k: v.to(self.device) for k, v in inputs_with_offsets.items()}
            offsets = inputs_with_offsets["offset_mapping"]

            # Perform the forward pass through the model
            with torch.no_grad():
                outputs = self.trainer_model(**{k: v for k, v in inputs_with_offsets.items() if k != "offset_mapping"})
                probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1).tolist()
                predictions = outputs.logits.argmax(dim=-1).tolist()

            # Iterate over the predictions and the offsets
            batch_formatted_predictions = []
            for batch_idx, example in enumerate(text):
                formatted_predictions = []
                idx = 0
                while idx < len(predictions[batch_idx]):
                    pred = predictions[batch_idx][idx]
                    label = self.trainer_model.config.id2label[pred]
                    if label != "O":
                        # Remove the B- or I-
                        label = label[2:]
                        start, end = offsets[batch_idx][idx]

                        # Grab all the tokens labeled with I-label
                        all_scores = []
                        while (
                            idx < len(predictions[batch_idx])
                            and self.trainer_model.config.id2label[predictions[batch_idx][idx]] == f"I-{label}"
                        ):
                            all_scores.append(probabilities[batch_idx][idx][pred])
                            _, end = offsets[batch_idx][idx]
                            idx += 1

                        # If the entity is only one token, we don't need to do anything
                        if start != end:
                            # The score is the mean of all the scores of the tokens in that grouped entity
                            score = None if np.isnan(np.mean(all_scores).item()) else np.mean(all_scores).item()
                            word = example[start:end]
                            formatted_predictions.append(
                                {
                                    "entity_group": label,
                                    "score": score,
                                    "word": word,
                                    "start": int(start),
                                    "end": int(end),
                                }
                            )
                    idx += 1
                batch_formatted_predictions.append(formatted_predictions)
            predictions = batch_formatted_predictions

        if as_argilla_records:
            formatted_prediction = []

            for val, pred in zip(text, predictions):
                if self._record_class == TextClassificationRecord:
                    formatted_prediction.append(
                        self._record_class(
                            text=val,
                            prediction=[(entry["label"], entry["score"]) for entry in pred],
                            multi_label=self._multi_label,
                        )
                    )
                elif self._record_class == TokenClassificationRecord:
                    formatted_prediction.append(
                        self._record_class(
                            text=val,
                            tokens=val.split(),
                            prediction=[
                                (
                                    char_spans["entity_group"],
                                    char_spans["start"],
                                    char_spans["end"],
                                    char_spans["score"],
                                )
                                for char_spans in pred
                            ],
                        )
                    )

                else:
                    raise NotImplementedError("`rg.Text2TextRecord` is not supported yet.")
        else:
            formatted_prediction = predictions

        if str_input:
            formatted_prediction = formatted_prediction[0]

        return formatted_prediction

    def save(self, output_dir: str):
        """
        The function saves the model to the path specified and also saves the label2id and id2label
        dictionaries to the same path

        Args:
          output_dir (str): the path to save the model to
        """
        self.trainer_model.save_pretrained(output_dir)
        self.trainer_tokenizer.save_pretrained(output_dir)
