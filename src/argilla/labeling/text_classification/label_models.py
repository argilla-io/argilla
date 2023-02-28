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
import hashlib
import logging
from enum import Enum
from typing import Dict, List, Tuple, Union

import numpy as np

from argilla import DatasetForTextClassification, TextClassificationRecord
from argilla.labeling.text_classification.weak_labels import WeakLabels, WeakMultiLabels
from argilla.utils.dependency import requires_version

_LOGGER = logging.getLogger(__name__)


class TieBreakPolicy(Enum):
    """A tie break policy"""

    ABSTAIN = "abstain"
    RANDOM = "random"
    TRUE_RANDOM = "true-random"

    @classmethod
    def _missing_(cls, value):
        raise ValueError(
            f"{value} is not a valid {cls.__name__}, please select one of" f" {list(cls._value2member_map_.keys())}"
        )


class LabelModel:
    """Abstract base class for a label model implementation.

    Args:
        weak_labels: Every label model implementation needs at least a `WeakLabels` instance.
    """

    # When we break a tie, by how much shall we increase the probability of the winner?
    _PROBABILITY_INCREASE_ON_TIE_BREAK = 0.0001

    def __init__(self, weak_labels: WeakLabels):
        self._weak_labels = weak_labels

    @property
    def weak_labels(self) -> WeakLabels:
        """The underlying `WeakLabels` object, containing the weak labels and records."""
        return self._weak_labels

    def fit(self, include_annotated_records: bool = False, *args, **kwargs):
        """Fits the label model.

        Args:
            include_annotated_records: Whether to include annotated records in the fitting.
        """
        raise NotImplementedError

    def score(self, *args, **kwargs) -> Dict:
        """Evaluates the label model."""
        raise NotImplementedError

    def predict(
        self,
        include_annotated_records: bool = False,
        prediction_agent: str = "LabelModel",
        **kwargs,
    ) -> DatasetForTextClassification:
        """Applies the label model.

        Args:
            include_annotated_records: Whether to include annotated records.
            prediction_agent: String used for the ``prediction_agent`` in the returned records.
            **kwargs: Specific to the label model implementations

        Returns:
            A dataset of records that include the predictions of the label model.
        """
        raise NotImplementedError


