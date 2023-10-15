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
import warnings
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from argilla.client.feedback.schemas.records import FeedbackRecord
from argilla.client.feedback.training.schemas import TrainingTaskForTextClassification, TrainingTaskTypes
from argilla.client.models import Framework, TextClassificationRecord
from argilla.training import ArgillaTrainer as ArgillaTrainerV1

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

if TYPE_CHECKING:
    import spacy
    from transformers import PreTrainedModel, PreTrainedTokenizer

    from argilla.client.feedback.dataset import FeedbackDataset
    from argilla.client.feedback.integrations.huggingface.model_card import ArgillaModelCard, FrameworkCardData


class ArgillaTrainer(ArgillaTrainerV1):
    def __init__(
        self,
        dataset: "FeedbackDataset",
        task: TrainingTaskTypes,
        framework: Framework,
        lang: Optional["spacy.Language"] = None,
        model: Optional[Union[str, "PreTrainedModel"]] = None,
        tokenizer: Optional["PreTrainedTokenizer"] = None,
        train_size: Optional[float] = None,
        seed: Optional[int] = None,
        gpu_id: Optional[int] = -1,
        framework_kwargs: Optional[dict] = {},
    ) -> None:
        """
        Initialize an Argilla Trainer.

        Args:
            dataset: the dataset to be used for training.
            task: the training data to be used for training.
            framework: the framework to use for training. Currently, "transformers", "setfit", "spacy", "peft",
                "openai", "span_marker", "trl" and "sentence-transformers" are supported.
            lang: the spaCy language model to use for training, just required when `framework="spacy"`.
                Defaults to None, but it will be set to `spacy.blank("en")` if not specified.
            model: name or path to the baseline model to be used, or a transformers PreTrainedModel instance
                if the framework is "transformers", "peft" or "trl". If not specified will set to a good default
                per framework, if applicable. Defaults to None.
            tokenizer: a transformers PreTrainedTokenizer instance to tokenize the text. Only used with the
                "transformers", "peft" or "trl" frameworks.
            train_size: the size of the training set. If not specified, the entire dataset will be used for training,
                which may be an issue if `framework="spacy"` as it requires a validation set. Defaults to None.
            seed: the random seed to ensure reproducibility. Defaults to None.
            gpu_id: the GPU ID to use when training a SpaCy model. Defaults to -1, which means that the CPU
                will be used by default. GPU IDs start in 0, which stands for the default GPU in the system,
                if available.
            framework_kwargs: arguments for the framework's trainer. A special key (model_card_kwargs) is reserved
                for the arguments that can be passed to the model card.
            **load_kwargs: arguments for the rg.load() function.
        """
        self._dataset = dataset
        self._train_size = train_size
        self._task = task
        self._seed = seed  # split is used for train-test-split and should therefore be fixed
        self._model = model
        self._tokenizer = tokenizer

        self._prepared_data = self._dataset.prepare_for_training(
            framework=framework,
            task=task,
            train_size=train_size,
            seed=seed,
            lang=lang,
        )

        if isinstance(framework, str):
            framework = Framework(framework)

        if tokenizer and framework not in (Framework.TRANSFORMERS, Framework.PEFT, Framework.TRL):
            warnings.warn(
                f"Passing a tokenizer is not supported for the {framework} framework.", UserWarning, stacklevel=2
            )

        # Save the model_card arguments if given by the user
        if model_card_kwargs := framework_kwargs.pop("model_card_kwargs", None):
            self.model_card_kwargs = model_card_kwargs
        else:
            self.model_card_kwargs = {}

        if framework is Framework.SETFIT:
            if not isinstance(task, TrainingTaskForTextClassification):
                raise NotImplementedError(f"{Framework.SETFIT} only supports `TextClassification` tasks.")
            from argilla.client.feedback.training.frameworks.setfit import ArgillaSetFitTrainer

            self._trainer = ArgillaSetFitTrainer(
                dataset=self._dataset,
                task=self._task,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
            )
        elif framework is Framework.TRANSFORMERS:
            from argilla.client.feedback.training.frameworks.transformers import ArgillaTransformersTrainer

            self._trainer = ArgillaTransformersTrainer(
                dataset=self._dataset,
                task=self._task,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
                tokenizer=self._tokenizer,
            )
        elif framework is Framework.PEFT:
            from argilla.client.feedback.training.frameworks.peft import ArgillaPeftTrainer

            self._trainer = ArgillaPeftTrainer(
                dataset=self._dataset,
                task=self._task,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
                tokenizer=self._tokenizer,
            )
        elif framework is Framework.SPACY:
            from argilla.client.feedback.training.frameworks.spacy import ArgillaSpaCyTrainer

            self._trainer = ArgillaSpaCyTrainer(
                dataset=self._dataset,
                task=self._task,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
                gpu_id=gpu_id,
                framework_kwargs=framework_kwargs,  # freeze_tok2vec
            )
        elif framework is Framework.SPACY_TRANSFORMERS:
            from argilla.client.feedback.training.frameworks.spacy import ArgillaSpaCyTransformersTrainer

            self._trainer = ArgillaSpaCyTransformersTrainer(
                dataset=self._dataset,
                task=self._task,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
                gpu_id=gpu_id,
                framework_kwargs=framework_kwargs,  # update_transformer
            )
        elif framework is Framework.OPENAI:
            from argilla.client.feedback.training.frameworks.openai import ArgillaOpenAITrainer

            self._trainer = ArgillaOpenAITrainer(
                dataset=self._dataset,
                task=self._task,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
            )
        elif framework is Framework.SPAN_MARKER:
            from argilla.client.feedback.training.frameworks.span_marker import ArgillaSpanMarkerTrainer

            self._trainer = ArgillaSpanMarkerTrainer(
                dataset=self._dataset,
                task=self._task,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
            )
        elif framework is Framework.TRL:
            from argilla.client.feedback.training.frameworks.trl import ArgillaTRLTrainer

            self._trainer = ArgillaTRLTrainer(
                dataset=self._dataset,
                task=self._task,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
                tokenizer=self._tokenizer,
            )
        elif framework is Framework.SENTENCE_TRANSFORMERS:
            from argilla.client.feedback.training.frameworks.sentence_transformers import (
                ArgillaSentenceTransformersTrainer,
            )

            self._trainer = ArgillaSentenceTransformersTrainer(
                dataset=self._dataset,
                task=self._task,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
                **framework_kwargs,  # cross_encoder
            )
        else:
            raise NotImplementedError(f"{framework} is not a valid framework.")

        self._logger.info(self)
        self._track_trainer_usage(framework=framework, task=self._task.__class__.__name__)

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
                task: {self._task}
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

    def save(self, output_dir: str, generate_card: bool = True) -> None:
        """
        Saves the model to the specified path and optionally generates a `ModelCard` at the same `output_dir`.

        Args:
            output_dir: The path to the directory where the model will be saved.
            generate_card: Whether to generate a model card of the `ArgillaTrainer` for the HuggingFace Hub. Defaults
                to `True`.
        """
        super().save(output_dir)

        if generate_card:
            self.generate_model_card(output_dir)

    def generate_model_card(self, output_dir: str) -> "ArgillaModelCard":
        """Generate and return a model card based on the model card data.

        Args:
            output_dir: Folder where the model card will be written.

        Returns:
            model_card: The model card.
        """
        from argilla.client.feedback.integrations.huggingface.model_card import ArgillaModelCard

        if not self.model_card_kwargs.get("output_dir"):
            self.model_card_kwargs.update({"output_dir": f'"{output_dir}"'})

        model_card = ArgillaModelCard.from_template(
            card_data=self._trainer.get_model_card_data(**self.model_card_kwargs),
            template_path=ArgillaModelCard.default_template_path,
        )

        model_card_path = Path(output_dir) / "README.md"
        model_card.save(model_card_path)
        self._logger.info(f"Model card generated at: {model_card_path}")
        return model_card


