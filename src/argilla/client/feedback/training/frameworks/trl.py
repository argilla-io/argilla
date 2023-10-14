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
from typing import TYPE_CHECKING, Dict, List, Optional, Union

from argilla.client.feedback.training.base import ArgillaTrainerSkeleton
from argilla.client.feedback.training.schemas import (
    TrainingTaskForDPO,
    TrainingTaskForPPO,
    TrainingTaskForRM,
    TrainingTaskForSFT,
)
from argilla.training.utils import filter_allowed_args
from argilla.utils.dependency import require_dependencies

if TYPE_CHECKING:
    import transformers
    from transformers import PreTrainedModel, PreTrainedTokenizer
    from trl import PPOConfig

    from argilla.client.feedback.dataset import FeedbackDataset
    from argilla.client.feedback.integrations.huggingface.model_card import TRLModelCardData


class PPOArgs:
    def __init__(
        self,
        config: "PPOConfig",
        reward_model: Union[str, "transformers.pipeline"],
        length_sampler_kwargs: dict,
        generation_kwargs: dict,
    ) -> None:
        """
        Additional arguments for PPO training process.

        Args:
            reward_model (Union[str, "transformers.pipeline"]): Reward model to use for creating PPO rewards for training.
            length_sampler_kwargs (dict): Arguments for the length sampler.
                min_value: Minimum length for the generated samples.
                max_value: Maximum length for the generated samples.
            generation_kwargs (dict): Arguments for the generation process.
                min_length: Minimum length for the generated samples.
                max_length: Maximum length for the generated samples.
                num_beams: Number of beams to use for the generation process.
                num_return_sequences: Number of sequences to generate.
                temperature: Temperature for the generation process.
                top_k: Top k for the generation process.
                top_p: Top p for the generation process.
        """
        if isinstance(reward_model, str):
            from transformers import pipeline

            reward_model = pipeline("text-classifcation", model=reward_model)
        self.config = config
        self.reward_model = reward_model
        self.length_sampler_kwargs = length_sampler_kwargs
        self.generation_kwargs = generation_kwargs


