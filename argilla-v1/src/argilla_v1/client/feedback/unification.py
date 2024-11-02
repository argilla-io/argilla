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

import pandas as pd

from argilla_v1.client.feedback.schemas import (
    FeedbackRecord,
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    ValueSchema,
)
from argilla_v1.pydantic_v1 import BaseModel, root_validator, validator


class UnifiedValueSchema(ValueSchema):
    """A value schema for a unification value.

    Args:
        value (Union[StrictStr, StrictInt, List[str]]): The unification value of the record.
        strategy (Literal["mean", "majority", "max", "min"]): The strategy to unify the responses. Defaults to "majority".

    Examples:
        >>> import argilla_v1 as rg
        >>> value = rg.UnifiedValueSchema(value="Yes", strategy="majority")
        >>> # or use a dict
        >>> value = {"value": "Yes", "strategy": "majority"}
    """

    strategy: Union[
        "RatingQuestionStrategy", "LabelQuestionStrategy", "MultiLabelQuestionStrategy", "RankingQuestionStrategy"
    ]


class RatingQuestionStrategyMixin:
    def compute_unified_responses(
        self, records: List[FeedbackRecord], question: Union["RatingQuestionStrategy", "RankingQuestionStrategy"]
    ):
        """
        The function `compute_unified_responses` takes a list of feedback records and a rating question, and
        returns a unified value based on the specified unification method.

        Args:
        - records The `records` parameter is a list of `FeedbackRecord` objects. Each
            `FeedbackRecord` object represents a feedback response and contains information such as the
            respondent's name, the question being answered, and the response value.
        - question The `question` parameter is the question for which you want to unify the
            responses. It can be either a string or a `RatingQuestion` object. If it is a string, it
            represents the name of the question. If it is a `RatingQuestion` object, it represents the
            actual question

        Returns:
        The method `compute_unified_responses` returns the result of either the `_majority` or
        `_aggregate` method, depending on the value of `self.value`.
        """
        UnifiedValueSchema.update_forward_refs()
        # check if field is a str or a RatingQuestion
        if isinstance(question, str):
            pass
        elif isinstance(question, (RatingQuestion, RankingQuestion)):
            question = question.name
        else:
            raise ValueError(f"Invalid field type. Must be a str or {type(self).__name__}")
        # choose correct unification method
        if self.value == self.MAJORITY.value:
            return self._majority(records, question)
        else:
            return self._aggregate(records, question)


class RatingQuestionStrategy(RatingQuestionStrategyMixin, Enum):
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

    def compute_unified_responses(self, records: List[FeedbackRecord], question: RatingQuestion):
        return super().compute_unified_responses(records, question)

    def _aggregate(self, records: List[FeedbackRecord], question: str):
        """
        The function `_aggregate` takes a list of feedback records and a question, and aggregates the
        responses for that question using a specified method (mean, max, or min) and returns the updated
        records.

        Args:
        - records The `records` parameter is a list of `FeedbackRecord` objects. Each
            `FeedbackRecord` object represents a feedback submission and contains information about the
            responses given by the user.
        - question The "question" parameter in the code represents the specific question or
            attribute for which the feedback records need to be aggregated. It is a string that identifies
            the question or attribute being considered.

        Returns: the updated list of feedback records with the unified responses for the specified
        question.
        """
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


class TextQuestionStrategy(Enum):
    """
    The TextQuestionStrategy class is an enumeration class that represents the different strategies.add()
    Options:
        - "disagreement": preserve the natural disagreement between annotators
    """

    DISAGREEMENT = "disagreement"

    def compute_unified_responses(self, records: List[FeedbackRecord], question: str):
        UnifiedValueSchema.update_forward_refs()
        unified_records = []
        for rec in records:
            if not rec.responses:
                continue
            # only allow for submitted responses
            responses = [resp for resp in rec.responses if resp.status == "submitted"]
            # get responses with a value that is most frequent
            if question.name not in rec._unified_responses:
                rec._unified_responses[question.name] = []
            for resp in responses:
                if question.name not in resp.values:
                    continue
                else:
                    rec._unified_responses[question.name] = UnifiedValueSchema(
                        value=resp.values[question.name].value, strategy=self.value
                    )
                unified_records.append(rec)

        return unified_records


