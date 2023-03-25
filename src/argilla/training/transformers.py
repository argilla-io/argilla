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
from argilla.training.utils import _apply_column_mapping, get_default_args


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
            self.model = "microsoft/deberta-v3-base"
        else:
            self.model = model

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
                self._label_list = self._train_dataset.features["label"][0].names
            else:
                self._id2label = dict(enumerate(self._train_dataset.features["label"].names))
                self._label_list = self._train_dataset.features["label"].names
            self._label2id = {v: k for k, v in self._id2label.items()}

        elif self._record_class == rg.TokenClassificationRecord:
            self._column_mapping = {"text": "text", "token": "tokens", "ner_tags": "ner_tags"}
            self._id2label = dict(enumerate(self._label_list))
            self._label2id = {v: k for k, v in self._id2label.items()}
            self._label_list = self._train_dataset.features["ner_tags"].feature.names
            raise NotImplementedError("rg.TokenClassificationRecord")
        else:
            raise NotImplementedError("rg.Text2TextRecord are not supported")

        self.init_args()

    def init_args(self):
        from transformers import (
            AutoModelForSequenceClassification,
            AutoModelForTokenClassification,
            TrainingArguments,
        )

        # self.tokenizer_kwargs = get_default_args(AutoTokenizer.from_pretrained)

        if self._record_class == rg.TextClassificationRecord:
            self._model_class = AutoModelForSequenceClassification
            if self._multi_label:
                self._train_dataset = _apply_column_mapping(self._train_dataset, self._column_mapping)
                if self._eval_dataset is not None:
                    self._eval_dataset = _apply_column_mapping(self._eval_dataset, self._column_mapping)
            # self.model_kwargs = get_default_args(AutoModelForSequenceClassification.from_pretrained)
        elif self._record_class == rg.TokenClassificationRecord:
            self._model_class = AutoModelForTokenClassification
            # self.model_kwargs = get_default_args(AutoModelForTokenClassification.from_pretrained)
        else:
            raise NotImplementedError("rg.Text2TextRecords are not supported yet.")
        self.model_kwargs = {}
        self.model_kwargs["pretrained_model_name_or_path"] = self.model
        self.model_kwargs["num_labels"] = len(self._label_list)
        self.model_kwargs["id2label"] = self._id2label
        self.model_kwargs["label2id"] = self._label2id
        if self._multi_label:
            self.model_kwargs["problem_type"] = "multi_label_classification"

        self.trainer_kwargs = get_default_args(TrainingArguments.__init__)
        self.trainer_kwargs["evaluation_strategy"] = "epoch"
        self.trainer_kwargs["logging_steps"] = 30

    def update_config(
        self,
        **kwargs,
    ):
        """
        Updates the `setfit_model_kwargs` and `setfit_trainer_kwargs` dictionaries with the keyword
        arguments passed to the `update_config` function.
        """

        # self.tokenizer_kwargs.update(setfit_kwargs)
        # self.tokenizer_kwargs = filter_allowed_args(SetFitModel.from_pretrained, self.tokenizer_kwargs)

        pass

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

    def preprocess_datasets(self):
        from transformers import (
            DataCollatorForTokenClassification,
        )

        def text_classification_preprocess_function(examples):
            tokens = self._tokenizer(examples["text"], truncation=True, padding=True, max_length=512)
            return tokens

        def token_classification_preprocess_function(examples):
            tokenized_inputs = self._tokenizer(
                examples["tokens"], truncation=True, padding=True, is_split_into_words=True, max_length=512
            )

            labels = []
            for i, label in enumerate(examples["ner_tags"]):
                word_ids = tokenized_inputs.word_ids(batch_index=i)  # Map tokens to their respective word.
                previous_word_idx = None
                label_ids = []
                for word_idx in word_ids:  # Set the special tokens to -100.
                    if word_idx is None:
                        label_ids.append(-100)
                    elif word_idx != previous_word_idx:  # Only label the first token of a given word.
                        label_ids.append(label[word_idx])
                    else:
                        label_ids.append(-100)
                    previous_word_idx = word_idx
                labels.append(label_ids)

            tokenized_inputs["labels"] = labels
            return tokenized_inputs

        # set correct tokenization
        if self._record_class == rg.TextClassificationRecord:
            preprocess_function = text_classification_preprocess_function
            self._data_collator = None
        elif self._record_class == rg.TokenClassificationRecord:
            preprocess_function = token_classification_preprocess_function
            self._data_collator = DataCollatorForTokenClassification(tokenizer=self._tokenizer, max_length=512)
        else:
            raise NotImplementedError("")

        self._tokenized_train_dataset = self._train_dataset.map(preprocess_function, batched=True)
        if self._eval_dataset is not None:
            self._tokenized_eval_dataset = self._eval_dataset.map(preprocess_function, batched=True)

    def compute_metrics(self):
        import evaluate
        import numpy as np

        func = None
        if self._record_class == rg.TextClassificationRecord:
            accuracy = evaluate.load("accuracy")
            f1 = evaluate.load("f1", config_name="multilabel")

            def compute_metrics_text_classification_multi_label(eval_pred):
                logits, labels = eval_pred

                # apply sigmoid
                predictions = (1.0 / (1 + np.exp(-logits))) > 0.5

                # f1 micro averaged
                metrics = f1.compute(predictions=predictions, references=labels, average="micro")
                # f1 per label
                per_label_metric = f1.compute(predictions=predictions, references=labels, average=None)
                for label, f1_score in zip(self._label_list, per_label_metric["f1"]):
                    metrics[f"f1_{label}"] = f1_score

                return metrics

            def compute_metrics_text_classification(eval_pred):
                predictions, labels = eval_pred
                predictions = np.argmax(predictions, axis=1)
                return accuracy.compute(predictions=predictions, references=labels)

            if self._multi_label:
                func = compute_metrics_text_classification_multi_label
            else:
                func = compute_metrics_text_classification

        elif self._record_class == rg.TokenClassificationRecord:
            seqeval = evaluate.load("seqeval")

            def compute_metrics(p):
                predictions, labels = p
                predictions = np.argmax(predictions, axis=2)

                true_predictions = [
                    [self._label_list[p] for (p, l) in zip(prediction, label) if l != -100]
                    for prediction, label in zip(predictions, labels)
                ]
                true_labels = [
                    [self._label_list[l] for (p, l) in zip(prediction, label) if l != -100]
                    for prediction, label in zip(predictions, labels)
                ]

                results = seqeval.compute(predictions=true_predictions, references=true_labels)
                return {
                    "precision": results["overall_precision"],
                    "recall": results["overall_recall"],
                    "f1": results["overall_f1"],
                    "accuracy": results["overall_accuracy"],
                }

            func = compute_metrics
        else:
            raise NotImplementedError("")
        return func

    # @require_version("setfit", "0.6")
    def train(self, path: str = None):
        """
        We create a SetFitModel object from a pretrained model, then create a SetFitTrainer object with
        the model, and then train the model
        """
        from transformers import (
            AutoTokenizer,
            Trainer,
            TrainingArguments,
            pipeline,
        )

        # check required path argument
        if path is not None:
            self.trainer_kwargs["output_dir"] = path
        else:
            raise ValueError("You must specify a path to save the model to use `trainer.train(path=<my_path>).")

        # prepare data
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_kwargs.get("pretrained_model_name_or_path"))
        self.preprocess_datasets()

        # load model
        self._model = self._model_class.from_pretrained(**self.model_kwargs)

        # get metrics function
        compute_metrics = self.compute_metrics()

        # set trainer
        self._training_args = TrainingArguments(**self.trainer_kwargs)
        self.__trainer = Trainer(
            args=self._training_args,
            model=self._model,
            train_dataset=self._tokenized_train_dataset,
            eval_dataset=self._tokenized_eval_dataset,
            compute_metrics=compute_metrics,
            data_collator=self._data_collator,
        )

        #  train
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
