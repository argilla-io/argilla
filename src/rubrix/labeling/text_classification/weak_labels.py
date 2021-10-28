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
from typing import Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from tqdm.auto import tqdm

from rubrix import load
from rubrix.client.models import TextClassificationRecord
from rubrix.labeling.text_classification.rule import Rule


class WeakLabels:
    """Computes the weak labels of a dataset given a list of rules.

    Args:
        rules: A list of rules (labeling functions). They must return a string, or `None` in case of abstention.
        dataset: Name of the dataset to which the rules will be applied.
        ids: An optional list of record ids to filter the dataset.
        query: An optional ElasticSearch query with the
            [query string syntax](https://rubrix.readthedocs.io/en/stable/reference/rubrix_webapp_reference.html#search-input)
            to filter the dataset.
        label2int: An optional dict, mapping the labels to integers. Use the string "None" to refer to the return
            type `None` (abstention). By default, we will construct a mapping on the fly when applying the rules.

    Raises:
        MultiLabelError: When trying to get weak labels for a multi-label text classification task.
        MissingLabelError: When provided with a `label2int` dict, and a
            weak label or annotation label is not present in its keys.

    Examples:
        Get the weak label matrix and a summary of the applied rules:

        >>> def awesome_rule(record: TextClassificationRecord) -> str:
        ...     return "Positive" if "awesome" in record.inputs["text"] else None
        >>> weak_labels = WeakLabels(rules=[awesome_rule], dataset="my_dataset")
        >>> weak_labels.matrix
        >>> weak_labels.summary()

        Use snorkel's LabelModel:

        >>> from snorkel.labeling.model import LabelModel
        >>> label_model = LabelModel()
        >>> label_model.fit(L_train=weak_labels.train_matrix())
        >>> label_model.score(L=weak_labels.test_matrix(), Y=weak_labels.annotation())
        >>> label_model.predict(L=weak_labels.train_matrix())
    """

    def __init__(
        self,
        rules: List[Callable],
        dataset: str,
        ids: Optional[List[Union[int, str]]] = None,
        query: Optional[str] = None,
        label2int: Optional[Dict[str, int]] = None,
    ):
        self._rules = rules
        self._dataset = dataset

        # load records and check compatibility
        self._records: List[TextClassificationRecord] = load(
            dataset, query=query, ids=ids, as_pandas=False
        )
        if self._records[0].multi_label:
            raise MultiLabelError(
                "Multi-label text classification is not yet supported."
            )

        # apply rules -> create the weak label matrix, annotation array, final label2int mapping
        self._matrix, self._annotation_array, self._label2int = self._apply_rules(
            label2int
        )

    def _apply_rules(
        self, label2int: Optional[Dict[str, int]]
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, int]]:
        """Apply the rules to the dataset.

        Args:
            label2int: An optional custom label2int mapping.

        Returns:
            The weak label matrix, the annotation array and their label2int mapping.

        Raises:
            MissingLabelError: When provided with a `label2int` dict, and a
                weak label or annotation label is not present in its keys.
        """
        # call apply on the ElasticSearch rules
        for rule in tqdm(self._rules, desc="Preparing rules"):
            if isinstance(rule, Rule):
                rule.apply(self._dataset)

        # create weak label matrix, annotation array, final label2int
        weak_label_matrix = np.empty(
            (len(self._records), len(self._rules)), dtype=np.short
        )
        annotation_array = np.empty(len(self._records), dtype=np.short)
        _label2int = {"None": -1} if label2int is None else label2int

        for n, record in tqdm(
            enumerate(self._records), total=len(self._records), desc="Applying rules"
        ):
            # First: fill annotation array
            annotation = record.annotation or "None"

            try:
                annotation = _label2int[annotation]
            except KeyError as error:
                # When a label2int was provided, we want to raise an error if the label is missing!
                if label2int is not None:
                    raise MissingLabelError(
                        f"The annotation label '{annotation}' is missing in the `label2int` dict {label2int}"
                    ) from error
                # we already have "None" -> we need to subtract 1
                _label2int[annotation] = len(_label2int) - 1
                annotation = _label2int[annotation]

            annotation_array[n] = annotation

            # Second: fill weak label matrix
            for m, rule in enumerate(self._rules):
                weak_label = rule(record) or "None"

                try:
                    weak_label = _label2int[weak_label]
                except KeyError as error:
                    if label2int is not None:
                        raise MissingLabelError(
                            f"A rule returned the weak label '{weak_label}', "
                            f"but it is missing in the `label2int` dict {label2int}"
                        ) from error
                    _label2int[weak_label] = len(_label2int) - 1
                    weak_label = _label2int[weak_label]

                weak_label_matrix[n, m] = weak_label

        return weak_label_matrix, annotation_array, _label2int

    @property
    def records(self) -> List[TextClassificationRecord]:
        """The records corresponding to the weak labels."""
        return self._records

    @property
    def label2int(self) -> Dict[str, int]:
        """The dictionary that maps the weak/annotation labels to integers."""
        return self._label2int

    @property
    def matrix(self) -> np.ndarray:
        """The weak label matrix."""
        return self._matrix

    def train_matrix(self) -> np.ndarray:
        """Returns part of the weak label `self.matrix` that has NO corresponding annotation."""
        return self._matrix[self._annotation_array == self._label2int["None"]]

    def test_matrix(self) -> np.ndarray:
        """Returns part of the weak label `self.matrix` that has A corresponding annotation."""
        return self._matrix[self._annotation_array != self._label2int["None"]]

    def annotation(self, exclude_missing_annotations: bool = True) -> np.ndarray:
        """Returns the annotation labels as an array of integers.

        Args:
            exclude_missing_annotations: If True, excludes missing annotations,
                that is all entries with the `self.label2int["None"]` int.
        """
        if not exclude_missing_annotations:
            return self._annotation_array
        return self._annotation_array[self._annotation_array != self._label2int["None"]]

    def summary(
        self,
        normalize_by_coverage: bool = False,
        annotation: Optional[np.ndarray] = None,
    ) -> pd.DataFrame:
        """Returns following summary statistics for each rule:

        - polarity: Set of unique labels returned by the rule, excluding "None" (abstain).
        - coverage: Fraction of the records labeled by the rule.
        - overlaps: Fraction of the records labeled by the rule together with at least one other rule.
        - conflicts: Fraction of the records where the rule disagrees with at least one other rule.
        - correct: Number of records the rule labeled correctly (if annotations are available).
        - incorrect: Number of records the rule labels incorrectly (if annotations are available).
        - precision: Fraction of correct labels given by the rule (if annotations are available).
            The precision does not penalize the rule for abstains.

        Args:
            normalize_by_coverage: Normalize the overlaps and conflicts by the respective coverage.
            annotation: An optional array with ints holding the annotations.
                By default we will use `self.annotation(exclude_missing_annotations=False)`.

        Returns:
            A summary DataFrame with polarity, coverage, overlaps and conflicts of the rules.
            If annotated records are available, we also provide the precision of the rules.
        """
        has_weak_label = self._matrix != self._label2int["None"]

        # polarity
        polarity = [
            set(
                np.unique(
                    self._matrix[:, i][self._matrix[:, i] != self._label2int["None"]]
                )
            )
            for i in range(len(self._rules))
        ]
        polarity.append(set().union(*polarity))

        # coverage
        coverage = has_weak_label.sum(axis=0) / len(self._records)
        coverage = np.append(
            coverage,
            (has_weak_label.sum(axis=1) > 0).sum() / len(self._records),
        )

        # overlaps
        has_overlaps = has_weak_label.sum(axis=1) > 1
        overlaps = self._compute_overlaps_conflicts(
            has_weak_label, has_overlaps, coverage, normalize_by_coverage
        )

        # conflicts
        # TODO: For a lot of records (~1e6), this could become slow ... not sure if there is a vectorized solution.
        has_conflicts = np.apply_along_axis(
            lambda x: len(np.unique(x[x != self._label2int["None"]])) > 1,
            axis=1,
            arr=self._matrix,
        )
        conflicts = self._compute_overlaps_conflicts(
            has_weak_label, has_conflicts, coverage, normalize_by_coverage
        )

        # index for the summary
        # TODO: Get better names
        index = [f"rule{i}" for i in range(len(self._rules))] + ["total"]

        # only add correct, incorrect and precision if we have annotations
        if (
            any(self._annotation_array != self._label2int["None"])
            or annotation is not None
        ):
            correct, incorrect = self._compute_correct_incorrect(
                has_weak_label,
                annotation if annotation is not None else self._annotation_array,
            )
            precision = np.nan_to_num(correct / (correct + incorrect))

            return pd.DataFrame(
                {
                    "polarity": polarity,
                    "coverage": coverage,
                    "overlaps": overlaps,
                    "conflicts": conflicts,
                    "correct": correct,
                    "incorrect": incorrect,
                    "precision": precision,
                },
                index=index,
            )

        return pd.DataFrame(
            {
                "polarity": polarity,
                "coverage": coverage,
                "overlaps": overlaps,
                "conflicts": conflicts,
            },
            index=index,
        )

    def _compute_overlaps_conflicts(
        self,
        has_weak_label: np.ndarray,
        has_overlaps_or_conflicts: np.ndarray,
        coverage: np.ndarray,
        normalize_by_coverage: bool,
    ) -> np.ndarray:
        """Helper method to compute the overlaps/conflicts and optionally normalize them by the respective coverage"""
        overlaps_or_conflicts = (
            has_weak_label
            * np.repeat(has_overlaps_or_conflicts, len(self._rules)).reshape(
                has_weak_label.shape
            )
        ).sum(axis=0) / len(self._records)
        # total
        overlaps_or_conflicts = np.append(
            overlaps_or_conflicts, has_overlaps_or_conflicts.sum() / len(self._records)
        )

        if normalize_by_coverage:
            overlaps_or_conflicts /= coverage
            return np.nan_to_num(overlaps_or_conflicts)

        return overlaps_or_conflicts

    def _compute_correct_incorrect(
        self, has_weak_label: np.ndarray, annotation: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Helper method to compute the correctly and incorrectly predicted annotations by the rules"""
        annotation_matrix = np.repeat(annotation, len(self._rules)).reshape(
            self._matrix.shape
        )

        # correct
        correct_with_abstain = annotation_matrix == self._matrix
        correct = np.where(has_weak_label, correct_with_abstain, False).sum(axis=0)

        # incorrect
        incorrect_with_abstain = annotation_matrix != self._matrix
        incorrect = np.where(
            has_weak_label & (annotation_matrix != self._label2int["None"]),
            incorrect_with_abstain,
            False,
        ).sum(axis=0)

        # add totals at the end
        return np.append(correct, correct.sum()), np.append(incorrect, incorrect.sum())

    def bucket(self, labels: List[str], rules: List[int]) -> pd.DataFrame:
        raise NotImplementedError


class WeakLabelsError(Exception):
    pass


class MultiLabelError(WeakLabelsError):
    pass


class MissingLabelError(WeakLabelsError):
    pass
