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

from argilla_v1.client.models import TextClassificationRecord, TokenClassificationRecord
from argilla_v1.training.base import ArgillaTrainerSkeleton
from argilla_v1.training.utils import _apply_column_mapping, filter_allowed_args, get_default_args
from argilla_v1.utils.dependency import require_dependencies


class ArgillaTransformersTrainer(ArgillaTrainerSkeleton):
    _logger = logging.getLogger("ArgillaTransformersTrainer")
    _logger.setLevel(logging.INFO)

    def __init__(self, *args, **kwargs):
        require_dependencies(["torch", "datasets", "transformers", "evaluate", "seqeval"])
        super().__init__(*args, **kwargs)

        import torch
        from transformers import (
            AutoModelForSequenceClassification,
            AutoModelForTokenClassification,
            set_seed,
        )

        self.trainer_model = None
        self.trainer_tokenizer = None
        self.trainer_pipeline = None

        self.device = "cpu"
        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"

        if self._seed is None:
            self._seed = 42
        set_seed(self._seed)

        if self._model is None:
            self._model = "bert-base-cased"
            self._logger.warning(f"No model defined. Using the default model {self._model}.")

        if isinstance(self._dataset, DatasetDict):
            self._train_dataset = self._dataset["train"]
            self._eval_dataset = self._dataset["test"]
        else:
            self._train_dataset = self._dataset
            self._eval_dataset = None

        if self._record_class == TextClassificationRecord:
            if self._multi_label:
                self._id2label = dict(enumerate(self._train_dataset.features["label"][0].names))
                self._label_list = self._train_dataset.features["label"][0].names
            else:
                self._id2label = dict(enumerate(self._train_dataset.features["label"].names))
                self._label_list = self._train_dataset.features["label"].names
            self._label2id = {v: k for k, v in self._id2label.items()}

            self._model_class = AutoModelForSequenceClassification

        elif self._record_class == TokenClassificationRecord:
            self._label_list = self._train_dataset.features["ner_tags"].feature.names
            self._id2label = dict(enumerate(self._label_list))
            self._label2id = {v: k for k, v in self._id2label.items()}

            self._model_class = AutoModelForTokenClassification
        else:
            raise NotImplementedError("Text2TextRecord is not supported.")

        self.init_training_args()

    def init_training_args(self):
        import torch
        from transformers import TrainingArguments

        def convert_to_floats(dataset):
            dataset.set_format("torch")
            return dataset.map(
                lambda x: {"float_label": x["label"].to(torch.float)}, remove_columns=["label"]
            ).rename_column("float_label", "label")

        self.model_kwargs = {}
        self.model_kwargs["pretrained_model_name_or_path"] = (
            self._model if isinstance(self._model, str) else self._model.config._name_or_path
        )

        if self._record_class in [TextClassificationRecord, TokenClassificationRecord]:
            self.model_kwargs["num_labels"] = len(self._label_list)
            self.model_kwargs["id2label"] = self._id2label
            self.model_kwargs["label2id"] = self._label2id
            if self._multi_label:
                self.model_kwargs["problem_type"] = "multi_label_classification"

            if self._record_class == TextClassificationRecord:
                columns_mapping = {"text": "text", "label": "binarized_label"}
                if self._multi_label:
                    self._train_dataset = _apply_column_mapping(self._train_dataset, columns_mapping)
                    self._train_dataset = convert_to_floats(self._train_dataset)

                    if self._eval_dataset is not None:
                        self._eval_dataset = _apply_column_mapping(self._eval_dataset, columns_mapping)
                        self._eval_dataset = convert_to_floats(self._eval_dataset)

        self.trainer_kwargs = get_default_args(TrainingArguments.__init__)
        self.trainer_kwargs["evaluation_strategy"] = "no" if self._eval_dataset is None else "epoch"
        self.trainer_kwargs["logging_steps"] = 30
        self.trainer_kwargs["logging_steps"] = 1
        self.trainer_kwargs["num_train_epochs"] = 1

    def init_model(self, new: bool = False):
        from transformers import AutoTokenizer

        if self.trainer_tokenizer is None:
            if any(k in self.model_kwargs.get("pretrained_model_name_or_path") for k in ("gpt", "opt", "bloom")):
                padding_side = "left"
            else:
                padding_side = "right"

            self.trainer_tokenizer = AutoTokenizer.from_pretrained(
                self.model_kwargs.get("pretrained_model_name_or_path"),
                padding_side=padding_side,
                add_prefix_space=True,
            )
            if getattr(self.trainer_tokenizer, "pad_token_id") is None:
                self.trainer_tokenizer.pad_token_id = self.trainer_tokenizer.eos_token_id
            if getattr(self.trainer_tokenizer, "model_max_length") is None:
                self.trainer_tokenizer.model_max_length = 512

        if new:
            model_kwargs = self.model_kwargs
        else:
            model_kwargs = {"pretrained_model_name_or_path": self.model_kwargs.get("pretrained_model_name_or_path")}

        if self.trainer_model is None:
            self.trainer_model = self._model_class.from_pretrained(**model_kwargs, return_dict=True)
        if new:
            self.trainer_model = self.trainer_model.to(self.device)

    def init_pipeline(self):
        import transformers
        from transformers import AutoModelForQuestionAnswering, pipeline

        if self.device == "cuda":
            device = 0
        else:
            device = -1

        if self._record_class == TextClassificationRecord:
            if transformers.__version__ >= "4.20.0":
                kwargs = {"top_k": None}
            else:
                kwargs = {"return_all_scores": True}
            self.trainer_pipeline = pipeline(
                task="text-classification",
                model=self.trainer_model,
                tokenizer=self.trainer_tokenizer,
                device=device,
                **kwargs,
            )
        elif self._record_class == TokenClassificationRecord:
            self.trainer_pipeline = pipeline(
                task="token-classification",
                model=self.trainer_model,
                tokenizer=self.trainer_tokenizer,
                aggregation_strategy="first",
                device=device,
            )
        elif self._model_class == AutoModelForQuestionAnswering:
            self.trainer_pipeline = pipeline(
                task="question-answering",
                model=self.trainer_model,
                tokenizer=self.trainer_tokenizer,
                device=device,
            )
        else:
            raise NotImplementedError(f"{self._record_class} is not supported yet.")

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
            AutoModelForQuestionAnswering,
            DataCollatorForTokenClassification,
            DataCollatorWithPadding,
            DefaultDataCollator,
        )

        def text_classification_preprocess_function(examples):
            return self.trainer_tokenizer(examples["text"], truncation=True, max_length=None)

        def token_classification_preprocess_function(examples):
            tokenized_inputs = self.trainer_tokenizer(examples["tokens"], truncation=True, is_split_into_words=True)

            labels = []
            for i, label in enumerate(examples["ner_tags"]):
                word_ids = tokenized_inputs.word_ids(batch_index=i)
                previous_word_idx = None
                label_ids = []
                for word_idx in word_ids:
                    if word_idx is None:
                        label_ids.append(-100)
                    elif word_idx != previous_word_idx:
                        label_ids.append(label[word_idx])
                    else:
                        label_ids.append(-100)
                    previous_word_idx = word_idx
                labels.append(label_ids)

            tokenized_inputs["labels"] = labels
            return tokenized_inputs

        def question_answering_preprocess_function(examples):
            questions = [q.strip() for q in examples["question"]]
            inputs = self.trainer_tokenizer(
                questions,
                examples["context"],
                truncation="only_second",
                return_offsets_mapping=True,
                padding="max_length",
            )

            offset_mapping = inputs.pop("offset_mapping")
            answers = examples["answer"]
            start_positions = []
            end_positions = []

            for i, offset in enumerate(offset_mapping):
                answer = answers[i]
                start_char = answer["answer_start"][0]
                end_char = answer["answer_start"][0] + len(answer["text"][0])
                sequence_ids = inputs.sequence_ids(i)

                # Find the start and end of the context
                idx = 0
                while sequence_ids[idx] != 1:
                    idx += 1
                context_start = idx
                while sequence_ids[idx] == 1:
                    idx += 1
                context_end = idx - 1

                # If the answer is not fully inside the context, label it (0, 0)
                if offset[context_start][0] > end_char or offset[context_end][1] < start_char:
                    start_positions.append(0)
                    end_positions.append(0)
                else:
                    # Otherwise it's the start and end token positions
                    idx = context_start
                    while idx <= context_end and offset[idx][0] <= start_char:
                        idx += 1
                    start_positions.append(idx - 1)

                    idx = context_end
                    while idx >= context_start and offset[idx][1] >= end_char:
                        idx -= 1
                    end_positions.append(idx + 1)

            inputs["start_positions"] = start_positions
            inputs["end_positions"] = end_positions
            return inputs

        def question_answering_preprocess_function_validation(examples):
            questions = [q.strip() for q in examples["question"]]
            inputs = self.trainer_tokenizer(
                questions,
                examples["context"],
                truncation="only_second",
                return_overflowing_tokens=True,
                return_offsets_mapping=True,
                padding="max_length",
            )

            sample_map = inputs.pop("overflow_to_sample_mapping")
            example_ids = []

            for i in range(len(inputs["input_ids"])):
                sample_idx = sample_map[i]
                example_ids.append(examples["id"][sample_idx])

                sequence_ids = inputs.sequence_ids(i)
                offset = inputs["offset_mapping"][i]
                inputs["offset_mapping"][i] = [o if sequence_ids[k] == 1 else None for k, o in enumerate(offset)]

            inputs["example_id"] = example_ids
            return inputs

        # set correct tokenization
        if self._record_class == TextClassificationRecord:
            preprocess_function = text_classification_preprocess_function
            self._data_collator = DataCollatorWithPadding(tokenizer=self.trainer_tokenizer)
            if self._multi_label:
                remove_columns = ["feat_id", "text", "feat_label"]
            else:
                remove_columns = ["id", "text"]
            replace_labels = True
        elif self._record_class == TokenClassificationRecord:
            preprocess_function = token_classification_preprocess_function
            self._data_collator = DataCollatorForTokenClassification(tokenizer=self.trainer_tokenizer)
            remove_columns = ["id", "tokens", "ner_tags"]
            replace_labels = False
        elif self._model_class == AutoModelForQuestionAnswering:
            preprocess_function = question_answering_preprocess_function
            self._data_collator = DefaultDataCollator()
            remove_columns = self._train_dataset.column_names
            replace_labels = False
        else:
            raise NotImplementedError("`Text2TextRecord` is not supported yet.")

        self._tokenized_train_dataset = self._train_dataset.map(
            preprocess_function, batched=True, remove_columns=remove_columns
        )
        if replace_labels:
            self._tokenized_train_dataset = self._tokenized_train_dataset.rename_column("label", "labels")

        if self._eval_dataset is not None:
            if self._model_class == AutoModelForQuestionAnswering:
                # We need to preprocess the validation dataset separately, because we need to return the example_id
                self._tokenized_eval_dataset = self._eval_dataset.map(
                    question_answering_preprocess_function_validation,
                    batched=True,
                    remove_columns=remove_columns,
                )
            else:
                self._tokenized_eval_dataset = self._eval_dataset.map(
                    preprocess_function, batched=True, remove_columns=remove_columns
                )

            if replace_labels:
                self._tokenized_eval_dataset = self._tokenized_eval_dataset.rename_column("label", "labels")
        else:
            self._tokenized_eval_dataset = None

    def compute_metrics(self):
        import collections

        import evaluate
        import numpy as np
        from transformers import AutoModelForQuestionAnswering

        func = None
        if self._record_class == TextClassificationRecord:
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

        elif self._record_class == TokenClassificationRecord:
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
        elif AutoModelForQuestionAnswering:
            squad = evaluate.load("squad")

            # Copy from https://huggingface.co/learn/nlp-course/chapter7/7?fw=pt#fine-tuning-the-model-with-the-trainer-api
            n_best = 20

            def compute_metrics_question_answering(pred):
                start_logits, end_logits = pred.predictions
                features = self._tokenized_eval_dataset
                examples = self._eval_dataset

                example_to_features = collections.defaultdict(list)
                for idx, feature in enumerate(features):
                    example_to_features[feature["example_id"]].append(idx)

                predicted_answers = []
                for example in examples:
                    example_id = example["id"]
                    context = example["context"]
                    answers = []

                    # Loop through all features associated with that example
                    for feature_index in example_to_features[example_id]:
                        start_logit = start_logits[feature_index]
                        end_logit = end_logits[feature_index]
                        offsets = features[feature_index]["offset_mapping"]

                        start_indexes = np.argsort(start_logit)[-1 : -n_best - 1 : -1].tolist()
                        end_indexes = np.argsort(end_logit)[-1 : -n_best - 1 : -1].tolist()
                        for start_index in start_indexes:
                            for end_index in end_indexes:
                                # Skip answers that are not fully in the context
                                if offsets[start_index] is None or offsets[end_index] is None:
                                    continue
                                # Skip answers with a length that is either < 0 or > max_answer_length
                                if (
                                    end_index < start_index
                                    or end_index - start_index + 1 > self.trainer_tokenizer.model_max_length
                                ):
                                    continue

                                answer = {
                                    "text": context[offsets[start_index][0] : offsets[end_index][1]],
                                    "logit_score": start_logit[start_index] + end_logit[end_index],
                                }
                                answers.append(answer)

                    # Select the answer with the best score
                    if len(answers) > 0:
                        best_answer = max(answers, key=lambda x: x["logit_score"])
                        predicted_answers.append({"id": example_id, "prediction_text": best_answer["text"]})
                    else:
                        predicted_answers.append({"id": example_id, "prediction_text": ""})

                theoretical_answers = [{"id": ex["id"], "answers": ex["answers"]} for ex in examples]

                return squad.compute(predictions=predicted_answers, references=theoretical_answers)

            func = compute_metrics_question_answering
        else:
            raise NotImplementedError("Other record types are not supported yet.")
        return func

    def train(self, output_dir: str):
        from transformers import Trainer, TrainingArguments

        # check required path argument
        self.trainer_kwargs["output_dir"] = output_dir

        # prepare data
        self.init_model(new=True)
        self.preprocess_datasets()

        # get metrics function
        compute_metrics = self.compute_metrics()

        self.trainer_model.to(self.device)
        # set trainer
        if self.device == "cuda":
            self.trainer_kwargs["no_cuda"] = False
        elif self.device == "mps":
            self.trainer_kwargs["use_mps_device"] = True
        self._trainer = Trainer(
            args=TrainingArguments(**self.trainer_kwargs),
            model=self.trainer_model,
            tokenizer=self.trainer_tokenizer,
            train_dataset=self._tokenized_train_dataset,
            eval_dataset=self._tokenized_eval_dataset,
            compute_metrics=compute_metrics,
            data_collator=self._data_collator,
        )

        #  train
        self._trainer.train()
        if self._tokenized_eval_dataset:
            self._metrics = self._trainer.evaluate()
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
        if self.trainer_pipeline is None:
            self._logger.warning("Using model without fine-tuning.")
            self.init_model(new=False)
            self.init_pipeline()

        str_input = False
        if isinstance(text, str):
            text = [text]
            str_input = True

        predictions = self.trainer_pipeline(text, **kwargs)

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
                    _pred = [(value["entity_group"], value["start"], value["end"]) for value in pred]
                    encoding = self.trainer_pipeline.tokenizer(val)
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
        The function saves the model to the path specified and also saves the label2id and id2label
        dictionaries to the same path

        Args:
          output_dir (str): the path to save the model to
        """
        self.trainer_model.save_pretrained(output_dir)
        self.trainer_tokenizer.save_pretrained(output_dir)
