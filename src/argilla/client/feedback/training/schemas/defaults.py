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

from typing import List, Optional, Union

from argilla.client.feedback.schemas import (
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    TextField,
    TextQuestion,
)
from argilla.client.feedback.unification import (
    LabelQuestionUnification,
    MultiLabelQuestionUnification,
    RankingQuestionUnification,
    RatingQuestionUnification,
)
from argilla.pydantic_v1 import BaseModel


class TextClassificationDefaults(BaseModel):
    text: Optional[TextField] = None
    label: Optional[
        Union[
            RatingQuestion,
            LabelQuestion,
            MultiLabelQuestion,
            RankingQuestion,
            LabelQuestionUnification,
            MultiLabelQuestionUnification,
            RankingQuestionUnification,
            RatingQuestionUnification,
        ]
    ] = None


class QuestionAnsweringDefaults(BaseModel):
    question: TextField
    context: TextField
    answer: TextQuestion


class SentenceSimilarityDefaults(BaseModel):
    texts: Optional[List[TextField]] = None
    label: Optional[Union[LabelQuestion, RatingQuestion, LabelQuestionUnification, RankingQuestionUnification]] = None