class RankingQuestionStrategy(RatingQuestionStrategyMixin, Enum):
    """
    Options:
        - "majority": the majority value of the rankings
        - "max": the max value of the rankings
        - "min": the min value of the rankings
    """

    MEAN: str = "mean"
    MAJORITY: str = "majority"
    MAX: str = "max"
    MIN: str = "min"

    def compute_unified_responses(self, records: List[FeedbackRecord], question: RankingQuestion):
        return super().compute_unified_responses(records, question)

    def _aggregate(self, records: List[FeedbackRecord], question: str):
        """
        The function `_aggregate` takes a list of `FeedbackRecord` objects and a question, and
        aggregates the responses for that question based on a specified aggregation method.

        Args:
        - records The `records` parameter is a list of `FeedbackRecord` objects. Each
        `FeedbackRecord` object represents a feedback record and contains information about the
        responses given for a particular feedback.
        - question The `question` parameter in the `_aggregate` method is a string that represents
        the question for which the responses are being aggregated.

        Returns:
        the updated list of FeedbackRecord objects after aggregating the responses for the
        specified question.
        """
        if self.value == self.MEAN.value:
            return self._mean(records, question)

        for rec in records:
            if not rec.responses:
                continue
            # only allow for submitted responses
            responses = [resp for resp in rec.responses if resp.status == "submitted"]
            # get responses with a value that is most frequent
            total_values = []
            total_ranks = []
            for resp in responses:
                if question in resp.values:
                    values = []
                    ranks = []
                    for value in resp.values[question].value:
                        values.append(value.value)
                        ranks.append(value.rank)

                    total_values.append(tuple(values))
                    total_ranks.append(tuple(ranks))

            if not total_values:
                continue
            df = pd.DataFrame({"value": total_values, "rank": total_ranks})

            # unified response
            if self.value == self.MAX.value:
                df = df[df["rank"] == df["rank"].max()]
            elif self.value == self.MIN.value:
                df = df[df["rank"] == df["rank"].min()]
            else:
                raise ValueError("Invalid aggregation method")

            if len(df) > 0:
                # Extract the first of the possible values (in case there is more than one).
                unified_rank = [{"rank": item[1], "value": item[0]} for item in zip(*df.iloc[0].to_list())]
                rec._unified_responses[question] = [UnifiedValueSchema(value=unified_rank, strategy=self.value)]

        return records

    def _mean(self, records: List[FeedbackRecord], question: str):
        """
        The function `_mean` takes a list of `FeedbackRecord` objects and a question, and
        aggregates the responses for that question based on the average of the ranks.

        Args:
        - records The `records` parameter is a list of `FeedbackRecord` objects. Each
        `FeedbackRecord` object represents a feedback record and contains information about the
        responses given for a particular feedback.
        - question The `question` parameter in the `_aggregate` method is a string that represents
        the question for which the responses are being aggregated.

        Returns:
        the updated list of FeedbackRecord objects after aggregating the responses for the
        specified question.
        """
        from collections import defaultdict

        UnifiedValueSchema.update_forward_refs()

        for rec in records:
            if not rec.responses:
                continue
            # only allow for submitted responses
            responses = [resp for resp in rec.responses if resp.status == "submitted"]
            # Step 1: Create an empty dictionary to store cumulative ranks and counts
            cumulative_ranks = defaultdict(lambda: {"sum": 0, "count": 0})

            # Step 2: Iterate through each ranking and update cumulative ranks and counts
            for resp in responses:
                if question in resp.values:
                    for item in resp.values[question].value:
                        value = item.value
                        rank = item.rank
                        cumulative_ranks[value]["sum"] += rank
                        cumulative_ranks[value]["count"] += 1

            # Step 3: Calculate the average rank for each response
            average_ranking = [
                {"rank": round(cumulative_ranks[value]["sum"] / cumulative_ranks[value]["count"]), "value": value}
                for value in cumulative_ranks
            ]

            # Step 4: Create a new list representing the average ranking
            average_ranking = sorted(average_ranking, key=lambda x: x["rank"])
            rec._unified_responses[question] = [UnifiedValueSchema(value=average_ranking, strategy=self.value)]

        return records

    def _majority(self, records: List[FeedbackRecord], question: str):
        """
        The `_majority` function calculates the majority value for a given question based on the
        responses in a list of feedback records.

        Args:
        - records The `records` parameter is a list of `FeedbackRecord` objects. Each
        `FeedbackRecord` object represents a feedback record and contains information such as the
        responses given by the user.
        - question The "question" parameter in the code represents the specific question for which
        you want to determine the majority value. It is a string that identifies the question in the
        feedback records.

        Returns:
        The updated list of FeedbackRecord objects, with the "_unified_responses" attribute of
        each record updated for the specified question.
        """
        UnifiedValueSchema.update_forward_refs()
        for rec in records:
            if not rec.responses:
                continue
            counter = Counter()
            # only allow for submitted responses
            responses = [resp for resp in rec.responses if resp.status == "submitted"]
            # get responses with a value that is most frequent
            ranks = []
            for resp in responses:
                if question in resp.values:
                    rank_per_response = []
                    for value in resp.values[question].value:
                        rank_per_response.append((value.rank, value.value))
                    ranks.append(tuple(rank_per_response))

            counter.update(ranks)
            if not counter.values():
                continue
            # Find the maximum count
            max_count = max(counter.values())
            # Get a list of values with the maximum count
            most_common_values = [value for value, count in counter.items() if count == max_count]
            if len(most_common_values) > 1:
                majority_value = random.choice(most_common_values)
            else:
                majority_value = counter.most_common()[0][0]

            # Recreate the final ranking
            majority_rank = [{"rank": item[0], "value": item[1]} for item in majority_value]
            rec._unified_responses[question] = [UnifiedValueSchema(value=majority_rank, strategy=self.value)]

        return records


