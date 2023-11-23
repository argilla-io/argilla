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

from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

import numpy as np

from argilla.client.feedback.schemas import RankingQuestion, TextQuestion
from argilla.client.feedback.schemas.enums import ResponseStatusFilter

if TYPE_CHECKING:
    from argilla.client.feedback.dataset import FeedbackDataset
    from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
    from argilla.client.feedback.metrics.base import Responses, Suggestions
    from argilla.client.feedback.schemas.enums import ResponseStatusFilter
    from argilla.client.feedback.schemas.records import SortBy


def get_responses_and_suggestions_per_user(
    dataset: Union["FeedbackDataset", "RemoteFeedbackDataset"],
    question_name: str,
    filter_by: Optional[Dict[str, Union["ResponseStatusFilter", List["ResponseStatusFilter"]]]] = None,
    sort_by: Optional[List["SortBy"]] = None,
    max_records: Optional[int] = None,
) -> Tuple[Dict[int, "Responses"], "Suggestions"]:
    """Extract the responses per user and the suggestions from a FeedbackDataset.

    Helper function for the metrics module where we want to compare the responses
    in relation to the suggestions offered.

    Args:
        dataset: FeedbackDataset or RemoteFeedbackDataset.
        question_name: The name of the question to filter from the dataset.
        filter_by: A dict with key the field to filter by, and values the filters to apply.
            Can be one of: draft, pending, submitted, and discarded. If set to None,
            no filter will be applied. Defaults to None (no filter is applied).
        sort_by: A list of `SortBy` objects to sort your dataset by.
            Defaults to None (no filter is applied).
        max_records: The maximum number of records to use for training. Defaults to None.

    Raises:
        NotImplementedError:
            When no user_id is given. We need that information to compute the metrics.

    Returns:
        Tuple containing the responses per user as a dict, with keys the user id and values the responses,
        and the suggestions.
    """
    if filter_by:
        dataset = dataset.filter_by(**filter_by)
    if sort_by:
        dataset = dataset.sort_by(sort_by)
    if max_records:
        dataset = dataset.pull(max_records=max_records)

    hf_dataset = dataset.format_as("datasets")
    question_type = type(dataset.question_by_name(question_name))
    responses_per_user = defaultdict(list)

    for responses_ in hf_dataset[question_name]:
        for response in responses_:
            user_id = response["user_id"]
            if user_id is None:
                raise NotImplementedError(
                    "In order to use this functionality the records need to be assigned to a user."
                )
            if question_type == RankingQuestion:
                value = response["value"]["rank"]
            else:
                value = response["value"]

            responses_per_user[user_id].append(value)

    suggestions = hf_dataset[f"{question_name}-suggestion"]
    if question_type == RankingQuestion:
        suggestions = [suggestion["rank"] for suggestion in suggestions]

    return responses_per_user, suggestions


def get_unified_responses_and_suggestions(
    dataset: Union["FeedbackDataset", "RemoteFeedbackDataset"],
    question_name: str,
    filter_by: Optional[Dict[str, Union["ResponseStatusFilter", List["ResponseStatusFilter"]]]] = None,
    sort_by: Optional[List["SortBy"]] = None,
    max_records: Optional[int] = None,
) -> Tuple["Responses", "Suggestions"]:
    """Extract the unified responses and the suggestions from a FeedbackDataset.

    Helper function for the metrics module where we want to compare the responses
    in relation to the suggestions offered.

    Args:
        dataset: FeedbackDataset or RemoteFeedbackDataset.
        question_name: The name of the question to filter from the dataset.
        filter_by: A dict with key the field to filter by, and values the filters to apply.
            Can be one of: draft, pending, submitted, and discarded. If set to None,
            no filter will be applied. Defaults to None (no filter is applied).
        sort_by: A list of `SortBy` objects to sort your dataset by.
            Defaults to None (no filter is applied).
        max_records: The maximum number of records to use for training. Defaults to None.

    Raises:
        NotImplementedError:
            When asked for a TextQuestion.
        ValueError:
            If the dataset hasn't been unified yet.

    Returns:
        Tuple containing the unified responses and the suggestions.
    """
    if filter_by:
        dataset = dataset.filter_by(**filter_by)
    if sort_by:
        dataset = dataset.sort_by(sort_by)
    if max_records:
        dataset = dataset.pull(max_records=max_records)

    question_type = type(dataset.question_by_name(question_name))
    if question_type == TextQuestion:
        raise NotImplementedError("This function is not available for `TextQuestion`.")

    unified_responses = []
    suggestions = []

    if not dataset.records[0].unified_responses:
        raise ValueError("Please unify the responses first: `dataset.compute_unified_responses(question, strategy)`.")

    # Get the position of the suggestion from the first record to avoid the nested loop,
    # and the type of the value to cast the unified responses.
    for idx_suggestion, suggestion in enumerate(dataset.records[0].suggestions):
        if suggestion.question_name == question_name:
            value_type = type(suggestion.value)
            break

    for record in dataset.records:
        unified_response = value_type(record.unified_responses[question_name][0].value)
        unified_responses.append(unified_response)
        suggestions.append(record.suggestions[idx_suggestion].value)

    if question_type == RankingQuestion:
        # TODO: Not ready yet
        map_rank_value = {rank_value["value"]: rank_value["rank"] for rank_value in suggestion.value}
        unified_responses = [map_rank_value[resp[0]] for resp in unified_responses]
        suggestions = [suggestion[0]["rank"] for suggestion in suggestions]

    return unified_responses, suggestions


def map_str_to_int(values: List[str]) -> List[int]:
    """Helper function to work with label questions as numerical values.

    Args:
        values: responses or suggestions with the string labels.

    Returns:
        values: corresponding values as integers to compute the metric
    """
    unique_values = np.unique(values)
    map_values = {value: i for i, value in enumerate(unique_values)}
    return [map_values[value] for value in values]


def is_multiclass(data) -> bool:
    """Helper function to check if a list of responses from LabelQuestion is also multiclass."""
    return len(np.unique(data)) > 2
