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

from argilla_v1.client.feedback.training.frameworks.transformers import ArgillaTransformersTrainer
from argilla_v1.training.peft import ArgillaPeftTrainer as ArgillaPeftTrainerV1
from argilla_v1.utils.dependency import requires_dependencies

if TYPE_CHECKING:
    from argilla_v1.client.feedback.integrations.huggingface.model_card import PeftModelCardData


class ArgillaPeftTrainer(ArgillaPeftTrainerV1, ArgillaTransformersTrainer):
    def __init__(self, *args, **kwargs):
        ArgillaTransformersTrainer.__init__(self, *args, **kwargs)

    def get_model_card_data(self, **card_data_kwargs) -> "PeftModelCardData":
        """
        Generate the card data to be used for the `ArgillaModelCard`.

        Args:
            card_data_kwargs: Extra arguments provided by the user when creating the `ArgillaTrainer`.

        Returns:
            PeftModelCardData: Container for the data to be written on the `ArgillaModelCard`.
        """
        from argilla_v1.client.feedback.integrations.huggingface.model_card import PeftModelCardData

        return PeftModelCardData(
            model_id=self._model,
            task=self._task,
            update_config_kwargs=self.lora_kwargs,
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
        """
        if not self.trainer_model:
            raise ValueError(
                "The model must be initialized prior to this point. You can either call `train` or `init_model`."
            )
        model_url = self.trainer_model.push_to_hub(repo_id, **kwargs)
        self._logger.info(f"Model pushed to: {model_url}")
        tokenizer_url = self.trainer_tokenizer.push_to_hub(repo_id, **kwargs)
        self._logger.info(f"Tokenizer pushed to: {tokenizer_url}")
