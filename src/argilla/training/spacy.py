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

from typing import Dict, List, Optional, Union, TYPE_CHECKING

import argilla as rg

if TYPE_CHECKING:
    from spacy.tokens import DocBin


class ArgillaSpaCyTrainer:
    def __init__(
        self,
        dataset: Dict[str, "DocBin"],
        record_class: Union[
            rg.TextClassificationRecord, rg.TokenClassificationRecord, rg.Text2TextRecord
        ] = rg.DatasetForTokenClassification._RECORD_TYPE,
        model: Optional[str] = None,
    ) -> None:
        self._train_dataset, self._valid_dataset = (
            dataset if isinstance(dataset, tuple) and len(dataset) == 2 else (dataset, None)
        )
        self._train_dataset_path = self._train_dataset.to_disk("./train.spacy")
        if self._valid_dataset:
            self._valid_dataset = self._valid_dataset.to_disk("./valid.spacy")

        self.model = model  #  or "en_core_web_trf"

        self._record_class = record_class
        if self._record_class == rg.TokenClassificationRecord:
            self._column_mapping = {"text": "text", "token": "tokens", "ner_tags": "ner_tags"}
        else:
            raise NotImplementedError("`rg.TextClassificationRecord` and `rg.Text2TextRecord` are not supported yet.")

    def train(self) -> None:
        import spacy
        from spacy.cli.train import train as spacy_train
        from spacy.cli.init_config import init_config

        config_path = "train.cfg"
        init_config(
            lang="en",
            pipeline=["ner"],
        ).to_disk(config_path)

        output_model_path = "ner"
        spacy_train(
            config_path,
            output_path=output_model_path,
            overrides={
                "paths.train": "train.spacy",
                "paths.dev": "valid.spacy",
                "paths.vectors": self.model,
                "training.max_steps": 50,
            },
        )
        self._model = spacy.load(f"{output_model_path}/model-best")

    def save(self, path: str) -> None:
        pass

    def predict(self, text: Union[List[str], str], as_argilla_records: bool = True):
        if isinstance(text, str):
            text = [text]

        preds = []
        for t in text:
            doc = self._model(t)
            entities = [(ent.label_, ent.start_char, ent.end_char) for ent in doc.ents]
            pred = {
                "text": t,
                "tokens": [t.text for t in doc],
                "prediction": entities,
            }
            if as_argilla_records:
                pred = self._record_class(**pred)
            preds.append(pred)
        return preds
