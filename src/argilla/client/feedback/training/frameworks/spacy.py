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

from typing import Optional

from argilla.client.feedback.training.base import ArgillaTrainerSkeleton
from argilla.client.models import TextClassificationRecord, TokenClassificationRecord
from argilla.training.spacy import ArgillaSpaCyTrainer as ArgillaSpaCyTrainerV1
from argilla.utils.dependency import require_version


class ArgillaSpaCyTrainer(ArgillaSpaCyTrainerV1, ArgillaTrainerSkeleton):
    def __init__(
        self,
        language: Optional[str] = None,
        gpu_id: Optional[int] = -1,
        model: Optional[str] = None,
        *args,
        **kwargs,
    ) -> None:
        """Initialize the `ArgillaSpaCyTrainer` class.

        Args:
            dataset: A `spacy.tokens.DocBin` object or a tuple of `spacy.tokens.DocBin` objects.
            record_class:
                A `TextClassificationRecord`, `TokenClassificationRecord`, or `Text2TextRecord`
                object. Defaults to None.
            model:
                A `str` with either the `spaCy` model name if using the CPU e.g. "en_core_web_sm". Defaults to None.
            seed: A `int` with the seed for the random number generator. Defaults to None.
            multi_label: A `bool` indicating whether the task is multi-label or not. Defaults to False.
            language:
                A `str` with the `spaCy` language code e.g. "en". See all the supported languages and their
                codes in `spaCy` at https://spacy.io/usage/models#languages. Defaults to None.
            gpu_id:
                the GPU ID to use. Defaults to -1, which means that the CPU will be used by default.
                GPU IDs start in 0, which stands for the default GPU in the system, if available.

        Raises:
            NotImplementedError: If `record_class` is `Text2TextRecord`.

        Example:
            >>> from argilla import TokenClassificationRecord
            >>> from argilla.training import ArgillaSpaCyTrainer
            >>> dataset = ... # Load the dataset
            >>> trainer = ArgillaSpaCyTrainer(dataset, record_class=TokenClassificationRecord)
            >>> trainer.update_config(max_epochs=10)
            >>> trainer.train()
            >>> trainer.save("./model")
        """
        ArgillaTrainerSkeleton.__init__(self, *args, **kwargs)
        import spacy

        self._nlp = None
        self._model = model

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
            raise NotImplementedError("`Text2TextRecord` is not supported yet.")

        self._train_dataset, self._eval_dataset = (
            self._dataset if isinstance(self._dataset, tuple) and len(self._dataset) > 1 else (self._dataset, None)
        )
        self._train_dataset_path = "./train.spacy"
        self._eval_dataset_path = "./dev.spacy" if self._eval_dataset else None

        self.language = language or "en"

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