class LabelQuestionStrategyMixin:
    def compute_unified_responses(
        self, records: List[FeedbackRecord], question: Union[str, LabelQuestion, MultiLabelQuestion]
    ):
        """
        The function `compute_unified_responses` takes a list of feedback records and a question, and returns a
        unified value based on the specified unification method.

        Args:
        - records `records` is a list of `FeedbackRecord` objects. Each `FeedbackRecord` represents
        a feedback response and contains information such as the respondent's ID, the question being
        answered, and the response value.
        - question The `question` parameter can be either a string, a `LabelQuestion` object, or a
        `MultiLabelQuestion` object. It represents the question for which you want to unify the
        responses.

        Returns: The method `compute_unified_responses` returns the result of one of the following methods:
        `_majority`, `_majority_weighted`, or `_disagreement`. The specific method that is called
        depends on the value of `self.value`.
        """
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
        """
        The function `_disagreement` takes a list of `FeedbackRecord` objects and a question as input,
        and returns a list of unified records based on the most frequent responses for that question.

        Args:
        - records The "records" parameter is a list of FeedbackRecord objects. Each FeedbackRecord
        object represents a feedback record and contains information about the responses given by a
        user.
        - question The "question" parameter is a string that represents the specific question for
        which you want to unify the responses.

        Returns: a list of unified records.
        """
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
        >>> from argilla_v1 import LabelQuestion, LabelQuestionStrategy
        >>> strategy = LabelQuestionStrategy("majority")
        >>> records = strategy.compute_unified_responses(records, question=LabelQuestion(...))
    """

    MAJORITY: str = "majority"
    MAJORITY_WEIGHTED: str = "majority_weighted"
    DISAGREEMENT: str = "disagreement"

    def _majority(self, records: List[FeedbackRecord], question: str):
        """
        The function `_majority` takes a list of feedback records and a question, and determines the
        majority value for that question based on the submitted responses.

        Args:
        - records The `records` parameter is a list of `FeedbackRecord` objects. Each
        `FeedbackRecord` object represents a feedback record and contains information about the
        responses given by a user.
        - question The "question" parameter is a string that represents the specific question for
        which you want to determine the majority value.

        Returns: a modified version of the input `FeedbackRecord` object.
        """
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
    def _majority_weighted(cls, records: List[FeedbackRecord], question: LabelQuestion):
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
        """
        The `_majority` function calculates the majority value for a given question based on the
        submitted responses in a list of feedback records.

        Args:
        - records The `records` parameter is a list of `FeedbackRecord` objects. Each
        `FeedbackRecord` object represents a feedback record and contains information about the
        responses given by a user.
        - question The "question" parameter in the code represents the specific question for which
        you want to determine the majority response. It is a string that identifies the question.

        Returns: the updated list of FeedbackRecord objects with the "_unified_responses" attribute
        updated for each record.
        """
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

            if not majority_value:
                majority_value = [random.choice(list(counter.keys()))]

            rec._unified_responses[question] = [UnifiedValueSchema(value=list(majority_value), strategy=self.value)]
        return records

    @classmethod
    def _majority_weighted(cls, records: List[FeedbackRecord], question: MultiLabelQuestion):
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
        >>> from argilla_v1 import RatingQuestion, RatingQuestionUnification, RatingQuestionStrategy
        >>> RatingQuestionUnification(question=RatingQuestion(...), strategy="mean")
        >>> # or use a RatingQuestionStrategy
        >>> RatingQuestionUnification(question=RatingQuestion(...), strategy=RatingQuestionStrategy.MEAN)
    """

    question: RatingQuestion
    strategy: Union[str, RatingQuestionStrategy] = "mean"

    @validator("strategy", always=True)
    def strategy_must_be_valid(cls, v: Union[str, RatingQuestionStrategy]) -> RatingQuestionStrategy:
        if isinstance(v, str):
            return RatingQuestionStrategy(v)
        return v


