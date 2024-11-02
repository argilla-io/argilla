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

from datasets import DatasetDict

from argilla_v1.client.models import TokenClassificationRecord
from argilla_v1.training.base import ArgillaTrainerSkeleton
from argilla_v1.training.utils import filter_allowed_args, get_default_args
from argilla_v1.utils.dependency import require_dependencies


class ArgillaSpanMarkerTrainer(ArgillaTrainerSkeleton):
    _logger = logging.getLogger("ArgillaSpanMarkerTrainer")
    _logger.setLevel(logging.INFO)

    def __init__(self, *args, **kwargs) -> None:
        require_dependencies(["datasets", "span_marker>=1.2", "transformers>=4.19.0"])
        super().__init__(*args, **kwargs)

        import torch
        from span_marker import SpanMarkerModel

        self.trainer_model = None

        self.device = "cpu"
        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"

        if self._seed is None:
            self._seed = 42

        if self._model is None:
            self._model = "bert-base-cased"
            self._logger.warning(f"No model defined. Using the default model {self._model}.")

        if isinstance(self._dataset, DatasetDict):
            self._train_dataset = self._dataset["train"]
            self._eval_dataset = self._dataset["test"]
        else:
            self._train_dataset = self._dataset
            self._eval_dataset = None

        if self._record_class == TokenClassificationRecord:
            self._column_mapping = {"text": "text", "token": "tokens", "ner_tags": "ner_tags"}
            self._label_list = self._train_dataset.features["ner_tags"].feature.names

            self._model_class = SpanMarkerModel
        else:
            raise NotImplementedError("Text2TextRecord and TextClassification are not supported.")

        self.init_training_args()

    def init_training_args(self) -> None:
        from transformers import TrainingArguments

        self.model_kwargs = {"pretrained_model_name_or_path": self._model, "labels": self._label_list}

        self.trainer_kwargs = get_default_args(TrainingArguments.__init__)
        self.trainer_kwargs["evaluation_strategy"] = "no" if self._eval_dataset is None else "epoch"
        self.trainer_kwargs["logging_steps"] = 30
        self.trainer_kwargs["learning_rate"] = 5e-5
        self.trainer_kwargs["weight_decay"] = 0.01

    def init_model(self) -> None:
        self.trainer_model = self._model_class.from_pretrained(**self.model_kwargs).to(self.device)

    def update_config(self, **kwargs) -> None:
        """
        Updates the `model_kwargs` and `trainer_kwargs` dictionaries with the keyword
        arguments passed to the `update_config` function.
        """
        from span_marker import SpanMarkerConfig
        from transformers import TrainingArguments

        self.model_kwargs.update(filter_allowed_args(SpanMarkerConfig.__init__, **kwargs))
        self.trainer_kwargs.update(filter_allowed_args(TrainingArguments.__init__, **kwargs))

    def __repr__(self):
        formatted_string = []
        arg_dict = {"'SpanMarkerModel'": self.model_kwargs, "'Trainer'": self.trainer_kwargs}
        for arg_dict_key, arg_dict_single in arg_dict.items():
            formatted_string.append(arg_dict_key)
            for key, val in arg_dict_single.items():
                formatted_string.append(f"{key}: {val}")
        return "\n".join(formatted_string)

    def train(self, output_dir: str):
        """
        We create a SetFitModel object from a pretrained model, then create a SetFitTrainer object with
        the model, and then train the model
        """
        from span_marker import Trainer
        from transformers import TrainingArguments

        self.trainer_kwargs["output_dir"] = output_dir

        # prepare data
        self.init_model()

        # set trainer
        self.trainer = Trainer(
            args=TrainingArguments(**self.trainer_kwargs),
            model=self.trainer_model,
            train_dataset=self._train_dataset,
            eval_dataset=self._eval_dataset,
        )

        # train
        self.trainer.train()
        if self._eval_dataset:
            self._metrics = self.trainer.evaluate()
            self._logger.info(self._metrics)
        else:
            self._metrics = None

        self.save(output_dir)

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
        from datasets import Dataset

        if self.trainer_model is None:
            self._logger.warning("Using model without fine-tuning.")
            self.init_model()

        str_input = False
        if isinstance(text, str):
            text = [text]
            str_input = True

        entities_list = self.trainer_model.predict(text, **kwargs)

        if as_argilla_records:
            formatted_prediction = []

            for sentence, entities in zip(text, entities_list):
                predictions = [
                    (entity["label"], entity["char_start_index"], entity["char_end_index"], entity["score"])
                    for entity in entities
                ]
                dataset = Dataset.from_dict({"tokens": text})
                encoding = self.trainer_model.tokenizer({"tokens": dataset["tokens"]}, return_batch_encoding=True)[
                    "batch_encoding"
                ]
                word_ids = sorted(set(encoding.word_ids()) - {None})
                tokens = []
                for word_id in word_ids:
                    char_span = encoding.word_to_chars(word_id)
                    tokens.append(sentence[char_span.start : char_span.end].lstrip().rstrip())
                formatted_prediction.append(self._record_class(text=sentence, tokens=tokens, prediction=predictions))
        else:
            formatted_prediction = entities_list

        if str_input:
            return formatted_prediction[0]
        return formatted_prediction

    def save(self, output_dir: str):
        """
        The function saves the model to the path specified, and also saves the label2id and id2label
        dictionaries to the same path

        Args:
          output_dir (str): the path to save the model to
        """
        self.trainer_model.save_pretrained(output_dir)
