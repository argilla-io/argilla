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
import warnings
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from argilla.client.datasets import DatasetForText2Text, DatasetForTextClassification, DatasetForTokenClassification
from argilla.client.models import Framework, Text2TextRecord, TextClassificationRecord, TokenClassificationRecord
from argilla.client.singleton import active_client
from argilla.datasets import TextClassificationSettings, TokenClassificationSettings, load_dataset_settings
from argilla.utils.telemetry import get_telemetry_client

if TYPE_CHECKING:
    import spacy

    from argilla.client.feedback.integrations.huggingface import FrameworkCardData


class ArgillaTrainer(object):
    _logger = logging.getLogger("ArgillaTrainer")
    _logger.setLevel(logging.INFO)
    _CLIENT = get_telemetry_client()

    def __init__(
        self,
        name: str,
        framework: str,
        workspace: str = None,
        lang: Optional["spacy.Language"] = None,
        model: Optional[str] = None,
        train_size: Optional[float] = None,
        seed: Optional[int] = None,
        gpu_id: Optional[int] = -1,
        framework_kwargs: Optional[dict] = {},
        **load_kwargs: Optional[dict],
    ) -> None:
        """
        Initialize an Argilla Trainer.

        Args:
            name (str): the name of the dataset you want to load.
            framework (str):
                the framework to use for training. Currently, only "transformers", "setfit", and "spacy"
                are supported.
            lang (spacy.Language):
                the spaCy language model to use for training, just required when `framework="spacy"`.
                Defaults to None, but it will be set to `spacy.blank("en")` if not specified.
            model (str):
                name or path to the baseline model to be used. If not specified will set to a good default
                per framework, if applicable. Defaults to None.
            train_size (float):
                the size of the training set. If not specified, the entire dataset will be used for training,
                which may be an issue if `framework="spacy"` as it requires a validation set. Defaults to None.
            seed (int): the random seed to ensure reproducibility. Defaults to None.
            gpu_id (int):
                the GPU ID to use when training a SpaCy model. Defaults to -1, which means that the CPU
                will be used by default. GPU IDs start in 0, which stands for the default GPU in the system,
                if available.
            framework_kwargs (dict): additional arguments for the framework.
            **load_kwargs: arguments for the rg.load() function.
        """
        argilla = active_client()

        self._name = name
        self._workspace = workspace or argilla.get_workspace()
        self._multi_label = False
        self._split_applied = False
        self._train_size = train_size
        self._seed = seed  # split is used for train-test-split and should therefore be fixed
        self.model = model

        if train_size:
            self._split_applied = True

        _pytorch_fallback_env = "PYTORCH_ENABLE_MPS_FALLBACK"
        if _pytorch_fallback_env not in os.environ:
            os.environ[_pytorch_fallback_env] = "1"
            warnings.warn(f"{_pytorch_fallback_env} not set. Setting it to 1.", UserWarning, stacklevel=2)

        self.rg_dataset_snapshot = argilla.load(name=self._name, limit=1, workspace=workspace)
        if not len(self.rg_dataset_snapshot) > 0:
            raise ValueError(f"Dataset {self._name} is empty")

        if isinstance(self.rg_dataset_snapshot, DatasetForTextClassification):
            self._rg_dataset_type = DatasetForTextClassification
            self._multi_label = self.rg_dataset_snapshot[0].multi_label
        elif isinstance(self.rg_dataset_snapshot, DatasetForTokenClassification):
            self._rg_dataset_type = DatasetForTokenClassification
        elif isinstance(self.rg_dataset_snapshot, DatasetForText2Text):
            self._rg_dataset_type = DatasetForText2Text
        else:
            raise NotImplementedError(f"Dataset type {type(self.rg_dataset_snapshot)} is not supported.")

        self.dataset_full = argilla.load(name=self._name, **load_kwargs)

        # settings for the dataset
        self._settings = load_dataset_settings(name=self._name, workspace=workspace)
        if self._rg_dataset_type in [DatasetForTextClassification, DatasetForTokenClassification]:
            if self._settings is None:
                self._settings = self.dataset_full._infer_settings_from_records()

        framework = Framework(framework)
        if framework in [Framework.SPACY, Framework.SPACY_TRANSFORMERS]:
            import spacy

            self.dataset_full_prepared = self.dataset_full.prepare_for_training(
                framework=framework,
                settings=self._settings,
                train_size=self._train_size,
                seed=self._seed,
                lang=spacy.blank("en") if lang is None else lang,
            )
        else:
            self.dataset_full_prepared = self.dataset_full.prepare_for_training(
                framework=framework,
                settings=self._settings,
                train_size=self._train_size,
                seed=self._seed,
            )

        if framework is Framework.SETFIT:
            from argilla.training.setfit import ArgillaSetFitTrainer

            self._trainer = ArgillaSetFitTrainer(
                name=self._name,
                workspace=self._workspace,
                record_class=self._rg_dataset_type._RECORD_TYPE,
                dataset=self.dataset_full_prepared,
                multi_label=self._multi_label,
                settings=self._settings,
                seed=self._seed,
                model=self.model,
            )
        elif framework is Framework.TRANSFORMERS:
            from argilla.training.transformers import ArgillaTransformersTrainer

            self._trainer = ArgillaTransformersTrainer(
                name=self._name,
                workspace=self._workspace,
                record_class=self._rg_dataset_type._RECORD_TYPE,
                dataset=self.dataset_full_prepared,
                multi_label=self._multi_label,
                settings=self._settings,
                seed=self._seed,
                model=self.model,
            )
        elif framework is Framework.PEFT:
            from argilla.training.peft import ArgillaPeftTrainer

            self._trainer = ArgillaPeftTrainer(
                name=self._name,
                workspace=self._workspace,
                record_class=self._rg_dataset_type._RECORD_TYPE,
                dataset=self.dataset_full_prepared,
                multi_label=self._multi_label,
                settings=self._settings,
                seed=self._seed,
                model=self.model,
            )
        elif framework is Framework.SPACY:
            from argilla.training.spacy import ArgillaSpaCyTrainer

            self._trainer = ArgillaSpaCyTrainer(
                name=self._name,
                workspace=self._workspace,
                record_class=self._rg_dataset_type._RECORD_TYPE,
                dataset=self.dataset_full_prepared,
                model=self.model,
                multi_label=self._multi_label,
                settings=self._settings,
                seed=self._seed,
                gpu_id=gpu_id,
                **framework_kwargs,  # freeze_tok2vec
            )
        elif framework is Framework.SPACY_TRANSFORMERS:
            from argilla.training.spacy import ArgillaSpaCyTransformersTrainer

            self._trainer = ArgillaSpaCyTransformersTrainer(
                name=self._name,
                workspace=self._workspace,
                record_class=self._rg_dataset_type._RECORD_TYPE,
                dataset=self.dataset_full_prepared,
                model=self.model,
                multi_label=self._multi_label,
                settings=self._settings,
                seed=self._seed,
                gpu_id=gpu_id,
                **framework_kwargs,  # update_transformer
            )
        elif framework is Framework.OPENAI:
            from argilla.training.openai import ArgillaOpenAITrainer

            self._trainer = ArgillaOpenAITrainer(
                name=self._name,
                workspace=self._workspace,
                record_class=self._rg_dataset_type._RECORD_TYPE,
                dataset=self.dataset_full_prepared,
                model=self.model,
                multi_label=self._multi_label,
                settings=self._settings,
                seed=self._seed,
            )
        elif framework is Framework.SPAN_MARKER:
            if self._rg_dataset_type is not DatasetForTokenClassification:
                raise NotImplementedError(f"{Framework.SPAN_MARKER} only supports `TokenClassification` tasks.")
            from argilla.training.span_marker import ArgillaSpanMarkerTrainer

            self._trainer = ArgillaSpanMarkerTrainer(
                name=self._name,
                workspace=self._workspace,
                record_class=self._rg_dataset_type._RECORD_TYPE,
                dataset=self.dataset_full_prepared,
                model=self.model,
                multi_label=self._multi_label,
                settings=self._settings,
                seed=self._seed,
            )

        self._logger.info(self)
        self._track_trainer_usage(framework=framework, task=self._rg_dataset_type._RECORD_TYPE.__name__)

    def _track_trainer_usage(self, framework: str, task: str):
        self._CLIENT.track_data(action="ArgillaTrainerUsage", data={"framework": framework, "task": task})

    def __repr__(self) -> str:
        """
        `trainer.__repr__()` prints out the trainer's parameters and a summary of how to use the trainer

        Returns:
          The trainer object.
        """
        return f"""\
ArgillaBaseTrainer info:
_________________________________________________________________
These baseline params are fixed:
    dataset: {self._name}
    task: {self._rg_dataset_type.__name__}
    multi_label: {self._multi_label}
    train_size: {self._train_size}
    seed: {self._seed}

{self._trainer.__class__} info:
_________________________________________________________________
The parameters are configurable via `trainer.update_config()`:
    {self._trainer}

Using the trainer:
_________________________________________________________________
`trainer.train(output_dir)` to train to start training. `output_dir` is the directory to save the model automatically.
`trainer.predict(text, as_argilla_records=True)` to make predictions.
`trainer.save(output_dir)` to save the model manually."""

    def update_config(self, *args, **kwargs):
        """
        It updates the configuration of the trainer, but the parameters depend on the trainer.subclass.
        """
        self._trainer.update_config(*args, **kwargs)
        self._logger.info(
            "Updated parameters:\n"
            + "_________________________________________________________________\n"
            + f"{self._trainer}"
        )

    def predict(self, text: Union[List[str], str], as_argilla_records: bool = True, **kwargs):
        """
        `predict` takes a string or list of strings and returns a list of dictionaries, each dictionary
        containing the text, the predicted label, and the confidence score.

        Args:
          text (Union[List[str], str]): The text to be classified.
          as_argilla_records (bool): If True, the output will be a list of Argilla records instead of dictionaries. Defaults to True.

        Returns:
          A list of predictions or Argilla records.
        """
        return self._trainer.predict(text=text, as_argilla_records=as_argilla_records, **kwargs)

    def train(self, output_dir: str):
        """
        `train` takes in a path to a file and trains the model. If a path is provided,
        the model is saved to that path.

        Args:
          output_dir (str): The path to the model file.
        """
        self._trainer.train(output_dir)

    def save(self, output_dir: str):
        """
        Saves the model to the specified path.

        Args:
          output_dir (str): The path to the directory where the model will be saved.
        """
        self._trainer.save(output_dir)

    def get_model_kwargs(self):
        """
        Returns the model kwargs.
        """
        return self._trainer.get_model_kwargs()

    def get_trainer_kwargs(self):
        """
        Returns the training kwargs.
        """
        return self._trainer.get_trainer_kwargs()

    def get_trainer_model(self):
        """
        Returns the trainer model.
        """
        return self._trainer.get_model()

    def get_trainer_tokenizer(self):
        """
        Returns the trainer tokenizer.
        """
        return self._trainer.get_tokenizer()

    def get_trainer(self):
        """
        Returns the trainer trainer.
        """
        return self._trainer.get_trainer()


