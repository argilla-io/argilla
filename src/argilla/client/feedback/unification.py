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

import random
from abc import abstractmethod
from collections import Counter
from enum import Enum
from typing import Any, Dict, List, Union

from pydantic import BaseModel, root_validator, validator

from argilla.client.feedback.schemas import (
    FeedbackRecord,
    LabelQuestion,
    MultiLabelQuestion,
    RatingQuestion,
    ValueSchema,
)


class UnifiedValueSchema(ValueSchema):
    """A value schema for a unification value.

    Args:
        value (Union[StrictStr, StrictInt, List[str]]): The unification value of the record.
        strategy (Literal["mean", "majority", "max", "min"]): The strategy to unify the responses. Defaults to "majority".

    Examples:
        >>> import argilla as rg
        >>> value = rg.UnifiedValueSchema(value="Yes", strategy="majority")
        >>> # or use a dict
        >>> value = {"value": "Yes", "strategy": "majority"}
    """

    strategy: Union["RatingQuestionStrategy", "LabelQuestionStrategy", "MultiLabelQuestionStrategy"]


class RatingQuestionStrategy(Enum):
    """
    Options:
        - "mean": the mean value of the ratings
        - "majority": the majority value of the ratings
        - "max": the max value of the ratings
        - "min": the min value of the ratings
    """

    MEAN: str = "mean"
    MAJORITY: str = "majority"
    MAX: str = "max"
    MIN: str = "min"

    def unify_responses(self, records: List[FeedbackRecord], question: RatingQuestion):
        UnifiedValueSchema.update_forward_refs()
        # check if field is a str or a RatingQuestion
        if isinstance(question, str):
            pass
        elif isinstance(question, RatingQuestion):
            question = question.name
        else:
            raise ValueError("Invalid field type. Must be a str or RatingQuestion")
        # choose correct unification method
        if self.value == self.MAJORITY.value:
            return self._majority(records, question)
        else:
            return self._aggregate(records, question)

    def _aggregate(self, records: List[FeedbackRecord], question: str):
        for rec in records:
            if not rec.responses:
                continue
            # only allow for submitted responses
            responses = [resp for resp in rec.responses if resp.status == "submitted"]
            # get responses with a value that is most frequent
            ratings = []
            for resp in responses:
                if question in resp.values:
                    ratings.append(int(resp.values[question].value))
            if not ratings:
                continue
            # unified response
            if self.value == self.MEAN.value:
                unified_value = str(int(sum(ratings) / len(ratings)))
            elif self.value == self.MAX.value:
                unified_value = str(max(ratings))
            elif self.value == self.MIN.value:
                unified_value = str(min(ratings))
            else:
                raise ValueError("Invalid aggregation method")
            rec._unified_responses[question] = [UnifiedValueSchema(value=unified_value, strategy=self.value)]
        return records

    def _majority(self, records: List[FeedbackRecord], question: str):
        for rec in records:
            if not rec.responses:
                continue
            counter = Counter()
            # only allow for submitted responses
            responses = [resp for resp in rec.responses if resp.status == "submitted"]
            # get responses with a value that is most frequent
            for resp in responses:
                if question in resp.values:
                    counter.update([resp.values[question].value])
            if not counter.values():
                continue
            # Find the maximum count
            max_count = max(counter.values())
            # Get a list of values with the maximum count
            most_common_values = [value for value, count in counter.items() if count == max_count]
            if len(most_common_values) > 1:
                majority_value = random.choice(most_common_values)
            else:
                majority_value = counter.most_common(1)[0][0]
            rec._unified_responses[question] = [UnifiedValueSchema(value=majority_value, strategy=self.value)]
        return records


class LabelQuestionStrategyMixin:
    def unify_responses(self, records: List[FeedbackRecord], question: Union[str, LabelQuestion, MultiLabelQuestion]):
        UnifiedValueSchema.update_forward_refs()
        # check if field is a str or a LabelQuestion
        if isinstance(question, (LabelQuestion, MultiLabelQuestion)):
            question = question.name
        elif isinstance(question, str):
            pass
        else:
            raise ValueError("Invalid field type. Must be a str, LabelQuestion, MultiLabelQuestion")
        # choose correct unification method
        if self.value == self.MAJORITY.value:
            return self._majority(records, question)
        elif self.value == self.MAJORITY_WEIGHTED.value:
            return self._majority_weighted(records, question)
        elif self.value == self.DISAGREEMENT.value:
            return self._disagreement(records, question)

    @abstractmethod
    def _majority(self, records: List[FeedbackRecord], question: str):
        """Must be implemented by subclasses"""

    @abstractmethod
    def _majority_weighted(self, records: List[FeedbackRecord], question: str):
        """Must be implemented by subclasses"""

    def _disagreement(self, records: List[FeedbackRecord], question: str):
        unified_records = []
        for rec in records:
            if not rec.responses:
                continue
            # only allow for submitted responses
            responses = [resp for resp in rec.responses if resp.status == "submitted"]
            # get responses with a value that is most frequent
            if question not in rec._unified_responses:
                rec._unified_responses[question] = []
            for resp in responses:
                if question not in resp.values:
                    continue
                else:
                    rec._unified_responses[question].append(
                        UnifiedValueSchema(value=resp.values[question].value, strategy=self.value)
                    )
        return unified_records


