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
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel

import argilla as rg
from argilla.utils.dependency import require_version

if TYPE_CHECKING:
    import spacy


class ArgillaSpaCyTrainer:
    _logger = logging.getLogger("ArgillaSpaCyTrainer")
    _logger.setLevel(logging.INFO)

    require_version("spacy")

    def __init__(
        self,
        dataset: Union["spacy.tokens.DocBin", Tuple["spacy.tokens.DocBin", "spacy.tokens.DocBin"]],
        record_class: Union[rg.TextClassificationRecord, rg.TokenClassificationRecord, rg.Text2TextRecord, None] = None,
        model: Optional[str] = None,
        seed: Optional[int] = None,
        multi_label: bool = False,
        language: Optional[str] = None,
        gpu_id: Optional[int] = -1,
    ) -> None:
        """Initialize the `ArgillaSpaCyTrainer` class.

        Args:
            dataset: A `spacy.tokens.DocBin` object or a tuple of `spacy.tokens.DocBin` objects.
            record_class:
                A `rg.TextClassificationRecord`, `rg.TokenClassificationRecord`, or `rg.Text2TextRecord`
                object. Defaults to None.
            model:
                A `str` with either the `spaCy` model name if using the CPU e.g. "en_core_web_lg", or
                the `spacy-transformers` model name if using the GPU instead e.g. "roberta-base". Defaults to None.
            seed: A `int` with the seed for the random number generator. Defaults to None.
            multi_label: A `bool` indicating whether the task is multi-label or not. Defaults to False.
            language:
                A `str` with the `spaCy` language code e.g. "en". See all the supported languages and their
                codes in `spaCy` at https://spacy.io/usage/models#languages. Defaults to None.
            gpu_id:
                the GPU ID to use. Defaults to -1, which means that the CPU will be used by default.
                GPU IDs start in 0, which stands for the default GPU in the system, if available.

        Raises:
            NotImplementedError: If `record_class` is `rg.Text2TextRecord`.

        Example:
            >>> from argilla import TokenClassificationRecord
            >>> from argilla.training import ArgillaSpaCyTrainer
            >>> dataset = ... # Load the dataset
            >>> trainer = ArgillaSpaCyTrainer(dataset, record_class=TokenClassificationRecord)
            >>> trainer.update_config(max_epochs=10)
            >>> trainer.train()
            >>> trainer.save("./model")
        """
        import spacy
        from spacy.cli.init_config import init_config

        self._multi_label = multi_label

        self._record_class = record_class
        if self._record_class == rg.TokenClassificationRecord:
            self._column_mapping = {"text": "text", "token": "tokens", "ner_tags": "ner_tags"}
            self._pipeline = ["ner"]
        elif self._record_class == rg.TextClassificationRecord:
            if self._multi_label:
                self._column_mapping = {"text": "text", "binarized_label": "label"}
                self._pipeline = ["textcat_multilabel"]
            else:
                self._column_mapping = {"text": "text", "label": "label"}
                self._pipeline = ["textcat"]
        else:
            raise NotImplementedError("`rg.Text2TextRecord` is not supported yet.")

        self._train_dataset, self._eval_dataset = (
            dataset if isinstance(dataset, tuple) and len(dataset) > 1 else (dataset, None)
        )
        self._train_dataset_path = "./train.spacy"
        self._eval_dataset_path = "./dev.spacy" if self._eval_dataset else None

        self.language = language or "en"
        self.model = model
        self.gpu_id = gpu_id
        self.use_gpu = self.gpu_id != -1
        if self.use_gpu:
            try:
                require_version("spacy-transformers")
                spacy.prefer_gpu(self.gpu_id)
            except:
                self.gpu_id = -1
                self.use_gpu = False
                if self.model is not None:
                    self.model = None

        self.config = init_config(
            lang=self.language,
            pipeline=self._pipeline,
            optimize="accuracy",
            gpu=self.use_gpu,
        )
        self.config["paths"]["train"] = self._train_dataset_path
        self.config["paths"]["dev"] = self._eval_dataset_path or self._train_dataset_path
        self.config["system"]["seed"] = seed or 42
        if self.use_gpu:
            self.config["components"]["transformer"]["model"]["name"] = model or "roberta-base"
        else:
            self.config["paths"]["vectors"] = model or "en_core_web_lg"

        self._nlp = None

    def _init_model(self):
        from spacy.training.initialize import init_nlp

        self._nlp = init_nlp(self.config, use_gpu=self.gpu_id)

    def __repr__(self) -> None:
        """Return the string representation of the `ArgillaSpaCyTrainer` object containing
        just the args that can be updated via `update_config`."""
        formatted_string = []
        formatted_string.append(
            "WARNING:`ArgillaSpaCyTrainer.update_config` only supports the update of the `training` "
            "arguments defined in the `config.yaml`."
        )
        formatted_string.append("\n`ArgillaSpaCyTrainer`")
        for key, val in self.config["training"].items():
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
        we will support all the `spaCy` config values supported for a more precise control
        over the training process. Also note that the arguments may differ between the CPU
        and GPU training.

        Args:
            **spacy_training_config: The `spaCy` training config.
        """
        self.config["training"].update(spacy_training_config)

    def train(self, output_dir: Optional[str] = None) -> None:
        """Train the pipeline using `spaCy`.

        Args:
            path: A `str` with the path to save the trained pipeline. Defaults to None.
        """
        from spacy.training.initialize import init_nlp
        from spacy.training.loop import train as train_nlp

        self._logger.warn(
            "Note that the spaCy training is expected to be used through the CLI rather than "
            "programatically, so the dataset needs to be dumped into the disk and then "
            "loaded from disk. More information at https://spacy.io/usage/training#api"
        )
        self._logger.info(f"Dumping the train dataset to {self._train_dataset_path}")
        self._train_dataset.to_disk(self._train_dataset_path)
        if self._eval_dataset:
            self._logger.info(f"Dumping the dev dataset to {self._eval_dataset_path}")
            self._eval_dataset.to_disk(self._eval_dataset_path)

        self._nlp = init_nlp(self.config, use_gpu=self.gpu_id)
        self._nlp, _ = train_nlp(self._nlp, use_gpu=self.gpu_id, stdout=sys.stdout, stderr=sys.stderr)
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
        self._nlp.to_disk(output_dir)

    def predict(
        self, text: Union[List[str], str], as_argilla_records: bool = True
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
        if self._nlp is None:
            self._logger.warn("Using model without fine-tuning.")
            self._init_model()

        str_input = False
        if isinstance(text, str):
            text = [text]
            str_input = True

        formatted_prediction = []
        docs = self._nlp.pipe(text)
        if as_argilla_records:
            for doc in docs:
                if "ner" in self._pipeline:
                    entities = [(ent.label_, ent.start_char, ent.end_char) for ent in doc.ents]
                    pred = {
                        "text": doc.text,
                        "tokens": [t.text for t in doc],
                        "prediction": entities,
                    }
                    pred = self._record_class(**pred)
                elif any([p in self._pipeline for p in ["textcat", "multilabel_textcat"]]):
                    pred = {
                        "text": doc.text,
                        "prediction": [(k, v) for k, v in doc.cats.items()],
                    }
                    pred = self._record_class(**pred, multi_label=self._multi_label)
                formatted_prediction.append(pred)
        else:
            formatted_prediction = docs

        if str_input:
            formatted_prediction = list(formatted_prediction)[0]
        return formatted_prediction
