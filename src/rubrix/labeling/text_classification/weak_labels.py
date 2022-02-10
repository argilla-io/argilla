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
import warnings
from collections import Counter
from typing import Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from tqdm.auto import tqdm

from rubrix import load
from rubrix.client.datasets import DatasetForTextClassification
from rubrix.client.models import TextClassificationRecord
from rubrix.labeling.text_classification.rule import Rule, load_rules


class WeakLabels:
    """Computes the weak labels of a dataset by applying a given list of rules.

    Args:
        dataset: Name of the dataset to which the rules will be applied.
        rules: A list of rules (labeling functions). They must return a string, or ``None`` in case of abstention.
            If None, we will use the rules of the dataset (Default).
        ids: An optional list of record ids to filter the dataset before applying the rules.
        query: An optional ElasticSearch query with the
            `query string syntax <https://rubrix.readthedocs.io/en/stable/reference/webapp/search_records.html>`_
            to filter the dataset before applying the rules.
        label2int: An optional dict, mapping the labels to integers. Remember that the return type ``None`` means
            abstention (e.g. ``{None: -1}``). By default, we will build a mapping on the fly when applying the rules.

    Raises:
        NoRulesFoundError: When you do not provide rules, and the dataset has no rules either.
        DuplicatedRuleNameError: When you provided multiple rules with the same name.
        NoRecordsFoundError: When the filtered dataset is empty.
        MultiLabelError: When trying to get weak labels for a multi-label text classification task.
        MissingLabelError: When provided with a ``label2int`` dict, and a
            weak label or annotation label is not present in its keys.

    Examples:
        Get the weak label matrix from a dataset with rules:

        >>> weak_labels = WeakLabels(dataset="my_dataset")
        >>> weak_labels.matrix()
        >>> weak_labels.summary()

        Get the weak label matrix from rules defined in Python:

        >>> def awesome_rule(record: TextClassificationRecord) -> str:
        ...     return "Positive" if "awesome" in record.inputs["text"] else None
        >>> another_rule = Rule(query="good OR best", label="Positive")
        >>> weak_labels = WeakLabels(rules=[awesome_rule, another_rule], dataset="my_dataset")
        >>> weak_labels.matrix()
        >>> weak_labels.summary()

        Use the WeakLabels object with snorkel's LabelModel:

        >>> from snorkel.labeling.model import LabelModel
        >>> label_model = LabelModel()
        >>> label_model.fit(L_train=weak_labels.matrix(has_annotation=False))
        >>> label_model.score(L=weak_labels.matrix(has_annotation=True), Y=weak_labels.annotation())
        >>> label_model.predict(L=weak_labels.matrix(has_annotation=False))

        For a builtin integration with Snorkel, see `rubrix.labeling.text_classification.Snorkel`.
    """

    def __init__(
        self,
        dataset: str,
        rules: Optional[List[Callable]] = None,
        ids: Optional[List[Union[int, str]]] = None,
        query: Optional[str] = None,
        label2int: Optional[Dict[Optional[str], int]] = None,
    ):
        if not isinstance(dataset, str):
            raise TypeError(
                f"The name of the dataset must be a string, but you provided: {dataset}"
            )
        self._dataset = dataset

        self._rules = rules or load_rules(dataset)
        if self._rules == []:
            raise NoRulesFoundError(
                f"No rules were found in the given dataset '{dataset}'"
            )

        self._rules_index2name = {
            # covers our Rule class, snorkel's LabelingFunction class and arbitrary methods
            index: (
                getattr(rule, "name", None)
                or (
                    getattr(rule, "__name__", None)
                    # allow multiple lambda functions
                    if getattr(rule, "__name__", None) != "<lambda>"
                    else None
                )
                or f"rule_{index}"
            )
            for index, rule in enumerate(self._rules)
        }
        # raise error if there are duplicates
        counts = Counter(self._rules_index2name.values())
        if len(counts.keys()) < len(self._rules):
            raise DuplicatedRuleNameError(
                f"Following rule names are duplicated x times: { {key: val for key, val in counts.items() if val > 1} }"
                " Please make sure to provide unique rule names."
            )
        self._rules_name2index = {
            val: key for key, val in self._rules_index2name.items()
        }

        # load records and check compatibility
        self._records: DatasetForTextClassification = load(
            dataset, query=query, ids=ids, as_pandas=False
        )
        if not self._records:
            raise NoRecordsFoundError(
                f"No records found in dataset '{dataset}'"
                + (f" with query '{query}'" if query else "")
                + (" and" if query and ids else "")
                + (f" with ids {ids}." if ids else ".")
            )

        if self._records[0].multi_label:
            raise MultiLabelError(
                "Multi-label text classification is not yet supported."
            )

        # apply rules -> create the weak label matrix, annotation array, final label2int mapping
        self._matrix, self._annotation_array, self._label2int = self._apply_rules(
            label2int
        )
        self._int2label = {v: k for k, v in self._label2int.items()}

    def _apply_rules(
        self, label2int: Optional[Dict[str, int]]
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, int]]:
        """Apply the rules to the dataset.

        Args:
            label2int: An optional custom label2int mapping.

        Returns:
            The weak label matrix, the annotation array and their label2int mapping.

        Raises:
            MissingLabelError: When provided with a ``label2int`` dict, and a
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
        _label2int = {None: -1} if label2int is None else label2int
        if None not in _label2int:
            raise MissingLabelError(
                "Your provided `label2int` mapping does not contain the required abstention label `None`."
            )

        for n, record in tqdm(
            enumerate(self._records), total=len(self._records), desc="Applying rules"
        ):
            # First: fill annotation array
            try:
                annotation = _label2int[record.annotation]
            except KeyError as error:
                # When a label2int was provided, we want to raise an error if the label is missing!
                if label2int is not None:
                    raise MissingLabelError(
                        f"The annotation label '{record.annotation}' is missing in the `label2int` dict {label2int}"
                    ) from error
                # we already have `None` -> we need to subtract 1
                _label2int[record.annotation] = len(_label2int) - 1
                annotation = _label2int[record.annotation]

            annotation_array[n] = annotation

            # Second: fill weak label matrix
            for m, rule in enumerate(self._rules):
                weak_label = rule(record)

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
    def rules(self) -> List[Callable]:
        """The rules (labeling functions) that were used to produce the weak labels."""
        return self._rules

    @property
    def label2int(self) -> Dict[Optional[str], int]:
        """The dictionary that maps weak/annotation labels to integers."""
        return self._label2int

    @property
    def int2label(self) -> Dict[int, Optional[str]]:
        """The dictionary that maps integers to weak/annotation labels."""
        return self._int2label

    def matrix(self, has_annotation: Optional[bool] = None) -> np.ndarray:
        """Returns the weak label matrix, or optionally just a part of it.

        Args:
            has_annotation: If True, return only the part of the matrix that has a corresponding annotation.
                If False, return only the part of the matrix that has NOT a corresponding annotation.
                By default, we return the whole weak label matrix.

        Returns:
            The weak label matrix, or optionally just a part of it.
        """
        if has_annotation is True:
            return self._matrix[self._annotation_array != self._label2int[None]]
        if has_annotation is False:
            return self._matrix[self._annotation_array == self._label2int[None]]

        return self._matrix

    def records(
        self, has_annotation: Optional[bool] = None
    ) -> List[TextClassificationRecord]:
        """Returns the records corresponding to the weak label matrix.

        Args:
            has_annotation: If True, return only the records that have an annotation. If False, return only the records
                that have NO annotation. By default, we return all the records.

        Returns:
            A list of records, or optionally just a part of them.
        """
        if has_annotation is True:
            return [rec for rec in self._records if rec.annotation is not None]
        if has_annotation is False:
            return [rec for rec in self._records if rec.annotation is None]

        return self._records

    def annotation(
        self,
        include_missing: bool = False,
        exclude_missing_annotations: Optional[bool] = None,
    ) -> np.ndarray:
        """Returns the annotation labels as an array of integers.

        Args:
            include_missing: If True, returns an array of the length of the record list (``self.records()``).
                For this we will fill the array with the ``self.label2int[None]`` integer for records without an annotation.
            exclude_missing_annotations: DEPRECATED

        Returns:
            The annotation array of integers.
        """
        if exclude_missing_annotations is not None:
            warnings.warn(
                "'exclude_missing_annotations' is deprecated and will be removed in the next major release. "
                "Please use the 'include_missing' argument.",
                category=FutureWarning,
            )
            include_missing = not exclude_missing_annotations

        if include_missing:
            return self._annotation_array

        return self._annotation_array[self._annotation_array != self._label2int[None]]

    def summary(
        self,
        normalize_by_coverage: bool = False,
        annotation: Optional[np.ndarray] = None,
    ) -> pd.DataFrame:
        """Returns following summary statistics for each rule:

        - **label**: Set of unique labels returned by the rule, excluding "None" (abstain).
        - **coverage**: Fraction of the records labeled by the rule.
        - **annotated_coverage**: Fraction of annotated records labeled by the rule (if annotations are available).
        - **overlaps**: Fraction of the records labeled by the rule together with at least one other rule.
        - **conflicts**: Fraction of the records where the rule disagrees with at least one other rule.
        - **correct**: Number of records the rule labeled correctly (if annotations are available).
        - **incorrect**: Number of records the rule labeled incorrectly (if annotations are available).
        - **precision**: Fraction of correct labels given by the rule (if annotations are available). The precision does not penalize the rule for abstains.


        Args:
            normalize_by_coverage: Normalize the overlaps and conflicts by the respective coverage.
            annotation: An optional array with ints holding the annotations.
                By default we will use ``self.annotation(exclude_missing_annotations=False)``.

        Returns:
            The summary statistics for each rule in a pandas DataFrame.
        """
        has_weak_label = self._matrix != self._label2int[None]

        # polarity (label)
        polarity = [
            set(
                self._int2label[integer]
                for integer in np.unique(
                    self._matrix[:, i][self._matrix[:, i] != self._label2int[None]]
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
        # TODO: For a lot of records (~1e6), this could become slow (~10s) ... a vectorized solution would be better.
        has_conflicts = np.apply_along_axis(
            lambda x: len(np.unique(x[x != self._label2int[None]])) > 1,
            axis=1,
            arr=self._matrix,
        )
        conflicts = self._compute_overlaps_conflicts(
            has_weak_label, has_conflicts, coverage, normalize_by_coverage
        )

        # index for the summary
        index = list(self._rules_name2index.keys()) + ["total"]

        # only add annotated_coverage, correct, incorrect and precision if we have annotations
        if (
            any(self._annotation_array != self._label2int[None])
            or annotation is not None
        ):
            # annotated coverage
            has_annotation = (
                annotation if annotation is not None else self._annotation_array
            ) != self._label2int[None]
            annotated_coverage = (
                has_weak_label[has_annotation].sum(axis=0) / has_annotation.sum()
            )
            annotated_coverage = np.append(
                annotated_coverage,
                (has_weak_label[has_annotation].sum(axis=1) > 0).sum()
                / has_annotation.sum(),
            )

            # correct/incorrect
            correct, incorrect = self._compute_correct_incorrect(
                has_weak_label,
                annotation if annotation is not None else self._annotation_array,
            )

            # precision
            precision = correct / (correct + incorrect)

            return pd.DataFrame(
                {
                    "label": polarity,
                    "coverage": coverage,
                    "annotated_coverage": annotated_coverage,
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
                "label": polarity,
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
            has_weak_label & (annotation_matrix != self._label2int[None]),
            incorrect_with_abstain,
            False,
        ).sum(axis=0)

        # add totals at the end
        return np.append(correct, correct.sum()), np.append(incorrect, incorrect.sum())

    def show_records(
        self,
        labels: Optional[List[str]] = None,
        rules: Optional[List[Union[str, int]]] = None,
    ) -> pd.DataFrame:
        """Shows records in a pandas DataFrame, optionally filtered by weak labels and non-abstaining rules.

        If you provide both ``labels`` and ``rules``, we take the intersection of both filters.

        Args:
            labels: All of these labels are in the record's weak labels. If None, do not filter by labels.
            rules: All of these rules did not abstain for the record. If None, do not filter by rules.
                You can refer to the rules by their (function) name or by their index in the ``self.rules`` list.

        Returns:
            The optionally filtered records as a pandas DataFrame.
        """
        # get labels mask
        if labels is not None:
            labels = [self._label2int[label] for label in labels]
            idx_by_labels = np.isin(self._matrix, labels).sum(axis=1) >= len(labels)
        else:
            idx_by_labels = np.ones_like(self._records).astype(bool)

        # get rule mask
        if rules is not None:
            rules = [
                self._rules_name2index[rule] if isinstance(rule, str) else rule
                for rule in rules
            ]
            idx_by_rules = (self._matrix[:, rules] != self._label2int[None]).sum(
                axis=1
            ) == len(rules)
        else:
            idx_by_rules = np.ones_like(self._records).astype(bool)

        # apply mask
        filtered_records = np.array(self._records)[idx_by_labels & idx_by_rules]

        return pd.DataFrame(map(lambda x: x.dict(), filtered_records))

    def change_mapping(self, label2int: Dict[str, int]):
        """Allows you to change the mapping between labels and integers.

        This will update the ``self.matrix`` as well as the ``self.annotation``.

        Args:
            label2int: New label to integer mapping. Must cover all previous labels.
        """
        # save masks for swapping
        label_masks = {}
        annotation_masks = {}

        for label in self._label2int:
            # Check new label2int mapping
            if label not in label2int:
                raise MissingLabelError(
                    f"The label '{label}' is missing in the new mapping."
                )
            # compute masks
            label_masks[label] = self._matrix == self._label2int[label]
            annotation_masks[label] = self._annotation_array == self._label2int[label]

        # swap integers
        for label in self._label2int:
            self._matrix[label_masks[label]] = label2int[label]
            self._annotation_array[annotation_masks[label]] = label2int[label]

        # update mapping dicts
        self._label2int = label2int.copy()
        self._int2label = {val: key for key, val in self._label2int.items()}


class WeakLabelsError(Exception):
    pass


class NoRulesFoundError(WeakLabelsError):
    pass


class DuplicatedRuleNameError(WeakLabelsError):
    pass


class NoRecordsFoundError(WeakLabelsError):
    pass


class MultiLabelError(WeakLabelsError):
    pass


class MissingLabelError(WeakLabelsError):
    pass
