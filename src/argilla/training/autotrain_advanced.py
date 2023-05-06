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
from typing import List, Union
from uuid import uuid4

from autotrain.utils import get_project_cost
from datasets import DatasetDict

import argilla as rg
from argilla.training.base import ArgillaTrainerSkeleton
from argilla.training.utils import (
    filter_allowed_args,
)
from argilla.utils.dependency import require_version


def get_job_params(
    job_params,
    task,
    param_choice,
):
    if param_choice.lower() == "AutoTrain".lower():
        if len(job_params) > 1:
            raise ValueError("❌ Only one job parameter is allowed for AutoTrain.")
        job_params[0].update({"task": task})
    elif param_choice.lower() == "manual":
        for i in range(len(job_params)):
            job_params[i].update({"task": task})

    return job_params
    # """
    # Get job parameters list of dicts for AutoTrain and HuggingFace Hub models
    # :param job_params: job parameters
    # :param selected_rows: selected rows
    # :param task: task
    # :param param_choice: model choice
    # :return: job parameters list of dicts
    # """
    # if param_choice == "AutoTrain":
    #     if len(job_params) > 1:
    #         raise ValueError("❌ Only one job parameter is allowed for AutoTrain.")
    #     job_params[0].update({"task": task})
    # elif param_choice.lower() == "manual":
    #     for i in range(len(job_params)):
    #         job_params[i].update({"task": task})
    #     job_params = [job_params[i] for i in selected_rows]
    # return job_params


class ArgillaAutoTrainTrainer(ArgillaTrainerSkeleton):
    _logger = logging.getLogger("ArgillaAutoTrainTrainer")
    _logger.setLevel(logging.INFO)

    AUTOTRAIN_USERNAME = os.environ["AUTOTRAIN_USERNAME"]
    HF_TOKEN = os.environ["HF_AUTH_TOKEN"]

    require_version("autotrain-advanced")
    require_version("datasets")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_name = f"{self._workspace}_{self._name}_{str(uuid4())}"

        self._transformers_model = None
        self._transformers_tokenizer = None
        self._pipeline = None

        if self._seed is None:
            self._seed = 42

        if self._model is None:
            self._model = "AutoTrain"

        data_dict = {}
        self._num_samples = 0
        if isinstance(self._dataset, DatasetDict):
            self._train_dataset = self._dataset["train"]
            self._eval_dataset = self._dataset["test"]
            data_dict["valid_data"] = [self._eval_dataset.to_pandas().set_index("id")]
            data_dict["valid_data"][0]["label"] = data_dict["valid_data"][0]["label"].apply(
                lambda x: self._settings.id2label[x]
            )
            self._num_samples += len(self._eval_dataset)
        else:
            self._train_dataset = self._dataset
            self._eval_dataset = None
        data_dict["train_data"] = [self._train_dataset.to_pandas().set_index("id")]
        data_dict["train_data"][0]["label"] = data_dict["train_data"][0]["label"].apply(
            lambda x: self._settings.id2label[x]
        )

        self._num_samples += len(self._train_dataset)
        data_dict["train_data"][0].to_csv("train.csv")
        # exit()
        if self._record_class == rg.TextClassificationRecord:
            if self._multi_label:
                raise NotImplementedError("rg.TextClassificaiton multi_label is not supported by `autotrain-advanced`.")
            elif self._multi_label is False:
                n_classes = len(self._train_dataset.features["label"].names)
                if n_classes > 2:
                    self.task = "text_multi_class_classification"
                else:
                    self.task = "text_binary_classification"
                self._id2label = dict(enumerate(self._train_dataset.features["label"].names))
                self._label_list = self._train_dataset.features["label"].names
            self._label2id = {v: k for k, v in self._id2label.items()}
        elif self._record_class == rg.TokenClassificationRecord:
            self.task = "text_entity_extraction"
            raise NotImplementedError(
                "rg.Text2TextRecord and rg.TokenClassificationRecord is not supported by `autotrain-advanced`."
            )
        else:
            raise NotImplementedError(
                "rg.Text2TextRecord and rg.TokenClassificationRecord is not supported by `autotrain-advanced`."
            )

        from autotrain.dataset import AutoTrainDataset

        self.dset = AutoTrainDataset(
            task=self.task,
            token=self.HF_TOKEN,
            username=self.AUTOTRAIN_USERNAME,
            project_name=self.project_name,
            **data_dict,
            percent_valid=None,
            column_mapping={
                "text": "text",
                "label": "label",
            },
        )

        self.init_training_args()

    def get_project_cost(self):
        return get_project_cost(
            username=self.AUTOTRAIN_USERNAME,
            token=self.HF_TOKEN,
            task=self.task,
            num_samples=self._num_samples,
            num_models=5,
        )

    def init_training_args(self):
        from autotrain.params import Params

        self.trainer_kwargs = {}
        for training_type in ["autotrain", "hub_model"]:
            params = Params(
                task=self.task,
                training_type=training_type,
            ).get()
            default_params = {}

            for key, value in params.items():
                default_params[key] = value.DEFAULT
            self.trainer_kwargs[training_type] = default_params

        estimated_costs = self.get_project_cost()
        self._logger.info(f"Estimated cost: {estimated_costs}")

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
        for arg_dict_key, arg_dict_single in self.trainer_kwargs.items():
            formatted_string.append(arg_dict_key.upper())
            for key, val in arg_dict_single.items():
                formatted_string.append(f"{key}: {val}")
        return "\n".join(formatted_string)

    def train(self, output_dir: str):
        """
        We create a SetFitModel object from a pretrained model, then create a SetFitTrainer object with
        the model, and then train the model
        """
        from autotrain.project import Project

        print(self.trainer_kwargs)
        project = Project(
            dataset=self.dset,
            # hub_model=self._model if self._model != "AutoTrain" else None,
            job_params=get_job_params(
                job_params=[self.trainer_kwargs["hub_model"]]
                if self._model != "AutoTrain"
                else [self.trainer_kwargs["autotrain"]],
                task=self.task,
                param_choice=self._model,
            ),
        )
        self._logger.info(f"Project cost: {self.get_project_cost()}")
        project_id = project.create()
        project.approve(project_id)

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
