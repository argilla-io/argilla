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

import argilla as rg
from argilla.training.transformers import ArgillaTransformersTrainer
from argilla.training.utils import (
    filter_allowed_args,
)
from argilla.utils.dependency import require_version


class ArgillaTransformersPEFTTrainer(ArgillaTransformersTrainer):
    _logger = logging.getLogger("ArgillaTransformersPEFTTrainer")
    _logger.setLevel(logging.INFO)

    import sys

    if sys.version_info[1] < 9 or sys.version_info[0] < 3:
        raise Exception("Must be using Python 3.9 or higher or PEFT won't work.")

    require_version("peft")

    def init_training_args(self):
        super().init_training_args()
        self.lora_training_args = {
            "r": 8,
            "target_modules": None,
            "lora_alpha": 16,
            "lora_dropout": 0.1,
            "fan_in_fan_out": False,
            "bias": "none",
            "modules_to_save": None,
            "init_lora_weights": True,
        }

    def init_model(self, new: bool = False):
        from peft import LoraConfig, PeftConfig, PeftModel, get_peft_model
        from transformers import AutoTokenizer

        if self._record_class == rg.TextClassificationRecord:
            task_type = "SEQ_CLS"
        elif self._record_class == rg.TokenClassificationRecord:
            task_type = "TOKEN_CLS"
        else:
            raise NotImplementedError("This is not implemented yet.")

        try:
            config = PeftConfig.from_pretrained(self.model_kwargs["pretrained_model_name_or_path"])
            model = self._model_class.from_pretrained(config.base_model_name_or_path, return_dict=True)
            self._model_sub_class = model.__class__
            model = PeftModel.from_pretrained(model, self.model_kwargs["pretrained_model_name_or_path"])
        except Exception:
            config = LoraConfig(task_type=task_type, inference_mode=False, r=8, lora_alpha=16, lora_dropout=0.1)
            model = self._model_class.from_pretrained(**self.model_kwargs, return_dict=True)
            self._model_sub_class = model.__class__
            model = get_peft_model(model, config)
        self._transformers_tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path)
        self._transformers_model = model

    def init_pipeline(self):
        pass
        import transformers
        from transformers import pipeline

        if self.device == "cuda":
            device = 0
        else:
            device = -1

        self._transformers_model.__class__ = self._model_sub_class

        if self._record_class == rg.TextClassificationRecord:
            if transformers.__version__ >= "4.20.0":
                kwargs = {"top_k": None}
            else:
                kwargs = {"return_all_scores": True}
            self._pipeline = pipeline(
                task="text-classification",
                model=self._transformers_model,
                tokenizer=self._transformers_tokenizer,
                device=device,
                **kwargs,
            )
        elif self._record_class == rg.TokenClassificationRecord:
            self._pipeline = pipeline(
                task="token-classification",
                model=self._transformers_model,
                tokenizer=self._transformers_tokenizer,
                aggregation_strategy="first",
                device=device,
            )
        else:
            raise NotImplementedError("This is not implemented.")

    def update_config(self, **kwargs):
        """
        Updates the `setfit_model_kwargs` and `setfit_trainer_kwargs` dictionaries with the keyword
        arguments passed to the `update_config` function.
        """
        from transformers import TrainingArguments

        self.trainer_kwargs.update(filter_allowed_args(TrainingArguments.__init__, **kwargs))

    def __repr__(self):
        formatted_string = []
        arg_dict = {
            "'AutoModel'": self.model_kwargs,
            "'Trainer'": self.trainer_kwargs,
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

        if self._transformers_model is None:
            self._logger.warning("Using model without fine-tuning.")
            self.init_model(new=False)

        str_input = False
        if isinstance(text, str):
            text = [text]
            str_input = True

        inputs = self._transformers_tokenizer(text, truncation=True, padding="longest", return_tensors="pt")

        with torch.no_grad():
            logits = self._transformers_model(**inputs).logits

        if self._record_class == rg.TextClassificationRecord:
            probabilities = torch.softmax(logits, dim=1)
            predictions = []
            for probability in probabilities:
                prediction = []
                for label, score in zip(self._id2label.values(), probability):
                    prediction.append({"label": label, "score": score})
                predictions.append(prediction)
        else:
            tokens = inputs.tokens()
            predictions = logits.argmax(dim=2)

        if as_argilla_records:
            formatted_prediction = []

            for val, pred in zip(text, predictions):
                if self._record_class == rg.TextClassificationRecord:
                    formatted_prediction.append(
                        self._record_class(
                            text=val,
                            prediction=[(entry["label"], entry["score"]) for entry in pred],
                            multi_label=self._multi_label,
                        )
                    )
                elif self._record_class == rg.TokenClassificationRecord:
                    _pred = [(value["entity_group"], value["start"], value["end"]) for value in pred]
                    encoding = self._pipeline.tokenizer(val)
                    word_ids = sorted(set(encoding.word_ids()) - {None})
                    tokens = []
                    for word_id in word_ids:
                        char_span = encoding.word_to_chars(word_id)
                        tokens.append(val[char_span.start : char_span.end].lstrip().rstrip())
                    formatted_prediction.append(
                        self._record_class(
                            text=val,
                            tokens=tokens,
                            prediction=_pred,
                        )
                    )

                else:
                    raise NotImplementedError("This is not implemented yet.")
        else:
            formatted_prediction = predictions

        if str_input:
            formatted_prediction = formatted_prediction[0]

        return formatted_prediction

    def save(self, output_dir: str):
        """
        The function saves the model to the path specified, and also saves the label2id and id2label
        dictionaries to the same path

        Args:
          output_dir (str): the path to save the model to
        """
        self._transformers_model.save_pretrained(output_dir)
        self._transformers_tokenizer.save_pretrained(output_dir)
