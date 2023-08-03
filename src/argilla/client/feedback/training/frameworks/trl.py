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
from typing import TYPE_CHECKING, List, Union

from argilla.client.feedback.training.base import ArgillaTrainerSkeleton
from argilla.client.feedback.training.schemas import (
    TrainingTaskForDirectPreferenceOptimization,
    TrainingTaskForRewardModelling,
    TrainingTaskForSupervisedFinetuning,
)
from argilla.training.utils import filter_allowed_args
from argilla.utils.dependency import require_version

if TYPE_CHECKING:
    from argilla.client.feedback.dataset import FeedbackDataset


class ArgillaTRLTrainer(ArgillaTrainerSkeleton):
    _logger = logging.getLogger("ArgillaTRLTrainer")
    _logger.setLevel(logging.INFO)

    require_version("trl>=0.5.0")

    def __init__(
        self,
        feedback_dataset: "FeedbackDataset",
        task: Union[
            TrainingTaskForSupervisedFinetuning,
            TrainingTaskForRewardModelling,
            TrainingTaskForDirectPreferenceOptimization,
        ],
        prepared_data=None,
        model: str = None,
        seed: int = None,
    ):
        super().__init__(
            feedback_dataset=feedback_dataset, task=task, prepared_data=prepared_data, model=model, seed=seed
        )
        import torch
        from datasets import DatasetDict
        from transformers import set_seed

        self._transformers_model = None
        self._transformers_tokenizer = None
        self.device = "cpu"
        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"

        if self._seed is None:
            self._seed = 42
        set_seed(self._seed)

        if self._model is None:
            self._model = "gpt2"

        if isinstance(self._dataset, DatasetDict):
            self._train_dataset = self._dataset["train"]
            self._eval_dataset = self._dataset["test"]
        else:
            self._train_dataset = self._dataset
            self._eval_dataset = None

        if not isinstance(
            self._task,
            (
                TrainingTaskForSupervisedFinetuning,
                TrainingTaskForRewardModelling,
                TrainingTaskForDirectPreferenceOptimization,
            ),
        ):
            raise NotImplementedError(f"Task {self._task} not supported in TRL.")

        from trl import DPOTrainer, RewardTrainer, SFTTrainer

        self.trainer_mapping = {
            TrainingTaskForSupervisedFinetuning: SFTTrainer,
            TrainingTaskForRewardModelling: RewardTrainer,
            TrainingTaskForDirectPreferenceOptimization: DPOTrainer,
        }
        self.trainer_cls = self.trainer_mapping[type(self._task)]

        self.init_training_args()

    def init_training_args(self):
        """
        Initializes the training arguments.
        """
        self.training_args_kwargs = {}
        self.training_args_kwargs["evaluation_strategy"] = "no" if self._eval_dataset is None else "epoch"
        self.training_args_kwargs["logging_steps"] = 30
        self.training_args_kwargs["logging_steps"] = 1
        self.training_args_kwargs["num_train_epochs"] = 1

        self.trainer_kwargs = {}

    def init_model(self, new: bool = False):
        """
        Initializes a model.
        """
        from transformers import (
            AutoModelForCausalLM,
            AutoModelForSequenceClassification,
            AutoTokenizer,
            PreTrainedModel,
            PreTrainedTokenizer,
        )

        if isinstance(self._task, (TrainingTaskForSupervisedFinetuning, TrainingTaskForDirectPreferenceOptimization)):
            auto_model_class = AutoModelForCausalLM
        elif isinstance(self._task, TrainingTaskForRewardModelling):
            auto_model_class = AutoModelForSequenceClassification
        self._transformers_model: PreTrainedModel = auto_model_class.from_pretrained(self._model)
        self._transformers_tokenizer: PreTrainedTokenizer = AutoTokenizer.from_pretrained(self._model)
        self._transformers_tokenizer.pad_token = self._transformers_tokenizer.eos_token
        self._transformers_model.config.pad_token_id = self._transformers_tokenizer.pad_token_id

        if isinstance(self._task, TrainingTaskForDirectPreferenceOptimization):
            self._transformers_ref_model: PreTrainedModel = auto_model_class.from_pretrained(self._model)
        # if new:
        self._transformers_model.to(self.device)

    def update_config(self, *args, **kwargs):
        """
        Updates the configuration of the trainer, but the parameters depend on the trainer.subclass.
        """
        from transformers import TrainingArguments

        self.training_args_kwargs.update(filter_allowed_args(TrainingArguments.__init__, **kwargs))
        self.trainer_kwargs.update(filter_allowed_args(self.trainer_cls.__init__, **kwargs))

    def predict(self, text: Union[List[str], str], as_argilla_records: bool = True, **kwargs):
        """
        Predicts the label of the text.
        """

    def train(self, output_dir: str) -> None:
        """
        Trains the model.
        """
        from transformers import TrainingArguments

        # check required path argument
        self.training_args_kwargs["output_dir"] = output_dir

        self.init_model(new=True)

        if isinstance(self._task, TrainingTaskForSupervisedFinetuning):
            self._training_args = TrainingArguments(**self.training_args_kwargs)
            self._trainer = self.trainer_cls(
                self._transformers_model,
                args=self._training_args,
                train_dataset=self._train_dataset,
                eval_dataset=self._eval_dataset,
                dataset_text_field="text",
                tokenizer=self._transformers_tokenizer,
                **self.trainer_kwargs,
            )

        elif isinstance(self._task, TrainingTaskForRewardModelling):

            def preprocess_function(examples):
                new_examples = {
                    "input_ids_chosen": [],
                    "attention_mask_chosen": [],
                    "input_ids_rejected": [],
                    "attention_mask_rejected": [],
                }
                for chosen, rejected in zip(examples["chosen"], examples["rejected"]):
                    tokenized_j = self._transformers_tokenizer(chosen, truncation=True)
                    tokenized_k = self._transformers_tokenizer(rejected, truncation=True)

                    new_examples["input_ids_chosen"].append(tokenized_j["input_ids"])
                    new_examples["attention_mask_chosen"].append(tokenized_j["attention_mask"])
                    new_examples["input_ids_rejected"].append(tokenized_k["input_ids"])
                    new_examples["attention_mask_rejected"].append(tokenized_k["attention_mask"])

                return new_examples

            self._training_args = TrainingArguments(**self.training_args_kwargs)
            train_dataset = self._train_dataset.map(preprocess_function, batched=True)
            eval_dataset = None
            if self._eval_dataset:
                eval_dataset = self._eval_dataset.map(preprocess_function, batched=True)

            self._trainer = self.trainer_cls(
                self._transformers_model,
                args=self._training_args,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                tokenizer=self._transformers_tokenizer,
                **self.trainer_kwargs,
            )

        elif isinstance(self._task, TrainingTaskForDirectPreferenceOptimization):
            self._training_args = TrainingArguments(**self.training_args_kwargs)
            self._trainer = self.trainer_cls(
                model=self._transformers_model,
                ref_model=self._transformers_ref_model,
                args=self._training_args,
                train_dataset=self._train_dataset,
                eval_dataset=self._eval_dataset,
                tokenizer=self._transformers_tokenizer,
                **self.trainer_kwargs,
            )

        #  train
        self._trainer.train()
        if self._trainer.eval_dataset:
            self._metrics = self._trainer.evaluate()
            self._logger.info(self._metrics)
        else:
            self._metrics = None

        self.save(output_dir)

    def save(self, output_dir: str):
        """
        Saves the model to the specified path.
        """
        self._transformers_model.save_pretrained(output_dir)
        self._transformers_tokenizer.save_pretrained(output_dir)

    def __repr__(self):
        formatted_string = []
        arg_dict = {
            repr(self.trainer_cls.__name__): self.trainer_kwargs,
            "'TrainingArguments'": self.training_args_kwargs,
        }
        for arg_dict_key, arg_dict_single in arg_dict.items():
            formatted_string.append(arg_dict_key)
            for key, val in arg_dict_single.items():
                formatted_string.append(f"{key}: {val}")
        return "\n".join(formatted_string)
