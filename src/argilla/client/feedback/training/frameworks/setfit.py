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

from argilla.client.feedback.training.frameworks.transformers import (
    ArgillaTransformersTrainer,
)
from argilla.client.models import TextClassificationRecord
from argilla.training.setfit import ArgillaSetFitTrainer as ArgillaSetFitTrainerV1
from argilla.utils.dependency import require_version


class ArgillaSetFitTrainer(ArgillaSetFitTrainerV1, ArgillaTransformersTrainer):
    _logger = logging.getLogger("ArgillaSetFitTrainer")
    _logger.setLevel(logging.INFO)

    require_version("torch")
    require_version("datasets")
    require_version("transformers")
    require_version("setfit>=0.6")

    def __init__(self, *args, **kwargs):
        if kwargs.get("model") is None and "model" in kwargs:
            kwargs["model"] = "all-MiniLM-L6-v2"
        self.multi_target_strategy = None
        self._column_mapping = None
        ArgillaTransformersTrainer.__init__(self, *args, **kwargs)

        if self._record_class is not TextClassificationRecord:
            raise NotImplementedError("SetFit only supports the `TextClassification` task.")

        if self._multi_label:
            self._column_mapping = {"text": "text", "binarized_label": "label"}
            self.multi_target_strategy = "one-vs-rest"
        else:
            self.multi_target_strategy = None
            self._column_mapping = {"text": "text", "label": "label"}
        self.init_training_args()
