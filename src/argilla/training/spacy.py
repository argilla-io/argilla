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

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel

import argilla as rg

if TYPE_CHECKING:
    import spacy


class ArgillaSpaCyTrainer:
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
            model: A `str` with the `spaCy` model name e.g. "en_core_web_sm". Defaults to None.
            seed: A `int` with the seed for the random number generator. Defaults to None.
            multi_label: A `bool` indicating whether the task is multi-label or not. Defaults to False.
            language:
                A `str` with the `spaCy` language code e.g. "en". See all the supported languages and their
                codes in `spaCy` at https://spacy.io/usage/models#languages. Defaults to None.
            gpu_id: A `int` with the GPU id. Defaults to -1.

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

        self._train_dataset, self._valid_dataset = (
            dataset if isinstance(dataset, tuple) and len(dataset) > 1 else (dataset, None)
        )
        self._train_dataset_path = "./train.spacy"
        self._train_dataset.to_disk(self._train_dataset_path)
        if self._valid_dataset:
            self._valid_dataset_path = "./valid.spacy"
            self._valid_dataset.to_disk(self._valid_dataset_path)

        self._multi_label = multi_label

        self._record_class = record_class
        if self._record_class == rg.TokenClassificationRecord:
            self._column_mapping = {"text": "text", "token": "tokens", "ner_tags": "ner_tags"}
            self._pipeline_name = "ner"
        elif self._record_class == rg.TextClassificationRecord:
            self._column_mapping = {"text": "text", "label": "label"}
            self._pipeline_name = "textcat_multilabel" if self._multi_label else "textcat"
        else:
            raise NotImplementedError("`rg.Text2TextRecord` is not supported yet.")

        self.language = language or "en"
        self.gpu_id = gpu_id if spacy.prefer_gpu(gpu_id) else -1

        self.config = init_config(
            lang=self.language,
            pipeline=[self._pipeline_name],
        )
        self.config["paths"]["train"] = self._train_dataset_path
        self.config["paths"]["dev"] = self._valid_dataset_path or self._train_dataset_path
        self.config["paths"]["vectors"] = model
        self.config["system"]["seed"] = seed or 42

    def __repr__(self) -> None:
        """Return the string representation of the `ArgillaSpaCyTrainer` object containing
        just the args that can be updated via `update_config`."""
        formatted_string = []
        formatted_string.append("`ArgillaSpaCyTrainer`")
        for key, val in self.config["training"].items():
            if isinstance(val, dict):
                continue
            formatted_string.append(f"{key}: {val}")
        return "\n".join(formatted_string)

    def update_config(
        self,
        **spacy_training_config,
    ) -> None:
        """Update the `spaCy` training config.

        Disclaimer: currently just the `training` config is supported, but in the future
        we will support all the `spaCy` config values supported for a more precise control
        over the training process.

        Args:
            **spacy_training_config: The `spaCy` training config.
        """
        self.config["training"].update(spacy_training_config)

    def train(self) -> None:
        """Train the pipeline using `spaCy`."""
        from spacy.training.initialize import init_nlp
        from spacy.training.loop import train as train_nlp

        self._nlp = init_nlp(self.config, use_gpu=self.gpu_id)
        self._nlp, _ = train_nlp(self._nlp, use_gpu=self.gpu_id, stdout=sys.stdout, stderr=sys.stderr)

    def save(self, path: str) -> None:
        """Save the trained pipeline to disk.

        Args:
            path: A `str` with the path to save the pipeline.
        """
        path = Path(path) if isinstance(path, str) else path
        if path and not path.exists():
            path.mkdir(parents=True)
        self._nlp.to_disk(path)

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
        str_input = False
        if isinstance(text, str):
            text = [text]
            str_input = True

        formatted_prediction = []
        for t in text:
            doc = self._nlp(t)
            if self._pipeline_name == "ner":
                entities = [(ent.label_, ent.start_char, ent.end_char) for ent in doc.ents]
                pred = {
                    "text": t,
                    "tokens": [t.text for t in doc],
                    "prediction": entities,
                }
                if as_argilla_records:
                    pred = self._record_class(**pred)
            elif self._pipeline_name in ["textcat", "textcat_multilabel"]:
                pred = {
                    "text": t,
                    "prediction": [(k, v) for k, v in doc.cats.items()],
                }
                if as_argilla_records:
                    pred = self._record_class(**pred, multi_label=self._multi_label)
            formatted_prediction.append(pred)

        if str_input:
            formatted_prediction = formatted_prediction[0]
        return formatted_prediction
