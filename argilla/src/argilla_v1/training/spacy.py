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
import sys
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel

from argilla_v1.client.models import TextClassificationRecord, TokenClassificationRecord
from argilla_v1.training.base import ArgillaTrainerSkeleton
from argilla_v1.utils.dependency import require_dependencies

__all__ = ["ArgillaSpaCyTrainer", "ArgillaSpaCyTransformersTrainer"]


class _ArgillaSpaCyTrainerBase(ArgillaTrainerSkeleton):
    _logger = logging.getLogger("ArgillaSpaCyTrainer")
    _logger.setLevel(logging.INFO)

    def __init__(
        self,
        language: Optional[str] = None,
        gpu_id: Optional[int] = -1,
        model: Optional[str] = None,
        optimize: Literal["efficiency", "accuracy"] = "efficiency",
        *args,
        **kwargs,
    ) -> None:
        """Initialize the `_ArgillaSpaCyTrainerBase` class.

        Args:
            dataset: A `spacy.tokens.DocBin` object or a tuple of `spacy.tokens.DocBin` objects.
            record_class:
                A `TextClassificationRecord`, `TokenClassificationRecord`, or `Text2TextRecord`
                object. Defaults to None.
            seed: A `int` with the seed for the random number generator. Defaults to None.
            multi_label: A `bool` indicating whether the task is multi-label or not. Defaults to False.
            language:
                A `str` with the `spaCy` language code e.g. "en". See all the supported languages and their
                codes in `spaCy` at https://spacy.io/usage/models#languages. Defaults to None.
            gpu_id:
                the GPU ID to use. Defaults to -1, which means that the CPU will be used by default.
                GPU IDs start in 0, which stands for the default GPU in the system, if available.
            model:
                A `str` with the `spaCy` model name to use. If it contains vectors it
                can also be used for training/fine-tuning, e.g. "en_core_web_lg"
                contains vectors, while "en_core_web_sm" doesn't. Defaults to None.
            optimize:
                A `str` with the optimization strategy to use. Either "efficiency" or "accuracy".
                Defaults to "efficiency", which means that the model will be smaller, faster,
                and use less memory, but it will be less accurate. If "accuracy" is used, the model
                will be larger, slower, and use more memory, but it will be more accurate.
                Defaults to "efficiency".

        Raises:
            NotImplementedError: If the `record_class` is not supported or if the
                `init_training_args` method has not been implemented.
        """
        require_dependencies("spacy")
        super().__init__(*args, **kwargs)
        import spacy

        self._model = model

        if self._model is None:
            self._model = "en_core_web_sm"
            self._logger.warning(f"No model defined. Using the default model {self._model}.")

        if self._record_class == TokenClassificationRecord:
            self._column_mapping = {
                "text": "text",
                "token": "tokens",
                "ner_tags": "ner_tags",
            }
            self._spacy_pipeline_components = ["ner"]
        elif self._record_class == TextClassificationRecord:
            if self._multi_label:
                self._column_mapping = {"text": "text", "binarized_label": "label"}
                self._spacy_pipeline_components = ["textcat_multilabel"]
            else:
                self._column_mapping = {"text": "text", "label": "label"}
                self._spacy_pipeline_components = ["textcat"]
        else:
            raise NotImplementedError("`rg.Text2TextRecord` is not supported yet.")

        self._train_dataset, self._eval_dataset = (
            self._dataset if isinstance(self._dataset, tuple) and len(self._dataset) > 1 else (self._dataset, None)
        )
        self._train_dataset_path = "./train.spacy"
        self._eval_dataset_path = "./dev.spacy" if self._eval_dataset else "./train.spacy"

        self.language = language or "en"
        self.optimize = optimize

        self.gpu_id = gpu_id
        self.use_gpu = False
        if self.gpu_id != -1:
            self.use_gpu = spacy.prefer_gpu(self.gpu_id)

        if self.use_gpu:
            try:
                require_dependencies("torch")
                self.has_torch = True
            except Exception:
                self.has_torch = False

            try:
                require_dependencies("tensorflow")
                self.has_tensorflow = True
            except Exception:
                self.has_tensorflow = False

            if not self.has_torch and not self.has_tensorflow:
                self._logger(
                    "Either `torch` or `tensorflow` need to be installed to use the"
                    " GPU, since any of those is required as the GPU allocator. Falling"
                    " back to the CPU."
                )
                self.use_gpu = False
                self.gpu_id = -1

        self.init_training_args()

    def init_model(self):
        import spacy

        self.trainer_model = spacy.load(self._model)

    def __repr__(self) -> None:
        """Return the string representation of the `ArgillaSpaCyTrainer` object containing
        just the args that can be updated via `update_config`."""
        formatted_string = []
        formatted_string.append(
            "WARNING:`ArgillaSpaCyTrainer.update_config` only supports the update of"
            " the `training` arguments defined in the `config.yaml`."
        )
        formatted_string.append("\n`ArgillaSpaCyTrainer`")
        for key, val in self.trainer_kwargs["training"].items():
            if isinstance(val, dict):
                continue
            formatted_string.append(f"\t{key}: {val}")
        return "\n".join(formatted_string)

    def update_config(
        self,
        **spacy_training_config,
    ) -> None:
        """Update the `spaCy` training config.

        Disclaimer: currently just the `training` config is supported, but in the future
        we will support all the `spaCy` config values for more precise control
        over the training process. Also, note that the arguments may differ between the CPU
        and GPU training.

        Args:
            **spacy_training_config: The `spaCy` training config.
        """
        self.trainer_kwargs["training"].update(spacy_training_config)

    def train(self, output_dir: Optional[str] = None) -> None:
        """Train the pipeline using `spaCy`.

        Args:
            output_dir: A `str` with the path to save the trained pipeline. Defaults to None.
        """
        from spacy.training.initialize import init_nlp
        from spacy.training.loop import train as train_nlp

        self._logger.warning(
            "Note that the spaCy training is expected to be used through the CLI rather"
            " than programmatically, so the dataset needs to be dumped into the disk and"
            " then loaded from disk. More information at"
            " https://spacy.io/usage/training#api"
        )
        self._logger.info(f"Dumping the train dataset to {self._train_dataset_path}")
        self._train_dataset.to_disk(self._train_dataset_path)
        if self._eval_dataset:
            self._logger.info(f"Dumping the dev dataset to {self._eval_dataset_path}")
            self._eval_dataset.to_disk(self._eval_dataset_path)

        # Both `init_nlp` and `train_nlp` must be executed in the same Jupyter Notebook
        # cell if using the GPU, otherwise, since `thinc` is using `ContextVars` to
        # store the `Config` object, the `Config` object will be lost between cells and
        # the training will fail.
        self.trainer_model = init_nlp(self.trainer_kwargs, use_gpu=self.gpu_id)
        self.trainer_model, _ = train_nlp(self.trainer_model, use_gpu=self.gpu_id, stdout=sys.stdout, stderr=sys.stderr)

        if output_dir:
            self.save(output_dir)

    def save(self, output_dir: str) -> None:
        """Save the trained pipeline to disk.

        Args:
            output_dir: A `str` with the path to save the pipeline.
        """
        output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir
        if output_dir and not output_dir.exists():
            output_dir.mkdir(parents=True)
        self.trainer_model.to_disk(output_dir)

    def predict(
        self, text: Union[List[str], str], as_argilla_records: bool = True, **kwargs
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], BaseModel, List[BaseModel]]:
        """Predict the labels for the given text using the trained pipeline.

        Args:
            text: A `str` or a `List[str]` with the text to predict the labels for.
            as_argilla_records:
                A `bool` indicating whether to return the predictions as `argilla` records
                or as `dicts`. Defaults to True.

        Returns:
            Either a `dict`, `BaseModel` (if `as_argilla_records` is True) or a `List[dict]`,
            `List[BaseModel]` (if `as_argilla_records` is True) with the predictions.
        """
        if self.trainer_model is None:
            self._logger.warning("Using model without fine-tuning.")
            self.init_model()

        str_input = False
        if isinstance(text, str):
            text = [text]
            str_input = True

        formatted_prediction = []
        docs = self.trainer_model.pipe(text, **kwargs)
        if as_argilla_records:
            for doc in docs:
                if "ner" in self._spacy_pipeline_components:
                    entities = [(ent.label_, ent.start_char, ent.end_char) for ent in doc.ents]
                    pred = {
                        "text": doc.text,
                        "tokens": [t.text for t in doc],
                        "prediction": entities,
                    }
                    pred = self._record_class(**pred)
                elif any([p in self._spacy_pipeline_components for p in ["textcat", "textcat_multilabel"]]):
                    pred = {
                        "text": doc.text,
                        "prediction": [(k, v) for k, v in doc.cats.items()],
                    }
                    pred = self._record_class(**pred, multi_label=self._multi_label)
                else:
                    continue
                formatted_prediction.append(pred)
        else:
            formatted_prediction = docs

        if str_input:
            formatted_prediction = list(formatted_prediction)[0]
        return formatted_prediction


