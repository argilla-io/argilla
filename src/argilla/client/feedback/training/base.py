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

import os
import textwrap
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional, Union

from argilla.client.feedback.training.schemas import (
    TrainingTaskMappingForTextClassification,
)
from argilla.client.models import Framework, TextClassificationRecord
from argilla.training import ArgillaTrainer as ArgillaTrainerV1

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

if TYPE_CHECKING:
    import spacy


class ArgillaTrainer(ArgillaTrainerV1):
    def __init__(
        self,
        dataset: "argilla.client.feedback.schemas.FeedbackDataset",
        task_mapping: TrainingTaskMappingForTextClassification,
        framework: Framework,
        lang: Optional["spacy.Language"] = None,
        model: Optional[str] = None,
        train_size: Optional[float] = None,
        seed: Optional[int] = None,
        gpu_id: Optional[int] = -1,
        framework_kwargs: Optional[dict] = {},
        fetch_records: bool = True,
    ) -> None:
        """
        Initialize an Argilla Trainer.

        Args:
            dataset (FeedbackDataset): the dataset to be used for training.
            task_mapping (TrainingTaskMappingForTextClassification): the training data to be used for training.
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
            framework_kwargs (dict): arguments for the framework's trainer.
            **load_kwargs: arguments for the rg.load() function.
        """
        self._dataset = dataset
        self._train_size = train_size
        self._task_mapping = task_mapping
        self._seed = seed  # split is used for train-test-split and should therefore be fixed
        self._model = model

        self._prepared_data = self._dataset.prepare_for_training(
            framework=framework,
            task_mapping=task_mapping,
            fetch_records=fetch_records,
            train_size=train_size,
            seed=seed,
            lang=lang,
        )

        if isinstance(framework, str):
            framework = Framework(framework)

        if framework is Framework.SETFIT:
            if not isinstance(task_mapping, TrainingTaskMappingForTextClassification):
                raise NotImplementedError(f"{Framework.SETFIT} only supports `TextClassification` tasks.")
            from argilla.client.feedback.training.frameworks.setfit import (
                ArgillaSetFitTrainer,
            )

            self._trainer = ArgillaSetFitTrainer(
                feedback_dataset=self._dataset,
                task_mapping=self._task_mapping,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
            )
        elif framework is Framework.TRANSFORMERS:
            from argilla.client.feedback.training.frameworks.transformers import (
                ArgillaTransformersTrainer,
            )

            self._trainer = ArgillaTransformersTrainer(
                feedback_dataset=self._dataset,
                task_mapping=self._task_mapping,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
            )
        elif framework is Framework.PEFT:
            from argilla.client.feedback.training.frameworks.peft import (
                ArgillaPeftTrainer,
            )

            self._trainer = ArgillaPeftTrainer(
                feedback_dataset=self._dataset,
                task_mapping=self._task_mapping,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
            )
        elif framework is Framework.SPACY:
            from argilla.client.feedback.training.frameworks.spacy import (
                ArgillaSpaCyTrainer,
            )

            self._trainer = ArgillaSpaCyTrainer(
                feedback_dataset=self._dataset,
                task_mapping=self._task_mapping,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
                gpu_id=gpu_id,
                framework_kwargs=framework_kwargs,  # freeze_tok2vec
            )
        elif framework is Framework.SPACY_TRANSFORMERS:
            from argilla.client.feedback.training.frameworks.spacy import (
                ArgillaSpaCyTransformersTrainer,
            )

            self._trainer = ArgillaSpaCyTransformersTrainer(
                feedback_dataset=self._dataset,
                task_mapping=self._task_mapping,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
                gpu_id=gpu_id,
                framework_kwargs=framework_kwargs,  # update_transformer
            )
        elif framework is Framework.OPENAI:
            from argilla.client.feedback.training.frameworks.openai import (
                ArgillaOpenAITrainer,
            )

            self._trainer = ArgillaOpenAITrainer(
                feedback_dataset=self._dataset,
                task_mapping=self._task_mapping,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
            )
        elif framework is Framework.SPAN_MARKER:
            from argilla.client.feedback.training.frameworks.span_marker import (
                ArgillaSpanMarkerTrainer,
            )

            self._trainer = ArgillaSpanMarkerTrainer(
                feedback_dataset=self._dataset,
                task_mapping=self._task_mapping,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
            )
        else:
            raise NotImplementedError(f"{framework} is not a valid framework.")

        self._logger.info(self)

    def __repr__(self) -> str:
        """
        `trainer.__repr__()` prints out the trainer's parameters and a summary of how to use the trainer

        Returns:
          The trainer object.
        """
        return textwrap.dedent(
            f"""\
            ArgillaBaseTrainer info:
            _________________________________________________________________
            These baseline params are fixed:
                dataset: {self._dataset}
                task: {self._task_mapping}
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
            `trainer.save(output_dir)` to save the model manually.
            """
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
        return self._trainer.predict(text=text, as_argilla_records=False, **kwargs)


class ArgillaTrainerSkeleton(ABC):
    def __init__(
        self,
        feedback_dataset: "argilla.client.feedback.schemas.FeedbackDataset",
        task_mapping: TrainingTaskMappingForTextClassification,
        prepared_data=None,
        model: str = None,
        seed: int = None,
        *arg,
        **kwargs,
    ):
        self._feedback_dataset = feedback_dataset
        self._task_mapping = task_mapping
        self._dataset = prepared_data
        self._model = model
        self._seed = seed
        if isinstance(self._task_mapping, TrainingTaskMappingForTextClassification):
            self._multi_label = self._task_mapping.__multi_label__ or False
            self._label_list = self._task_mapping.__all_labels__ or None
            self._label2id = self._task_mapping.__label2id__
            self._id2label = self._task_mapping.__id2label__
            self._record_class = TextClassificationRecord  # TODO: dirty hack to inherit from original trainers

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
