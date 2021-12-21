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
from enum import Enum
from typing import Dict, List, Tuple, Union

import numpy as np

from rubrix.client.models import TextClassificationRecord

_LOGGER = logging.getLogger(__name__)


class SortBy(Enum):
    """A sort by strategy"""

    LIKELIHOOD = "likelihood"
    PREDICTION = "prediction"
    NONE = "none"

    @classmethod
    def _missing_(cls, value):
        raise ValueError(
            f"{value} is not a valid {cls.__name__}, please select one of {list(cls._value2member_map_.keys())}"
        )


def find_label_errors(
    records: List[TextClassificationRecord],
    sort_by: Union[str, SortBy] = "likelihood",
    metadata_key: str = "label_error_candidate",
    **kwargs,
) -> List[TextClassificationRecord]:
    """Finds potential annotation/label errors in your records using [cleanlab](https://github.com/cleanlab/cleanlab).

    We will consider all records for which a prediction AND annotation is available. Make sure the predictions were made
    in a holdout manner, that is you should only include records that were not used in the training of the predictor.

    Args:
        records: A list of text classification records
        sort_by: One of the three options
            - "likelihood": sort the returned records by likelihood of containing a label error (most likely first)
            - "prediction": sort the returned records by the probability of the prediction (highest probability first)
            - "none": do not sort the returned records
        metadata_key: The key added to the record's metadata that holds the order, if ``sort_by`` is not "none".
        **kwargs: Passed on to `cleanlab.pruning.get_noise_indices`

    Returns:
        A list of records containing potential annotation/label errors

    Raises:
        NoRecordsError: If none of the records has a prediction AND annotation.
        MissingPredictionError: If a prediction is missing for one of the labels.
        ValueError: If not supported kwargs are passed on, e.g. 'sorted_index_method'.

    Examples:
        >>> import rubrix as rb
        >>> records = rb.load("my_dataset", as_pandas=False)
        >>> records_with_label_errors = find_label_errors(records)
    """
    try:
        import cleanlab
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            "'cleanlab' must be installed to use the `find_label_errors` method! "
            "You can install 'cleanlab' with the command: `pip install cleanlab`"
        )
    else:
        from cleanlab.pruning import get_noise_indices

    if isinstance(sort_by, str):
        sort_by = SortBy(sort_by)

    # select only records with prediction and annotation
    records = [rec for rec in records if rec.prediction and rec.annotation]
    if not records:
        raise NoRecordsError(
            "It seems that none of your records have a prediction AND annotation!"
        )

    # check and update kwargs for get_noise_indices
    _check_and_update_kwargs(records[0], sort_by, kwargs)

    # construct "noisy" label vector and probability matrix of the predictions
    s, psx = _construct_s_and_psx(records)

    indices = get_noise_indices(s, psx, **kwargs)

    records_with_label_errors = np.array(records)[indices].tolist()

    # add metadata
    if sort_by is not SortBy.NONE:
        for i, rec in enumerate(records_with_label_errors):
            rec.metadata[metadata_key] = i

    return records_with_label_errors


def _check_and_update_kwargs(
    record: TextClassificationRecord, sort_by: SortBy, kwargs: Dict
):
    """Helper function to check and update the kwargs passed on to cleanlab's `get_noise_indices`.

    Args:
        record: One of the records passed in the `find_label_error` function.
        sort_by: The sorting policy.
        kwargs: The passed on kwargs.

    Raises:
        ValueError: If not supported kwargs ('sorted_index_method') are passed on.
    """
    if "sorted_index_method" in kwargs:
        raise ValueError(
            "The 'sorted_index_method' kwarg is not supported, please use 'sort_by' instead."
        )
    kwargs["sorted_index_method"] = "normalized_margin"
    if sort_by is SortBy.PREDICTION:
        kwargs["sorted_index_method"] = "prob_given_label"
    elif sort_by is SortBy.NONE:
        kwargs["sorted_index_method"] = None

    if "multi_label" in kwargs:
        _LOGGER.warning(
            "You provided the kwarg 'multi_label', but it is determined automatically. "
            f"We will set it to '{record.multi_label}'."
        )
    kwargs["multi_label"] = record.multi_label


def _construct_s_and_psx(
    records: List[TextClassificationRecord],
) -> Tuple[np.ndarray, np.ndarray]:
    """Helper function to construct the s array and psx matrix.

    Args:
        records: List of records.

    Returns:
        A tuple containing the s array and the psx matrix.

    Raises:
        MissingPredictionError: If predictions are missing for certain labels.
    """
    predictions = []
    labels = set()  # use a dict to preserve the order
    for rec in records:
        predictions.append({pred[0]: pred[1] for pred in rec.prediction})
        labels.update(predictions[-1].keys())
    labels_mapping = {label: i for i, label in enumerate(sorted(labels))}

    s = (
        np.empty(len(records), dtype=object)
        if records[0].multi_label
        else np.zeros(len(records), dtype=np.short)
    )
    psx = np.zeros((len(records), len(labels)), dtype=np.float)

    for i, rec, pred in zip(range(len(records)), records, predictions):
        try:
            psx[i] = [pred[label] for label in labels_mapping]
        except KeyError as error:
            raise MissingPredictionError(
                f"It seems a prediction for {error} is missing in the following record: {rec}"
            )

        try:
            s[i] = (
                [labels_mapping[label] for label in rec.annotation]
                if rec.multi_label
                else labels_mapping[rec.annotation]
            )
        except KeyError as error:
            raise MissingPredictionError(
                f"It seems predictions are missing for the label {error}!"
            )

    return s, psx


class LabelErrorsException(Exception):
    pass


class NoRecordsError(LabelErrorsException):
    pass


class MissingPredictionError(LabelErrorsException):
    pass
