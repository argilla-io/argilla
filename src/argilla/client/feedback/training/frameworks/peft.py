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

from typing import TYPE_CHECKING

from argilla.client.feedback.training.frameworks.transformers import ArgillaTransformersTrainer
from argilla.training.peft import ArgillaPeftTrainer as ArgillaPeftTrainerV1

if TYPE_CHECKING:
    from argilla.client.feedback.integrations.huggingface.card import PeftModelCardData


class ArgillaPeftTrainer(ArgillaPeftTrainerV1, ArgillaTransformersTrainer):
    def __init__(self, *args, **kwargs):
        ArgillaTransformersTrainer.__init__(self, *args, **kwargs)

    def model_card_data(self, **card_data_kwargs) -> "PeftModelCardData":
        """
        Generate the card data to be used for the `ArgillaModelCard`.

        Args:
            card_data_kwargs: Extra arguments provided by the user when creating the `ArgillaTrainer`.

        Returns:
            PeftModelCardData: Container for the data to be written on the `ArgillaModelCard`.
        """
        from argilla.client.feedback.integrations.huggingface.model_card import PeftModelCardData

        return PeftModelCardData(
            model_name=self._model,
            task=self._task,
            update_config_kwargs=self.lora_kwargs,
            **card_data_kwargs,
        )
