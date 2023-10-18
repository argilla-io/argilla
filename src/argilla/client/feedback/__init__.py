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

from argilla.client.feedback.training import (
    ArgillaTrainer,
    TrainingTask,
    TrainingTaskForDPO,
    TrainingTaskForPPO,
    TrainingTaskForRM,
    TrainingTaskForSFT,
    TrainingTaskForTextClassification,
    TrainingTaskForQuestionAnswering,
    TrainingTaskForChatCompletion,
    TrainingTaskForSentenceSimilarity,
    TrainingTaskMapping,  # <- Deprecated
    TrainingTaskMappingForTextClassification,  # <- Deprecated
)
from argilla.client.feedback.unification import (
    LabelQuestionStrategy,
    LabelQuestionUnification,
    MultiLabelQuestionStrategy,
    MultiLabelQuestionUnification,
    RankingQuestionStrategy,
    RankingQuestionUnification,
    RatingQuestionStrategy,
    RatingQuestionUnification,
    UnifiedValueSchema,
)

__all__ = [
    "ArgillaTrainer",
    "LabelQuestionStrategy",
    "MultiLabelQuestionStrategy",
    "RatingQuestionStrategy",
    "TrainingTask",
    "TrainingTaskForTextClassification",
    "TrainingTaskForSFT",
    "TrainingTaskForRM",
    "TrainingTaskForPPO",
    "TrainingTaskForDPO",
    "TrainingTaskMapping",
    "TrainingTaskMappingForTextClassification",
    "TrainingTaskForQuestionAnswering",
    "TrainingTaskForChatCompletion",
    "TrainingTaskForSentenceSimilarity",
    "RankingQuestionStrategy",
    "UnifiedValueSchema",
    "LabelQuestionUnification",
    "MultiLabelQuestionUnification",
    "RatingQuestionUnification",
    "RankingQuestionUnification",
]