class MajorityVoter(LabelModel):
    """A basic label model that computes the majority vote across all rules.

    For single-label classification, it will predict the label with the most votes.
    For multi-label classification, it will predict all labels that got at least one vote by the rules.

    Args:
        weak_labels: The weak labels object.
    """

    def __init__(self, weak_labels: Union[WeakLabels, WeakMultiLabels]):
        super().__init__(weak_labels=weak_labels)

    def fit(self, *args, **kwargs):
        """Raises a NotImplementedError.

        No need to call fit on the ``MajorityVoter``!
        """
        raise NotImplementedError("No need to call fit on the 'MajorityVoter'!")

    def predict(
        self,
        include_annotated_records: bool = False,
        include_abstentions: bool = False,
        prediction_agent: str = "MajorityVoter",
        tie_break_policy: Union[TieBreakPolicy, str] = "abstain",
    ) -> DatasetForTextClassification:
        """Applies the label model.

        Args:
            include_annotated_records: Whether to include annotated records.
            include_abstentions: Whether to include records in the output, for which the label model abstained.
            prediction_agent: String used for the ``prediction_agent`` in the returned records.
            tie_break_policy: Policy to break ties (IGNORED FOR MULTI-LABEL!). You can choose among two policies:

                - `abstain`: Do not provide any prediction
                - `random`: randomly choose among tied option using deterministic hash

                The last policy can introduce quite a bit of noise, especially when the tie is among many labels,
                as is the case when all the labeling functions (rules) abstained.

        Returns:
            A dataset of records that include the predictions of the label model.
        """
        wl_matrix = self._weak_labels.matrix(has_annotation=None if include_annotated_records else False)
        records = self._weak_labels.records(has_annotation=None if include_annotated_records else False)

        assert records, ValueError(
            "No records are being passed. Use `include_annotated_records` to include"
            " also include annotated records or us `rg.log` to add records."
        )

        if isinstance(self._weak_labels, WeakMultiLabels):
            records = self._make_multi_label_records(
                probabilities=self._compute_multi_label_probs(wl_matrix),
                records=records,
                include_abstentions=include_abstentions,
                prediction_agent=prediction_agent,
            )
        else:
            if isinstance(tie_break_policy, str):
                tie_break_policy = TieBreakPolicy(tie_break_policy)

            records = self._make_single_label_records(
                probabilities=self._compute_single_label_probs(wl_matrix),
                records=records,
                include_abstentions=include_abstentions,
                prediction_agent=prediction_agent,
                tie_break_policy=tie_break_policy,
            )

        return DatasetForTextClassification(records)

    def _compute_single_label_probs(self, wl_matrix: np.ndarray) -> np.ndarray:
        """Helper methods that computes the probabilities.

        Args:
            wl_matrix: The weak label matrix.

        Returns:
            A matrix of "probabilities" with nr or records x nr of labels.
            The label order matches the one from `self.weak_labels.labels`.
        """
        counts = np.column_stack(
            [
                np.count_nonzero(wl_matrix == self._weak_labels.label2int[label], axis=1)
                for label in self._weak_labels.labels
            ]
        )
        with np.errstate(invalid="ignore"):
            probabilities = counts / counts.sum(axis=1).reshape(len(counts), -1)

        # we treat abstentions as ties among all labels (see snorkel)
        probabilities[np.isnan(probabilities)] = 1.0 / len(self._weak_labels.labels)

        return probabilities

    def _make_single_label_records(
        self,
        probabilities: np.ndarray,
        records: List[TextClassificationRecord],
        include_abstentions: bool,
        prediction_agent: str,
        tie_break_policy: TieBreakPolicy,
    ) -> List[TextClassificationRecord]:
        """Helper method to create records given predicted probabilities.

        Args:
            probabilities: The predicted probabilities.
            records: The records associated with the probabilities.
            include_abstentions: Whether to include records in the output, for which the label model abstained.
            prediction_agent: String used for the ``prediction_agent`` in the returned records.
            tie_break_policy: Policy to break ties. You can choose among two policies:

                - `abstain`: Do not provide any prediction
                - `random`: randomly choose among tied option using deterministic hash

                The last policy can introduce quite a bit of noise, especially when the tie is among many labels,
                as is the case when all the labeling functions (rules) abstained.

        Returns:
            A list of records that include the predictions of the label model.
        """
        records_with_prediction = []
        for i, prob, rec in zip(range(len(records)), probabilities, records):
            # Check if model abstains, that is if the highest probability is assigned to more than one label
            # 1.e-8 is taken from the abs tolerance of np.isclose
            equal_prob_idx = np.nonzero(np.abs(prob.max() - prob) < 1.0e-8)[0]
            tie = False
            if len(equal_prob_idx) > 1:
                tie = True

            # maybe skip record
            if not include_abstentions and (tie and tie_break_policy is TieBreakPolicy.ABSTAIN):
                continue

            if not tie:
                pred_for_rec = [(self._weak_labels.labels[idx], prob[idx]) for idx in np.argsort(prob)[::-1]]
            # resolve ties following the tie break policy
            elif tie_break_policy is TieBreakPolicy.ABSTAIN:
                pred_for_rec = None
            elif tie_break_policy is TieBreakPolicy.RANDOM:
                random_idx = int(hashlib.sha1(f"{i}".encode()).hexdigest(), 16) % len(equal_prob_idx)
                for idx in equal_prob_idx:
                    if idx == random_idx:
                        prob[idx] += self._PROBABILITY_INCREASE_ON_TIE_BREAK
                    else:
                        prob[idx] -= self._PROBABILITY_INCREASE_ON_TIE_BREAK / (len(equal_prob_idx) - 1)
                pred_for_rec = [(self._weak_labels.labels[idx], prob[idx]) for idx in np.argsort(prob)[::-1]]
            else:
                raise NotImplementedError(
                    f"The tie break policy '{tie_break_policy.value}' is not"
                    f" implemented for {self.__class__.__name__}!"
                )

            records_with_prediction.append(rec.copy(deep=True))
            records_with_prediction[-1].prediction = pred_for_rec
            records_with_prediction[-1].prediction_agent = prediction_agent

        return records_with_prediction

    def _compute_multi_label_probs(self, wl_matrix: np.ndarray) -> np.ndarray:
        """Helper methods that computes the probabilities.

        Args:
            wl_matrix: The weak label matrix.

        Returns:
            A matrix of "probabilities" with nr or records x nr of labels.
            The label order matches the one from `self.weak_labels.labels`.
        """
        # turn abstentions (-1) into 0
        counts = np.where(wl_matrix == -1, 0, wl_matrix).sum(axis=1)
        # binary probability, predict all labels with at least one vote
        probabilities = np.where(counts > 0, 1, 0).astype(np.float16)

        all_rules_abstained = wl_matrix.sum(axis=1).sum(axis=1) == (
            -1 * self._weak_labels.cardinality * len(self._weak_labels.rules)
        )
        probabilities[all_rules_abstained] = [np.nan] * len(self._weak_labels.labels)

        # more "nuanced probability", not sure if useful though
        # with np.errstate(invalid="ignore"):
        #     probabilities = counts / counts.sum(axis=1).reshape(len(counts), -1)

        return probabilities

    def _make_multi_label_records(
        self,
        probabilities: np.ndarray,
        records: List[TextClassificationRecord],
        include_abstentions: bool,
        prediction_agent: str,
    ) -> List[TextClassificationRecord]:
        """Helper method to create records given predicted probabilities.

        Args:
            probabilities: The predicted probabilities.
            records: The records associated with the probabilities.
            include_abstentions: Whether to include records in the output, for which the label model abstained.
            prediction_agent: String used for the ``prediction_agent`` in the returned records.

        Returns:
            A list of records that include the predictions of the label model.
        """
        records_with_prediction = []
        for prob, rec in zip(probabilities, records):
            all_abstained = np.isnan(prob).all()
            # maybe skip record
            if not include_abstentions and all_abstained:
                continue

            pred_for_rec = None
            if not all_abstained:
                pred_for_rec = [(self._weak_labels.labels[i], prob[i]) for i in np.argsort(prob)[::-1]]

            records_with_prediction.append(rec.copy(deep=True))
            records_with_prediction[-1].prediction = pred_for_rec
            records_with_prediction[-1].prediction_agent = prediction_agent

        return records_with_prediction

    @requires_version("scikit-learn")
    def score(
        self,
        tie_break_policy: Union[TieBreakPolicy, str] = "abstain",
        output_str: bool = False,
    ) -> Union[Dict[str, float], str]:
        """Returns some scores/metrics of the label model with respect to the annotated records.

        The metrics are:

        - accuracy
        - micro/macro averages for precision, recall and f1
        - precision, recall, f1 and support for each label

        For more details about the metrics, check out the
        `sklearn docs <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html#sklearn-metrics-precision-recall-fscore-support>`__.

        .. note:: Metrics are only calculated over non-abstained predictions!

        Args:
            tie_break_policy: Policy to break ties (IGNORED FOR MULTI-LABEL). You can choose among two policies:

                - `abstain`: Do not provide any prediction
                - `random`: randomly choose among tied option using deterministic hash

                The last policy can introduce quite a bit of noise, especially when the tie is among many labels,
                as is the case when all the labeling functions (rules) abstained.
            output_str: If True, return output as nicely formatted string.

        Returns:
            The scores/metrics in a dictionary or as a nicely formatted str.

        Raises:
            MissingAnnotationError: If the ``weak_labels`` do not contain annotated records.
        """
        from sklearn.metrics import classification_report

        wl_matrix = self._weak_labels.matrix(has_annotation=True)

        if isinstance(self._weak_labels, WeakMultiLabels):
            probabilities = self._compute_multi_label_probs(wl_matrix)

            annotation, prediction = self._score_multi_label(probabilities)
            target_names = self._weak_labels.labels
        else:
            if isinstance(tie_break_policy, str):
                tie_break_policy = TieBreakPolicy(tie_break_policy)

            probabilities = self._compute_single_label_probs(wl_matrix)

            annotation, prediction = self._score_single_label(probabilities, tie_break_policy)
            target_names = self._weak_labels.labels[: annotation.max() + 1]

        return classification_report(
            annotation,
            prediction,
            target_names=target_names,
            output_dict=not output_str,
        )

    def _score_single_label(
        self, probabilities: np.ndarray, tie_break_policy: TieBreakPolicy
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Helper method to compute scores for single-label classifications.

        Args:
            probabilities: The probabilities.
            tie_break_policy: Policy to break ties. You can choose among two policies:

                - `abstain`: Exclude from scores.
                - `random`: randomly choose among tied option using deterministic hash.

                The last policy can introduce quite a bit of noise, especially when the tie is among many labels,
                as is the case when all the labeling functions (rules) abstained.

        Returns:
            A tuple of the annotation and prediction array.
        """
        # 1.e-8 is taken from the abs tolerance of np.isclose
        is_max = np.abs(probabilities.max(axis=1, keepdims=True) - probabilities) < 1.0e-8
        is_tie = is_max.sum(axis=1) > 1

        prediction = np.argmax(is_max, axis=1)
        # we need to transform the indexes!
        annotation = np.array(
            [self._weak_labels.labels.index(self._weak_labels.int2label[i]) for i in self._weak_labels.annotation()],
            dtype=np.short,
        )

        if not is_tie.any():
            pass
        # resolve ties
        elif tie_break_policy is TieBreakPolicy.ABSTAIN:
            prediction, annotation = prediction[~is_tie], annotation[~is_tie]
        elif tie_break_policy is TieBreakPolicy.RANDOM:
            for i in np.nonzero(is_tie)[0]:
                equal_prob_idx = np.nonzero(is_max[i])[0]
                random_idx = int(hashlib.sha1(f"{i}".encode()).hexdigest(), 16) % len(equal_prob_idx)
                prediction[i] = equal_prob_idx[random_idx]
        else:
            raise NotImplementedError(
                f"The tie break policy '{tie_break_policy.value}' is not implemented" " for MajorityVoter!"
            )

        return annotation, prediction

    def _score_multi_label(self, probabilities: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Helper method to compute scores for multi-label classifications.

        Args:
            probabilities: The probabilities.

        Returns:
            A tuple of the annotation and prediction array.
        """
        prediction = np.where(probabilities > 0.5, 1, 0)

        is_abstain = np.isnan(probabilities).all(axis=1)

        prediction, annotation = (
            prediction[~is_abstain],
            self._weak_labels.annotation()[~is_abstain],
        )

        return annotation, prediction


@requires_version("snorkel")
class Snorkel(LabelModel):
    """The label model by `Snorkel <https://github.com/snorkel-team/snorkel/>`__.

    .. note:: It is not suited for multi-label classification and does not support it!

    Args:
        weak_labels: A `WeakLabels` object containing the weak labels and records.
        verbose: Whether to show print statements
        device: What device to place the model on ('cpu' or 'cuda:0', for example).
            Passed on to the `torch.Tensor.to()` calls.

    Examples:
        >>> from argilla.labeling.text_classification import WeakLabels
        >>> weak_labels = WeakLabels(dataset="my_dataset")
        >>> label_model = Snorkel(weak_labels)
        >>> label_model.fit()
        >>> records = label_model.predict()
    """

    def __init__(self, weak_labels: WeakLabels, verbose: bool = True, device: str = "cpu"):
        from snorkel.labeling.model import LabelModel as SnorkelLabelModel

        super().__init__(weak_labels)

        # Check if we need to remap the weak labels to int mapping
        # Snorkel expects the abstain id to be -1 and the rest of the labels to be sequential
        if self._weak_labels.label2int[None] != -1 or sorted(self._weak_labels.int2label) != list(
            range(-1, self._weak_labels.cardinality)
        ):
            self._need_remap = True
            self._weaklabelsInt2snorkelInt = {
                self._weak_labels.label2int[label]: i for i, label in enumerate([None] + self._weak_labels.labels, -1)
            }
        else:
            self._need_remap = False
            self._weaklabelsInt2snorkelInt = {i: i for i in range(-1, self._weak_labels.cardinality)}

        self._snorkelInt2weaklabelsInt = {val: key for key, val in self._weaklabelsInt2snorkelInt.items()}

        # instantiate Snorkel's label model
        self._model = SnorkelLabelModel(
            cardinality=self._weak_labels.cardinality,
            verbose=verbose,
            device=device,
        )

    def fit(self, include_annotated_records: bool = False, **kwargs):
        """Fits the label model.

        Args:
            include_annotated_records: Whether to include annotated records in the fitting.
            **kwargs: Additional kwargs are passed on to Snorkel's
                `fit method <https://snorkel.readthedocs.io/en/latest/packages/_autosummary/labeling/snorkel.labeling.model.label_model.LabelModel.html#snorkel.labeling.model.label_model.LabelModel.fit>`__.
                They must not contain ``L_train``, the label matrix is provided automatically.
        """
        if "L_train" in kwargs:
            raise ValueError("Your kwargs must not contain 'L_train', it is provided automatically.")

        l_train = self._weak_labels.matrix(has_annotation=None if include_annotated_records else False)
        if self._need_remap:
            l_train = self._copy_and_remap(l_train)

        self._model.fit(L_train=l_train, **kwargs)

    def _copy_and_remap(self, matrix_or_array: np.ndarray):
        """Helper function to copy and remap the weak label matrix or annotation array to be compatible with snorkel.

        Snorkel expects the abstain id to be -1 and the rest of the labels to be sequential.

        Args:
            matrix_or_array: The original weak label matrix or annotation array

        Returns:
            A copy of the weak label matrix, remapped to match snorkel's requirements.
        """
        matrix_or_array = matrix_or_array.copy()

        # save masks for swapping
        label_masks = {}

        # compute masks
        for idx in self._weaklabelsInt2snorkelInt:
            label_masks[idx] = matrix_or_array == idx

        # swap integers
        for idx in self._weaklabelsInt2snorkelInt:
            matrix_or_array[label_masks[idx]] = self._weaklabelsInt2snorkelInt[idx]

        return matrix_or_array

    def predict(
        self,
        include_annotated_records: bool = False,
        include_abstentions: bool = False,
        prediction_agent: str = "Snorkel",
        tie_break_policy: Union[TieBreakPolicy, str] = "abstain",
    ) -> DatasetForTextClassification:
        """Returns a list of records that contain the predictions of the label model

        Args:
            include_annotated_records: Whether to include annotated records.
            include_abstentions: Whether to include records in the output, for which the label model abstained.
            prediction_agent: String used for the ``prediction_agent`` in the returned records.
            tie_break_policy: Policy to break ties. You can choose among three policies:

                - `abstain`: Do not provide any prediction
                - `random`: randomly choose among tied option using deterministic hash
                - `true-random`: randomly choose among the tied options. NOTE: repeated runs may have slightly different results due to differences in broken ties

                The last two policies can introduce quite a bit of noise, especially when the tie is among many labels,
                as is the case when all the labeling functions (rules) abstained.

        Returns:
            A dataset of records that include the predictions of the label model.
        """
        if isinstance(tie_break_policy, str):
            tie_break_policy = TieBreakPolicy(tie_break_policy)

        l_pred = self._weak_labels.matrix(has_annotation=None if include_annotated_records else False)
        if self._need_remap:
            l_pred = self._copy_and_remap(l_pred)

        # get predictions and probabilities
        predictions, probabilities = self._model.predict(
            L=l_pred,
            return_probs=True,
            tie_break_policy=tie_break_policy.value,
        )

        # add predictions to records
        records_with_prediction = []
        for rec, pred, prob in zip(
            self._weak_labels.records(has_annotation=None if include_annotated_records else False),
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
                # 1.e-8 is taken from the abs tolerance of np.isclose
                equal_prob_idx = np.nonzero(np.abs(prob.max() - prob) < 1.0e-8)[0]
                if len(equal_prob_idx) > 1:
                    for idx in equal_prob_idx:
                        if idx == pred:
                            prob[idx] += self._PROBABILITY_INCREASE_ON_TIE_BREAK
                        else:
                            prob[idx] -= self._PROBABILITY_INCREASE_ON_TIE_BREAK / (len(equal_prob_idx) - 1)

                pred_for_rec = [
                    (
                        self._weak_labels.int2label[self._snorkelInt2weaklabelsInt[snorkel_idx]],
                        prob[snorkel_idx],
                    )
                    for snorkel_idx in np.argsort(prob)[::-1]
                ]

            records_with_prediction[-1].prediction = pred_for_rec
            records_with_prediction[-1].prediction_agent = prediction_agent

        return DatasetForTextClassification(records_with_prediction)

    @requires_version("scikit-learn")
    def score(
        self,
        tie_break_policy: Union[TieBreakPolicy, str] = "abstain",
        output_str: bool = False,
    ) -> Union[Dict[str, float], str]:
        """Returns some scores/metrics of the label model with respect to the annotated records.

        The metrics are:

        - accuracy
        - micro/macro averages for precision, recall and f1
        - precision, recall, f1 and support for each label

        For more details about the metrics, check out the
        `sklearn docs <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html#sklearn-metrics-precision-recall-fscore-support>`__.

        .. note:: Metrics are only calculated over non-abstained predictions!

        Args:
            tie_break_policy: Policy to break ties. You can choose among three policies:

                - `abstain`: Do not provide any prediction
                - `random`: randomly choose among tied option using deterministic hash
                - `true-random`: randomly choose among the tied options. NOTE: repeated runs may have slightly different results due to differences in broken ties

                The last two policies can introduce quite a bit of noise, especially when the tie is among many labels,
                as is the case when all the labeling functions (rules) abstained.
            output_str: If True, return output as nicely formatted string.

        Returns:
            The scores/metrics in a dictionary or as a nicely formatted str.

        Raises:
            MissingAnnotationError: If the ``weak_labels`` do not contain annotated records.
        """
        from sklearn.metrics import classification_report

        if isinstance(tie_break_policy, str):
            tie_break_policy = TieBreakPolicy(tie_break_policy)

        if self._weak_labels.annotation().size == 0:
            raise MissingAnnotationError(
                "You need annotated records to compute scores/metrics for your label" " model."
            )

        l_pred = self._weak_labels.matrix(has_annotation=True)
        if self._need_remap:
            l_pred = self._copy_and_remap(l_pred)

        # get predictions and probabilities
        predictions, probabilities = self._model.predict(
            L=l_pred,
            return_probs=True,
            tie_break_policy=tie_break_policy.value,
        )

        # metrics are only calculated for non-abstained data points
        idx = predictions != -1

        annotation = self._weak_labels.annotation()[idx]
        if self._need_remap:
            annotation = self._copy_and_remap(annotation)

        return classification_report(
            annotation,
            predictions[idx],
            target_names=self._weak_labels.labels[: annotation.max() + 1],
            output_dict=not output_str,
        )


@requires_version("flyingsquid")
@requires_version("pgmpy")
class FlyingSquid(LabelModel):
    """The label model by `FlyingSquid <https://github.com/HazyResearch/flyingsquid>`__.

    .. note:: It is not suited for multi-label classification and does not support it!

    Args:
        weak_labels: A `WeakLabels` object containing the weak labels and records.
        **kwargs: Passed on to the init of the FlyingSquid's
            `LabelModel <https://github.com/HazyResearch/flyingsquid/blob/master/flyingsquid/label_model.py#L18>`__.

    Examples:
        >>> from argilla.labeling.text_classification import WeakLabels
        >>> weak_labels = WeakLabels(dataset="my_dataset")
        >>> label_model = FlyingSquid(weak_labels)
        >>> label_model.fit()
        >>> records = label_model.predict()
    """

    def __init__(self, weak_labels: WeakLabels, **kwargs):
        from flyingsquid.label_model import LabelModel as FlyingSquidLabelModel

        self._FlyingSquidLabelModel = FlyingSquidLabelModel

        super().__init__(weak_labels)

        if len(self._weak_labels.rules) < 3:
            raise TooFewRulesError("The FlyingSquid label model needs at least three (independent) rules!")

        if "m" in kwargs:
            raise ValueError("Your kwargs must not contain 'm', it is provided automatically.")

        self._init_kwargs = kwargs
        self._models: List[FlyingSquidLabelModel] = []

    def fit(self, include_annotated_records: bool = False, **kwargs):
        """Fits the label model.

        Args:
            include_annotated_records: Whether to include annotated records in the fitting.
            **kwargs: Passed on to the FlyingSquid's
                `LabelModel.fit() <https://github.com/HazyResearch/flyingsquid/blob/master/flyingsquid/label_model.py#L320>`__
                method.
        """
        wl_matrix = self._weak_labels.matrix(has_annotation=None if include_annotated_records else False)

        models = []
        # create a label model for each label (except for binary classification)
        # much of the implementation is taken from wrench:
        # https://github.com/JieyuZ2/wrench/blob/main/wrench/labelmodel/flyingsquid.py
        # If binary, we only need one model
        for i in range(1 if self._weak_labels.cardinality == 2 else self._weak_labels.cardinality):
            model = self._FlyingSquidLabelModel(m=len(self._weak_labels.rules), **self._init_kwargs)
            wl_matrix_i = self._copy_and_transform_wl_matrix(wl_matrix, i)
            model.fit(L_train=wl_matrix_i, **kwargs)
            models.append(model)

        self._models = models

    def _copy_and_transform_wl_matrix(self, weak_label_matrix: np.ndarray, i: int):
        """Helper function to copy and transform the weak label matrix with respect to a target label.

         FlyingSquid expects the matrix to contain -1, 0 and 1, which are mapped the following way:

        - target label: -1
        - abstain label: 0
        - other label: 1

        Args:
            weak_label_matrix: The original weak label matrix
            i: Index of the target label

        Returns:
            A copy of the weak label matrix, transformed with respect to the target label.
        """
        wl_matrix_i = weak_label_matrix.copy()

        target_mask = wl_matrix_i == self._weak_labels.label2int[self._weak_labels.labels[i]]
        abstain_mask = wl_matrix_i == self._weak_labels.label2int[None]
        other_mask = (~target_mask) & (~abstain_mask)

        wl_matrix_i[target_mask] = -1
        wl_matrix_i[abstain_mask] = 0
        wl_matrix_i[other_mask] = 1

        return wl_matrix_i

    def predict(
        self,
        include_annotated_records: bool = False,
        include_abstentions: bool = False,
        prediction_agent: str = "FlyingSquid",
        verbose: bool = True,
        tie_break_policy: Union[TieBreakPolicy, str] = "abstain",
    ) -> DatasetForTextClassification:
        """Applies the label model.

        Args:
            include_annotated_records: Whether to include annotated records.
            include_abstentions: Whether to include records in the output, for which the label model abstained.
            prediction_agent: String used for the ``prediction_agent`` in the returned records.
            verbose: If True, print out messages of the progress to stderr.
            tie_break_policy: Policy to break ties. You can choose among two policies:

                - `abstain`: Do not provide any prediction
                - `random`: randomly choose among tied option using deterministic hash

                The last policy can introduce quite a bit of noise, especially when the tie is among many labels,
                as is the case when all the labeling functions (rules) abstained.

        Returns:
            A dataset of records that include the predictions of the label model.

        Raises:
            NotFittedError: If the label model was still not fitted.
        """
        if isinstance(tie_break_policy, str):
            tie_break_policy = TieBreakPolicy(tie_break_policy)

        wl_matrix = self._weak_labels.matrix(has_annotation=None if include_annotated_records else False)
        probabilities = self._predict(wl_matrix, verbose)

        # add predictions to records
        records_with_prediction = []
        for i, prob, rec in zip(
            range(len(probabilities)),
            probabilities,
            self._weak_labels.records(has_annotation=None if include_annotated_records else False),
        ):
            # Check if model abstains, that is if the highest probability is assigned to more than one label
            # 1.e-8 is taken from the abs tolerance of np.isclose
            equal_prob_idx = np.nonzero(np.abs(prob.max() - prob) < 1.0e-8)[0]
            tie = False
            if len(equal_prob_idx) > 1:
                tie = True

            # maybe skip record
            if not include_abstentions and (tie and tie_break_policy is TieBreakPolicy.ABSTAIN):
                continue

            if not tie:
                pred_for_rec = [(self._weak_labels.labels[i], prob[i]) for i in np.argsort(prob)[::-1]]
            # resolve ties following the tie break policy
            elif tie_break_policy is TieBreakPolicy.ABSTAIN:
                pred_for_rec = None
            elif tie_break_policy is TieBreakPolicy.RANDOM:
                random_idx = int(hashlib.sha1(f"{i}".encode()).hexdigest(), 16) % len(equal_prob_idx)
                for idx in equal_prob_idx:
                    if idx == random_idx:
                        prob[idx] += self._PROBABILITY_INCREASE_ON_TIE_BREAK
                    else:
                        prob[idx] -= self._PROBABILITY_INCREASE_ON_TIE_BREAK / (len(equal_prob_idx) - 1)
                pred_for_rec = [(self._weak_labels.labels[i], prob[i]) for i in np.argsort(prob)[::-1]]
            else:
                raise NotImplementedError(
                    f"The tie break policy '{tie_break_policy.value}' is not" " implemented for FlyingSquid!"
                )

            records_with_prediction.append(rec.copy(deep=True))
            records_with_prediction[-1].prediction = pred_for_rec
            records_with_prediction[-1].prediction_agent = prediction_agent

        return DatasetForTextClassification(records_with_prediction)

    def _predict(self, weak_label_matrix: np.ndarray, verbose: bool) -> np.ndarray:
        """Helper function that calls the ``predict_proba`` method of FlyingSquid's label model.

        Much of the implementation is taken from wrench:
        https://github.com/JieyuZ2/wrench/blob/main/wrench/labelmodel/flyingsquid.py

        Args:
            weak_label_matrix: The weak label matrix.
            verbose: If True, print out messages of the progress to stderr.

        Returns:
            A matrix containing the probability for each label and record.

        Raises:
            NotFittedError: If the label model was still not fitted.
        """
        if not self._models:
            raise NotFittedError("This FlyingSquid instance is not fitted yet. Call `fit` before using" " this model.")
        # create predictions for each label
        if self._weak_labels.cardinality > 2:
            probas = np.zeros((len(weak_label_matrix), self._weak_labels.cardinality))
            for i in range(self._weak_labels.cardinality):
                wl_matrix_i = self._copy_and_transform_wl_matrix(weak_label_matrix, i)
                probas[:, i] = self._models[i].predict_proba(L_matrix=wl_matrix_i, verbose=verbose)[:, 0]
            probas = np.nan_to_num(probas, nan=-np.inf)  # handle NaN
            probas = np.exp(probas) / np.sum(np.exp(probas), axis=1, keepdims=True)
        # if binary, we only have one model
        else:
            wl_matrix_i = self._copy_and_transform_wl_matrix(weak_label_matrix, 0)
            probas = self._models[0].predict_proba(L_matrix=wl_matrix_i, verbose=verbose)

        return probas

    @requires_version("scikit-learn")
    def score(
        self,
        tie_break_policy: Union[TieBreakPolicy, str] = "abstain",
        verbose: bool = False,
        output_str: bool = False,
    ) -> Union[Dict[str, float], str]:
        """Returns some scores/metrics of the label model with respect to the annotated records.

        The metrics are:

        - accuracy
        - micro/macro averages for precision, recall and f1
        - precision, recall, f1 and support for each label

        For more details about the metrics, check out the
        `sklearn docs <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html#sklearn-metrics-precision-recall-fscore-support>`__.

        .. note:: Metrics are only calculated over non-abstained predictions!

        Args:
            tie_break_policy: Policy to break ties. You can choose among two policies:

                - `abstain`: Do not provide any prediction
                - `random`: randomly choose among tied option using deterministic hash

                The last policy can introduce quite a bit of noise, especially when the tie is among many labels,
                as is the case when all the labeling functions (rules) abstained.
            verbose: If True, print out messages of the progress to stderr.
            output_str: If True, return output as nicely formatted string.

        Returns:
            The scores/metrics in a dictionary or as a nicely formatted str.

        Raises:
            NotFittedError: If the label model was still not fitted.
            MissingAnnotationError: If the ``weak_labels`` do not contain annotated records.
        """
        from sklearn.metrics import classification_report

        if isinstance(tie_break_policy, str):
            tie_break_policy = TieBreakPolicy(tie_break_policy)

        wl_matrix = self._weak_labels.matrix(has_annotation=True)
        probabilities = self._predict(wl_matrix, verbose)

        # 1.e-8 is taken from the abs tolerance of np.isclose
        is_max = np.abs(probabilities.max(axis=1, keepdims=True) - probabilities) < 1.0e-8
        is_tie = is_max.sum(axis=1) > 1

        prediction = np.argmax(is_max, axis=1)
        # we need to transform the indexes!
        annotation = np.array(
            [self._weak_labels.labels.index(self._weak_labels.int2label[i]) for i in self._weak_labels.annotation()],
            dtype=np.short,
        )

        if not is_tie.any():
            pass
        # resolve ties
        elif tie_break_policy is TieBreakPolicy.ABSTAIN:
            prediction, annotation = prediction[~is_tie], annotation[~is_tie]
        elif tie_break_policy is TieBreakPolicy.RANDOM:
            for i in np.nonzero(is_tie)[0]:
                equal_prob_idx = np.nonzero(is_max[i])[0]
                random_idx = int(hashlib.sha1(f"{i}".encode()).hexdigest(), 16) % len(equal_prob_idx)
                prediction[i] = equal_prob_idx[random_idx]
        else:
            raise NotImplementedError(
                f"The tie break policy '{tie_break_policy.value}' is not implemented" " for FlyingSquid!"
            )

        return classification_report(
            annotation,
            prediction,
            target_names=self._weak_labels.labels[: annotation.max() + 1],
            output_dict=not output_str,
        )


class LabelModelError(Exception):
    pass


class MissingAnnotationError(LabelModelError):
    pass


class TooFewRulesError(LabelModelError):
    pass


class NotFittedError(LabelModelError):
    pass
