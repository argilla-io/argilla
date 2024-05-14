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
import os
import time
from typing import List, Optional, Union

import numpy as np

from argilla._constants import OPENAI_END_TOKEN, OPENAI_LEGACY_MODELS, OPENAI_SEPARATOR, OPENAI_WHITESPACE
from argilla.client.models import TextClassificationRecord, TokenClassificationRecord
from argilla.datasets import TextClassificationSettings, TokenClassificationSettings
from argilla.training.base import ArgillaTrainerSkeleton
from argilla.training.utils import filter_allowed_args
from argilla.utils.dependency import require_dependencies


class ArgillaOpenAITrainer(ArgillaTrainerSkeleton):
    _logger = logging.getLogger("ArgillaOpenAITrainer")
    _logger.setLevel(logging.INFO)
    _separator = OPENAI_SEPARATOR
    _end_token = OPENAI_END_TOKEN
    _whitespace = OPENAI_WHITESPACE

    OPENAI_API_KEY = "OPENAI_API_KEY"
    if OPENAI_API_KEY not in os.environ:
        raise ValueError(f"{OPENAI_API_KEY} not found in environment variables.")

    def __init__(self, *args, **kwargs):
        require_dependencies("openai>=0.27.10")
        super().__init__(*args, **kwargs)

        if self._record_class is TokenClassificationRecord:
            raise NotImplementedError("OpenAI does not support `TokenClassification` tasks.")
        elif self._record_class is TextClassificationRecord and self._multi_label:
            raise NotImplementedError("OpenAI does not support `multi-label=True` TextClassification tasks.")
        else:
            pass

        self.sleep_timer = 10
        self.device = None
        self.finetune_id = None

        if self._seed is not None:
            self._logger.warning("Seed is not supported for OpenAI. Ignoring seed for training.")

        if self._model is None:
            self._model = "gpt-3.5-turbo"
            self._logger.warning(f"No model defined. Using the default model {self._model}.")

        if any([self._model in model for model in OPENAI_LEGACY_MODELS]):
            self._logger.warning(
                "Using the OpenAI legacy mnodels within the Trainer, please use a newer model and take a look here https://platform.openai.com/docs/guides/legacy-fine-tuning.append()"
            )
            self.__legacy = True
        else:
            self.__legacy = False

        if isinstance(self._dataset, tuple):
            self._train_dataset = self._dataset[0]
            self._eval_dataset = self._dataset[1]
        else:
            self._train_dataset = self._dataset
            self._eval_dataset = None

        if not self.__legacy:
            self._train_dataset = self._convert_data_to_new_format(self._train_dataset)
            if self._eval_dataset is not None:
                self._eval_dataset = self._convert_data_to_new_format(self._eval_dataset)

        self.init_training_args(model=self._model)

    def _convert_data_to_new_format(self, dataset) -> List[dict]:
        new_dataset = []
        for entry in dataset:
            new_dataset.append(
                {
                    "messages": [
                        {"role": "user", "content": f"Classify the following text: {entry['prompt']}"},
                        {"role": "assistant", "content": entry["completion"]},
                    ]
                }
            )
        return new_dataset

    def init_training_args(
        self,
        training_file: Optional[str] = None,
        validation_file: str = None,
        model: str = "curie",
        n_epochs: int = None,
        batch_size: int = None,
        learning_rate_multiplier: float = 0.1,
        prompt_loss_weight: float = 0.1,
        compute_classification_metrics: bool = False,
        classification_n_classes: int = None,
        classification_positive_class: str = None,
        classification_betas: list = None,
        suffix: str = None,
        hyperparameters: dict = None,
    ) -> None:
        self.trainer_kwargs["training_file"] = training_file
        self.trainer_kwargs["validation_file"] = validation_file
        self.trainer_kwargs["model"] = model
        self.trainer_kwargs["suffix"] = suffix

        if self.__legacy:
            if isinstance(self._record_class, TextClassificationRecord):
                self.trainer_kwargs["n_epochs"] = n_epochs or 4
            else:
                self.trainer_kwargs["n_epochs"] = n_epochs or 2
            self.trainer_kwargs["batch_size"] = batch_size
            self.trainer_kwargs["learning_rate_multiplier"] = learning_rate_multiplier
            self.trainer_kwargs["prompt_loss_weight"] = prompt_loss_weight
            self.trainer_kwargs["compute_classification_metrics"] = compute_classification_metrics
            self.trainer_kwargs["classification_n_classes"] = classification_n_classes
            self.trainer_kwargs["classification_positive_class"] = classification_positive_class
            self.trainer_kwargs["classification_betas"] = classification_betas

            if isinstance(self._record_class, TextClassificationRecord) and self._eval_dataset:
                label_schema = self._label_list
                if len(label_schema) == 2:
                    self.trainer_kwargs["classification_positive_class"] = label_schema[0]
                    self.trainer_kwargs["compute_classification_metrics"] = True
                else:
                    self.trainer_kwargs["classification_n_classes"] = len(label_schema)
                    self.trainer_kwargs["compute_classification_metrics"] = True
        else:
            if "hyperparameters":
                self.trainer_kwargs["hyperparameters"] = hyperparameters
            else:
                self.trainer_kwargs["hyperparameters"] = {}
                self.trainer_kwargs["hyperparameters"]["n_epochs"] = n_epochs or 1

    def update_config(
        self,
        **kwargs,
    ):
        """
        Updates the `model_kwargs` dictionaries with the keyword
        arguments passed to the `update_config` function.
        """
        self.trainer_kwargs.update(kwargs)
        self.trainer_kwargs = filter_allowed_args(self.init_training_args, **self.trainer_kwargs)

        keys = []
        for key, value in self.trainer_kwargs.items():
            if value is None:
                keys.append(key)
        for key in keys:
            del self.trainer_kwargs[key]

        if "model" in self.trainer_kwargs:
            self._model = self.trainer_kwargs["model"]

    def __repr__(self):
        formatted_string = []
        arg_dict = {
            "'OpenAI.fine_tune'": self.trainer_kwargs,
        }
        for arg_dict_key, arg_dict_single in arg_dict.items():
            formatted_string.append(arg_dict_key)
            for key, val in arg_dict_single.items():
                formatted_string.append(f"{key}: {val}")
        return "\nhttps://platform.openai.com/docs/api-reference/fine-tune\n" + "\n".join(formatted_string)

    def upload_dataset_to_openai(self, dataset, file_name) -> str:
        import io
        import json

        import openai

        for rec in dataset:
            if "id" in rec:
                del rec["id"]

        # Create a bytes buffer to hold the serialized data
        byte_stream = io.BytesIO()

        # Serialize the data to the bytes buffer
        for item in dataset:
            item_bytes = (json.dumps(item) + "\n").encode("utf-8")
            byte_stream.write(item_bytes)

        upload_response = openai.File.create(file=byte_stream.getvalue(), purpose="fine-tune")
        self._logger.info(upload_response)
        file_id = upload_response.id
        return file_id

    def train(self, output_dir: str = None) -> None:
        """
        We create an openai.FineTune object from a pre-trained model, and send data to finetune it.
        """

        import openai

        if output_dir is not None:
            self.trainer_kwargs["suffix"] = output_dir

        if self._train_dataset is not None and self.trainer_kwargs["training_file"] is None:
            self.trainer_kwargs["training_file"] = self.upload_dataset_to_openai(
                self._train_dataset, "data_train.jsonl"
            )
        if (self._eval_dataset is not None and self.trainer_kwargs["validation_file"] is None) and self.trainer_kwargs[
            "compute_classification_metrics"
        ]:
            self.trainer_kwargs["validation_file"] = self.upload_dataset_to_openai(
                self._eval_dataset, "data_test.jsonl"
            )

        self.update_config()

        started_training = False
        while not started_training:
            try:
                if self.__legacy:
                    response = openai.FineTune.create(
                        **self.trainer_kwargs,
                    )
                else:
                    response = openai.FineTuningJob.create(**self.trainer_kwargs)
                started_training = True
            except Exception as e:
                self._logger.warning(e)
                self._logger.warning(f"Retrying in {self.sleep_timer} seconds.")

                time.sleep(self.sleep_timer)

        self._logger.info(response)
        self.finetune_id = response.id

        if self.__legacy:
            message = f"`openai.FineTune.retrieve('{self.finetune_id}')`"
        else:
            message = f"`openai.FineTuningJob.retrieve('{self.finetune_id}')`"
        self._logger.info(f"Waiting for training OpenAI will send an email when done. Get info by running: {message}.")

    def init_model(self) -> None:
        import openai

        if self.finetune_id is not None:
            if self.__legacy:
                response = openai.FineTune.retrieve(self.finetune_id)
            else:
                response = openai.FineTuningJob.retrieve(self.finetune_id)
            potential_model = response.fine_tuned_model
            if potential_model is None:
                self._logger.warning("Fine-tuning is still in progress.")
            else:
                self._model = potential_model
        else:
            response = openai.Model.retrieve(self._model)
            self._model = response.id
            self._logger.info(response)

    def predict(self, text: Union[List[str], str], as_argilla_records: bool = True, **kwargs) -> Union[List, str]:
        """
        The function takes in a list of strings and returns a list of predictions

        Args:
          text (Union[List[str], str]): The text to be classified.
          as_argilla_records (bool): If True, the prediction will be returned as an Argilla record. If
        False, the prediction will be returned as a string. Defaults to True

        Returns:
          A list of predictions
        """

        import openai

        responses = []
        was_string = False

        if self.__legacy:
            if isinstance(text, str):
                text = [text]
                was_string = True

            if isinstance(self._settings, TextClassificationSettings):
                for kwarg in ["logprobs", "max_tokens", "temperature", "n"]:
                    if kwarg in kwargs:
                        del kwargs[kwarg]
                        self._logger.warning(
                            f"Argument `{kwarg}` has default value for text classification. Deleting it."
                        )
                kwargs["logprobs"] = len(self._settings.label_schema)
                kwargs["max_tokens"] = 1
                kwargs["temperature"] = 0
                kwargs["n"] = 1
            else:
                if "stop" in kwargs:
                    del kwargs[kwarg]
                self._logger.warning("Argument `stop` has default value for text classification. Deleting it.")
                kwargs["stop"] = self._end_token
                if "logprobs" not in kwargs:
                    kwargs["logprobs"] = 1

            for entry in text:
                prompt = f"{entry.strip()}{self._separator}"
                response = openai.Completion.create(model=self._model, prompt=prompt, **kwargs)

                if isinstance(self._settings, TextClassificationSettings):
                    logprobs = response["choices"][0]["logprobs"]["top_logprobs"][0]
                    keys = [self._settings.id2label[int(key.strip())] for key in list(logprobs.keys())]
                    values = np.exp(list(logprobs.values()))
                    response["choices"][0]["logprobs"]["top_logprobs"][0] = dict(zip(keys, values))
                    if as_argilla_records:
                        response = self._record_class(text=entry, prediction=list(zip(keys, values)))
                elif isinstance(self._settings, TokenClassificationSettings):
                    raise NotImplementedError("TokenClassification is not supported yet.")
                else:
                    if as_argilla_records:
                        predictions = [choice["text"] for choice in response["choices"]]
                        response = self._record_class(text=entry, prediction=predictions)

                responses.append(response)
        else:
            raise NotImplementedError(
                f"Prediction for the new OpenAI API is not supported yet. Take a look at their docs https://platform.openai.com/docs/api-reference/chat/create and use `model={self._model}`"
            )

        if was_string:
            return responses[0]
        else:
            return responses

    def save(self, *arg, **kwargs) -> None:
        """
        The function saves the model to the path specified and also saves the label2id and id2label
        dictionaries to the same path

        Args:
          output_dir (str): the path to save the model to
        """
        self._logger.warning("Saving is not supported for OpenAI and is passed via the `suffix` argument in `train`.")