class LabelQuestionStrategy(LabelQuestionStrategyMixin, Enum):
    """
    Options:
        - "majority": the majority value of the labels
        - "majority_weighted": the majority value of the labels, weighted by annotator's confidence
        - "disagreement": preserve the natural disagreement between annotators

    Examples:
        >>> from argilla import LabelQuestion, LabelQuestionStrategy
        >>> strategy = LabelQuestionStrategy("majority")
        >>> records = strategy.unify_responses(records, question=LabelQuestion(...))
    """

    MAJORITY: str = "majority"
    MAJORITY_WEIGHTED: str = "majority_weighted"
    DISAGREEMENT: str = "disagreement"

    def _majority(self, records: List[FeedbackRecord], question: str):
        for rec in records:
            if not rec.responses:
                continue
            counter = Counter()
            # only allow for submitted responses
            responses = [resp for resp in rec.responses if resp.status == "submitted"]
            # get responses with a value that is most frequent
            for resp in responses:
                if question in resp.values:
                    counter.update([resp.values[question].value])
            if not counter.values():
                continue
            # Find the maximum count
            max_count = max(counter.values())
            # Get a list of values with the maximum count
            most_common_values = [value for value, count in counter.items() if count == max_count]
            if len(most_common_values) > 1:
                majority_value = random.choice(most_common_values)
            else:
                majority_value = counter.most_common(1)[0][0]

            rec._unified_responses[question] = [UnifiedValueSchema(value=majority_value, strategy=self.value)]
        return rec

    @classmethod
    def _majority_weighted(self, records: List[FeedbackRecord], question: LabelQuestion):
        raise NotImplementedError("'majority_weighted'-strategy not implemented yet")


class MultiLabelQuestionStrategy(LabelQuestionStrategyMixin, Enum):
    """
    Options:
        - "majority": the majority value of the labels
        - "majority_weighted": the majority value of the labels, weighted by annotator's confidence
        - "disagreement": preserve the natural disagreement between annotators
    """

    MAJORITY: str = "majority"
    MAJORITY_WEIGHTED: str = "majority_weighted"
    DISAGREEMENT: str = "disagreement"

    def _majority(self, records: List[FeedbackRecord], question: str):
        for rec in records:
            if not rec.responses:
                continue
            counter = Counter()
            # only allow for submitted responses
            responses = [resp for resp in rec.responses if resp.status == "submitted"]
            # get responses with a value that is most frequent
            for resp in responses:
                if isinstance(resp.values[question].value, list):
                    for value in resp.values[question].value:
                        counter.update([value])
                else:
                    counter.update([resp.values[question].value])
            # check if there is a majority based on the number of responses
            majority = int(len(responses) // 2) + 1
            majority_value = []
            for value, count in counter.items():
                if count >= majority:
                    majority_value.append(value)

            rec._unified_responses[question] = [UnifiedValueSchema(value=majority_value, strategy=self.value)]
        return records

    @classmethod
    def _majority_weighted(self, records: List[FeedbackRecord], question: MultiLabelQuestion):
        raise NotImplementedError("'majority_weighted'-strategy not implemented yet")


class RatingQuestionUnification(BaseModel):
    """Rating unification for a rating question

    Args:
        question (RatingQuestion): rating question
        strategy (Union[str, RatingQuestionStrategy]): unification strategy. Defaults to "mean".
            mean (str): the mean value of the ratings.
            majority (str): the majority value of the ratings.
            max (str): the max value of the ratings
            min (str): the min value of the ratings

    Examples:
        >>> from argilla import RatingQuestion, RatingUnification, RatingQuestionStrategy
        >>> RatingUnification(question=RatingQuestion(...), strategy="mean")
        >>> # or use a RatingQuestionStrategy
        >>> RatingUnification(question=RatingQuestion(...), strategy=RatingQuestionStrategy.MEAN)
    """

    question: RatingQuestion
    strategy: Union[str, RatingQuestionStrategy] = "mean"

    @validator("strategy", always=True)
    def strategy_must_be_valid(cls, v: Union[str, RatingQuestionStrategy]) -> RatingQuestionStrategy:
        if isinstance(v, str):
            return RatingQuestionStrategy(v)
        return v


class LabelQuestionUnification(BaseModel):
    """Label unification for a label question

    Args:
        question (Union[LabelQuestion, MultiLabelQuestion]): label question
        strategy (Union[str, LabelQuestionStrategy, MultiLabelQuestionStrategy]): unification strategy. Defaults to "majority".
            majority (str): the majority value of the labels
            majority_weighted (str): the majority value of the labels, weighted by annotator's confidence
            disagreement (str): preserve the natural disagreement between annotators

    Examples:
        >>> from argilla import LabelQuestion, LabelUnification, LabelQuestionStrategy
        >>> LabelUnification(question=LabelQuestion(...), strategy="majority")
        >>> # or use a LabelQuestionStrategy
        >>> LabelUnification(question=LabelQuestion(...), strategy=LabelQuestionStrategy.MAJORITY)
    """

    question: Union[LabelQuestion, MultiLabelQuestion]
    strategy: Union[str, LabelQuestionStrategy, MultiLabelQuestionStrategy] = "majority"

    def unify_responses(self, records: List[FeedbackRecord]):
        return self.strategy.unify_responses(records, self.question)

    @root_validator
    def strategy_must_be_valid_and_align_with_question(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        strategy = values.get("strategy", "majority")
        question = values.get("question")
        if isinstance(question, LabelQuestion):
            if isinstance(strategy, str):
                strategy = LabelQuestionStrategy(strategy)
            if strategy.value in LabelQuestionStrategy.__members__:
                raise ValueError(f"Only LabelQuestionStrategy is compatible with LabelQuestion not {strategy}")
        elif isinstance(question, MultiLabelQuestion):
            if isinstance(strategy, str):
                strategy = MultiLabelQuestionStrategy(strategy)
            if strategy.value in MultiLabelQuestionStrategy.__members__:
                raise ValueError(
                    f"Only MultiLabelQuestionStrategy is compatible with MultiLabelQuestion not {strategy}"
                )
        values["strategy"] = strategy
        return values


MultiLabelQuestionUnification = LabelQuestionUnification
