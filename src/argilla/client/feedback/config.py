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

from typing import List, Optional

from pydantic import BaseModel

from argilla.client.feedback.typing import AllowedFieldTypes, AllowedQuestionTypes


class FeedbackDatasetConfig(BaseModel):
    """`FeedbackDatasetConfig`

    Args:
        fields (List[AllowedFieldTypes]): The fields of the feedback dataset.
        questions (List[AllowedQuestionTypes]): The questions of the feedback dataset.
        guidelines (Optional[str]): the guidelines of the feedback dataset. Defaults to None.

    Examples:
        >>> import argilla as rg
        >>> config = rg.FeedbackDatasetConfig(
        ...     fields=[
        ...         rg.TextField(name="text", title="Human prompt"),
        ...     ],
        ...     questions =[
        ...         rg.TextQuestion(
        ...             name="question-1",
        ...             description="This is the first question",
        ...             required=True,
        ...         ),
        ...         rg.RatingQuestion(
        ...             name="question-2",
        ...             description="This is the second question",
        ...             required=True,
        ...             values=[1, 2, 3, 4, 5],
        ...         ),
        ...         rg.LabelQuestion(
        ...             name="relevant",
        ...             title="Is the response relevant for the given prompt?",
        ...             labels=["Yes","No"],
        ...             required=True,
        ...             visible_labels=None
        ...         ),
        ...         rg.MultiLabelQuestion(
        ...             name="content_class",
        ...             title="Does the response include any of the following?",
        ...             description="Select all that apply",
        ...             labels={"cat-1": "Category 1" , "cat-2": "Category 2"},
        ...             required=False,
        ...             visible_labels=4
        ...         ),
        ...     ],
        ...     guidelines="Add some guidelines for the annotation team here."
        ... )

    """

    fields: List[AllowedFieldTypes]
    questions: List[AllowedQuestionTypes]
    guidelines: Optional[str] = None

    class Config:
        smart_union = True
