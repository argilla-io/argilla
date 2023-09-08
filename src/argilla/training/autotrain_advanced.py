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
from typing import List, Optional, Union
from uuid import uuid4

from datasets import DatasetDict

from argilla.client.models import TextClassificationRecord, TokenClassificationRecord
from argilla.training.base import ArgillaTrainerSkeleton
from argilla.utils.dependency import require_dependencies


class AutoTrainMixin:
    def prepare_dataset(self, data_dict: Optional[dict] = {}) -> None:
        """
        This function prepares a dataset for autotrain using a dictionary of data and specific column
        mappings.

        Args:
          data_dict_params: A dictionary that contains additional parameters to be passed
            to the `AutoTrainDataset` constructor. These parameters are optional and can be used to
            customize the dataset preparation process.
        """
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

    def get_project_cost(self):
        """
        This function returns the project cost based on various parameters.

        Returns:
          The `get_project_cost` function is being called with several arguments and its return value is
        being returned by the `get_project_cost` method. The exact return value depends on the
        implementation of the `get_project_cost` function.
        """
        from autotrain.utils import get_project_cost

        return get_project_cost(
            username=self.AUTOTRAIN_USERNAME,
            token=self.HF_TOKEN,
            task=self.task,
            num_samples=self._num_samples,
            num_models=self.trainer_kwargs["autotrain"][0]["num_models"]
            if self._model.lower() == "autotrain"
            else len(self.trainer_kwargs["hub_model"]),
        )

    def initialize_project(self):
        """
        This function initializes a project with a dataset, hub model, and job parameters, and logs
        information about the project and its cost.
        """
        import copy

        from autotrain.project import Project

        self.project = Project(
            dataset=self.dset,
            hub_model=None if self._model.lower() == "autotrain" else self._model,
            job_params=copy.deepcopy(self.get_job_params()),
        )
        self._logger.info(self.project)
        self._logger.info(f"Project cost: {self.get_project_cost()}")

    def get_job_params(self):
        if self._model.lower() == "autotrain":
            job_params = self.trainer_kwargs["autotrain"]
            model_choice = "autotrain"
        else:
            job_params = self.trainer_kwargs["hub_model"]
            model_choice = "HuggingFace Hub"
        if model_choice == "autotrain":
            if len(job_params) > 1:
                raise ValueError("Only one job parameter is allowed for AutoTrain.")
            job_params[0].update({"task": self.task})
        elif model_choice == "HuggingFace Hub":
            for i in range(len(job_params)):
                job_params[i].update({"task": self.task})
        return job_params


