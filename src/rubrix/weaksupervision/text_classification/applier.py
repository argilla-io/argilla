#  coding=utf-8
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
from typing import Callable, Dict, List, Optional

import numpy as np
import pandas as pd
from tqdm.auto import tqdm

from rubrix import load
from rubrix.client.models import TextClassificationRecord
from rubrix.weaksupervision.text_classification.rule import Rule


class Applier:
    """Applies a list of rules to a dataset, and returns the weak label matrix.

    Args:
        rules: A list of rules (labeling functions).

    Example:
        >>> def awesome_rule(record: TextClassificationRecord) -> str:
        ...     return "Positive" if "awesome" in record.inputs["text"] else None
        >>> applier = Applier(rules=[awesome_rule])
        >>> weak_label_matrix = applier("my_dataset")
    """

    def __init__(self, rules: List[Callable]):
        self._rules = rules
        self._int2label = None

    def __call__(
        self,
        dataset: str,
        label2int: Optional[Dict[str, int]] = None,
        progress_bar: bool = True,
    ) -> np.array:
        """Compute the weak label matrix given a dataset.

        Args:
            dataset: Name of the dataset.
            label2int: An optional dict, mapping the labels to integers.
                Use the string "None" to refer to the return type `None`.
            progress_bar: If False, the progress bar is disabled.

        Returns:
            The weak labels in a `n x m` matrix (`n` is the number of records in the dataset, `m` the number of rules).
            If a `label2int` dict is provided, the matrix will contain integers, otherwise strings.
        """
        # get records
        records = load(dataset, return_pandas=False)

        # call apply on the ElasticSearch rules
        for rule in self._rules:
            if isinstance(rule, Rule):
                rule.apply(dataset)

        # create empty weak label matrix with appropriate dtype
        dtype = object
        if label2int is not None:
            dtype = np.short
        weak_label_matrix = np.empty((len(records), len(self._rules)), dtype=dtype)

        # fill weak label matrix
        for n, record in tqdm(
            enumerate(records),
            total=len(records),
            disable=None if progress_bar else True,
        ):
            for m, rule in enumerate(self._rules):
                weak_label = rule(record)
                if weak_label is None:
                    weak_label = "None"

                if label2int is not None:
                    try:
                        weak_label = label2int[weak_label]
                    except KeyError as error:
                        raise KeyError(
                            f"A rule returned the weak label '{weak_label}', "
                            f"but it is missing in the `label2int` dict."
                        ) from error

                weak_label_matrix[n, m] = weak_label

        # save int2label mapping for eventual `self.summary` call
        if label2int is not None:
            self._int2label = {integer: label for label, integer in label2int.items()}

        return weak_label_matrix

    def summary(
        self, weak_label_matrix: np.array, int2label: Optional[Dict[int, str]] = None
    ) -> pd.DataFrame:
        """Return a summary of the rules given a weak label matrix.

        - coverage:
        - overlaps:
        - conflicts:
        - precision:

        Args:
            weak_label_matrix: The weak label matrix, containing either strings or integers.
            int2label: An optional dict, mapping the integers of the weak label matrix to labels. If not provided and
                the weak label matrix contains integers, we will use the `label2int` mapping from the `applier()` call.

        Returns:
            A summary DataFrame with coverage, overlaps and conflicts of the rules.
            If the dataset contains annotated records, we also provide the precision of each rule.
        """
        raise NotImplementedError
