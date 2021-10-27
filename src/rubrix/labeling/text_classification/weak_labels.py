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
        rules: A list of rules (labeling functions).
        dataset: Name of the dataset.
        ids: An optional list of record ids to filter the dataset.
        query: An optional ElasticSearch query with the
            [query string syntax](https://rubrix.readthedocs.io/en/stable/reference/rubrix_webapp_reference.html#search-input)
            to filter the dataset.
        label2int: An optional dict, mapping the labels to integers.
            Use the string "None" to refer to the return type `None`.

    Example:
        >>> def awesome_rule(record: TextClassificationRecord) -> str:
        ...     return "Positive" if "awesome" in record.inputs["text"] else None
        >>> weak_labels = WeakLabels(rules=[awesome_rule], dataset="my_dataset")
        >>> weak_label_matrix = weak_labels.matrix
        >>> weak_labels.summary()
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

        self._records: List[TextClassificationRecord] = load(
            dataset, query=query, ids=ids, as_pandas=False
        )

        self._matrix, self._label2int = self._apply_rules(label2int)

    def _apply_rules(
        self, label2int: Optional[Dict[str, int]]
    ) -> Tuple[np.ndarray, Dict[str, int]]:
        """Apply the rules to the dataset.

        Args:
            label2int: An optional custom label2int mapping.

        Returns:
            The weak label matrix and its label2int mapping.
        """
        # call apply on the ElasticSearch rules
        for rule in tqdm(self._rules, desc="Preparing rules"):
            if isinstance(rule, Rule):
                rule.apply(self._dataset)

        # create weak label matrix
        weak_label_matrix = np.empty(
            (len(self._records), len(self._rules)), dtype=np.short
        )
        default_label2int = {"None": -1}

        for n, record in tqdm(
            enumerate(self._records), total=len(self._records), desc="Applying rules"
        ):
            for m, rule in enumerate(self._rules):
                weak_label = rule(record)
                if weak_label is None:
                    weak_label = "None"

                # If a label2int is defined we want to raise an error if the weak label is missing!
                if label2int is not None:
                    try:
                        weak_label = label2int[weak_label]
                    except KeyError as error:
                        raise KeyError(
                            f"A rule returned the weak label '{weak_label}', "
                            f"but it is missing in the `label2int` dict {label2int}."
                        ) from error
                else:
                    try:
                        weak_label = default_label2int[weak_label]
                    except KeyError:
                        # we already have "None" -> we need to subtract 1
                        default_label2int[weak_label] = len(default_label2int) - 1
                        weak_label = default_label2int[weak_label]

                weak_label_matrix[n, m] = weak_label

        return weak_label_matrix, label2int or default_label2int

    @property
    def records(self) -> List[TextClassificationRecord]:
        return self._records

    @property
    def label2int(self) -> Dict[str, int]:
        return self._label2int

    @property
    def matrix(self) -> np.ndarray:
        return self._matrix

    @property
    def train_matrix(self) -> np.ndarray:
        raise NotImplementedError

    @property
    def test_matrix(self) -> np.ndarray:
        raise NotImplementedError

    def annotation(self, pad: bool = False) -> np.ndarray:
        raise NotImplementedError

    def summary(self, annotation: np.ndarray) -> pd.DataFrame:
        """Return a summary of the rules given a weak label matrix.

        - coverage:
        - overlaps:
        - conflicts:
        - precision:

        Args:
            annotation: An optional array with ints holding the annotations.
                By default we will use `self.annotation(pad=True)`.

        Returns:
            A summary DataFrame with coverage, overlaps and conflicts of the rules.
            If the dataset contains annotated records, we also provide the precision of each rule.
        """
        raise NotImplementedError

    def bucket(self, labels: List[str], rules: List[int]) -> pd.DataFrame:
        raise NotImplementedError
