#  coding=utf-8
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
from typing import Dict, List

import numpy as np

from rubrix import TextClassificationRecord
from rubrix.labeling.text_classification.weak_labels import WeakLabels

try:
    import snorkel
except ModuleNotFoundError:
    SNORKEL_INSTALLED = False
else:
    SNORKEL_INSTALLED = True
    from snorkel.labeling.model import LabelModel as SnorkelLabelModel
    from snorkel.utils.lr_schedulers import LRSchedulerConfig
    from snorkel.utils.optimizers import OptimizerConfig

_LOGGER = logging.getLogger(__name__)


class LabelModel:
    """Abstract base class for a label model implementation.

    Args:
        weak_labels: Every label model implementation needs at least a `WeakLabels` instance.
    """

    def __init__(self, weak_labels: WeakLabels):
        self._weak_labels = weak_labels

    @property
    def weak_labels(self) -> WeakLabels:
        """The underlying `WeakLabels` object, containing the weak labels and records."""
        return self._weak_labels

    def fit(self, include_annotated_records: bool = False, *args, **kwargs):
        """Fits the label model.

        Args:
            include_annotated_records: Whether or not to include annotated records in the training.
        """
        raise NotImplementedError

    def score(self, *args, **kwargs) -> Dict:
        """Evaluates the label model."""
        raise NotImplementedError

    def predict(
        self,
        include_annotated_records: bool = False,
        include_abstentions: bool = False,
        **kwargs,
    ) -> List[TextClassificationRecord]:
        """Applies the label model.

        Args:
            include_annotated_records: Whether or not to include annotated records.
            include_abstentions: Whether or not to include records in the output, for which the label model abstained.

        Returns:
            A list of records that include the predictions of the label model.
        """
        raise NotImplementedError


