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
from typing import TYPE_CHECKING, Dict, List, Tuple, Union

import numpy as np

from argilla.client.feedback.schemas import RankingQuestion
from argilla.client.feedback.schemas.enums import ResponseStatusFilter

if TYPE_CHECKING:
    from argilla.client.feedback.dataset import FeedbackDataset
    from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
    from argilla.client.feedback.metrics.base import Responses, Suggestions


def get_responses_and_suggestions_per_user(
    dataset: Union["FeedbackDataset", "RemoteFeedbackDataset"],
    question_name: str,
    response_status: str = ResponseStatusFilter.submitted.value,
) -> Tuple[Dict[int, "Responses"], "Suggestions"]:
    """Extract the responses per user and the suggestions from a FeedbackDataset.

    Helper function for the metrics module where we want to compare the responses
    in relation to the suggestions offered.

    Args:
        dataset: FeedbackDataset or RemoteFeedbackDataset.
        question_name: The name of the question to filter from the dataset.
        response_status: The responses status for the responses. Defaults to "submitted".

    Raises:
        NotImplementedError:
            When no user_id is given. We need that information to compute the metrics.

    Returns:
        Tuple containing the responses per user as a dict, with keys the user id and values the responses,
        and the suggestions.
    """
    dataset = dataset.filter_by(response_status=response_status)

    hf_dataset = dataset.format_as("datasets")
    question_type = type(dataset.question_by_name(question_name))
    responses_per_user = defaultdict(list)

    for responses_ in hf_dataset[question_name]:
        for response in responses_:
            # We do this check here because local datasets don't implement the filter_by method.
            if response["status"] != response_status:
                continue
            user_id = response["user_id"]
            if user_id is None:
                raise NotImplementedError(
                    "In order to use this functionality the records need to be assigned to a user."
                )
            if question_type == RankingQuestion:
                value = response["value"]["value"]
            else:
                value = response["value"]

            responses_per_user[user_id].append(value)

    suggestions = hf_dataset[f"{question_name}-suggestion"]
    if question_type == RankingQuestion:
        suggestions = [suggestion["value"] for suggestion in suggestions]

    return responses_per_user, suggestions


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
