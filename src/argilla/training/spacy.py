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
        self.config["system"]["seed"] = seed

    def __repr__(self) -> None:
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
        self.config["training"].update(spacy_training_config)

    def train(self) -> None:
        from spacy.training.initialize import init_nlp
        from spacy.training.loop import train as train_nlp

        self._nlp = init_nlp(self.config, use_gpu=self.gpu_id)
        self._nlp, _ = train_nlp(self._nlp, use_gpu=self.gpu_id, stdout=sys.stdout, stderr=sys.stderr)

    def save(self, path: str) -> None:
        path = Path(path) if isinstance(path, str) else path
        if path and not path.exists():
            path.mkdir(parents=True)
        self._nlp.to_disk(path)

    def predict(
        self, text: Union[List[str], str], as_argilla_records: bool = True
    ) -> Union[List[Dict[str, Any]], List[BaseModel]]:
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