class Snorkel(LabelModel):
    """The label model by `Snorkel <https://github.com/snorkel-team/snorkel/>`_.

    Args:
        weak_labels: A `WeakLabels` object containing the weak labels and records.
        verbose: Whether to show print statements
        device: What device to place the model on ('cpu' or 'cuda:0', for example).
            Passed on to the `torch.Tensor.to()` calls.

    Examples:
        >>> from rubrix.labeling.text_classification import Rule, WeakLabels
        >>> rule = Rule(query="good OR best", label="Positive")
        >>> weak_labels = WeakLabels(rules=[rule], dataset="my_dataset")
        >>> label_model = Snorkel(weak_labels)
        >>> label_model.fit()
        >>> records = label_model.predict()
    """

    def __init__(
        self, weak_labels: WeakLabels, verbose: bool = True, device: str = "cpu"
    ):
        if not SNORKEL_INSTALLED:
            raise ModuleNotFoundError(
                "'snorkel' must be installed! You can install 'snorkel' with the command: `pip install snorkel`"
            )
        super().__init__(weak_labels)

        # Check if we need to change the weak labels to int mapping
        # Snorkel expects the abstain id to be -1 and the rest of the labels to be sequential
        if self._weak_labels.label2int[None] != -1 or sorted(
            self._weak_labels.int2label
        ) != list(range(-1, len(self._weak_labels.label2int) - 1)):
            labels = [None] + [
                label for label in self._weak_labels.label2int if label is not None
            ]
            label2int = {
                label: integer
                for label, integer in zip(
                    labels, range(-1, len(self._weak_labels.label2int) - 1)
                )
            }
            self._weak_labels.change_mapping(label2int)

        # instantiate Snorkel's label model
        self._model = SnorkelLabelModel(
            cardinality=len(self._weak_labels.label2int) - 1,
            verbose=verbose,
            device=device,
        )

    def fit(self, include_annotated_records: bool = False, **kwargs):
        """Fits the label model.

        Args:
            include_annotated_records: Whether or not to include annotated records in the training.
            **kwargs: Additional kwargs are passed on to Snorkel's
                `fit method <https://snorkel.readthedocs.io/en/latest/packages/_autosummary/labeling/snorkel.labeling.model.label_model.LabelModel.html#snorkel.labeling.model.label_model.LabelModel.fit>`_.
                They must not contain ``L_train``, the label matrix is provided automatically.
        """
        if "L_train" in kwargs:
            raise ValueError(
                "Your kwargs must not contain 'L_train', it is provided automatically."
            )

        l_train = self._weak_labels.matrix(
            has_annotation=None if include_annotated_records else False
        )

        self._model.fit(L_train=l_train, **kwargs)

    def predict(
        self,
        include_annotated_records: bool = False,
        include_abstentions: bool = False,
        tie_break_policy: str = "abstain",
    ) -> List[TextClassificationRecord]:
        """Returns a list of records that contain the predictions of the label model

        Args:
            include_annotated_records: Whether or not to include annotated records.
            include_abstentions: Whether or not to include records in the output, for which the label model abstained.
            tie_break_policy: Policy to break ties. You can choose among three policies:

                - `abstain`: Do not provide any prediction
                - `random`: randomly choose among tied option using deterministic hash
                - `true-random`: randomly choose among the tied options. NOTE: repeated runs may have slightly different results due to differences in broken ties

                The last two policies can introduce quite a bit of noise, especially when the tie is among many labels,
                as is the case when all of the labeling functions abstained.

        Returns:
            A list of records that include the predictions of the label model.
        """
        # get predictions and probabilities
        predictions, probabilities = self._model.predict(
            L=self._weak_labels.matrix(
                has_annotation=None if include_annotated_records else False
            ),
            return_probs=True,
            tie_break_policy=tie_break_policy,
        )

        # add predictions to records
        records_with_prediction = []
        for rec, pred, prob in zip(
            self._weak_labels.records(
                has_annotation=None if include_annotated_records else False
            ),
            predictions,
            probabilities,
        ):
            if not include_abstentions and pred == -1:
                continue

            records_with_prediction.append(rec.copy(deep=True))

            # set predictions to None if model abstained
            pred_for_rec = None
            if pred != -1:
                # If we have a tie, increase a bit the probability of the random winner (see tie_break_policy)
                if np.isclose(prob, prob.max()).sum() > 1:
                    prob[pred] += 0.0001
                pred_for_rec = [
                    (self._weak_labels.int2label[idx], prob[idx])
                    for idx in np.argsort(prob)[::-1]
                ]

            records_with_prediction[-1].prediction = pred_for_rec

        return records_with_prediction

    def score(self, tie_break_policy="abstain") -> Dict[str, float]:
        """Returns some scores of the label model with respect to the annotated records.

        Args:
            tie_break_policy: Policy to break ties. You can choose among three policies:

                - `abstain`: Do not provide any prediction
                - `random`: randomly choose among tied option using deterministic hash
                - `true-random`: randomly choose among the tied options. NOTE: repeated runs may have slightly different results due to differences in broken ties

                The last two policies can introduce quite a bit of noise, especially when the tie is among many labels,
                as is the case when all of the labeling functions abstained.

        Returns:
            A list of records that include the predictions of the label model.

        Raises:
            MissingAnnotationError: If the ``weak_labels`` do not contain annotated records.
        """
        if self._weak_labels.annotation().size == 0:
            raise MissingAnnotationError(
                "You need annotated records to compute scores/metrics for your label model."
            )

        # get predictions and probabilities
        predictions, probabilities = self._model.predict(
            L=self._weak_labels.matrix(has_annotation=True),
            return_probs=True,
            tie_break_policy=tie_break_policy,
        )

        # metrics are only calculated for non-abstained data points
        idx = predictions != -1
        if not idx.all():
            _LOGGER.warning(
                "Metrics are only calculated over non-abstained predictions!"
            )

        # accuracy
        metrics = {
            "accuracy": (predictions[idx] == self._weak_labels.annotation()[idx]).sum()
            / len(predictions[idx])
        }

        return metrics


class MissingAnnotationError(Exception):
    pass