class ArgillaTRLTrainer(ArgillaTrainerSkeleton):
    _logger = logging.getLogger("ArgillaTRLTrainer")
    _logger.setLevel(logging.INFO)

    require_dependencies(["transformers", "torch", "trl>=0.5.0"])

    def __init__(
        self,
        dataset: "FeedbackDataset",
        task: Union[
            TrainingTaskForSFT,
            TrainingTaskForRM,
            TrainingTaskForPPO,
            TrainingTaskForDPO,
        ],
        prepared_data=None,
        model: Optional[Union[str, "PreTrainedModel"]] = None,
        tokenizer: Optional["PreTrainedTokenizer"] = None,
        seed: int = None,
    ) -> None:
        super().__init__(dataset=dataset, task=task, prepared_data=prepared_data, model=model, seed=seed)
        import torch
        from datasets import DatasetDict
        from transformers import set_seed

        self._transformers_model = model if not isinstance(model, str) else None
        self._transformers_tokenizer = tokenizer
        self.device = "cpu"
        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"

        if self._seed is None:
            self._seed = 42
        set_seed(self._seed)

        if self._model is None:
            self._model = "gpt2-medium"

        if isinstance(self._dataset, DatasetDict):
            self._train_dataset = self._dataset["train"]
            self._eval_dataset = self._dataset["test"]
        else:
            self._train_dataset = self._dataset
            self._eval_dataset = None

        if not isinstance(
            self._task,
            (
                TrainingTaskForSFT,
                TrainingTaskForRM,
                TrainingTaskForPPO,
                TrainingTaskForDPO,
            ),
        ):
            raise NotImplementedError(f"Task {self._task} not supported in TRL.")

        from trl import DPOTrainer, PPOTrainer, RewardTrainer, SFTTrainer

        self.trainer_mapping = {
            TrainingTaskForSFT: SFTTrainer,
            TrainingTaskForRM: RewardTrainer,
            TrainingTaskForPPO: PPOTrainer,
            TrainingTaskForDPO: DPOTrainer,
        }
        self.trainer_cls = self.trainer_mapping[type(self._task)]

        self.init_training_args()

    def init_training_args(self) -> None:
        """
        Initializes the training arguments.
        """
        self.training_args_kwargs = {}
        self.trainer_kwargs = {}

        if isinstance(self._task, TrainingTaskForPPO):
            from trl import PPOConfig

            self._logger.warning(
                "The PPOTrainer must be initialized by passing `reward_model`, `length_sampler_kwargs`, `generation_kwargs` as kwargs to the `update_config()`-method."
            )
            self.trainer_kwargs["config"] = PPOConfig()
            self.training_args_kwargs["reward_model"] = None
            self.training_args_kwargs["length_sampler_kwargs"] = {"min_value": 1, "max_value": 10}
            self.training_args_kwargs["generation_kwargs"] = {
                "min_length": -1,
                "top_k": 0.0,
                "top_p": 1.0,
                "do_sample": True,
            }
        else:
            self.training_args_kwargs["evaluation_strategy"] = "no" if self._eval_dataset is None else "epoch"
            self.training_args_kwargs["logging_steps"] = 30
            self.training_args_kwargs["logging_steps"] = 1
            self.training_args_kwargs["num_train_epochs"] = 1

    def init_model(self, new: bool = False) -> None:
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
        from trl import AutoModelForCausalLMWithValueHead, create_reference_model

        if isinstance(self._task, (TrainingTaskForSFT, TrainingTaskForDPO)):
            auto_model_class = AutoModelForCausalLM
        elif isinstance(self._task, TrainingTaskForPPO):
            auto_model_class = AutoModelForCausalLMWithValueHead
        elif isinstance(self._task, TrainingTaskForRM):
            auto_model_class = AutoModelForSequenceClassification

        if self._transformers_model is None:
            self._transformers_model: PreTrainedModel = auto_model_class.from_pretrained(self._model)
        if self._transformers_tokenizer is None:
            self._transformers_tokenizer: PreTrainedTokenizer = AutoTokenizer.from_pretrained(
                self._transformers_model.config.name_or_path
            )
            self._transformers_tokenizer.pad_token_id = self._transformers_tokenizer.eos_token_id
        self._transformers_model.config.pad_token_id = self._transformers_tokenizer.pad_token_id

        if isinstance(self._task, (TrainingTaskForPPO, TrainingTaskForDPO)):
            self._transformers_ref_model: PreTrainedModel = create_reference_model(self._transformers_model)
        if new:
            self._transformers_model.to(self.device)

    def update_config(self, **kwargs) -> None:
        """
        Updates the configuration of the trainer, but the parameters depend on the trainer.subclass.
        """
        from transformers import TrainingArguments

        self.training_args_kwargs.update(filter_allowed_args(TrainingArguments.__init__, **kwargs))
        self.training_args_kwargs.update(filter_allowed_args(PPOArgs.__init__, **kwargs))
        self.trainer_kwargs.update(filter_allowed_args(self.trainer_cls.__init__, **kwargs))

    def predict(self, text: Union[List[str], str], as_argilla_records: bool = True, **kwargs) -> None:
        """
        Predicts the label of the text.
        """
        raise NotImplementedError("Models trained with TRL cannot be used for label predictions.")

    def train(self, output_dir: str) -> None:
        """
        Trains the model.
        """
        if isinstance(self._task, TrainingTaskForPPO):
            if not all(
                x in self.training_args_kwargs for x in ["length_sampler_kwargs", "generation_kwargs", "reward_model"]
            ):
                raise ValueError(
                    "To train a PPO model, you need to specify the following arguments via `trainer.update_config`: length_sampler_kwargs, generation_kwargs, reward_model."
                )

        from transformers import TrainingArguments

        # check required path argument
        self.training_args_kwargs["output_dir"] = output_dir

        self.init_model(new=True)

        if isinstance(self._task, TrainingTaskForSFT):
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

        elif isinstance(self._task, TrainingTaskForRM):

            def preprocess_function(examples) -> Dict[str, List]:
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
        elif isinstance(self._task, TrainingTaskForPPO):
            from datasets import concatenate_datasets

            dataset = concatenate_datasets([x for x in [self._train_dataset, self._eval_dataset] if x is not None])

            def tokenize(sample):
                sample["input_ids"] = self._transformers_tokenizer.encode(sample["query"], truncation=True)
                return sample

            def data_collator(data):
                return dict((key, [d[key] for d in data]) for key in data[0])

            def remove_truncated(sample):
                return len(sample) < self._transformers_tokenizer.model_max_length

            dataset = dataset.map(tokenize, batched=False)
            size_before = len(dataset)
            dataset = dataset.filter(remove_truncated, batched=False)
            size_after = len(dataset)
            if size_after != size_before:
                self._logger.info(
                    f"Removed {size_before - size_after} samples ({1 - (size_after / size_before):%}), "
                    "as these samples were longer than the maximum model length even before the generation."
                )
            dataset.set_format(type="torch")
            self._trainer = self.trainer_cls(
                model=self._transformers_model,
                ref_model=self._transformers_ref_model,
                tokenizer=self._transformers_tokenizer,
                dataset=dataset,
                data_collator=data_collator,
                **self.trainer_kwargs,
            )
        elif isinstance(self._task, TrainingTaskForDPO):
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
        if isinstance(self._task, TrainingTaskForPPO):
            import torch
            from tqdm import tqdm
            from trl.core import LengthSampler

            output_length_sampler = LengthSampler(**self.training_args_kwargs["length_sampler_kwargs"])
            generation_kwargs = self.training_args_kwargs["generation_kwargs"]
            generation_kwargs["pad_token_id"] = self._transformers_tokenizer.eos_token_id
            reward_model = self.training_args_kwargs["reward_model"]

            for batch in tqdm(self._trainer.dataloader):
                query_tensors = batch["input_ids"]

                #### Get response from SFT
                response_tensors = self._trainer.generate(
                    query_tensors,
                    return_prompt=False,
                    length_sampler=output_length_sampler,
                    **generation_kwargs,
                )
                batch["response"] = self._transformers_tokenizer.batch_decode(
                    response_tensors, skip_special_tokens=True
                )

                #### Compute rewards scores
                texts = [q + r for q, r in zip(batch["query"], batch["response"])]
                pipe_outputs = reward_model(texts, top_k=None, truncation=True)
                rewards = [torch.tensor(output[-1]["score"] * len(output)) for output in pipe_outputs]

                #### Run PPO step
                stats = self._trainer.step(query_tensors, response_tensors, rewards)
                self._trainer.log_stats(stats, batch, rewards)
        else:
            self._trainer.train()
            if self._trainer.eval_dataset:
                self._metrics = self._trainer.evaluate()
                self._logger.info(self._metrics)
            else:
                self._metrics = None

        self.save(output_dir)

    def save(self, output_dir: str) -> None:
        """
        Saves the model to the specified path.
        """
        self._trainer.model.save_pretrained(output_dir)
        self._trainer.tokenizer.save_pretrained(output_dir)

    def __repr__(self) -> str:
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

    def get_model_card_data(self, **card_data_kwargs) -> "TRLModelCardData":
        """
        Generate the card data to be used for the `ArgillaModelCard`.

        Args:
            card_data_kwargs: Extra arguments provided by the user when creating the `ArgillaTrainer`.

        Returns:
            TRLModelCardData: Container for the data to be written on the `ArgillaModelCard`.
        """
        from argilla.client.feedback.integrations.huggingface.model_card import TRLModelCardData

        if not card_data_kwargs.get("tags"):
            if isinstance(self._task, TrainingTaskForSFT):
                tags = ["supervised-fine-tuning", "sft"]
            elif isinstance(self._task, TrainingTaskForRM):
                tags = ["reward-modeling", "rm"]
            elif isinstance(self._task, TrainingTaskForPPO):
                tags = ["proximal-policy-optimization", "ppo"]
            elif isinstance(self._task, TrainingTaskForDPO):
                tags = ["direct-preference-optimization", "dpo"]

            card_data_kwargs.update({"tags": tags + ["TRL", "argilla"]})

        return TRLModelCardData(
            model_id=self._model,
            task=self._task,
            update_config_kwargs={**self.training_args_kwargs, **self.trainer_kwargs},
            **card_data_kwargs,
        )
