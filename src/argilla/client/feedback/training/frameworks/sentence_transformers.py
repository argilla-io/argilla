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
from typing import List, Union, Optional, TYPE_CHECKING

from argilla.training.utils import get_default_args, filter_allowed_args
from argilla.utils.dependency import require_version

from argilla.client.feedback.training.base import ArgillaTrainerSkeleton
from argilla.client.feedback.training.schemas import TrainingTaskForSentenceSimilarity

if TYPE_CHECKING:
    from argilla.client.feedback.dataset import FeedbackDataset


class ArgillaSentenceTransformersTrainer(ArgillaTrainerSkeleton):
    _logger = logging.getLogger("ArgillaSentenceTransformersTrainer")
    _logger.setLevel(logging.INFO)

    # TODO: Update with https://github.com/argilla-io/argilla/pull/3555
    require_version("sentence-transformers")

    def __init__(
        self,
        dataset: "FeedbackDataset",
        task: TrainingTaskForSentenceSimilarity,
        prepared_data = None,
        model: str = None,
        seed: int = None,
        train_size: Optional[float] = 1,
        cross_encoder: bool = False
    ) -> None:
        super().__init__(dataset=dataset, task=task, prepared_data=prepared_data, model=model, train_size=train_size, seed=seed)

        # The prepared_data is lost in the TrainerSkeleton, is this intended?
        self._prepared_data = prepared_data
        self._cross_encoder = cross_encoder

        if model is None:
            if not self._cross_encoder:
                self._model = "sentence-transformers/all-MiniLM-L6-v2"
            else:
                self._model = "cross-encoder/ms-marco-MiniLM-L-6-v2"
 
        if isinstance(self._prepared_data, tuple):
            self._train_dataset = self._prepared_data[0]
            self._eval_dataset = self._prepared_data[1]
        else:
            self._train_dataset = self._prepared_data
            self._eval_dataset = None

        self._loss_cls = None
        self.init_training_args()

    def init_training_args(self) -> None:
        """
        Initializes the training arguments.
        """
        self.model_kwargs = {}

        # Use a sample of the dataset to do some checking
        sample = self._train_dataset[0]

        if self._cross_encoder:
            # Cross encoders don't support training with triplets
            if (n := len(sample.texts)) > 2:
                raise ValueError(f"Cross-encoders don't support training with triplets, the dataset has `{n}` sentences per sample.")

            from sentence_transformers import CrossEncoder
            self._trainer_cls = CrossEncoder
        else:
            from sentence_transformers import SentenceTransformer
            self._trainer_cls = SentenceTransformer

        self.model_kwargs = get_default_args(self._trainer_cls.__init__)
        self.trainer_kwargs = get_default_args(self._trainer_cls.fit)
        self.dataloader_kwargs = {}
        self.dataloader_kwargs["batch_size"] = 1
        self._dataset_type = None

        # For a guide on the selection of the loss function:
        # https://huggingface.co/blog/how-to-train-sentence-transformers#loss-functions-for-training-a-sentence-transformers-model
        if not self._loss_cls:
            if sample.label:
                if len(sample.texts) == 2:
                    if isinstance(sample.label, int):
                        from sentence_transformers.losses import ContrastiveLoss
                        self._loss_cls = ContrastiveLoss
                    else:
                        from sentence_transformers.losses import CosineSimilarityLoss
                        self._loss_cls = CosineSimilarityLoss
                else:
                    if isinstance(sample.label, int):
                        from sentence_transformers.losses import BatchHardTripletLoss
                        self._loss_cls = BatchHardTripletLoss
                    else:
                        from sentence_transformers.losses import BatchAllTripletLoss
                        self._loss_cls = BatchAllTripletLoss
                        from sentence_transformers.datasets import SentenceLabelDataset
                        self._dataset_type = SentenceLabelDataset
            else:
                if len(sample.texts) == 3:
                    from sentence_transformers.losses import TripletLoss
                    self._loss_cls = TripletLoss
                else:
                    from sentence_transformers.losses import MultipleNegativesRankingLoss
                    self._loss_cls = MultipleNegativesRankingLoss

    def init_model(self) -> None:
        """
        Initializes a model.
        """
        if "model_name_or_path" in self.model_kwargs:
            self.model_kwargs.pop("model_name_or_path")
        if "model_name" in self.model_kwargs:
            self.model_kwargs.pop("model_name")

        if "train_objectives" in self.trainer_kwargs:
            self.trainer_kwargs.pop("train_objectives")
        if "train_dataloader" in self.trainer_kwargs:
            self.trainer_kwargs.pop("train_dataloader")

        self._trainer = self._trainer_cls(self._model, **self.model_kwargs)
    
    def update_config(self, **kwargs) -> None:
        """
        Updates the configuration of the trainer, but the parameters depend on the trainer.subclass.
        """
        self.model_kwargs.update(filter_allowed_args(self._trainer_cls.__init__, **kwargs))
        self.trainer_kwargs.update(filter_allowed_args(self._trainer_cls.fit, **kwargs))

        if "batch_size" in kwargs:
            self.dataloader_kwargs["batch_size"] = kwargs["batch_size"]

        if "model" in self.model_kwargs:
            self._model = self.model_kwargs["model"]
            # self._model = self.model_kwargs["model_name_or_path"]

    def train(self, output_dir: Optional[str] = None) -> None:
        """
        Trains the model.
        """
        from torch.utils.data import DataLoader
        self.init_model()

        if self._dataset_type:
            dataloader = DataLoader(dataset=self._dataset_type(self._train_dataset), batch_size=self.dataloader_kwargs["batch_size"])
        else:
            dataloader = DataLoader(dataset=self._train_dataset, batch_size=self.dataloader_kwargs["batch_size"])

        train_loss = self._loss_cls(self._trainer)

        if self._cross_encoder:
            train_objectives = dataloader
        else:
            train_objectives = [(dataloader, train_loss)]
        
        self._trainer.fit(
            train_objectives,
            **self.trainer_kwargs
        )
        # NOTE: We haven't used the evaluator yet

        if output_dir is not None:
            self.save(output_dir)

    def predict(self, text: Union[List[str], str], as_argilla_records: bool = True, **kwargs):
        """
        Predicts the label of the text.
        """
        raise NotImplementedError("work in progress")

    def save(self, output_dir: str) -> None:
        """
        Saves the model to the specified path.
        """
        if self._cross_encoder:
            self._trainer.save(output_dir)
        else:
            # For the moment just save the in the simplest form, creating the model card or the
            # dataset for example should be done taking the extra information from the argilla 
            # dataset instead of the defaults
            self._trainer.save(output_dir, model_name=None, create_model_card=False, train_datasets=None)

    def __repr__(self) -> str:
        return type(self).__name__