class ArgillaSpaCyTrainer(_ArgillaSpaCyTrainerBase):
    def __init__(self, freeze_tok2vec: bool = False, **kwargs) -> None:
        """
        Initialize the ArgillaSpaCyTrainer class.

        Args:
            freeze_tok2vec: A flag indicating whether to freeze the tok2vec weights
                during training. Defaults to False.
            **kwargs: Additional arguments for ArgillaSpaCyTrainerBase.

        Examples:
            >>> from argilla_v1 import ArgillaSpaCyTrainer
            >>> trainer = ArgillaSpaCyTrainer(freeze_tok2vec=True)
        """
        self.freeze_tok2vec = freeze_tok2vec
        super().__init__(**kwargs)

    def init_training_args(self) -> None:
        """
        This method is used to generate the `spacy` configuration file, which is used to train
        """
        from spacy.cli.init_config import init_config

        # We generate the config with GPU just when we are using `spacy-transformers`,
        # otherwise the default configuration will be messed up for `spacy`.
        self.trainer_kwargs = init_config(
            lang=self.language,
            pipeline=self._spacy_pipeline_components,
            optimize=self.optimize,
            gpu=False,
        )

        self.trainer_kwargs["paths"]["train"] = self._train_dataset_path
        self.trainer_kwargs["paths"]["dev"] = self._eval_dataset_path
        self.trainer_kwargs["system"]["seed"] = self._seed or 42

        # Now we can already set the GPU properties if we want to train/fine-tune a
        # `spacy` model using the GPU, or a `spacy-transformers` model using the CPU.
        self.trainer_kwargs["system"]["gpu_allocator"] = (
            ("pytorch" if self.has_torch else "tensorflow" if self.has_tensorflow else None) if self.use_gpu else None
        )
        self.trainer_kwargs["nlp"]["batch_size"] = 128 if self.use_gpu else 1000

        if "tok2vec" in self.trainer_kwargs["nlp"]["pipeline"]:
            # If we want to fine-tune the `tok2vec` component, then we need to set the
            # `init_tok2vec` path to the model we want to fine-tune.
            if self.freeze_tok2vec is False:
                self.trainer_kwargs["paths"]["init_tok2vec"] = self._model
            else:
                # Otherwise, if we don't want to fine-tune the `tok2vec` component, then we
                # need to set the `frozen_components` and `annotating_components` to
                # `["tok2vec"]`.
                self.trainer_kwargs["training"]["frozen_components"] = ["tok2vec"]
                self.trainer_kwargs["training"]["annotating_components"] = ["tok2vec"]


