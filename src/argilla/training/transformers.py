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

import argilla as rg
from argilla.training.base import ArgillaTrainerSkeleton
from argilla.training.utils import (
    _apply_column_mapping,
    filter_allowed_args,
    get_default_args,
)
from argilla.utils.dependency import require_version


class ArgillaTransformersTrainer(ArgillaTrainerSkeleton):
    _logger = logging.getLogger("ArgillaTransformersTrainer")
    _logger.setLevel(logging.INFO)

    require_version("torch")
    require_version("datasets")
    require_version("transformers")
    require_version("evaluate")
    require_version("seqeval")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        import torch
        from transformers import (
            AutoModelForSequenceClassification,
            AutoModelForTokenClassification,
        )

        self._transformers_model = None
        self._transformers_tokenizer = None
        self._pipeline = None

        self.device = "cpu"
        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"

        if self._seed is None:
            self._seed = 42

        if self._model is None:
            self._model = "microsoft/deberta-v3-base"

        if isinstance(self._dataset, DatasetDict):
            self._train_dataset = self._dataset["train"]
            self._eval_dataset = self._dataset["test"]
        else:
            self._train_dataset = self._dataset
            self._eval_dataset = None

        if self._record_class == rg.TextClassificationRecord:
            if self._multi_label:
                self._id2label = dict(enumerate(self._train_dataset.features["label"][0].names))
                self._label_list = self._train_dataset.features["label"][0].names
            else:
                self._id2label = dict(enumerate(self._train_dataset.features["label"].names))
                self._label_list = self._train_dataset.features["label"].names
            self._label2id = {v: k for k, v in self._id2label.items()}

            self._model_class = AutoModelForSequenceClassification

        elif self._record_class == rg.TokenClassificationRecord:
            self._label_list = self._train_dataset.features["ner_tags"].feature.names
            self._id2label = dict(enumerate(self._label_list))
            self._label2id = {v: k for k, v in self._id2label.items()}

            self._model_class = AutoModelForTokenClassification
        else:
            raise NotImplementedError("rg.Text2TextRecord is not supported.")

        self.init_training_args()

    def init_training_args(self):
        from transformers import TrainingArguments

        if self._record_class == rg.TextClassificationRecord:
            columns_mapping = {"text": "text", "label": "binarized_label"}
            if self._multi_label:
                self._train_dataset = _apply_column_mapping(self._train_dataset, columns_mapping)

                if self._eval_dataset is not None:
                    self._eval_dataset = _apply_column_mapping(self._eval_dataset, columns_mapping)

        self.model_kwargs = {}
        self.model_kwargs["pretrained_model_name_or_path"] = self._model
        self.model_kwargs["num_labels"] = len(self._label_list)
        self.model_kwargs["id2label"] = self._id2label
        self.model_kwargs["label2id"] = self._label2id
        if self._multi_label:
            self.model_kwargs["problem_type"] = "multi_label_classification"

        self.trainer_kwargs = get_default_args(TrainingArguments.__init__)
        self.trainer_kwargs["evaluation_strategy"] = "no" if self._eval_dataset is None else "epoch"
        self.trainer_kwargs["logging_steps"] = 30

    def init_model(self, new: bool = False):
        from transformers import AutoTokenizer

        self._transformers_tokenizer = AutoTokenizer.from_pretrained(
            self.model_kwargs.get("pretrained_model_name_or_path")
        )
        if new:
            model_kwargs = self.model_kwargs
        else:
            model_kwargs = {"pretrained_model_name_or_path": self.model_kwargs.get("pretrained_model_name_or_path")}
        self._transformers_model = self._model_class.from_pretrained(**model_kwargs)

    def init_pipeline(self):
        import transformers
        from transformers import pipeline

        if self.device == "cuda":
            device = 0
        else:
            device = -1

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

    def preprocess_datasets(self):
        from transformers import (
            DataCollatorForTokenClassification,
        )

        def text_classification_preprocess_function(examples):
            tokens = self._transformers_tokenizer(examples["text"], padding=True, truncation=True)

            return tokens

        def token_classification_preprocess_function(examples):
            tokenized_inputs = self._transformers_tokenizer(
                examples["tokens"], padding=True, is_split_into_words=True, truncation=True
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
            self._data_collator = DataCollatorForTokenClassification(tokenizer=self._transformers_tokenizer)
        else:
            raise NotImplementedError("")

        self._tokenized_train_dataset = self._train_dataset.map(preprocess_function, batched=True)
        if self._eval_dataset is not None:
            self._tokenized_eval_dataset = self._eval_dataset.map(preprocess_function, batched=True)
        else:
            self._tokenized_eval_dataset = None

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
            raise NotImplementedError("Text2Text is not implemented.")
        return func

    def train(self, output_dir: str):
        """
        We create a SetFitModel object from a pretrained model, then create a SetFitTrainer object with
        the model, and then train the model
        """
        from transformers import (
            Trainer,
            TrainingArguments,
        )

        # check required path argument
        self.trainer_kwargs["output_dir"] = output_dir

        # prepare data
        self.init_model(new=True)
        self.preprocess_datasets()

        # get metrics function
        compute_metrics = self.compute_metrics()

        # set trainer
        self._training_args = TrainingArguments(**self.trainer_kwargs)
        self._transformers_trainer = Trainer(
            args=self._training_args,
            model=self._transformers_model,
            train_dataset=self._tokenized_train_dataset,
            eval_dataset=self._tokenized_eval_dataset,
            compute_metrics=compute_metrics,
            data_collator=self._data_collator,
        )

        #  train
        self._transformers_trainer.train()
        if self._tokenized_eval_dataset:
            self._metrics = self._transformers_trainer.evaluate()
            self._logger.info(self._metrics)
        else:
            self._metrics = None

        self.save(output_dir)

        self.init_pipeline()

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
        if self._pipeline is None:
            self._logger.warning("Using model without fine-tuning.")
            self.init_model(new=False)
            self.init_pipeline()

        str_input = False
        if isinstance(text, str):
            text = [text]
            str_input = True

        predictions = self._pipeline(text, **kwargs)

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
