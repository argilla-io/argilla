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

import argilla as rg
from argilla.training.setfit import ArgillaSetFitTrainer


class ArgillaBaseTrainer(object):
    logger = logging.getLogger("argilla.training")

    def __init__(self, name: str, framework: str, query: str = None, train_size: float = None, *args, **kwargs):
        self.name = name
        self.device = "cpu"
        self.multi_label = False
        self.split_applied = False
        if train_size:
            self.train_size = train_size
            self.split_applied = True

        self.rg_dataset_snapshot = rg.load(name=self.name, query="status: Validated", limit=1)
        assert len(self.rg_dataset) > 0, "Dataset must have at least one Validated record"
        if isinstance(self.rg_dataset_snapshot, rg.DatasetForTextClassification):
            self.rg_dataset_type = rg.DatasetForTextClassification
            self.required_fields = ["id", "text", "inputs", "annotation"]
            if self.rg_dataset_snapshot[0].multi_label:
                self.multi_label = True
        elif isinstance(self.rg_dataset_snapshot, rg.DatasetForTokenClassification):
            self.rg_dataset_type = rg.DatasetForTokenClassification
            self.required_fields = ["id", "text", "tokens", "ner_tags"]

        elif isinstance(self.rg_dataset_snapshot, rg.DatasetForText2Text):
            self.rg_dataset_type = rg.DatasetForText2Text
            self.required_fields = ["id", "text", "annotation"]
        else:
            raise NotImplementedError(f"Dataset type {type(self.rg_dataset_snapshot)} is not supported.")

        self.dataset_full = rg.load(name=self.name, query="status: Validated", fields=self.required_fields, **kwargs)
        self.dataset_full_prepared = self.dataset_full.prepare_for_training(
            framework=framework, train_size=self.train_size
        )

        if framework in ["transformers", "setfit"]:
            import torch

            if torch.backends.mps.is_available():
                self._device = "mps"
            elif torch.cuda.is_available():
                self._device = "cuda"
            else:
                self._device = "cpu"

        if framework == "setfit":
            assert self.rg_dataset_type == rg.DatasetForTextClassification, "SetFit supports only text classification"
            self._trainer = ArgillaSetFitTrainer(
                self.logger, dataset=self.dataset_full_prepared, multi_label=self.multi_label, device=self._device
            )
        else:
            raise NotImplementedError(f"Framework {framework} is not supported")

    def __repr__(self) -> str:
        return f"""
            Created a {self._trainer.__class__} trainer with decen parameters.
            1.
            _________________________________________________________________
            These baseline params are fixed:
                dataset: {self.name}
                multi_label: {self.multi_label}
                required_fields: {self.required_fields}
                train_size: {self.train_size*len(self.dataset_full)}
            2.
            _________________________________________________________________
            The {self._trainer.__trainer.__class__} parameters are configurable via `trainer.update_config()`:
                {self._trainer.__trainer.config.__doc__}
            3.
            _________________________________________________________________
            Use `trainer.train()` to train to start training.
            4.
            _________________________________________________________________
            Use trainer.save(path) to save the model.
        """

    def update_config(self, *args, **kwargs):
        self._trainer.update_config(*args, **kwargs)

    def train(self, path):
        self._trainer.train()

    def save(self, path: str):
        self._trainer.save(path)
