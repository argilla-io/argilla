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
from typing import TYPE_CHECKING, List, Union

from argilla.client.feedback.training.base import ArgillaTrainerSkeleton
from argilla.client.feedback.training.schemas import (
    TrainingTaskForDirectPreferenceOptimization,
    TrainingTaskForRewardModelling,
    TrainingTaskForSupervisedFinetuning,
)
from argilla.utils.dependency import require_version

if TYPE_CHECKING:
    from argilla.client.feedback.dataset import FeedbackDataset


class ArgillaTRLTrainer(ArgillaTrainerSkeleton):
    _logger = logging.getLogger("ArgillaTRLTrainer")
    _logger.setLevel(logging.INFO)

    require_version("trl")

    def __init__(
        self,
        feedback_dataset: "FeedbackDataset",
        task: Union[
            TrainingTaskForSupervisedFinetuning,
            TrainingTaskForRewardModelling,
            TrainingTaskForDirectPreferenceOptimization,
        ],
        prepared_data=None,
        model: str = None,
        seed: int = None,
    ):
        ArgillaTrainerSkeleton.__init__(
            self, feedback_dataset=feedback_dataset, task=task, prepared_data=prepared_data, model=model, seed=seed
        )

        # TODO: Do we need something like this?
        # if self._record_class is not FeedbackRecord:
        #     raise NotImplementedError("TRL only supports `FeedbackRecord` records.")

        self.init_training_args()

    def init_training_args(self):
        """
        Initializes the training arguments.
        """

    def init_model(self):
        """
        Initializes a model.
        """

    def update_config(self, *args, **kwargs):
        """
        Updates the configuration of the trainer, but the parameters depend on the trainer.subclass.
        """

    def predict(self, text: Union[List[str], str], as_argilla_records: bool = True, **kwargs):
        """
        Predicts the label of the text.
        """

    def train(self, output_dir: str = None):
        """
        Trains the model.
        """

    def save(self, output_dir: str):
        """
        Saves the model to the specified path.
        """
