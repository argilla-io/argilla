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

from datasets import Dataset, DatasetDict

from argilla.client.feedback.training.base import ArgillaTrainerSkeleton
from argilla.client.feedback.training.schemas.base import (
    TrainingTaskForQuestionAnswering,
    TrainingTaskForTextClassification,
)
from argilla.training.transformers import ArgillaTransformersTrainer as ArgillaTransformersTrainerV1
from argilla.utils.dependency import requires_dependencies

if TYPE_CHECKING:
    from argilla.client.feedback.integrations.huggingface.model_card import TransformersModelCardData


class ArgillaTransformersTrainer(ArgillaTransformersTrainerV1, ArgillaTrainerSkeleton):
    def __init__(self, *args, **kwargs):
        # init ArgillaTrainerSkeleton
        ArgillaTrainerSkeleton.__init__(self, *args, **kwargs)

        import torch
        from transformers import (
            AutoModelForQuestionAnswering,
            AutoModelForSequenceClassification,
            set_seed,
        )

        model = kwargs.get("model", None)
        self.trainer_model = model if model and not isinstance(model, str) else None
        self.trainer_tokenizer = kwargs.get("tokenizer", None)
        self.trainer_pipeline = None

        self.device = "cpu"
        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"

        if self._seed is None:
            self._seed = 42
        set_seed(self._seed)

        if self._model is None:
            self._model = "bert-base-cased"

        if isinstance(self._dataset, DatasetDict):
            self._train_dataset = self._dataset["train"]
            self._eval_dataset = self._dataset["test"]
        elif isinstance(self._dataset, Dataset):
            self._train_dataset = self._dataset
            self._eval_dataset = None
        else:
            raise NotImplementedError(f"We do not support {type(self._dataset)} yet.")

        if isinstance(self._task, TrainingTaskForTextClassification):
            self._model_class = AutoModelForSequenceClassification
        elif isinstance(self._task, TrainingTaskForQuestionAnswering):
            self._model_class = AutoModelForQuestionAnswering
        else:
            raise NotImplementedError(
                f"ArgillaTransformersTrainer does not support {self._task.__class__.__name__} yet."
            )

        self.init_training_args()

    def get_model_card_data(self, **card_data_kwargs) -> "TransformersModelCardData":
        """
        Generate the card data to be used for the `ArgillaModelCard`.

        Args:
            card_data_kwargs: Extra arguments provided by the user when creating the `ArgillaTrainer`.

        Returns:
            TransformersModelCardData: Container for the data to be written on the `ArgillaModelCard`.
        """
        from argilla.client.feedback.integrations.huggingface.model_card import TransformersModelCardData

        if not card_data_kwargs.get("tags"):
            if isinstance(self._task, TrainingTaskForTextClassification):
                tags = ["text-classification"]
            else:
                tags = ["question-answering"]

            card_data_kwargs.update({"tags": tags + ["transformers", "argilla"]})

        return TransformersModelCardData(
            model_id=self._model,
            task=self._task,
            update_config_kwargs=self.trainer_kwargs,
            **card_data_kwargs,
        )

    @requires_dependencies("huggingface_hub")
    def push_to_huggingface(self, repo_id: str, **kwargs) -> None:
        """Uploads the transformer model and tokenizer to [huggingface's model hub](https://huggingface.co/models).

        The full list of parameters can be seen at:
        [huggingface_hub](https://huggingface.co/docs/huggingface_hub/package_reference/mixins#huggingface_hub.ModelHubMixin.push_to_hub).

        Args:
            repo_id:
                The name of the repository you want to push your model and tokenizer to.
                It should contain your organization name when pushing to a given organization.

        Raises:
            NotImplementedError: If the model doesn't exist, meaning it hasn't been instantiated yet.
        """
        if not self.trainer_model:
            raise ValueError(
                "The model must be initialized prior to this point. You can either call `train` or `init_model`."
            )
        model_url = self.trainer_model.push_to_hub(repo_id, **kwargs)
        self._logger.info(f"Model pushed to: {model_url}")
        tokenizer_url = self.trainer_tokenizer.push_to_hub(repo_id, **kwargs)
        self._logger.info(f"Tokenizer pushed to: {tokenizer_url}")