class ArgillaTrainerSkeleton(ABC):
    def __init__(
        self,
        dataset: "FeedbackDataset",
        task: TrainingTaskTypes,
        prepared_data=None,
        model: str = None,
        seed: int = None,
        *arg,
        **kwargs,
    ):
        self._dataset = dataset
        self._task = task
        self._dataset = prepared_data
        self._model = model
        self._seed = seed
        if isinstance(self._task, TrainingTaskForTextClassification):
            self._multi_label = self._task.__multi_label__ or False
            self._label_list = self._task.__all_labels__ or None
            self._label2id = self._task.__label2id__
            self._id2label = self._task.__id2label__
            self._record_class = TextClassificationRecord  # TODO: dirty hack to inherit from original trainers
        else:
            self._record_class = FeedbackRecord

    @abstractmethod
    def init_training_args(self) -> None:
        """
        Initializes the training arguments.
        """

    @abstractmethod
    def init_model(self) -> None:
        """
        Initializes a model.
        """

    @abstractmethod
    def update_config(self, *args, **kwargs) -> None:
        """
        Updates the configuration of the trainer, but the parameters depend on the trainer.subclass.
        """

    @abstractmethod
    def predict(self, text: Union[List[str], str], as_argilla_records: bool = True, **kwargs) -> None:
        """
        Predicts the label of the text.
        """

    @abstractmethod
    def train(self, output_dir: Optional[str] = None) -> None:
        """
        Trains the model.
        """

    @abstractmethod
    def save(self, output_dir: str) -> None:
        """
        Saves the model to the specified path.
        """

    @abstractmethod
    def get_model_card_data(self, card_data_kwargs: Dict[str, Any]) -> "FrameworkCardData":
        """
        Generates a `FrameworkCardData` instance to generate a model card from.
        """
