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
from typing import TYPE_CHECKING, List, Optional, Tuple, Union

from argilla.client.feedback.training.base import ArgillaTrainerSkeleton
from argilla.client.feedback.training.schemas.base import TrainingTaskForSentenceSimilarity
from argilla.training.utils import filter_allowed_args, get_default_args
from argilla.utils.dependency import require_dependencies

if TYPE_CHECKING:
    from argilla.client.feedback.dataset import FeedbackDataset
    from argilla.client.feedback.integrations.huggingface.model_card import SentenceTransformerCardData


class ArgillaSentenceTransformersTrainer(ArgillaTrainerSkeleton):
    _logger = logging.getLogger("ArgillaSentenceTransformersTrainer")
    _logger.setLevel(logging.INFO)

    def __init__(
        self,
        dataset: "FeedbackDataset",
        task: TrainingTaskForSentenceSimilarity,
        prepared_data=None,
        model: str = None,
        seed: int = None,
        train_size: Optional[float] = 1,
        cross_encoder: bool = False,
    ) -> None:
        require_dependencies("sentence-transformers")

        super().__init__(
            dataset=dataset, task=task, prepared_data=prepared_data, model=model, train_size=train_size, seed=seed
        )

        # The prepared_data is lost in the TrainerSkeleton, is this intended?
        self._prepared_data = prepared_data
        self._cross_encoder = cross_encoder

        if model is None:
            if not self._cross_encoder:
                self._model = "sentence-transformers/all-MiniLM-L6-v2"
            else:
                self._model = "cross-encoder/ms-marco-MiniLM-L-6-v2"

            self._logger.info(
                f"No model was selected, using pre-defined `{'Cross-Encoder' if self._cross_encoder else 'Bi-Encoder'}` with `{self._model}`."
            )

        else:
            self._model = model

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
                raise ValueError(
                    f"Cross-encoders don't support training with triplets, the dataset has `{n}` sentences per sample."
                )

            from sentence_transformers import CrossEncoder

            self._trainer_cls = CrossEncoder
        else:
            from sentence_transformers import SentenceTransformer

            self._trainer_cls = SentenceTransformer

        self.model_kwargs = get_default_args(self._trainer_cls.__init__)
        self.trainer_kwargs = get_default_args(self._trainer_cls.fit)
        # These arguments don't exactly fit in either of the previous kwargs.
        # We store here arguments that can be passed to the DataLoader or
        # related to the dataset types defined in sentence-transformers.
        self.data_kwargs = {}
        self.data_kwargs["batch_size"] = 32
        self.data_kwargs["dataset_type"] = None

        # For a guide on the selection of the loss function:
        # https://huggingface.co/blog/how-to-train-sentence-transformers#loss-functions-for-training-a-sentence-transformers-model
        self._set_loss_cls(sample.label, len(sample.texts))
        self._logger.warning(f"`loss_cls` parameter set as default `{self._loss_cls}`.")

        if self._eval_dataset:
            self._set_evaluator(label=sample.label, number_of_sentences=len(sample.texts))
            self._logger.warning(f"`evaluator` parameter set to `{self.trainer_kwargs['evaluator']}` by default.")

    def _set_loss_cls(self, label: Optional[Union[int, float]], number_of_sentences: int) -> None:
        """
        Helper method to choose a loss class for the model based on the type
        of model, whether it has label or not and the number of sentences per example.

        Args:
            label: The label type, None should be passed if there is no label.
            number_of_sentences: number of sentences (two or three normally).
        """
        if label:
            if number_of_sentences == 2:
                if isinstance(label, int):
                    from sentence_transformers.losses import ContrastiveLoss

                    self._loss_cls = ContrastiveLoss
                else:
                    from sentence_transformers.losses import CosineSimilarityLoss

                    self._loss_cls = CosineSimilarityLoss

            else:
                if isinstance(label, int):
                    from sentence_transformers.losses import BatchHardTripletLoss

                    self._loss_cls = BatchHardTripletLoss
                else:
                    from sentence_transformers.losses import BatchAllTripletLoss

                    self._loss_cls = BatchAllTripletLoss
                    from sentence_transformers.datasets import SentenceLabelDataset

                    self.data_kwargs["dataset_type"] = SentenceLabelDataset

        else:
            if number_of_sentences == 3:
                from sentence_transformers.losses import TripletLoss

                self._loss_cls = TripletLoss
            else:
                from sentence_transformers.losses import MultipleNegativesRankingLoss

                self._loss_cls = MultipleNegativesRankingLoss

    def _set_evaluator(
        self, label: Optional[Union[int, float]] = None, number_of_sentences: int = None, evaluator_cls=None
    ) -> None:
        """
        Helper method to choose an evaluator for the model based on the type
        of model, whether it has label or not and the number of sentences per example.
        If neither label or number_of_sentences is set, it's assumed that evaluator_cls
        is passed (via update_config).

        Args:
            label: The label type, None should be passed if there is no label.
            number_of_sentences: Number of sentences (two or three normally).
            evaluator_cls: Class to set without "best guess".
        """
        if evaluator_cls:
            # When the user wants to set an evaluator on its own
            if self._eval_dataset:
                self._logger.warning("No `eval_dataset` found, `evaluator` cannot be set.")
            else:
                try:
                    self.trainer_kwargs["evaluator"] = evaluator_cls.from_input_examples(self._eval_dataset)
                except AttributeError:
                    # For the moment it's easier (and covers most of the cases?) to allow only
                    # a subset of the evaluators defined in sentence-transformers, inform
                    # the user the one selected is not allowed.
                    self.trainer_kwargs["evaluator"] = None
                    self._logger.warning(
                        "Currently only developed evaluators that implement `cls.from_input_examples` can be set."
                    )
        else:
            if label:
                if number_of_sentences == 2:
                    if isinstance(label, int):
                        # This should work, but for some reason in the tests with default values
                        # the classes cannot be instantiated, need some time to review.
                        # if self._cross_encoder:
                        #     from sentence_transformers.cross_encoder.evaluation import CEBinaryClassificationEvaluator
                        #     self.trainer_kwargs["evaluator"] = CEBinaryClassificationEvaluator.from_input_examples(self._eval_dataset)
                        # else:
                        #     from sentence_transformers.evaluation import BinaryClassificationEvaluator
                        #     self.trainer_kwargs["evaluator"] = BinaryClassificationEvaluator.from_input_examples(self._eval_dataset)
                        self.trainer_kwargs["evaluator"] = None

                    else:
                        if self._cross_encoder:
                            from sentence_transformers.cross_encoder.evaluation import CECorrelationEvaluator

                            self.trainer_kwargs["evaluator"] = CECorrelationEvaluator.from_input_examples(
                                self._eval_dataset
                            )
                        else:
                            from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator

                            self.trainer_kwargs["evaluator"] = EmbeddingSimilarityEvaluator.from_input_examples(
                                self._eval_dataset
                            )

                else:
                    from sentence_transformers.evaluation import TripletEvaluator

                    self.trainer_kwargs["evaluator"] = TripletEvaluator.from_input_examples(self._eval_dataset)
            else:
                if number_of_sentences == 3:
                    from sentence_transformers.evaluation import TripletEvaluator

                    self.trainer_kwargs["evaluator"] = TripletEvaluator.from_input_examples(self._eval_dataset)
                else:
                    # Hard to choose one here
                    self.trainer_kwargs["evaluator"] = None

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
            self.data_kwargs["batch_size"] = kwargs.pop("batch_size")

        # These parameters are allowed, but for simplicity
        # they are passed as self._model as positional argument to avoid errors
        # between Cross-Encoder/Bi-encoder.
        if "model_name_or_path" in kwargs:
            self._model = self.model_kwargs.pop("model_name_or_path")
        if "model_name" in kwargs:
            self._model = self.model_kwargs.pop("model_name")

        if "loss_cls" in kwargs:
            self._loss_cls = kwargs.pop("loss_cls")

        if "evaluator" in kwargs:
            self._set_evaluator(evaluator_cls=kwargs.pop("evaluator"))

    def train(self, output_dir: Optional[str] = None) -> None:
        """
        Trains the model.
        """
        from torch.utils.data import DataLoader

        self.init_model()

        if self.data_kwargs["dataset_type"]:
            dataloader = DataLoader(
                dataset=self.data_kwargs["dataset_type"](self._train_dataset), batch_size=self.data_kwargs["batch_size"]
            )
        else:
            dataloader = DataLoader(dataset=self._train_dataset, batch_size=self.data_kwargs["batch_size"])

        train_loss = self._loss_cls(self._trainer)

        if self._cross_encoder:
            train_objectives = dataloader
        else:
            train_objectives = [(dataloader, train_loss)]

        self._trainer.fit(train_objectives, **self.trainer_kwargs)

        if output_dir is not None:
            self.save(output_dir)

    def predict(
        self, text: Union[List[List[str]], Tuple[str, List[str]]], as_argilla_records: bool = False, **kwargs
    ) -> List[float]:
        """
        Predicts the similarity of the sentences.

        Args:
            text: The sentences to obtain the similarity from.
                Allowed inputs are:
                - A list with a single sentence (as a string) and a list of sentences to compare against.
                - A list with pair of sentences.
            as_argilla_records: If True, the prediction will be returned as an Argilla record. If
                False, the prediction will be returned as a string. Defaults to True

        Returns:
            A list of predicted similarities.
        """
        if isinstance(text[0], str):
            sentences = [(text[0], sentence) for sentence in text[1]]
        else:
            sentences = text

        if self._cross_encoder:
            prediction = list(self._trainer.predict(sentences, **kwargs))

        else:
            from sentence_transformers.util import cos_sim

            # Under this model we could potentially obtain the similarity of all vs all
            # the input sentences, but maybe is more intuitive to return only the similarities
            # between pairs as we do with the CrossEncoder predictions.
            sources, targets = zip(*sentences)
            embeds_source = self._trainer.encode(sources, **kwargs)
            embeds_target = self._trainer.encode(targets, **kwargs)
            prediction = list(cos_sim(embeds_source, embeds_target).numpy()[0])

        if as_argilla_records:
            raise NotImplementedError("To be done")

        return prediction

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

    def get_model_card_data(self, **card_data_kwargs) -> "SentenceTransformerCardData":
        """
        Generate the card data to be used for the `ArgillaModelCard`.

        Args:
            card_data_kwargs: Extra arguments provided by the user when creating the `ArgillaTrainer`.

        Returns:
            SentenceTransformerCardData: Container for the data to be written on the `ArgillaModelCard`.
        """
        from argilla.client.feedback.integrations.huggingface.model_card import SentenceTransformerCardData

        return SentenceTransformerCardData(
            model_id=self._model,
            task=self._task,
            framework_kwargs={"cross_encoder": self._cross_encoder},
            update_config_kwargs={**self.trainer_kwargs, **self.model_kwargs, **self.data_kwargs},
            trainer_cls=self._trainer_cls,
            **card_data_kwargs,
        )

    def push_to_huggingface(self, repo_id: str, **kwargs) -> None:
        """Uploads the model to [huggingface's model hub](https://huggingface.co/models).

        The full list of parameters can be seen at:
        [sentence-transformer api docs](https://www.sbert.net/docs/package_reference/SentenceTransformer.html#sentence_transformers.SentenceTransformer.save_to_hub).

        Args:
            repo_id:
                The name of the repository you want to push your model and tokenizer to.
                It should contain your organization name when pushing to a given organization.

        Raises:
            NotImplementedError:
                For `CrossEncoder` models, that currently aren't implemented underneath.
        """
        raise NotImplementedError("This method is not implemented for `ArgillaSentenceTransformersTrainer`.")
