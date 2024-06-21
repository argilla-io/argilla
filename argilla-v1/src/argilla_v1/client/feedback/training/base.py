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
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Union

from argilla_v1.client.feedback.schemas.records import FeedbackRecord
from argilla_v1.client.feedback.training.schemas.base import TrainingTaskForTextClassification, TrainingTaskTypes
from argilla_v1.client.models import Framework, TextClassificationRecord
from argilla_v1.training.base import ArgillaTrainer as ArgillaTrainerV1
from argilla_v1.training.base import ArgillaTrainerSkeleton as ArgillaTrainerSkeletonV1

if TYPE_CHECKING:
    import spacy
    from transformers import PreTrainedModel, PreTrainedTokenizer

    from argilla_v1.client.feedback.dataset.local.dataset import FeedbackDataset
    from argilla_v1.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
    from argilla_v1.client.feedback.integrations.huggingface.model_card import ArgillaModelCard
    from argilla_v1.client.feedback.schemas.enums import ResponseStatusFilter
    from argilla_v1.client.feedback.schemas.records import SortBy


class ArgillaTrainer(ArgillaTrainerV1):
    def __init__(
        self,
        dataset: ["FeedbackDataset", "RemoteFeedbackDataset"],
        task: TrainingTaskTypes,
        framework: Framework,
        lang: Optional["spacy.Language"] = None,
        model: Optional[Union[str, "PreTrainedModel"]] = None,
        tokenizer: Optional["PreTrainedTokenizer"] = None,
        train_size: Optional[float] = None,
        seed: Optional[int] = None,
        gpu_id: Optional[int] = -1,
        filter_by: Optional[Dict[str, Union["ResponseStatusFilter", List["ResponseStatusFilter"]]]] = None,
        sort_by: Optional[List["SortBy"]] = None,
        max_records: Optional[int] = None,
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
            filter_by: A dict with key the field to filter by, and values the filters to apply. Currently only
                defined for `response_status` filters. Can be one of: draft, pending, submitted, and discarded.
                Defaults to `None` (no filter is applied).
            sort_by: A list of `SortBy` objects to sort your dataset by.
                Defaults to `None` (no filter is applied).
            max_records: the maximum number of records to use for training. Defaults to None.
            framework_kwargs: arguments for the framework's trainer. A special key (model_card_kwargs) is reserved
                for the arguments that can be passed to the model card.
            **load_kwargs: arguments for the rg.load() function.
        """
        if filter_by:
            dataset = dataset.filter_by(**filter_by)
        if sort_by:
            dataset = dataset.sort_by(sort_by)
        if max_records:
            dataset = dataset.pull(max_records=max_records)

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
            from argilla_v1.client.feedback.training.frameworks.setfit import ArgillaSetFitTrainer

            self._trainer = ArgillaSetFitTrainer(
                dataset=self._dataset,
                task=self._task,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
            )
        elif framework is Framework.TRANSFORMERS:
            from argilla_v1.client.feedback.training.frameworks.transformers import ArgillaTransformersTrainer

            self._trainer = ArgillaTransformersTrainer(
                dataset=self._dataset,
                task=self._task,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
                tokenizer=self._tokenizer,
            )
        elif framework is Framework.PEFT:
            from argilla_v1.client.feedback.training.frameworks.peft import ArgillaPeftTrainer

            self._trainer = ArgillaPeftTrainer(
                dataset=self._dataset,
                task=self._task,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
                tokenizer=self._tokenizer,
            )
        elif framework is Framework.SPACY:
            from argilla_v1.client.feedback.training.frameworks.spacy import ArgillaSpaCyTrainer

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
            from argilla_v1.client.feedback.training.frameworks.spacy import ArgillaSpaCyTransformersTrainer

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
            from argilla_v1.client.feedback.training.frameworks.openai import ArgillaOpenAITrainer

            self._trainer = ArgillaOpenAITrainer(
                dataset=self._dataset,
                task=self._task,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
            )
        elif framework is Framework.SPAN_MARKER:
            from argilla_v1.client.feedback.training.frameworks.span_marker import ArgillaSpanMarkerTrainer

            self._trainer = ArgillaSpanMarkerTrainer(
                dataset=self._dataset,
                task=self._task,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
            )
        elif framework is Framework.TRL:
            from argilla_v1.client.feedback.training.frameworks.trl import ArgillaTRLTrainer

            self._trainer = ArgillaTRLTrainer(
                dataset=self._dataset,
                task=self._task,
                prepared_data=self._prepared_data,
                seed=self._seed,
                model=self._model,
                tokenizer=self._tokenizer,
            )
        elif framework is Framework.SENTENCE_TRANSFORMERS:
            from argilla_v1.client.feedback.training.frameworks.sentence_transformers import (
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

    @property
    def task(self) -> TrainingTaskTypes:
        """The task to be trained."""
        return self._task

    @property
    def trainer(
        self,
    ):
        return self._trainer

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

    def generate_model_card(self, output_dir: Optional[str] = None) -> "ArgillaModelCard":
        """Generate and return a model card based on the model card data.

        Args:
            output_dir: If given, folder where the model card will be written.

        Returns:
            model_card: The model card.
        """
        from argilla_v1.client.feedback.integrations.huggingface.model_card import ArgillaModelCard

        if not self.model_card_kwargs.get("output_dir"):
            self.model_card_kwargs.update({"output_dir": f'"{output_dir}"'})

        model_card = ArgillaModelCard.from_template(
            card_data=self._trainer.get_model_card_data(**self.model_card_kwargs),
            template_path=ArgillaModelCard.default_template_path,
        )

        if output_dir:
            model_card_path = Path(output_dir) / "README.md"
            model_card.save(model_card_path)
            self._logger.info(f"Model card generated at: {model_card_path}")

        return model_card

    def push_to_huggingface(self, repo_id: str, generate_card: Optional[bool] = True, **kwargs) -> None:
        """Push your model to [huggingface's model hub](https://huggingface.co/models).

        Args:
            repo_id:
                The name of the repository you want to push your model and tokenizer to.
                It should contain your organization name when pushing to a given organization.
            generate_card:
                Whether to generate (and push) a model card for your model. Defaults to True.
        """
        if not kwargs.get("token"):
            # Try obtaining the token with huggingface_hub utils as a last resort, or let it fail.
            from huggingface_hub import HfFolder

            if token := HfFolder.get_token():
                kwargs["token"] = token

            # One last check for the tests. We use a different env var name
            # that the one gathered with HfFolder.get_token
            if token := kwargs.get("token", os.environ.get("HF_HUB_ACCESS_TOKEN", None)):
                kwargs["token"] = token

        url = self._trainer.push_to_huggingface(repo_id, **kwargs)

        if generate_card:
            model_card = self.generate_model_card()
            # For spacy based models, overwrite the repo_id with the url variable returned
            # from its trainer.
            if getattr(self._trainer, "language", None):
                repo_id = url

            model_card.push_to_hub(repo_id, repo_type="model", token=kwargs["token"])

    def update_config(self, *args, **kwargs) -> None:
        """
        Updates the `model_kwargs` and `trainer_kwargs` dictionaries with the keyword.add()

        Provides a warning if the keyword argument is not valid for the trainer or model.
        """

        def get_all_keys(d):
            keys = []
            for k, v in d.items():
                keys.append(k)
                if isinstance(v, dict):
                    keys += get_all_keys(v)
            return keys

        trainer_kwargs = self._trainer.get_trainer_kwargs()
        model_kwargs = self._trainer.get_model_kwargs()

        all_keys = get_all_keys({**trainer_kwargs, **model_kwargs})

        for kwarg in kwargs:
            if kwarg not in all_keys:
                warnings.warn(
                    f"'{kwarg}' is not a valid default argument for '{self._trainer.__class__.__name__}'. "
                    f"Valid default arguments are: {all_keys}. ",
                    UserWarning,
                    stacklevel=2,
                )
        return super().update_config(*args, **kwargs)


class ArgillaTrainerSkeleton(ArgillaTrainerSkeletonV1):
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
        self.model_kwargs = {}
        self.trainer_kwargs = {}
        self.trainer_model = None
        self.trainer_tokenizer = None
        self._trainer = None