class ArgillaAutoTrainTrainer(ArgillaTrainerSkeleton, AutoTrainMixin):
    _logger = logging.getLogger("ArgillaAutoTrainTrainer")
    _logger.setLevel(logging.INFO)

    try:
        AUTOTRAIN_USERNAME = os.environ["AUTOTRAIN_USERNAME"]
        HF_TOKEN = os.environ["HF_AUTH_TOKEN"]
    except KeyError:
        raise KeyError("Please set the `AUTOTRAIN_USERNAME` and `HF_AUTH_TOKEN` environment variables.")

    require_dependencies(["autotrain-advanced", "datasets"])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.project_name = f"{self._workspace}_{self._name}_{str(uuid4())[:8]}"

        if self._seed:
            self._logger.warning("Setting a seed is not supported by `autotrain-advanced`.")
            self._seed = 42

        if self._model is None:
            self._model = "bert-base-uncased"
            self._logger.warning(f"No model defined. Using the default model {self._model}.")

        data_dict = {}
        self._num_samples = 0
        if isinstance(self._dataset, DatasetDict):
            self._train_dataset = self._dataset["train"]
            self._eval_dataset = self._dataset["test"]
            data_dict["valid_data"] = [self._eval_dataset.to_pandas()]
            self._num_samples += len(self._eval_dataset)
        else:
            self._train_dataset = self._dataset
            self._eval_dataset = None
            data_dict["valid_data"] = []
        data_dict["train_data"] = [self._train_dataset.to_pandas()]
        self._num_samples += len(self._train_dataset)

        if self._record_class == TextClassificationRecord:
            if self._multi_label:
                raise NotImplementedError(
                    "TextClassificaiton `multi_label=True` is not supported by `autotrain-advanced`."
                )
            elif self._multi_label is False:
                n_classes = len(self._train_dataset.features["label"].names)
                self.task = "text_multi_class_classification" if n_classes > 2 else "text_binary_classification"
                self._id2label = dict(enumerate(self._train_dataset.features["label"].names))
                self._label_list = self._train_dataset.features["label"].names
            self._label2id = {v: k for k, v in self._id2label.items()}
        elif self._record_class == TokenClassificationRecord:
            raise NotImplementedError(
                "`Text2Text` and `TokenClassification` tasks are not supported by `autotrain-advanced`."
            )

        self.init_training_args()

        self.prepare_dataset(data_dict=data_dict)
        self.initialize_project()

    def init_training_args(self):
        from autotrain.params import Params

        if not hasattr(self, "trainer_kwargs"):
            self.trainer_kwargs = {"autotrain": [{}], "hub_model": [{}]}
        for training_type in ["autotrain", "hub_model"]:
            for idx, set_params in enumerate(self.trainer_kwargs[training_type]):
                params = Params(
                    task=self.task,
                    training_type=training_type,
                ).get()
                for key, value in params.items():
                    if key not in set_params:
                        set_params[key] = value.DEFAULT

                self.trainer_kwargs[training_type][idx] = set_params

    def update_config(self, **kwargs):
        """
        Updates the `setfit_model_kwargs` and `setfit_trainer_kwargs` dictionaries with the keyword
        arguments passed to the `update_config` function.
        """
        self._model = kwargs.get("model", self._model)
        if self._model.lower() == "autotrain":
            self._model = "autotrain"
        if "hub_model" in kwargs:
            if not isinstance(kwargs["hub_model"], list):
                raise ValueError("hub_model must be a list of dictionaries.")
            self.trainer_kwargs["hub_model"] = kwargs["hub_model"]
        if "autotrain" in kwargs:
            if not isinstance(kwargs["autotrain"], list):
                raise ValueError("autotrain must be a list of dictionaries.")
            self.trainer_kwargs["autotrain"] = kwargs["autotrain"]

        self.init_training_args()
        self.initialize_project()

    def __repr__(self):
        formatted_string = [
            "Choose EITHER `autotrain` OR a model from the hub `hub_model` as main key to update parameters.",
            f"model: {self._model}",
        ]
        for arg_dict_key, arg_dict_single in self.trainer_kwargs.items():
            arg_dict_key += ": List[dict]"
            formatted_string.append(arg_dict_key)
            for idx, item in enumerate(arg_dict_single):
                for key, val in item.items():
                    formatted_string.append(f"\tjob{idx+1}-{key}: {val}")
        return "\n".join(formatted_string)

    def train(self, output_dir: str):
        """
        We create a SetFitModel object from a pretrained model, then create a SetFitTrainer object with
        the model, and then train the model
        """
        self.project.dataset.prepare()
        project_id = self.project.create()
        self.project.approve(project_id)

    def init_model(self, new: bool = False):
        pass

    def init_pipeline(self):
        pass

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
        self._logger.error(
            f"Use ArgillaTrainer(name={self._name}, workspace={self._workspace}, framework='transformers', model='my_model_name') for inference via `.predict()`."
        )

    def save(self, output_dir: str):
        """
        The function saves the model to the path specified, and also saves the label2id and id2label
        dictionaries to the same path

        Args:
          output_dir (str): the path to save the model to
        """
        self._logger.warning("Models are saved on the HuggingFace Hub, so this function is not supported.")
