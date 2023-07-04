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
from typing import Optional

from typing_extensions import Literal

from argilla.client.feedback.training.base import ArgillaTrainerSkeleton
from argilla.client.models import TextClassificationRecord, TokenClassificationRecord
from argilla.training.spacy import ArgillaSpaCyTrainer as ArgillaSpaCyTrainerV1
from argilla.training.spacy import (
    ArgillaSpaCyTransformersTrainer as ArgillaSpaCyTransformersTrainerV1,
)
from argilla.training.spacy import (
    _ArgillaSpaCyTrainerBase as _ArgillaSpaCyTrainerBaseV1,
)
from argilla.utils.dependency import require_version


class _ArgillaSpaCyTrainerBase(_ArgillaSpaCyTrainerBaseV1, ArgillaTrainerSkeleton):
    _logger = logging.getLogger("ArgillaSpaCyTrainer")
    _logger.setLevel(logging.INFO)

    require_version("spacy")

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

        self._nlp = None
        self._model = model

        self.config = {}

        if self._record_class == TokenClassificationRecord:
            self._column_mapping = {
                "text": "text",
                "token": "tokens",
                "ner_tags": "ner_tags",
            }
            self._pipeline = ["ner"]
        elif self._record_class == TextClassificationRecord:
            if self._multi_label:
                self._column_mapping = {"text": "text", "binarized_label": "label"}
                self._pipeline = ["textcat_multilabel"]
            else:
                self._column_mapping = {"text": "text", "label": "label"}
                self._pipeline = ["textcat"]
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
                require_version("torch")
                self.has_torch = True
            except Exception:
                self.has_torch = False

            try:
                require_version("tensorflow")
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
