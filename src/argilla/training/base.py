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
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional, Union

import argilla as rg
from argilla.client.models import (
    Framework,
    Text2TextRecord,
    TextClassificationRecord,
    TokenClassificationRecord,
)
from argilla.datasets import TextClassificationSettings, TokenClassificationSettings

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

if TYPE_CHECKING:
    import spacy


class ArgillaTrainer(object):
    _logger = logging.getLogger("ArgillaTrainer")
    _logger.setLevel(logging.INFO)

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
            **load_kwargs: arguments for the rg.load() function.
        """
        self._name = name
        self._multi_label = False
        self._split_applied = False
        self._train_size = train_size
        self._seed = seed  # split is used for train-test-split and should therefore be fixed
        self.model = model

        if train_size:
            self._split_applied = True

        self.rg_dataset_snapshot = rg.load(name=self._name, limit=1, workspace=workspace)
        if not len(self.rg_dataset_snapshot) > 0:
            raise ValueError(f"Dataset {self._name} is empty")

        # settings for the dataset
        self._settings = rg.load_dataset_settings(name=self._name, workspace=workspace)

        if isinstance(self.rg_dataset_snapshot, rg.DatasetForTextClassification):
            self._rg_dataset_type = rg.DatasetForTextClassification
            self._multi_label = self.rg_dataset_snapshot[0].multi_label
        elif isinstance(self.rg_dataset_snapshot, rg.DatasetForTokenClassification):
            self._rg_dataset_type = rg.DatasetForTokenClassification
        elif isinstance(self.rg_dataset_snapshot, rg.DatasetForText2Text):
            self._rg_dataset_type = rg.DatasetForText2Text
        else:
            raise NotImplementedError(f"Dataset type {type(self.rg_dataset_snapshot)} is not supported.")

        self.dataset_full = rg.load(name=self._name, **load_kwargs)

        framework = Framework(framework)
        if framework is Framework.SPACY:
            import spacy

            self.dataset_full_prepared = self.dataset_full.prepare_for_training(
                framework=framework,
                train_size=self._train_size,
                seed=self._seed,
                lang=spacy.blank("en") if lang is None else lang,
            )
        else:
            self.dataset_full_prepared = self.dataset_full.prepare_for_training(
                framework=framework,
                train_size=self._train_size,
                seed=self._seed,
            )

        if framework is Framework.SETFIT:
            if self._rg_dataset_type is not rg.DatasetForTextClassification:
                raise NotImplementedError(f"{Framework.SETFIT} only supports `TextClassification` tasks.")
            from argilla.training.setfit import ArgillaSetFitTrainer

            self._trainer = ArgillaSetFitTrainer(
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
                record_class=self._rg_dataset_type._RECORD_TYPE,
                dataset=self.dataset_full_prepared,
                model=self.model,
                multi_label=self._multi_label,
                settings=self._settings,
                seed=self._seed,
                gpu_id=gpu_id,
            )
        elif framework is Framework.OPENAI:
            from argilla.training.openai import ArgillaOpenAITrainer

            if self._rg_dataset_type is rg.DatasetForTokenClassification:
                raise NotImplementedError(f"{Framework.OPENAI} does not support `TokenClassification` tasks.")
            elif self._rg_dataset_type is rg.DatasetForTextClassification and self._multi_label:
                raise NotImplementedError(f"{Framework.OPENAI} does not support multi-label TextClassification tasks.")
            self._trainer = ArgillaOpenAITrainer(
                record_class=self._rg_dataset_type._RECORD_TYPE,
                dataset=self.dataset_full_prepared,
                model=self.model,
                multi_label=self._multi_label,
                settings=self._settings,
                seed=self._seed,
            )
        elif framework is Framework.SPAN_MARKER:
            if self._rg_dataset_type is not rg.DatasetForTokenClassification:
                raise NotImplementedError(f"{Framework.SPAN_MARKER} only supports `TokenClassification` tasks.")
            from argilla.training.span_marker import ArgillaSpanMarkerTrainer

            self._trainer = ArgillaSpanMarkerTrainer(
                record_class=self._rg_dataset_type._RECORD_TYPE,
                dataset=self.dataset_full_prepared,
                model=self.model,
                multi_label=self._multi_label,
                settings=self._settings,
                seed=self._seed,
            )

        self._logger.info(self)

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

    def train(self, output_dir: str = None):
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


class ArgillaTrainerSkeleton(ABC):
    def __init__(
        self,
        dataset,
        record_class: Union[TokenClassificationRecord, Text2TextRecord, TextClassificationRecord],
        multi_label: bool = False,
        settings: Union[TextClassificationSettings, TokenClassificationSettings] = None,
        model: str = None,
        seed: int = None,
        *arg,
        **kwargs,
    ):
        self._dataset = dataset
        self._record_class = record_class
        self._multi_label = multi_label
        self._settings = settings
        self._model = model
        self._seed = seed

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
