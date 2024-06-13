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
from typing import TYPE_CHECKING

from argilla_v1.client.feedback.training.frameworks.transformers import ArgillaTransformersTrainer
from argilla_v1.client.models import TextClassificationRecord
from argilla_v1.training.setfit import ArgillaSetFitTrainer as ArgillaSetFitTrainerV1
from argilla_v1.utils.dependency import require_dependencies, requires_dependencies

if TYPE_CHECKING:
    from argilla_v1.client.feedback.integrations.huggingface.model_card import SetFitModelCardData


class ArgillaSetFitTrainer(ArgillaSetFitTrainerV1, ArgillaTransformersTrainer):
    _logger = logging.getLogger("ArgillaSetFitTrainer")
    _logger.setLevel(logging.INFO)

    require_dependencies(["torch", "datasets", "transformers", "setfit>=0.6"])

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

    def get_model_card_data(self, **card_data_kwargs) -> "SetFitModelCardData":
        """
        Generate the card data to be used for the `ArgillaModelCard`.

        Args:
            card_data_kwargs: Extra arguments provided by the user when creating the `ArgillaTrainer`.

        Returns:
            SetFitModelCardData: Container for the data to be written on the `ArgillaModelCard`.
        """
        from argilla_v1.client.feedback.integrations.huggingface.model_card import SetFitModelCardData

        return SetFitModelCardData(
            model_id=self._model,
            task=self._task,
            update_config_kwargs={**self.model_kwargs, **self.trainer_kwargs},
            **card_data_kwargs,
        )

    @requires_dependencies("huggingface_hub")
    def push_to_huggingface(self, repo_id: str, **kwargs) -> None:
        """Uploads the model to [huggingface's model hub](https://huggingface.co/models).

        The full list of parameters can be seen at:
        [huggingface_hub](https://huggingface.co/docs/huggingface_hub/package_reference/mixins#huggingface_hub.ModelHubMixin.push_to_hub).

        Args:
            repo_id:
                The name of the repository you want to push your model and tokenizer to.
                It should contain your organization name when pushing to a given organization.

        Raises:
            NotImplementedError: If the model doesn't exist, meaning it hasn't been instantiated yet.
        """
        if not self._trainer:
            raise ValueError("The `trainer` must be initialized prior to this point. You should call `train`.")
        url = self._trainer.push_to_hub(repo_id, **kwargs)
        self._logger.info(f"Model pushed to: {url}")
