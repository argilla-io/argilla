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
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Optional

from typing_extensions import Literal

from argilla.client.feedback.training.base import ArgillaTrainerSkeleton
from argilla.client.models import TextClassificationRecord, TokenClassificationRecord
from argilla.training.spacy import ArgillaSpaCyTrainer as ArgillaSpaCyTrainerV1
from argilla.training.spacy import ArgillaSpaCyTransformersTrainer as ArgillaSpaCyTransformersTrainerV1
from argilla.training.spacy import _ArgillaSpaCyTrainerBase as _ArgillaSpaCyTrainerBaseV1
from argilla.utils.dependency import require_dependencies, requires_dependencies

if TYPE_CHECKING:
    from argilla.client.feedback.integrations.huggingface.model_card import (
        SpacyModelCardData,
        SpacyTransformersModelCardData,
    )


class _ArgillaSpaCyTrainerBase(_ArgillaSpaCyTrainerBaseV1, ArgillaTrainerSkeleton):
    _logger = logging.getLogger("ArgillaSpaCyTrainer")
    _logger.setLevel(logging.INFO)

    require_dependencies("spacy")

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
        ArgillaTrainerSkeleton.__init__(self, *args, **kwargs)
        import spacy

        self._model = model

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

    def get_trainer_kwargs(self):
        """Get the trainer kwargs to be used in the `spacy` trainer."""
        return self.trainer_kwargs["training"]

    @requires_dependencies("spacy-huggingface-hub")
    def push_to_huggingface(self, output_dir: str, **kwargs) -> str:
        r"""Uploads the model to [huggingface's model hub](https://huggingface.co/models).

        With spacy we don't need the `repo_id` as in the other frameworks, that
        variable is generated internally by `spacy_huggingface_hub`, we need the
        path to the nlp pipeline to package it and push it.

        See Also:
            The optional arguments are the following:
            namespace: Name of organization to which the pipeline should be uploaded.
            commit_msg: Commit message to use for update
            verbose: Output additional info for debugging, e.g. the full generated hub metadata.

        Args:
            output_dir: The same path passed to `save` method. The path where the nlp pipeline
                should be saved to.

        Returns:
            model_name:
                The model name will be used in the base trainer to find the repo to push the model card.
                If the url of a model is: https://huggingface.co/<NAMESPACE>/<MODEL_NAME>,
                pass <NAMESPACE>/<MODEL_NAME>.
        """
        from spacy.cli.package import package
        from spacy_huggingface_hub import push

        if self.trainer_model is None:
            raise ValueError(
                "No pipeline was initialized, you must call either `init_model` or `train` before calling this method."
            )

        output_dir = Path(output_dir)
        with TemporaryDirectory() as tmpdirname:
            output_dir_pkg = Path(tmpdirname) / "spacy-packaged"
            output_dir_pkg.mkdir(exist_ok=True, parents=True)

            if not output_dir.is_dir():
                raise ValueError(
                    f"output_dir: '{output_dir.resolve()}' doesn't exist, you must pass the path to the folder of the trained model."
                )
            self._logger.info("Packaging nlp pipeline")
            package(
                input_dir=output_dir.resolve(),
                output_dir=output_dir_pkg,
                create_sdist=False,
                create_wheel=True,
                name=output_dir.stem,
            )
            self._logger.info(f"spacy pipeline packaged at: {output_dir_pkg}")

            # The following line obtains the full path to the .whl file:
            # The output dir contains a single package name. Inside this package
            # there will be a `dist` folder containing the packages. As we always
            # force to generate only the `wheel` package option, there we can only
            # find the .whl file. In case we generated both the wheel and sdist,
            # we could find it by getting the file with .whl extension.
            whl_path = next((next(output_dir_pkg.iterdir()) / "dist").iterdir())
            # Remove unused parameters from push to avoid errors:
            expected_kwargs = set(("namespace", "commig_msg", "silent", "verbose"))
            for kw in tuple(kwargs.keys()):
                if kw not in expected_kwargs:
                    kwargs.pop(kw)

            self._logger.info(f"Pushing: {whl_path} to huggingface hub.")
            result = push(whl_path, **kwargs)
            url = result["url"]

        self._logger.info(f"Model pushed to: {url}")
        # Passing the model name generated with spacy-huggingface-hub to use
        # it in the base ArgillaTrainer, it's easier to grab
        # the generated repo name than forcing the user to pass an argument.
        return url.replace("https://huggingface.co/", "")


class ArgillaSpaCyTrainer(ArgillaSpaCyTrainerV1, _ArgillaSpaCyTrainerBase):
    def __init__(self, freeze_tok2vec: bool = False, **kwargs) -> None:
        """Initialize the `ArgillaSpaCyTrainer` class.

        Args:
            freeze_tok2vec: A `bool` indicating whether to freeze the `tok2vec` weights
                during the training. Defaults to False.
            **kwargs: The `ArgillaSpaCyTrainerBase` arguments.

        Examples:
            >>> from argilla import ArgillaSpaCyTrainer
            >>> trainer = ArgillaSpaCyTrainer(
        """
        self.freeze_tok2vec = freeze_tok2vec
        _ArgillaSpaCyTrainerBase.__init__(self, **kwargs)

    def get_model_card_data(self, **card_data_kwargs) -> "SpacyModelCardData":
        """
        Generate the card data to be used for the `ArgillaModelCard`.

        Args:
            card_data_kwargs: Extra arguments provided by the user when creating the `ArgillaTrainer`.

        Returns:
            SpacyModelCardData: Container for the data to be written on the `ArgillaModelCard`.
        """
        from argilla.client.feedback.integrations.huggingface.model_card import SpacyModelCardData

        return SpacyModelCardData(
            model_id=self._model,
            task=self._task,
            lang=self.language,
            gpu_id=self.gpu_id,
            framework_kwargs={"optimize": self.optimize, "freeze_tok2vec": self.freeze_tok2vec},
            pipeline=self._spacy_pipeline_components,  # Used only to keep track for the config arguments
            update_config_kwargs=self.trainer_kwargs["training"],
            **card_data_kwargs,
        )


class ArgillaSpaCyTransformersTrainer(ArgillaSpaCyTransformersTrainerV1, _ArgillaSpaCyTrainerBase):
    def __init__(self, update_transformer: bool = True, **kwargs) -> None:
        """Initialize the `ArgillaSpaCyTransformersTrainer` class.

        Args:
            update_transformer: A `bool` indicating whether to update the transformer
                weights during the training. Defaults to True.
            **kwargs: The `ArgillaSpaCyTrainerBase` arguments.
        """
        self.update_transformer = update_transformer
        _ArgillaSpaCyTrainerBase.__init__(self, **kwargs)

    def get_model_card_data(self, **card_data_kwargs) -> "SpacyTransformersModelCardData":
        """
        Generate the card data to be used for the `ArgillaModelCard`.

        Args:
            card_data_kwargs: Extra arguments provided by the user when creating the `ArgillaTrainer`.

        Returns:
            SpacyTransformersModelCardData: Container for the data to be written on the `ArgillaModelCard`.
        """
        from argilla.client.feedback.integrations.huggingface.model_card import SpacyTransformersModelCardData

        return SpacyTransformersModelCardData(
            model_id=self._model,
            task=self._task,
            lang=self.language,
            gpu_id=self.gpu_id,
            framework_kwargs={"optimize": self.optimize, "update_transformer": self.update_transformer},
            pipeline=self._spacy_pipeline_components,  # Used only to keep track for the config arguments
            update_config_kwargs=self.trainer_kwargs["training"],
            **card_data_kwargs,
        )
