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
import shutil
from pathlib import Path

from argilla.training import ArgillaTrainer


def cleanup(trainer: ArgillaTrainer, output_dir: str, train: bool = True):
    try:
        if train:
            trainer.train(output_dir)
        else:
            trainer.save(output_dir)
        assert Path(output_dir).exists()
    finally:
        shutil.rmtree(output_dir)


def cleanup_spacy_config(trainer: ArgillaTrainer):
    for split in ["train", "dev"]:
        path = trainer._trainer.config["paths"][split]
        if path is not None and Path(path).exists():
            os.remove(path)
