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
from typing import List, Optional, Union

import argilla as rg
from argilla.training.transformers import ArgillaTransformersTrainer
from argilla.training.utils import (
    _apply_column_mapping,
    filter_allowed_args,
    get_default_args,
)
from argilla.utils.dependency import require_version


class ArgillaTransformersPEFTTrainer(ArgillaTransformersTrainer):
    _logger = logging.getLogger("ArgillaTransformersPEFTTrainer")
    _logger.setLevel(logging.INFO)

    require_version("peft")

    def init_training_args(
        self,
        pretrained_model_name_or_path: str,
        r: int = 8,
        target_modules: Optional[Union[List[str], str]] = None,
        lora_alpha: int = 16,
        lora_dropout: float = 0.1,
        fan_in_fan_out: bool = False,
        bias: str = "none",
        modules_to_save: Optional[List[str]] = None,
        init_lora_weights: bool = True,
    ):
        from transformers import TrainingArguments

        if self._record_class == rg.TextClassificationRecord:
            columns_mapping = {"text": "text", "label": "binarized_label"}
            if self._multi_label:
                self._train_dataset = _apply_column_mapping(self._train_dataset, columns_mapping)

                if self._eval_dataset is not None:
                    self._eval_dataset = _apply_column_mapping(self._eval_dataset, columns_mapping)

        self.model_kwargs = {}

        self.model_kwargs["pretrained_model_name_or_path"] = pretrained_model_name_or_path
        self.model_kwargs["num_labels"] = len(self._label_list)
        self.model_kwargs["id2label"] = self._id2label
        self.model_kwargs["label2id"] = self._label2id
        if self._multi_label:
            self.model_kwargs["problem_type"] = "multi_label_classification"

        self.trainer_kwargs = get_default_args(TrainingArguments.__init__)
        self.trainer_kwargs["evaluation_strategy"] = "no" if self._eval_dataset is None else "epoch"
        self.trainer_kwargs["logging_steps"] = 5
        self.trainer_kwargs["num_train_epochs"] = 1
        self.trainer_kwargs["num_train_epochs"] = 1

    def init_model(self, new: bool = False):
        super().init_model(new=new)
        from peft import LoraConfig, get_peft_model

        if self._record_class == rg.TextClassificationRecord:
            task_type = "SEQ_CLS"
        elif self._record_class == rg.TokenClassificationRecord:
            task_type = "TOKEN_CLS"
        else:
            raise NotImplementedError("This is not implemented yet.")

        peft_config = LoraConfig(task_type=task_type, inference_mode=False, r=8, lora_alpha=16, lora_dropout=0.1)
        model = self._model_class.from_pretrained(**self.model_kwargs, return_dict=True)
        self._transformers_model = get_peft_model(model, peft_config)
        self._logger.info(self._transformers_model)

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

    # def train(self, output_dir: str):
    #     """
    #     We create a SetFitModel object from a pretrained model, then create a SetFitTrainer object with
    #     the model, and then train the model
    #     """

    #     import evaluate
    #     import torch
    #     from torch.optim import AdamW
    #     from torch.utils.data import DataLoader
    #     from transformers import get_linear_schedule_with_warmup

    #     # prepare data
    #     self.init_model(new=True)
    #     self.preprocess_datasets()

    #     self._training_args = TrainingArguments(**self.trainer_kwargs)
    #     self._transformers_trainer = Trainer(
    #         args=self._training_args,
    #         model=self._transformers_model,
    #         train_dataset=self._tokenized_train_dataset,
    #         eval_dataset=self._tokenized_eval_dataset,
    #         compute_metrics=compute_metrics,
    #         data_collator=self._data_collator,
    #     )

    #     #  train
    #     self._transformers_trainer.train()
    #     if self._tokenized_eval_dataset:
    #         self._metrics = self._transformers_trainer.evaluate()
    #         self._logger.info(self._metrics)
    #     else:
    #         self._metrics = None
    #     # # get metrics function
    #     # def collate_fn(examples):
    #     #     return self._transformers_tokenizer.pad(examples, padding="longest", return_tensors="pt")

    #     # # Instantiate dataloaders.
    #     # batch_size = 8
    #     # train_dataloader = DataLoader(self._tokenized_train_dataset, shuffle=True, batch_size=batch_size, collate_fn=collate_fn)
    #     # eval_dataloader = DataLoader(self._tokenized_eval_dataset, shuffle=False, batch_size=batch_size, collate_fn=collate_fn)

    #     # for i in train_dataloader:
    #     #     for key, value in i.items():
    #     #         print(key, value)
    #     #     break

    #     # for key, value in self._tokenized_train_dataset[0].items():
    #     #     print(key, value)

    #     # lr = 3e-4
    #     # num_epochs = 20
    #     # optimizer = AdamW(params=self._transformers_model.parameters(), lr=lr)

    #     # # Instantiate scheduler
    #     # lr_scheduler = get_linear_schedule_with_warmup(
    #     #     optimizer=optimizer,
    #     #     num_warmup_steps=0.06 * (len(train_dataloader) * num_epochs),
    #     #     num_training_steps=(len(train_dataloader) * num_epochs),
    #     # )

    #     # metric = evaluate.load("accuracy")
    #     # self._transformers_model.to(self.device)
    #     # for epoch in range(num_epochs):
    #     #     self._transformers_model.train()
    #     #     for _, batch in enumerate(tqdm(train_dataloader)):
    #     #         batch.to(self.device)
    #     #         outputs = self._transformers_model(**batch)
    #     #         loss = outputs.loss
    #     #         loss.backward()
    #     #         optimizer.step()
    #     #         lr_scheduler.step()
    #     #         optimizer.zero_grad()
    #     #         print(loss)

    #     #     self._transformers_model.eval()
    #     #     for _, batch in enumerate(tqdm(eval_dataloader)):
    #     #         batch.to(self.device)
    #     #         with torch.no_grad():
    #     #             outputs = self._transformers_model(**batch)
    #     #         predictions = outputs.logits.argmax(dim=-1)
    #     #         predictions, references = predictions, batch["labels"]
    #     #         metric.add_batch(
    #     #             predictions=predictions,
    #     #             references=references,
    #     #         )

    #     #     # eval_metric = metric.compute()
    #     #     eval_metric = 0
    #     #     print(f"epoch {epoch}:", eval_metric)

    #     self.save(output_dir)

    #     self.init_pipeline()

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