class ArgillaSpaCyTransformersTrainer(_ArgillaSpaCyTrainerBase):
    def __init__(self, update_transformer: bool = True, **kwargs) -> None:
        """Initialize the `ArgillaSpaCyTransformersTrainer` class.

        Args:
            update_transformer: A `bool` indicating whether to update the transformer
                weights during the training. Defaults to True.
            **kwargs: The `ArgillaSpaCyTrainerBase` arguments.
        """
        require_dependencies(
            ["spacy>=3.5.3", "spacy-transformers"]  # Required to generate the `spacy-transformers` configuration
        )
        self.update_transformer = update_transformer
        super().__init__(**kwargs)

    def init_training_args(self) -> None:
        """
        This method is used to generate the `spacy` configuration file, which is used to train
        """
        from spacy.cli.init_config import init_config

        # We generate the config with GPU just when we are using `spacy-transformers`,
        # otherwise the default configuration will be messed up for `spacy`.
        self.trainer_kwargs = init_config(
            lang=self.language,
            pipeline=self._spacy_pipeline_components,
            optimize=self.optimize,
            gpu=True,
        )

        self.trainer_kwargs["paths"]["train"] = self._train_dataset_path
        self.trainer_kwargs["paths"]["dev"] = self._eval_dataset_path
        self.trainer_kwargs["system"]["seed"] = self._seed or 42

        # Now we can already set the GPU properties if we want to train/fine-tune a
        # `spacy` model using the GPU, or a `spacy-transformers` model using the CPU.
        self.trainer_kwargs["system"]["gpu_allocator"] = (
            ("pytorch" if self.has_torch else "tensorflow" if self.has_tensorflow else None) if self.use_gpu else None
        )
        self.trainer_kwargs["nlp"]["batch_size"] = 128 if self.use_gpu else 16

        # If we use `spacy-transformers` then we need to set the `transformer` component
        # in the pipeline, and we need to set the `name` of the model to load.
        self.trainer_kwargs["components"]["transformer"]["name"] = self._model
        self.trainer_kwargs["nlp"]["pipeline"] = ["transformer"] + self._spacy_pipeline_components

        if "transformer" in self.trainer_kwargs["nlp"]["pipeline"]:
            # The `transformer` component cannot be frozen, but we can set the `grad_factor`
            # to 0.0 to avoid updating the weights of the `transformer` component. Even though
            # the computation of those weights will be performed, the gradients will be
            # multiplied by 0.0, so the weights will not be updated.
            # self.config["training"]["frozen_components"] = ["transformer"]
            # self.config["training"]["annotating_components"] = ["transformer"]
            if not self.update_transformer:
                self.trainer_kwargs["components"]["transformer"]["grad_factor"] = 0.0