class ArgillaTrainerSkeleton(ABC):
    def __init__(
        self,
        name: str,
        dataset,
        record_class: Union[TokenClassificationRecord, Text2TextRecord, TextClassificationRecord],
        workspace: Optional[str] = None,
        multi_label: bool = False,
        settings: Union[TextClassificationSettings, TokenClassificationSettings] = None,
        model: str = None,
        seed: int = None,
        *arg,
        **kwargs,
    ):
        self._name = name
        self._workspace = workspace or get_workspace()
        self._dataset = dataset
        self._record_class = record_class
        self._multi_label = multi_label
        self._settings = settings
        if self._settings:
            self._label2id = self._settings.label2id or None
            self._id2label = self._settings.id2label
            self._label_list = list(self._label2id.keys())
        else:
            self._label_list = None
            self._label2id = None
            self._id2label = None
        self._model = model
        self._seed = seed
        self.model_kwargs = {}
        self.trainer_kwargs = {}
        self.trainer_model = None
        self.trainer_tokenizer = None
        self._trainer = None

    @abstractmethod
    def init_training_args(self):
        """
        Initializes the training arguments.
        """

    @abstractmethod
    def init_model(self):
        """
        Initializes a model.
        """

    @abstractmethod
    def update_config(self, *args, **kwargs):
        """
        Updates the configuration of the trainer, but the parameters depend on the trainer.subclass.
        """

    @abstractmethod
    def predict(self, text: Union[List[str], str], as_argilla_records: bool = True, **kwargs):
        """
        Predicts the label of the text.
        """

    @abstractmethod
    def train(self, output_dir: str = None):
        """
        Trains the model.
        """

    @abstractmethod
    def save(self, output_dir: str):
        """
        Saves the model to the specified path.
        """

    def get_model_card_data(self, card_data_kwargs: Dict[str, Any]) -> "FrameworkCardData":
        """
        Generates a `FrameworkCardData` instance to generate a model card from.
        """

    def push_to_huggingface(self, repo_id: str, **kwargs) -> Optional[str]:
        """
        Uploads the model to [Huggingface Hub](https://huggingface.co/docs/hub/models-the-hub).
        """

    def get_model_kwargs(self):
        """
        Returns the model kwargs.
        """
        return self.model_kwargs

    def get_trainer_kwargs(self):
        """
        Returns the training kwargs.
        """
        return self.trainer_kwargs

    def get_model(self):
        """
        Returns the model.
        """
        return self._model

    def get_tokenizer(self):
        """
        Returns the tokenizer.
        """
        return self.trainer_tokenizer

    def get_trainer(self):
        """
        Returns the trainer.
        """
        return self._trainer
