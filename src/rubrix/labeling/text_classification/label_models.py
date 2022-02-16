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
from typing import Dict, List, Optional, Union

import numpy as np

from rubrix import TextClassificationRecord
from rubrix.labeling.text_classification.weak_labels import WeakLabels

_LOGGER = logging.getLogger(__name__)


class TieBreakPolicy(Enum):
    """A tie break policy"""

    ABSTAIN = "abstain"
    RANDOM = "random"
    TRUE_RANDOM = "true-random"

    @classmethod
    def _missing_(cls, value):
        raise ValueError(
            f"{value} is not a valid {cls.__name__}, please select one of {list(cls._value2member_map_.keys())}"
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
        prediction_agent: str = "LabelModel",
        **kwargs,
    ) -> List[TextClassificationRecord]:
        """Applies the label model.

        Args:
            include_annotated_records: Whether or not to include annotated records.
            include_abstentions: Whether or not to include records in the output, for which the label model abstained.
            prediction_agent: String used for the ``prediction_agent`` in the returned records.

        Returns:
            A list of records that include the predictions of the label model.
        """
        raise NotImplementedError


class Snorkel(LabelModel):
    """The label model by `Snorkel <https://github.com/snorkel-team/snorkel/>`__.

    Args:
        weak_labels: A `WeakLabels` object containing the weak labels and records.
        verbose: Whether to show print statements
        device: What device to place the model on ('cpu' or 'cuda:0', for example).
            Passed on to the `torch.Tensor.to()` calls.

    Examples:
        >>> from rubrix.labeling.text_classification import WeakLabels
        >>> weak_labels = WeakLabels(dataset="my_dataset")
        >>> label_model = Snorkel(weak_labels)
        >>> label_model.fit()
        >>> records = label_model.predict()
    """

    def __init__(
        self, weak_labels: WeakLabels, verbose: bool = True, device: str = "cpu"
    ):
        try:
            import snorkel
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "'snorkel' must be installed to use the `Snorkel` label model! "
                "You can install 'snorkel' with the command: `pip install snorkel`"
            )
        else:
            from snorkel.labeling.model import LabelModel as SnorkelLabelModel

        super().__init__(weak_labels)

        # Check if we need to remap the weak labels to int mapping
        # Snorkel expects the abstain id to be -1 and the rest of the labels to be sequential
        if self._weak_labels.label2int[None] != -1 or sorted(
            self._weak_labels.int2label
        ) != list(range(-1, len(self._weak_labels.label2int) - 1)):
            self._need_remap = True

            labels = [None] + [
                label for label in self._weak_labels.label2int if label is not None
            ]

            self._weaklabelsInt2snorkelInt = {
                self._weak_labels.label2int[label]: i
                for i, label in enumerate(labels, -1)
            }
        else:
            self._need_remap = False
            self._weaklabelsInt2snorkelInt = {
                i: i for i in range(-1, len(self._weak_labels.label2int) - 1)
            }

        self._snorkelInt2weaklabelsInt = {
            val: key for key, val in self._weaklabelsInt2snorkelInt.items()
        }

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
                `fit method <https://snorkel.readthedocs.io/en/latest/packages/_autosummary/labeling/snorkel.labeling.model.label_model.LabelModel.html#snorkel.labeling.model.label_model.LabelModel.fit>`__.
                They must not contain ``L_train``, the label matrix is provided automatically.
        """
        if "L_train" in kwargs:
            raise ValueError(
                "Your kwargs must not contain 'L_train', it is provided automatically."
            )

        l_train = self._weak_labels.matrix(
            has_annotation=None if include_annotated_records else False
        )
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
    ) -> List[TextClassificationRecord]:
        """Returns a list of records that contain the predictions of the label model

        Args:
            include_annotated_records: Whether or not to include annotated records.
            include_abstentions: Whether or not to include records in the output, for which the label model abstained.
            prediction_agent: String used for the ``prediction_agent`` in the returned records.
            tie_break_policy: Policy to break ties. You can choose among three policies:

                - `abstain`: Do not provide any prediction
                - `random`: randomly choose among tied option using deterministic hash
                - `true-random`: randomly choose among the tied options. NOTE: repeated runs may have slightly different results due to differences in broken ties

                The last two policies can introduce quite a bit of noise, especially when the tie is among many labels,
                as is the case when all of the labeling functions abstained.

        Returns:
            A list of records that include the predictions of the label model.
        """
        if isinstance(tie_break_policy, str):
            tie_break_policy = TieBreakPolicy(tie_break_policy)

        l_pred = self._weak_labels.matrix(
            has_annotation=None if include_annotated_records else False
        )
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
                    for idx in range(len(prob)):
                        if idx == pred:
                            prob[idx] += self._PROBABILITY_INCREASE_ON_TIE_BREAK
                        else:
                            prob[idx] -= self._PROBABILITY_INCREASE_ON_TIE_BREAK / (
                                len(prob) - 1
                            )

                pred_for_rec = [
                    (
                        self._weak_labels.int2label[
                            self._snorkelInt2weaklabelsInt[snorkel_idx]
                        ],
                        prob[snorkel_idx],
                    )
                    for snorkel_idx in np.argsort(prob)[::-1]
                ]

            records_with_prediction[-1].prediction = pred_for_rec
            records_with_prediction[-1].prediction_agent = prediction_agent

        return records_with_prediction

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

        Args:
            tie_break_policy: Policy to break ties. You can choose among three policies:

                - `abstain`: Do not provide any prediction
                - `random`: randomly choose among tied option using deterministic hash
                - `true-random`: randomly choose among the tied options. NOTE: repeated runs may have slightly different results due to differences in broken ties

                The last two policies can introduce quite a bit of noise, especially when the tie is among many labels,
                as is the case when all of the labeling functions abstained.
            output_str: If True, return output as nicely formatted string.

        Returns:
            The scores/metrics in a dictionary or as a nicely formatted str.

        .. note:: Metrics are only calculated over non-abstained predictions!

        Raises:
            MissingAnnotationError: If the ``weak_labels`` do not contain annotated records.
        """
        from sklearn.metrics import classification_report

        if isinstance(tie_break_policy, str):
            tie_break_policy = TieBreakPolicy(tie_break_policy)

        if self._weak_labels.annotation().size == 0:
            raise MissingAnnotationError(
                "You need annotated records to compute scores/metrics for your label model."
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
        if not idx.all():
            _LOGGER.warning(
                "Metrics are only calculated over non-abstained predictions!"
            )

        annotation = self._weak_labels.annotation()[idx]
        if self._need_remap:
            annotation = self._copy_and_remap(annotation)

        target_names = [
            self._weak_labels.int2label[i]
            for i in list(self._weaklabelsInt2snorkelInt.keys())[1:]
        ]

        return classification_report(
            annotation,
            predictions[idx],
            target_names=target_names[: annotation.max() + 1],
            output_dict=not output_str,
        )


class FlyingSquid(LabelModel):
    """The label model by `FlyingSquid <https://github.com/HazyResearch/flyingsquid>`__.

    Args:
        weak_labels: A `WeakLabels` object containing the weak labels and records.
        **kwargs: Passed on to the init of the FlyingSquid's
            `LabelModel <https://github.com/HazyResearch/flyingsquid/blob/master/flyingsquid/label_model.py#L18>`__.

    Examples:
        >>> from rubrix.labeling.text_classification import WeakLabels
        >>> weak_labels = WeakLabels(dataset="my_dataset")
        >>> label_model = FlyingSquid(weak_labels)
        >>> label_model.fit()
        >>> records = label_model.predict()
    """

    def __init__(self, weak_labels: WeakLabels, **kwargs):
        try:
            import flyingsquid
            import pgmpy
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "'flyingsquid' must be installed to use the `FlyingSquid` label model! "
                "You can install 'flyingsquid' with the command: `pip install pgmpy flyingsquid`"
            )
        else:
            from flyingsquid.label_model import LabelModel as FlyingSquidLabelModel

            self._FlyingSquidLabelModel = FlyingSquidLabelModel

        super().__init__(weak_labels)

        if len(self._weak_labels.rules) < 3:
            raise TooFewRulesError(
                "The FlyingSquid label model needs at least three (independent) rules!"
            )

        if "m" in kwargs:
            raise ValueError(
                "Your kwargs must not contain 'm', it is provided automatically."
            )

        self._init_kwargs = kwargs
        self._models: List[FlyingSquidLabelModel] = []
        self._labels = [
            label for label in self._weak_labels.label2int.keys() if label is not None
        ]

    def fit(self, include_annotated_records: bool = False, **kwargs):
        """Fits the label model.

        Args:
            include_annotated_records: Whether or not to include annotated records in the training.
            **kwargs: Passed on to the FlyingSquid's
                `LabelModel.fit() <https://github.com/HazyResearch/flyingsquid/blob/master/flyingsquid/label_model.py#L320>`__
                method.
        """
        wl_matrix = self._weak_labels.matrix(
            has_annotation=None if include_annotated_records else False
        )

        models = []
        # create a label model for each label (except for binary classification)
        # much of the implementation is taken from wrench:
        # https://github.com/JieyuZ2/wrench/blob/main/wrench/labelmodel/flyingsquid.py
        # If binary, we only need one model
        for i in range(1 if len(self._labels) == 2 else len(self._labels)):
            model = self._FlyingSquidLabelModel(
                m=len(self._weak_labels.rules), **self._init_kwargs
            )
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

        target_mask = wl_matrix_i == self._weak_labels.label2int[self._labels[i]]
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
        tie_break_policy: str = "abstain",
    ) -> List[TextClassificationRecord]:
        """Applies the label model.

        Args:
            include_annotated_records: Whether or not to include annotated records.
            include_abstentions: Whether or not to include records in the output, for which the label model abstained.
            prediction_agent: String used for the ``prediction_agent`` in the returned records.
            verbose: If True, print out messages of the progress to stderr.
            tie_break_policy: Policy to break ties. You can choose among two policies:

                - `abstain`: Do not provide any prediction
                - `random`: randomly choose among tied option using deterministic hash

                The last policy can introduce quite a bit of noise, especially when the tie is among many labels,
                as is the case when all of the labeling functions abstained.

        Returns:
            A list of records that include the predictions of the label model.

        Raises:
            NotFittedError: If the label model was still not fitted.
        """
        if isinstance(tie_break_policy, str):
            tie_break_policy = TieBreakPolicy(tie_break_policy)

        wl_matrix = self._weak_labels.matrix(
            has_annotation=None if include_annotated_records else False
        )
        probabilities = self._predict(wl_matrix, verbose)

        # add predictions to records
        records_with_prediction = []
        for i, prob, rec in zip(
            range(len(probabilities)),
            probabilities,
            self._weak_labels.records(
                has_annotation=None if include_annotated_records else False
            ),
        ):
            # Check if model abstains, that is if the highest probability is assigned to more than one label
            # 1.e-8 is taken from the abs tolerance of np.isclose
            equal_prob_idx = np.nonzero(np.abs(prob.max() - prob) < 1.0e-8)[0]
            tie = False
            if len(equal_prob_idx) > 1:
                tie = True

            # maybe skip record
            if not include_abstentions and (
                tie and tie_break_policy is TieBreakPolicy.ABSTAIN
            ):
                continue

            if not tie:
                pred_for_rec = [
                    (self._labels[i], prob[i]) for i in np.argsort(prob)[::-1]
                ]
            # resolve ties following the tie break policy
            elif tie_break_policy is TieBreakPolicy.ABSTAIN:
                pred_for_rec = None
            elif tie_break_policy is TieBreakPolicy.RANDOM:
                random_idx = int(hashlib.sha1(f"{i}".encode()).hexdigest(), 16) % len(
                    equal_prob_idx
                )
                for idx in range(len(prob)):
                    if idx == equal_prob_idx[random_idx]:
                        prob[idx] += self._PROBABILITY_INCREASE_ON_TIE_BREAK
                    else:
                        prob[idx] -= self._PROBABILITY_INCREASE_ON_TIE_BREAK / (
                            len(prob) - 1
                        )
                pred_for_rec = [
                    (self._labels[i], prob[i]) for i in np.argsort(prob)[::-1]
                ]
            else:
                raise NotImplementedError(
                    f"The tie break policy '{tie_break_policy.value}' is not implemented for FlyingSquid!"
                )

            records_with_prediction.append(rec.copy(deep=True))
            records_with_prediction[-1].prediction = pred_for_rec
            records_with_prediction[-1].prediction_agent = prediction_agent

        return records_with_prediction

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
            raise NotFittedError(
                "This FlyingSquid instance is not fitted yet. Call `fit` before using this model."
            )
        # create predictions for each label
        if len(self._labels) > 2:
            probas = np.zeros((len(weak_label_matrix), len(self._labels)))
            for i in range(len(self._labels)):
                wl_matrix_i = self._copy_and_transform_wl_matrix(weak_label_matrix, i)
                probas[:, i] = self._models[i].predict_proba(
                    L_matrix=wl_matrix_i, verbose=verbose
                )[:, 0]
            probas = np.nan_to_num(probas, nan=-np.inf)  # handle NaN
            probas = np.exp(probas) / np.sum(np.exp(probas), axis=1, keepdims=True)
        # if binary, we only have one model
        else:
            wl_matrix_i = self._copy_and_transform_wl_matrix(weak_label_matrix, 0)
            probas = self._models[0].predict_proba(
                L_matrix=wl_matrix_i, verbose=verbose
            )

        return probas

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

        Args:
            tie_break_policy: Policy to break ties. You can choose among two policies:

                - `abstain`: Do not provide any prediction
                - `random`: randomly choose among tied option using deterministic hash

                The last policy can introduce quite a bit of noise, especially when the tie is among many labels,
                as is the case when all of the labeling functions abstained.
            verbose: If True, print out messages of the progress to stderr.
            output_str: If True, return output as nicely formatted string.

        Returns:
            The scores/metrics in a dictionary or as a nicely formatted str.

        .. note:: Metrics are only calculated over non-abstained predictions!

        Raises:
            NotFittedError: If the label model was still not fitted.
            MissingAnnotationError: If the ``weak_labels`` do not contain annotated records.
        """
        try:
            import sklearn
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "'sklearn' must be installed to compute the metrics! "
                "You can install 'sklearn' with the command: `pip install scikit-learn`"
            )
        from sklearn.metrics import classification_report

        if isinstance(tie_break_policy, str):
            tie_break_policy = TieBreakPolicy(tie_break_policy)

        wl_matrix = self._weak_labels.matrix(has_annotation=True)
        probabilities = self._predict(wl_matrix, verbose)

        # 1.e-8 is taken from the abs tolerance of np.isclose
        is_max = (
            np.abs(probabilities.max(axis=1, keepdims=True) - probabilities) < 1.0e-8
        )
        is_tie = is_max.sum(axis=1) > 1

        prediction = np.argmax(is_max, axis=1)
        # we need to transform the indexes!
        annotation = np.array(
            [
                self._labels.index(self._weak_labels.int2label[i])
                for i in self._weak_labels.annotation()
            ],
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
                random_idx = int(hashlib.sha1(f"{i}".encode()).hexdigest(), 16) % len(
                    equal_prob_idx
                )
                prediction[i] = equal_prob_idx[random_idx]
        else:
            raise NotImplementedError(
                f"The tie break policy '{tie_break_policy.value}' is not implemented for FlyingSquid!"
            )

        return classification_report(
            annotation,
            prediction,
            target_names=self._labels[: annotation.max() + 1],
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