class RankingQuestionUnification(BaseModel):
    """Ranking unification for a ranking question

    Args:
        question (RankingQuestion): ranking question
        strategy (Union[str, RankingQuestionStrategy]): unification strategy. Defaults to "majority".
            mean (str): the mean value of the ratings.
            majority (str): the majority value of the ratings.
            max (str): the max value of the ratings
            min (str): the min value of the ratings

    Examples:
        >>> from argilla_v1 import RankingQuestionUnification, RankingQuestionStrategy, RankingQuestion
        >>> RankingQuestionUnification(question=RankingQuestion(...), strategy="majority")
        >>> # or use a RankingQuestionStrategy
        >>> RankingQuestionUnification(question=RankingQuestion(...), strategy=RankingQuestionStrategy.MAJORITY)
    """

    question: RankingQuestion
    strategy: Union[str, RankingQuestionStrategy] = "majority"

    @validator("strategy", always=True)
    def strategy_must_be_valid(cls, v: Union[str, RankingQuestionStrategy]) -> RankingQuestionStrategy:
        if isinstance(v, str):
            return RankingQuestionStrategy(v)
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
        >>> from argilla_v1 import LabelQuestion, LabelQuestionStrategy, LabelQuestionUnification
        >>> LabelQuestionUnification(question=LabelQuestion(...), strategy="majority")
        >>> # or use a LabelQuestionStrategy
        >>> LabelQuestionUnification(question=LabelQuestion(...), strategy=LabelQuestionStrategy.MAJORITY)
    """

    question: Union[LabelQuestion, MultiLabelQuestion]
    strategy: Union[str, LabelQuestionStrategy, MultiLabelQuestionStrategy] = "majority"

    def compute_unified_responses(self, records: List[FeedbackRecord]):
        """
        The function `compute_unified_responses` takes a list of `FeedbackRecord` objects and returns the unified
        responses using a strategy and a specific question.

        Args:
        - records The "records" parameter is a list of FeedbackRecord objects.

        Returns: The method `compute_unified_responses` returns the result of calling the `compute_unified_responses` method
        of the `strategy` object, passing in the `records` and `question` as arguments.
        """
        return self.strategy.compute_unified_responses(records, self.question)

    @root_validator(skip_on_failure=True)
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
