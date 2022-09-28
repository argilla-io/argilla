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

from argilla import load
from argilla.client.datasets import DatasetForTextClassification
from argilla.client.models import TextClassificationRecord
from argilla.labeling.text_classification.rule import Rule, load_rules


def _add_docstr(string: str):
    def docstring_decorator(fn):
        fn.__doc__ = string
        return fn

    return docstring_decorator


class WeakLabelsBase:
    """Base class for the weak label classes.

    Tries to facilitate the implementations, avoids code duplications.

    Args:
        dataset: Name of the dataset to which the rules will be applied.
        rules: A list of rules (labeling functions). They must return a string, or ``None`` in case of abstention.
            If None, we will use the rules of the dataset (Default).
        ids: An optional list of record ids to filter the dataset before applying the rules.
        query: An optional ElasticSearch query with the
            `query string syntax <https://argilla.readthedocs.io/en/stable/guides/queries.html>`_
            to filter the dataset before applying the rules.

    Raises:
        NoRulesFoundError: When you do not provide rules, and the dataset has no rules either.
        DuplicatedRuleNameError: When you provided multiple rules with the same name.
        NoRecordsFoundError: When the filtered dataset is empty.
    """

    def __init__(
        self,
        dataset: str,
        rules: Optional[List[Callable]] = None,
        ids: Optional[List[Union[int, str]]] = None,
        query: Optional[str] = None,
    ):
        if not isinstance(dataset, str):
            raise TypeError(
                f"The name of the dataset must be a string, but you provided: {dataset}"
            )
        self._dataset = dataset

        self._rules = rules or load_rules(dataset)
        if not self._rules:
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
            dataset, query=query, ids=ids
        )
        if not self._records:
            raise NoRecordsFoundError(
                f"No records found in dataset '{dataset}'"
                + (f" with query '{query}'" if query else "")
                + (" and" if query and ids else "")
                + (f" with ids {ids}." if ids else ".")
            )

        self._matrix = self._extended_matrix = self._extension_queries = None

    @property
    def rules(self) -> List[Callable]:
        """The rules (labeling functions) that were used to produce the weak labels."""
        return self._rules

    @property
    def labels(self) -> List[str]:
        """The list of labels."""
        raise NotImplementedError

    @property
    def cardinality(self) -> int:
        """The number of labels."""
        raise NotImplementedError

    def records(
        self, has_annotation: Optional[bool] = None
    ) -> List[TextClassificationRecord]:
        """Returns the records corresponding to the weak label matrix

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

        return list(self._records)

    def matrix(self, has_annotation: Optional[bool] = None) -> np.ndarray:
        """Returns the weak label matrix, or optionally just a part of it.

        Args:
            has_annotation: If True, return only the part of the matrix that has a corresponding annotation.
                If False, return only the part of the matrix that has NOT a corresponding annotation.
                By default, we return the whole weak label matrix.

        Returns:
            The weak label matrix, or optionally just a part of it.
        """
        raise NotImplementedError

    def annotation(
        self,
        include_missing: bool = False,
    ) -> np.ndarray:
        """Returns the annotation labels.

        Args:
            include_missing: If True, returns an array of the length of the record list (``self.records()``).

        Returns:
            The annotation labels.
        """
        raise NotImplementedError

    def summary(
        self,
        normalize_by_coverage: bool = False,
        annotation: Optional[np.ndarray] = None,
    ) -> pd.DataFrame:
        """Returns a summary statistics for each rule:

        Args:
            normalize_by_coverage: Normalize the overlaps and conflicts by the respective coverage.
            annotation: An optional array holding the annotations.
                By default, we will use ``self.annotation(include_missing=True)``.

        Returns:
            The summary statistics for each rule in a pandas DataFrame.
        """
        raise NotImplementedError

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
        raise NotImplementedError

    def _compute_overlaps_conflicts(
        self,
        has_weak_label: np.ndarray,
        has_overlaps_or_conflicts: np.ndarray,
        coverage: np.ndarray,
        normalize_by_coverage: bool,
    ) -> np.ndarray:
        """Helper method to compute the overlaps/conflicts and optionally normalize them by the respective coverage

        Args:
            has_weak_label: 2D boolean matrix (i, j) that indicates if the record i has a weak label from rule j.
            has_overlaps_or_conflicts: Array that indicates if the record has overlapping/conflicting weak labels.
            coverage: Array of coverages for each rule
            normalize_by_coverage: Normalize the overlaps/conflicts by the respective coverage.

        Returns:
            Array of fractions of overlaps/conflicts for each rule, optionally normalized by their coverages.
        """
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
            # ignore division by 0 warnings, as we convert the nan back to 0.0 afterwards
            with np.errstate(divide="ignore", invalid="ignore"):
                overlaps_or_conflicts /= coverage
            return np.nan_to_num(overlaps_or_conflicts)

        return overlaps_or_conflicts

    def extend_matrix(
        self,
        thresholds: Union[List[float], np.ndarray],
        embeddings: Optional[np.ndarray] = None,
        gpu: bool = False,
    ):
        """Extends the weak label matrix through embeddings according to the similarity thresholds for each rule.

        Implementation based on `Epoxy <https://github.com/HazyResearch/epoxy>`__.

        Args:
            thresholds: An array of thresholds between 0.0 and 1.0, one for each column of the weak labels matrix.
                Each one stands for the minimum cosine similarity between two sentences for a rule to be extended.
            embeddings: Embeddings for each row of the weak label matrix.
                If not provided, we will use the ones from the last ``WeakLabels.extend_matrix()`` call.
            gpu: If True, perform FAISS similarity queries on GPU.

        Examples:
            >>> # Choose any model to generate the embeddings.
            >>> from sentence_transformers import SentenceTransformer
            >>> model = SentenceTransformer('all-mpnet-base-v2', device='cuda')
            >>>
            >>> # Generate the embeddings and set the thresholds.
            >>> weak_labels = {class_name}(dataset="my_dataset")
            >>> embeddings = np.array([ model.encode(rec.text) for rec in weak_labels.records() ])
            >>> thresholds = [0.6] * len(weak_labels.rules)
            >>>
            >>> # Extend the weak labels matrix.
            >>> weak_labels.extend_matrix(thresholds, embeddings)
            >>>
            >>> # Calling the method below will now retrieve the extended matrix.
            >>> weak_labels.matrix()
            >>>
            >>> # Subsequent calls without the embeddings parameter will reutilize the faiss index built on the first call.
            >>> thresholds = [0.75] * len(weak_labels.rules)
            >>> weak_labels.extend_matrix(thresholds)
            >>> weak_labels.matrix()
        """
        abstains, supports = self._extend_matrix_preprocess()

        if embeddings is not None:
            self._extension_queries = self._find_dists_and_nearest(
                np.copy(embeddings).astype(np.float32), abstains, supports, gpu=gpu
            )
        elif self._extension_queries is None:
            raise ValueError(
                "Embeddings are not optional the first time a matrix is extended."
            )
        dists, nearest = self._extension_queries

        self._extended_matrix = np.copy(self._matrix)
        new_points = [(dists[i] > thresholds[i]) for i in range(self._matrix.shape[1])]
        for i in range(self._matrix.shape[1]):
            self._extended_matrix[abstains[i][new_points[i]], i] = self._matrix[
                supports[i], i
            ][nearest[i][new_points[i]]]

        self._extend_matrix_postprocess()

    def _find_dists_and_nearest(
        self,
        embeddings: np.ndarray,
        abstains: List[np.ndarray],
        support: List[np.ndarray],
        gpu: bool,
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """Helper method to extend the weak labels."""
        try:
            import faiss
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "'faiss' must be installed to extend a weak label matrix! "
                "You can install 'faiss' with the commands: `pip install faiss-cpu` or `pip install faiss-gpu`"
            )
        faiss.normalize_L2(embeddings)
        embeddings_length = embeddings.shape[1]

        label_fn_indexes = [
            faiss.IndexFlatIP(embeddings_length) for i in range(self._matrix.shape[1])
        ]

        if gpu:
            res = faiss.StandardGpuResources()
            label_fn_indexes = [
                faiss.index_cpu_to_gpu(res, 0, x) for x in label_fn_indexes
            ]

        for i in range(self._matrix.shape[1]):
            label_fn_indexes[i].add(embeddings[support[i]])

        dists_and_nearest = []
        for i in tqdm(range(self._matrix.shape[1]), total=self._matrix.shape[1]):
            embs_query = np.copy(embeddings[abstains[i]])
            faiss.normalize_L2(embs_query)
            dists_and_nearest.append(label_fn_indexes[i].search(embs_query, 1))

        dists = [
            dist_and_nearest[0].flatten() for dist_and_nearest in dists_and_nearest
        ]
        nearest = [
            dist_and_nearest[1].flatten() for dist_and_nearest in dists_and_nearest
        ]

        return dists, nearest

    def _extend_matrix_preprocess(self) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """Helper method to compute the abstains and supports.

        abstains: List of record indices per rule for which the rule abstained.
        supports: List of record indices per rule for which the rule voted.

        Returns:
            A tuple containing the abstains and supports
        """
        raise NotImplementedError

    def _extend_matrix_postprocess(self):
        """Helper method to optionally modify the extended matrix after calling ``self.extend_matrix``."""
        pass


class WeakLabels(WeakLabelsBase):
    """Computes the weak labels of a single-label text classification dataset by applying a given list of rules.

    Args:
        dataset: Name of the dataset to which the rules will be applied.
        rules: A list of rules (labeling functions). They must return a string, or ``None`` in case of abstention.
            If None, we will use the rules of the dataset (Default).
        ids: An optional list of record ids to filter the dataset before applying the rules.
        query: An optional ElasticSearch query with the
            `query string syntax <https://argilla.readthedocs.io/en/stable/guides/queries.html>`_
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
        >>> # Get the weak label matrix from a dataset with rules:
        >>> weak_labels = WeakLabels(dataset="my_dataset")
        >>> weak_labels.matrix()
        >>> weak_labels.summary()
        >>>
        >>> # Get the weak label matrix from rules defined in Python:
        >>> def awesome_rule(record: TextClassificationRecord) -> str:
        ...     return "Positive" if "awesome" in record.text else None
        >>> another_rule = Rule(query="good OR best", label="Positive")
        >>> weak_labels = WeakLabels(dataset="my_dataset", rules=[awesome_rule, another_rule])
        >>> weak_labels.matrix()
        >>> weak_labels.summary()
        >>>
        >>> # Use the WeakLabels object with snorkel's LabelModel:
        >>> from snorkel.labeling.model import LabelModel
        >>> label_model = LabelModel()
        >>> label_model.fit(L_train=weak_labels.matrix(has_annotation=False))
        >>> label_model.score(L=weak_labels.matrix(has_annotation=True), Y=weak_labels.annotation())
        >>> label_model.predict(L=weak_labels.matrix(has_annotation=False))
        >>>
        >>> # For a builtin integration with Snorkel, see `argilla.labeling.text_classification.Snorkel`.
    """

    def __init__(
        self,
        dataset: str,
        rules: Optional[List[Callable]] = None,
        ids: Optional[List[Union[int, str]]] = None,
        query: Optional[str] = None,
        label2int: Optional[Dict[Optional[str], int]] = None,
    ):
        super().__init__(dataset=dataset, rules=rules, ids=ids, query=query)

        if self._records[0].multi_label:
            raise MultiLabelError(
                "For multi-label text classification, use the `ar.labeling.text_classification.WeakMultiLabels` class."
            )

        # apply rules -> create the weak label matrix, annotation array, final label2int mapping
        self._matrix, self._annotation, self._label2int = self._apply_rules(label2int)
        self._int2label = {v: k for k, v in self._label2int.items()}

    def _apply_rules(
        self, label2int: Optional[Dict[str, int]]
    ) -> Tuple[np.ndarray, np.ndarray, Dict[Optional[str], int]]:
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
            # FIRST: fill annotation array
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

            # SECOND: fill weak label matrix
            for m, rule in enumerate(self._rules):
                weak_label = rule(record)
                if isinstance(weak_label, list):
                    if len(weak_label) != 1:
                        raise MultiLabelError(
                            "For rules that do not return exactly 1 label, use the `WeakMultiLabels` class."
                        )
                    weak_label = weak_label[0]

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
    def cardinality(self) -> int:
        return len(self._label2int) - 1

    @property
    def labels(self) -> List[str]:
        return [key for key in self._label2int.keys() if key is not None]

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
        matrix = (
            self._matrix if self._extended_matrix is None else self._extended_matrix
        )

        if has_annotation is True:
            return matrix[self._annotation != self._label2int[None]]
        if has_annotation is False:
            return matrix[self._annotation == self._label2int[None]]

        return matrix

    def annotation(
        self,
        include_missing: bool = False,
        exclude_missing_annotations: Optional[bool] = None,
    ) -> np.ndarray:
        """Returns the annotation labels as an array of integers.

        Args:
            include_missing: If True, returns an array of the length of the record list (``self.records()``).
                For this, we will fill the array with the ``self.label2int[None]`` integer for records without an annotation.
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
            return self._annotation

        return self._annotation[self._annotation != self._label2int[None]]

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
        - **correct**: Number of labels the rule predicted correctly (if annotations are available).
        - **incorrect**: Number of labels the rule predicted incorrectly (if annotations are available).
        - **precision**: Fraction of correct labels given by the rule (if annotations are available). The precision does not penalize the rule for abstains.


        Args:
            normalize_by_coverage: Normalize the overlaps and conflicts by the respective coverage.
            annotation: An optional array with ints holding the annotations.
                By default, we will use ``self.annotation(include_missing=True)``.

        Returns:
            The summary statistics for each rule in a pandas DataFrame.
        """
        annotation = annotation if annotation is not None else self._annotation
        has_weak_label = self.matrix() != self._label2int[None]

        # polarity (label)
        polarity = [
            set(
                self._int2label[integer]
                for integer in np.unique(
                    self.matrix()[:, i][self.matrix()[:, i] != self._label2int[None]]
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
            arr=self.matrix(),
        )
        conflicts = self._compute_overlaps_conflicts(
            has_weak_label, has_conflicts, coverage, normalize_by_coverage
        )

        # index for the summary
        index = list(self._rules_name2index.keys()) + ["total"]

        # only add annotated_coverage, correct, incorrect and precision if we have annotations
        has_annotation = annotation != self._label2int[None]
        if any(has_annotation):
            # annotated coverage
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
                annotation if annotation is not None else self._annotation,
            )

            # precision, ignore division by 0 warnings: we allow np.nan and np.inf
            with np.errstate(divide="ignore", invalid="ignore"):
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

    def _compute_correct_incorrect(
        self, has_weak_label: np.ndarray, annotation: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Helper method to compute the correctly and incorrectly predicted annotations by the rules"""
        annotation_matrix = np.repeat(annotation, len(self._rules)).reshape(
            self.matrix().shape
        )

        # correct
        correct_with_abstain = annotation_matrix == self.matrix()
        correct = np.where(has_weak_label, correct_with_abstain, False).sum(axis=0)

        # incorrect
        incorrect_with_abstain = annotation_matrix != self.matrix()
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
            idx_by_labels = np.isin(self.matrix(), labels).sum(axis=1) >= len(labels)
        else:
            idx_by_labels = np.ones_like(self._records).astype(bool)

        # get rule mask
        if rules is not None:
            rules = [
                self._rules_name2index[rule] if isinstance(rule, str) else rule
                for rule in rules
            ]
            idx_by_rules = (self.matrix()[:, rules] != self._label2int[None]).sum(
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
            label_masks[label] = self.matrix() == self._label2int[label]
            annotation_masks[label] = self._annotation == self._label2int[label]

        # swap integers
        for label in self._label2int:
            self.matrix()[label_masks[label]] = label2int[label]
            self._annotation[annotation_masks[label]] = label2int[label]

        # update mapping dicts
        self._label2int = label2int.copy()
        self._int2label = {val: key for key, val in self._label2int.items()}

    @_add_docstr(WeakLabelsBase.extend_matrix.__doc__.format(class_name="WeakLabels"))
    def extend_matrix(
        self,
        thresholds: Union[List[float], np.ndarray],
        embeddings: Optional[np.ndarray] = None,
        gpu: bool = False,
    ):
        super().extend_matrix(thresholds=thresholds, embeddings=embeddings, gpu=gpu)

    def _extend_matrix_preprocess(self) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        abstains = [
            np.argwhere(self._matrix[:, i] == self._label2int[None]).flatten()
            for i in range(self._matrix.shape[1])
        ]

        supports = [
            np.argwhere(self._matrix[:, i] != self._label2int[None]).flatten()
            for i in range(self._matrix.shape[1])
        ]

        return abstains, supports

    def _extend_matrix_postprocess(self):
        """Keeps the rows of the original weak label matrix, for which at least on rule did not abstain."""
        recs_with_votes = np.argwhere(
            (self._matrix != self._label2int[None]).sum(-1) > 0
        ).flatten()
        self._extended_matrix[recs_with_votes] = self._matrix[recs_with_votes]


class WeakMultiLabels(WeakLabelsBase):
    """Computes the weak labels of a multi-label text classification dataset by applying a given list of rules.

    Args:
        dataset: Name of the dataset to which the rules will be applied.
        rules: A list of rules (labeling functions). They must return a string, list of strings, or ``None`` in case of
            abstention. If None, we will use the rules of the dataset (Default).
        ids: An optional list of record ids to filter the dataset before applying the rules.
        query: An optional ElasticSearch query with the
            `query string syntax <https://argilla.readthedocs.io/en/stable/guides/queries.html>`_
            to filter the dataset before applying the rules.

    Raises:
        NoRulesFoundError: When you do not provide rules, and the dataset has no rules either.
        DuplicatedRuleNameError: When you provided multiple rules with the same name.
        NoRecordsFoundError: When the filtered dataset is empty.

    Examples:
        >>> # Get the 3 dimensional weak label matrix from a multi-label classification dataset with rules:
        >>> weak_labels = WeakMultiLabels(dataset="my_dataset")
        >>> weak_labels.matrix()
        >>> weak_labels.summary()
        >>>
        >>> # Get the 3 dimensional weak label matrix from rules defined in Python:
        >>> def awesome_rule(record: TextClassificationRecord) -> str:
        ...     return ["Positive", "Slang"] if "next level" in record.text else None
        >>> another_rule = Rule(query="amped OR psyched", label=["Positive", "Slang"])
        >>> weak_labels = WeakMultiLabels(dataset="my_dataset", rules=[awesome_rule, another_rule])
        >>> weak_labels.matrix()
        >>> weak_labels.summary()
    """

    def __init__(
        self,
        dataset: str,
        rules: Optional[List[Callable]] = None,
        ids: Optional[List[Union[int, str]]] = None,
        query: Optional[str] = None,
    ):
        super().__init__(dataset=dataset, rules=rules, ids=ids, query=query)

        # apply rules -> create the weak label matrix (3D), annotation (2D), label list
        self._matrix, self._annotation, self._labels = self._apply_rules()

    def _apply_rules(self) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        # call apply on the ElasticSearch rules
        for rule in tqdm(self._rules, desc="Preparing rules"):
            if isinstance(rule, Rule):
                rule.apply(self._dataset)

        # we make two passes over the records:
        # FIRST: Get labels from rules and annotations
        annotations, weak_labels = [], []
        for record in tqdm(
            self._records, total=len(self._records), desc="Applying rules"
        ):
            annotations.append(
                record.annotation
                if isinstance(record.annotation, list)
                else [record.annotation]
            )
            weak_labels.append([np.atleast_1d(rule(record)) for rule in self._rules])

        annotation_set = {ann for anns in annotations for ann in anns}
        weak_label_set = {
            wl for wl_record in weak_labels for wl_rule in wl_record for wl in wl_rule
        }
        labels = sorted(list(annotation_set.union(weak_label_set) - {None}))

        # create weak label matrix (3D), annotation matrix
        weak_label_matrix = np.empty(
            (len(self._records), len(self._rules), len(labels)), dtype=np.byte
        )
        annotation_matrix = np.empty((len(self._records), len(labels)), dtype=np.byte)

        # SECOND: Fill arrays with weak labels
        for n, annotation_n, weak_label_n in tqdm(
            zip(range(len(annotations)), annotations, weak_labels),
            desc="Filling weak label matrix",
            total=len(annotations),
        ):
            # first: fill annotation matrix
            if annotation_n == [None]:
                # "abstain" is an array with -1
                annotation_matrix[n] = -1 * np.ones(len(labels), dtype=np.byte)
            else:
                annotation_matrix[n] = np.array(
                    [1 if label in annotation_n else 0 for label in labels],
                    dtype=np.byte,
                )

            # second: fill weak label matrix (3D)
            for m, weak_labels_m in enumerate(weak_label_n):
                if weak_labels_m.tolist() == [None]:
                    weak_label_matrix[n, m] = -1 * np.ones(len(labels))
                else:
                    weak_label_matrix[n, m] = np.array(
                        [1 if label in weak_labels_m else 0 for label in labels],
                        dtype=np.byte,
                    )

        return weak_label_matrix, annotation_matrix, labels

    @property
    def labels(self) -> List[str]:
        """The labels of the multi-label text classification dataset."""
        return self._labels

    @property
    def cardinality(self) -> int:
        return len(self._labels)

    def matrix(self, has_annotation: Optional[bool] = None) -> np.ndarray:
        """Returns the 3 dimensional weak label matrix, or optionally just a part of it.

        It has the dimensions ("nr of record" x "nr of rules" x "nr of labels").
        It holds a 1 or 0 in case a rule votes for a label or not. If the rule abstains, it holds a -1 for each label.

        Args:
            has_annotation: If True, return only the part of the matrix that has a corresponding annotation.
                If False, return only the part of the matrix that has NOT a corresponding annotation.
                By default, we return the whole weak label matrix.

        Returns:
            The 3 dimensional weak label matrix, or optionally just a part of it.
        """
        matrix = (
            self._matrix if self._extended_matrix is None else self._extended_matrix
        )

        if has_annotation is True:
            return matrix[self._annotation.sum(1) >= 0]
        if has_annotation is False:
            return matrix[self._annotation.sum(1) < 0]

        return matrix

    def annotation(
        self,
        include_missing: bool = False,
    ) -> np.ndarray:
        """Returns the annotation labels as a matrix of integers.

        It has the dimensions ("nr of record" x "nr of labels").
        It holds a 1 or 0 to indicate if the record is annotated with the corresponding label.
        In case there is no annotation for the record, it holds a -1 for each label.

        Args:
            include_missing: If True, returns a matrix of the length of the record list (``self.records()``).
                For this, we will fill the matrix with -1 for records without an annotation.

        Returns:
            The annotation labels as a matrix of integers.
        """
        if include_missing:
            return self._annotation

        return self._annotation[self._annotation.sum(1) >= 0]

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
        - **correct**: Number of labels the rule predicted correctly (if annotations are available).
        - **incorrect**: Number of labels the rule predicted incorrectly or missed (if annotations are available).
        - **precision**: Fraction of correct labels given by the rule (if annotations are available). The precision does not penalize the rule for abstains.

        Args:
            normalize_by_coverage: Normalize the overlaps by the respective coverage.
            annotation: An optional matrix with ints holding the annotations (see ``self.annotation``).
                By default, we will use ``self.annotation(include_missing=True)``.

        Returns:
            The summary statistics for each rule in a pandas DataFrame.
        """
        annotation = annotation if annotation is not None else self._annotation
        has_weak_label = self.matrix().sum(2) >= 0

        # polarity (label)
        polarity = [
            set(
                [
                    self._labels[i]
                    # get indices of votes
                    for i in np.nonzero(
                        # remove abstentions
                        self.matrix()[:, m, :][self.matrix()[:, m, :].sum(1) >= 0]
                    )[1]
                ]
            )
            for m in range(len(self._rules))
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

        # index for the summary
        index = list(self._rules_name2index.keys()) + ["total"]

        # only add annotated_coverage, correct, incorrect and precision if we have annotations
        has_annotation = annotation.sum(1) >= 0
        if any(has_annotation):
            # annotated coverage
            annotated_coverage = (
                has_weak_label[has_annotation].sum(axis=0) / has_annotation.sum()
            )
            annotated_coverage = np.append(
                annotated_coverage,
                (has_weak_label[has_annotation].sum(axis=1) > 0).sum()
                / has_annotation.sum(),
            )

            # correct/incorrect
            correct, incorrect = self._compute_correct_incorrect(annotation)

            # precision, ignore division by 0 warnings: we allow np.nan and np.inf
            with np.errstate(divide="ignore", invalid="ignore"):
                precision = correct / (correct + incorrect)

            return pd.DataFrame(
                {
                    "label": polarity,
                    "coverage": coverage,
                    "annotated_coverage": annotated_coverage,
                    "overlaps": overlaps,
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
            },
            index=index,
        )

    def _compute_correct_incorrect(
        self, annotation: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Helper method to compute the correctly and incorrectly predicted annotations by the rules"""
        # transform annotation to tensor
        annotation = np.repeat(annotation, len(self._rules), axis=0).reshape(
            self.matrix().shape
        )

        # correct, we don't want to count the "correct non predictions"
        correct = ((annotation == self.matrix()) & (self.matrix() == 1)).sum(2).sum(0)

        # incorrect, we don't want to count the "misses", since we focus on precision, not recall
        incorrect = (
            ((annotation != self.matrix()) & (self.matrix() == 1) & (annotation != -1))
            .sum(2)
            .sum(0)
        )

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
            labels = [self._labels.index(label) for label in labels]
            idx_by_labels = np.all(((self.matrix() == 1).sum(1) > 0)[:, labels], axis=1)
        else:
            idx_by_labels = np.ones_like(self._records).astype(bool)

        # get rule mask
        if rules is not None:
            rules = [
                self._rules_name2index[rule] if isinstance(rule, str) else rule
                for rule in rules
            ]
            idx_by_rules = (self.matrix()[:, rules, :].sum(axis=2) >= 0).sum(
                axis=1
            ) == len(rules)
        else:
            idx_by_rules = np.ones_like(self._records).astype(bool)

        # apply mask
        filtered_records = np.array(self._records)[idx_by_labels & idx_by_rules]

        return pd.DataFrame(map(lambda x: x.dict(), filtered_records))

    @_add_docstr(
        WeakLabelsBase.extend_matrix.__doc__.format(class_name="WeakMultiLabels")
    )
    def extend_matrix(
        self,
        thresholds: Union[List[float], np.ndarray],
        embeddings: Optional[np.ndarray] = None,
        gpu: bool = False,
    ):
        super().extend_matrix(thresholds=thresholds, embeddings=embeddings, gpu=gpu)

    def _extend_matrix_preprocess(self) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        abstains = [
            np.argwhere(self._matrix[:, i].sum(-1) < 0).flatten()
            for i in range(self._matrix.shape[1])
        ]

        supports = [
            np.argwhere(self._matrix[:, i].sum(-1) >= 0).flatten()
            for i in range(self._matrix.shape[1])
        ]

        return abstains, supports


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
