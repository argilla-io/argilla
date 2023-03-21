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

import argilla as rg
from argilla.training.utils import filter_allowed_args, get_default_args


class ArgillaTransformersTrainer(object):
    # @require_version("setfit", "0.6")
    def __init__(self, dataset, record_class, multi_label: bool = False, model: str = None, seed: int = None):
        import torch

        self.device = "cpu"
        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"

        if seed is None:
            seed = 42
        self._seed = seed

        if model is None:
            self.model = "distilbert-base-uncased-finetuned-sst-2-english"

        self._record_class = record_class
        self._multi_label = multi_label

        if isinstance(dataset, DatasetDict):
            self._train_dataset = dataset["train"]
            self._eval_dataset = dataset["test"]
        else:
            self._train_dataset = dataset
            self._eval_dataset = None

        if self._record_class == rg.TextClassificationRecord:
            if self._multi_label:
                self.multi_target_strategy = "one-vs-rest"
                self._column_mapping = {"text": "text", "binarized_label": "label"}
            else:
                self.multi_target_strategy = None
                self._column_mapping = {"text": "text", "label": "label"}

            if self._multi_label:
                self._id2label = dict(enumerate(self._train_dataset.features["label"][0].names))
            else:
                self._id2label = dict(enumerate(self._train_dataset.features["label"].names))
            self._label2id = {v: k for k, v in self._id2label.items()}
        elif self._record_class == rg.TokenClassificationRecord:
            self._column_mapping = {"text": "text", "token": "tokens", "ner_tags": "ner_tags"}
            raise NotImplementedError("rg.TokenClassificationRecord")
        else:
            raise NotImplementedError("rg.Text2TextRecord are not supported")

        self.init_args()

    def init_args(self):
        from transformers import (
            AutoModelForSequenceClassification,
            AutoModelForTokenClassification,
            AutoTokenizer,
            TrainingArguments,
        )

        self.tokenizer_kwargs = get_default_args(AutoTokenizer.from_pretrained)
        self.tokenizer_kwargs = self.model

        if self._record_class == rg.TextClassificationRecord:
            self._model_class = AutoModelForSequenceClassification
            self.model_kwargs = get_default_args(AutoModelForSequenceClassification.from_pretrained)
        elif self._record_class == rg.TokenClassificationRecord:
            self._model_class = AutoModelForTokenClassification
            self.model_kwargs = get_default_args(AutoModelForTokenClassification.from_pretrained)
        else:
            raise NotImplementedError("rg.Text2TextRecords are not supported yet.")
        self.model_kwargs["model"] = self.model

        self.trainer_kwargs = get_default_args(TrainingArguments.__init__)
        self.trainer_kwargs["evaluation_strategy"] = "epoch"
        self.trainer_kwargs["logging_steps"] = 30

    def update_config(
        self,
        **setfit_kwargs,
    ):
        """
        Updates the `setfit_model_kwargs` and `setfit_trainer_kwargs` dictionaries with the keyword
        arguments passed to the `update_config` function.
        """
        from setfit import SetFitModel, SetFitTrainer

        self.tokenizer_kwargs.update(setfit_kwargs)
        self.tokenizer_kwargs = filter_allowed_args(SetFitModel.from_pretrained, self.tokenizer_kwargs)

        self.model_kwargs.update(setfit_kwargs)
        self.model_kwargs = filter_allowed_args(SetFitTrainer.__init__, self.setfit_trainer_kwargs)

    def __repr__(self):
        formatted_string = []
        arg_dict = {
            "'AutoTokenizer'": self.tokenizer_kwargs,
            "'AutoModel'": self.model_kwargs,
            "'Trainer'": self.trainer_kwargs,
        }
        for arg_dict_key, arg_dict_single in arg_dict.items():
            formatted_string.append(arg_dict_key)
            for key, val in arg_dict_single.items():
                formatted_string.append(f"{key}: {val}")
        return "\n".join(formatted_string)

    # @require_version("setfit", "0.6")
    def train(self):
        """
        We create a SetFitModel object from a pretrained model, then create a SetFitTrainer object with
        the model, and then train the model
        """
        import numpy as np
        from datasets import load_metric
        from transformers import AutoTokenizer, Trainer, TrainingArguments, pipeline

        self._tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_kwargs)
        self._model = self._model_class.from_pretrained(**self.model_kwargs)
        self._training_args = TrainingArguments(**self.trainer_kwargs)

        def tokenize_function(examples):
            return self._tokenizer(examples["text"], padding="max_length", truncation=True)

        metric = load_metric("accuracy")

        def compute_metrics(eval_pred):
            logits, labels = eval_pred
            predictions = np.argmax(logits, axis=-1)
            return metric.compute(predictions=predictions, references=labels)

        self._tokenized_train_dataset = self._train_dataset.map(tokenize_function, batched=True)
        self._tokenized_eval_dataset = self._eval_dataset.map(tokenize_function, batched=True)

        self.__trainer = Trainer(
            args=self._training_args,
            model=self._model,
            train_dataset=self._tokenized_train_dataset,
            eval_dataset=self._tokenized_eval_dataset,
            compute_metrics=compute_metrics,
        )

        self.__trainer.train()
        if self._tokenized_eval_dataset:
            self._metrics = self.__trainer.evaluate()
        else:
            self._metrics = None

        self._pipeline = pipeline(model=self._model.to(self.device), tokenizer=self._tokenizer)

    def predict(self, text: Union[List[str], str], as_argilla_records: bool = True):
        """
        The function takes in a list of strings and returns a list of predictions

        Args:
          text (Union[List[str], str]): The text to be classified.
          as_argilla_records (bool): If True, the prediction will be returned as an Argilla record. If
        False, the prediction will be returned as a string. Defaults to True

        Returns:
          A list of predictions
        """
        str_input = False
        if isinstance(text, str):
            text = [text]
            str_input = True

        predictions = self._model(text)

        formatted_prediction = []
        for val, pred in zip(text, predictions):
            if self._multi_label:
                pred = [self._id2label[idx] for idx, p in enumerate(pred) if p == 1]
                if as_argilla_records:
                    pred = self._record_class(text=val, prediction=[(p, 1) for p in pred])
            else:
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
