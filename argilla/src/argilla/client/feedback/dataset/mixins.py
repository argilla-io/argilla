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
from typing import TYPE_CHECKING, Dict, List, Optional, Union

from argilla.client.feedback.dataset.base import FeedbackDatasetBase
from argilla.client.feedback.schemas.questions import (
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    TextQuestion,
)
from argilla.client.feedback.unification import (
    LabelQuestionStrategy,
    MultiLabelQuestionStrategy,
    RankingQuestionStrategy,
    RatingQuestionStrategy,
    TextQuestionStrategy,
)

if TYPE_CHECKING:
    from argilla.client.feedback.dataset.local.dataset import FeedbackDataset
    from argilla.client.feedback.metrics.agreement_metrics import AgreementMetricResult
    from argilla.client.feedback.metrics.annotator_metrics import ModelMetricResult


class MetricsMixin:
    """Mixin to add functionality to compute the metrics directly from a `FeedbackDataset`."""

    def compute_model_metrics(
        self,
        metric_names: Union[str, List[str]] = None,
        question_name: Union[
            str, LabelQuestion, MultiLabelQuestion, RatingQuestion, TextQuestion, RankingQuestion
        ] = None,
        strategy: Optional[
            Union[str, LabelQuestionStrategy, MultiLabelQuestion, RatingQuestionStrategy, RankingQuestion]
        ] = None,
    ) -> Union[Dict[str, List["ModelMetricResult"]], "ModelMetricResult", List["ModelMetricResult"]]:
        """Compute metrics for the annotators using the suggestions as the ground truth, and the responses
        as the predicted value, or if a strategy is provided, the same but applied to unified responses.

        The metric interpretation is the same whether the responses are unified or not.

        Args:
            metric_names: Metric name or list of metric names of the metrics, dependent on the question type.
            question_name: Question for which we want to compute the metrics.
            strategy: Unification strategy. If given, will unify the responses of the dataset and compute
                the metrics on the unified responses vs the suggestions instead on a per user level.
                See `unified_responses` method for more information. Defaults to None.

        Note:
            Currently, the following types of questions are supported:
            - For annotator level questions: all the types of questions
            - For unified responses: all the questions except the `TextQuestion`.

        Returns:
            metrics_container: If strategy is provided it will unify the annotations and return
                the metrics for the unified responses. Otherwise, it will return the metrics for
                each annotator as a dict, where the key corresponds to the annotator id and the
                values are a list with the metrics.
        """
        from argilla.client.feedback.metrics.annotator_metrics import ModelMetric, UnifiedModelMetric

        if strategy:
            self.compute_unified_responses(question_name, strategy)
            return UnifiedModelMetric(self, question_name).compute(metric_names)
        else:
            return ModelMetric(self, question_name).compute(metric_names)

    def compute_agreement_metrics(
        self,
        metric_names: Union[str, List[str]] = None,
        question_name: Union[str, LabelQuestion, MultiLabelQuestion, RatingQuestion, RankingQuestion] = None,
    ) -> Union["AgreementMetricResult", List["AgreementMetricResult"]]:
        """Compute agreement or reliability of annotation metrics.

        This metrics can be used to determine the level of agreement across our annotation team,
        or whether the guidelines are clear enough for example.

        Args:
            metric_names: Metric name or list of metric names of the metrics, dependent on the question type.
            question_name: Question for which we want to compute the metrics.

        Note:
            Currently, TextQuestion is not supported.

        Returns:
            metrics_result: Agreement metrics result or a list of metrics results if a list of metric
                names is provided.
        """
        from argilla.client.feedback.metrics.agreement_metrics import AgreementMetric

        return AgreementMetric(self, question_name).compute(metric_names)


class UnificationMixin:
    def unify_responses(
        self: "FeedbackDatasetBase",
        question: Union[str, LabelQuestion, MultiLabelQuestion, RatingQuestion],
        strategy: Union[
            str, LabelQuestionStrategy, MultiLabelQuestionStrategy, RatingQuestionStrategy, RankingQuestionStrategy
        ],
    ) -> "FeedbackDataset":
        warnings.warn(
            "`unify_responses` method is deprecated and will be removed in future releases. "
            "Please use `compute_unified_responses` instead.",
            DeprecationWarning,
        )
        return self.compute_unified_responses(question=question, strategy=strategy)

    def compute_unified_responses(
        self: "FeedbackDatasetBase",
        question: Union[str, LabelQuestion, MultiLabelQuestion, RatingQuestion],
        strategy: Union[
            str, LabelQuestionStrategy, MultiLabelQuestionStrategy, RatingQuestionStrategy, RankingQuestionStrategy
        ],
    ) -> "FeedbackDataset":
        """
        The `compute_unified_responses` function takes a question and a strategy as input and applies the strategy
        to unify the responses for that question.

        Args:
            question The `question` parameter can be either a string representing the name of the
                question, or an instance of one of the question classes (`LabelQuestion`, `MultiLabelQuestion`,
                `RatingQuestion`, `RankingQuestion`).
            strategy The `strategy` parameter is used to specify the strategy to be used for unifying
                responses for a given question. It can be either a string or an instance of a strategy class.
        """
        if isinstance(question, str):
            question = self.question_by_name(question)

        if not strategy:
            strategy = "majority"

        if isinstance(strategy, str):
            if isinstance(question, LabelQuestion):
                strategy = LabelQuestionStrategy(strategy)
            elif isinstance(question, MultiLabelQuestion):
                strategy = MultiLabelQuestionStrategy(strategy)
            elif isinstance(question, RatingQuestion):
                strategy = RatingQuestionStrategy(strategy)
            elif isinstance(question, RankingQuestion):
                strategy = RankingQuestionStrategy(strategy)
            elif isinstance(question, TextQuestion):
                strategy = TextQuestionStrategy(strategy)
            else:
                raise ValueError(f"Question {question} is not supported yet")

        strategy.compute_unified_responses(self.records, question)
        return self
