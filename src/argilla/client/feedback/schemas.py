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
import warnings
from abc import abstractmethod
from collections import Counter
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from pydantic import (
    BaseModel,
    Extra,
    Field,
    PrivateAttr,
    StrictInt,
    StrictStr,
    conint,
    conlist,
    root_validator,
    validator,
)

FETCHING_BATCH_SIZE = 250
PUSHING_BATCH_SIZE = 32


class ValueSchema(BaseModel):
    """A value schema for a record.

    Args:
        value (Union[StrictStr, StrictInt, List[str]]): The value of the record.

    Examples:
        >>> import argilla as rg
        >>> value = rg.ValueSchema(value="Yes")
        >>> # or use a dict
        >>> value = {"value": "Yes"}

    """

    value: Union[StrictStr, StrictInt, List[str]]


class UnificatiedValueSchema(ValueSchema):
    """A value schema for a unification value.

    Args:
        value (Union[StrictStr, StrictInt, List[str]]): The unification value of the record.
        strategy (Literal["mean", "majority", "max", "min"]): The strategy to unify the responses. Defaults to "majority".

    Examples:
        >>> import argilla as rg
        >>> value = rg.UnificatiedValueSchema(value="Yes", strategy="majority")
        >>> # or use a dict
        >>> value = {"value": "Yes", "strategy": "majority"}
    """

    strategy: Union["RatingQuestionStrategy", "LabelQuestionStrategy", "MultiLabelQuestionStrategy"]


class ResponseSchema(BaseModel):
    """A response schema for a record.

    Args:
        user_id (Optional[UUID]): The user id of the response. Defaults to None.
        values (Dict[str, ValueSchema]): The values of the response. Defaults to None.
        status (Literal["submitted", "discarded"]): The status of the response. It can be either `submitted` or `discarded`. Defaults to "submitted".

    Examples:
        >>> import argilla as rg
        >>> response = rg.ResponseSchema(
        ...     user_id="user_id",
        ...     values={"question-1": {"value": "response-1"}}
        ... )
        >>> # or use a ValueSchema directly
        >>> response = rg.ResponseSchema(
        ...     user_id="user_id",
        ...     values={"question-1": rg.ValueSchema(value="response-1")}
        ... )

    """

    user_id: Optional[UUID] = None
    values: Dict[str, ValueSchema]
    status: Literal["submitted", "discarded"] = "submitted"

    @validator("user_id", always=True)
    def user_id_must_have_value(cls, v):
        if not v:
            warnings.warn(
                "`user_id` not provided, so it will be set to `None`. Which is not an"
                " issue, unless you're planning to log the response in Argilla, as "
                " it will be automatically set to the active `user_id`.",
                stacklevel=2,
            )
        return v


class FeedbackRecord(BaseModel):
    """A feedback record.

    Args:
        fields (Dict[str, str]): The fields of the record.
        metadata (Optional[Dict[str, Any]]): The metadata of the record. Defaults to None.
        responses (Optional[Union[ResponseSchema, List[ResponseSchema]]]): The responses of the record. Defaults to None.
        external_id (Optional[str]): The external id of the record. Defaults to None.

    Examples:
        >>> import argilla as rg
        >>> rg.FeedbackRecord(
        ...     fields={"text": "This is the first record", "label": "positive"},
        ...     metadata={"first": True, "nested": {"more": "stuff"}},
        ...     responses=[{"values": {"question-1": {"value": "This is the first answer"}, "question-2": {"value": 5}}}],
        ...     external_id="entry-1",
        ... )
        >>> # or use a ResponseSchema directly
        >>> rg.FeedbackRecord(
        ...     fields={"text": "This is the first record", "label": "positive"},
        ...     metadata={"first": True, "nested": {"more": "stuff"}},
        ...     responses=[rg.ResponseSchema(values={"question-1": {"value": "This is the first answer"}, "question-2": {"value": 5}}))],
        ...     external_id="entry-1",
        ... )

    """

    fields: Dict[str, str]
    metadata: Optional[Dict[str, Any]] = None
    responses: Optional[Union[ResponseSchema, List[ResponseSchema]]] = None
    external_id: Optional[str] = None
    _unified_responses: Optional[Dict[str, List[UnificatiedValueSchema]]] = PrivateAttr(default={})

    @validator("responses", always=True)
    def responses_must_be_a_list(cls, v: Optional[Union[ResponseSchema, List[ResponseSchema]]]) -> List[ResponseSchema]:
        if not v:
            return []
        if isinstance(v, ResponseSchema):
            return [v]
        return v

    class Config:
        extra = Extra.ignore
        fields = {"_unified_responses": {"exclude": True}}


class FieldSchema(BaseModel):
    """A field schema for a feedback dataset.

    Args:
        name (str): The name of the field.
        title (Optional[str]): The title of the field. Defaults to None.
        required (bool): Whether the field is required or not. Defaults to True.

    Examples:
        >>> import argilla as rg
        >>> field = rg.FieldSchema(
        ...     name="text",
        ...     title="Human prompt",
        ...     required=True
        ... )

    """

    name: str
    title: Optional[str] = None
    required: bool = True
    settings: Dict[str, Any] = Field(default_factory=dict, allow_mutation=False)

    @validator("title", always=True)
    def title_must_have_value(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values.get("name").capitalize()
        return v

    class Config:
        validate_assignment = True
        extra = Extra.forbid


class TextField(FieldSchema):
    """A text field schema for a feedback dataset.

    Args:
        name (str): The name of the field.
        title (Optional[str]): The title of the field. Defaults to None.
        required (bool): Whether the field is required or not. Defaults to True.
        use_markdown (bool): Whether the field should use markdown or not. Defaults to False.

    Examples:
        >>> import argilla as rg
        >>> field = rg.FieldSchema(
        ...     name="text",
        ...     title="Human prompt",
        ...     required=True,
        ...     use_markdown=True
        ... )

    """

    settings: Dict[str, Any] = Field({"type": "text"}, allow_mutation=False)
    use_markdown: bool = False

    @root_validator(skip_on_failure=True)
    def update_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values["settings"]["use_markdown"] = values.get("use_markdown", False)
        return values


class QuestionSchema(BaseModel):
    """A question schema for a feedback dataset.

    Args:
        name (str): The name of the question.
        title (Optional[str]): The title of the question. Defaults to None.
        description (Optional[str]): The description of the question. Defaults to None.
        required (bool): Whether the question is required or not. Defaults to True.

    Examples:
        >>> import argilla as rg
        >>> question = rg.QuestionSchema(
        ...     name="relevant",
        ...     title="Is the response relevant for the given prompt?",
        ...     description="Select all that apply",
        ...     required=True
        ... )

    """

    name: str
    title: Optional[str] = None
    description: Optional[str] = None
    required: bool = True
    settings: Dict[str, Any] = Field(default_factory=dict, allow_mutation=False)

    @validator("title", always=True)
    def title_must_have_value(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values.get("name").capitalize()
        return v

    class Config:
        validate_assignment = True
        extra = Extra.forbid


# TODO(alvarobartt): add `TextResponse` and `RatingResponse` classes
class TextQuestion(QuestionSchema):
    """A text question schema for a feedback dataset.

    Args:
        name (str): The name of the question.
        title (Optional[str]): The title of the question. Defaults to None.
        description (Optional[str]): The description of the question. Defaults to None.
        required (bool): Whether the question is required or not. Defaults to True.
        use_markdown (bool): Whether the field should use markdown or not. Defaults to False.

    Examples:
        >>> import argilla as rg
        >>> question = rg.TextQuestion(
        ...     name="relevant",
        ...     title="Is the response relevant for the given prompt?",
        ...     description="Select all that apply",
        ...     required=True,
        ...     use_markdown=True
        ... )

    """

    settings: Dict[str, Any] = Field({"type": "text", "use_markdown": False}, allow_mutation=False)
    use_markdown: bool = False

    @root_validator(skip_on_failure=True)
    def update_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values["settings"]["use_markdown"] = values.get("use_markdown", False)
        return values


class RatingQuestion(QuestionSchema):
    """A rating question schema for a feedback dataset.

    Args:
        name (str): The name of the question.
        title (Optional[str]): The title of the question. Defaults to None.
        description (Optional[str]): The description of the question. Defaults to None.
        required (bool): Whether the question is required or not. Defaults to True.
        values (List[int]): The values of the rating question.

    Examples:
        >>> import argilla as rg
        >>> question = rg.RatingQuestion(
        ...     name="relevant",
        ...     title="Is the response relevant for the given prompt?",
        ...     description="Select all that apply",
        ...     required=True,
        ...     values=[1, 2, 3, 4, 5]
        ... )

    """

    settings: Dict[str, Any] = Field({"type": "rating"}, allow_mutation=False)
    values: List[int] = Field(unique_items=True, min_items=2)

    @property
    def __all_labels__(self):
        return [entry["value"] for entry in self.settings["options"]]

    @property
    def __label2id__(self):
        return {label: idx for idx, label in enumerate(self.__all_labels__)}

    @property
    def __id2label__(self):
        return {idx: label for idx, label in enumerate(self.__all_labels__)}

    @root_validator(skip_on_failure=True)
    def update_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values["settings"]["options"] = [{"value": value} for value in values.get("values")]
        return values


class _LabelQuestion(QuestionSchema):
    settings: Dict[str, Any] = Field(default_factory=dict, allow_mutation=False)
    labels: Union[conlist(str, unique_items=True, min_items=2), Dict[str, str]]
    visible_labels: Optional[conint(ge=3)] = 20

    @validator("labels", always=True)
    def labels_dict_must_be_valid(cls, v: Union[List[str], Dict[str, str]]) -> Union[List[str], Dict[str, str]]:
        if isinstance(v, dict):
            assert len(v.keys()) > 1, "ensure this dict has at least 2 items"
            assert len(set(v.values())) == len(v.values()), "ensure this dict has unique values"
        return v

    @root_validator(skip_on_failure=True)
    def update_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(values.get("labels"), dict):
            values["settings"]["options"] = [
                {"value": key, "text": value} for key, value in values.get("labels").items()
            ]
        if isinstance(values.get("labels"), list):
            values["settings"]["options"] = [{"value": label, "text": label} for label in values.get("labels")]
        values["settings"]["visible_options"] = values.get(
            "visible_labels"
        )  # `None` is a possible value, which means all labels are visible
        return values

    @property
    def __all_labels__(self):
        return [entry["value"] for entry in self.settings["options"]]

    @property
    def __label2id__(self):
        return {label: idx for idx, label in enumerate(self.__all_labels__)}

    @property
    def __id2label__(self):
        return {idx: label for idx, label in enumerate(self.__all_labels__)}


class LabelQuestion(_LabelQuestion):
    """A label question schema for a feedback dataset.

    Args:
        name (str): The name of the question.
        title (Optional[str]): The title of the question. Defaults to None.
        description (Optional[str]): The description of the question. Defaults to None.
        required (bool): Whether the question is required or not. Defaults to True.
        labels (Union[Dict[str, str],conlist(str)]): The labels of the label question.
        visible_labels (conint(ge=3)): The number of visible labels of the label question. Defaults to 20.
            visible_labels=None implies that ALL the labels will be shown by default, which is not recommended if labels>20

    Examples:
        >>> import argilla as rg
        >>> question = rg.LabelQuestion(
        ...     name="relevant",
        ...     title="Is the response relevant for the given prompt?",
        ...     description="Select all that apply",
        ...     required=True,
        ...     labels=["Yes", "No"],
        ...     visible_labels=None
        ... )
        >>> # or use a dict
        >>> question = rg.LabelQuestion(
        ...     name="relevant",
        ...     title="Is the response relevant for the given prompt?",
        ...     description="Select all that apply",
        ...     required=True,
        ...     labels={"yes": "Yes", "no": "No"},
        ...     visible_labels=None
        ... )

    """

    settings: Dict[str, Any] = Field({"type": "label_selection"})


class MultiLabelQuestion(_LabelQuestion):
    """A multi label question schema for a feedback dataset.

    Args:
        name (str): The name of the question.
        title (Optional[str]): The title of the question. Defaults to None.
        description (Optional[str]): The description of the question. Defaults to None.
        required (bool): Whether the question is required or not. Defaults to True.
        labels (Union[Dict[str, str],conlist(str)]): The labels of the label question.
        visible_labels (conint(ge=3)): The number of visible labels of the label question. Defaults to 20.
            visible_labels=None implies that ALL the labels will be shown by default, which is not recommended if labels>20

    Examples:
        >>> import argilla as rg
        >>> question = rg.MultiLabelQuestion(
        ...     name="relevant",
        ...     title="Is the response relevant for the given prompt?",
        ...     description="Select all that apply",
        ...     required=True,
        ...     labels=["Yes", "No"],
        ...     visible_labels=None
        ... )
        >>> # or use a dict
        >>> question = rg.MultiLabelQuestion(
        ...     name="relevant",
        ...     title="Is the response relevant for the given prompt?",
        ...     description="Select all that apply",
        ...     required=True,
        ...     labels={"yes": "Yes", "no": "No"},
        ...     visible_labels=None
        ... )

    """

    settings: Dict[str, Any] = Field({"type": "multi_label_selection"})


AllowedFieldTypes = TextField
AllowedQuestionTypes = Union[TextQuestion, RatingQuestion, LabelQuestion, MultiLabelQuestion]


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
        UnificatiedValueSchema.update_forward_refs()
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
            # only allow for submitted responses
            responses = [resp for resp in rec.responses if resp.status == "submitted"]
            # get responses with a value that is most frequent
            ratings = [int(resp.values[question].value) for resp in responses]
            # unified response
            if self.value == self.MEAN.value:
                unified_value = str(int(sum(ratings) / len(ratings)))
            elif self.value == self.MAX.value:
                unified_value = str(max(ratings))
            elif self.value == self.MIN.value:
                unified_value = str(min(ratings))
            else:
                raise ValueError("Invalid aggregation method")
            rec._unified_responses[question] = [UnificatiedValueSchema(value=unified_value, strategy=self.value)]
        return records

    def _majority(self, records: List[FeedbackRecord], question: str):
        for rec in records:
            counter = Counter()
            # only allow for submitted responses
            responses = [resp for resp in rec.responses if resp.status == "submitted"]
            # get responses with a value that is most frequent
            for resp in responses:
                counter.update([resp.values[question].value])
            # Find the maximum count
            max_count = max(counter.values())
            # Get a list of values with the maximum count
            most_common_values = [value for value, count in counter.items() if count == max_count]
            if len(most_common_values) > 1:
                majority_value = random.choice(most_common_values)
            else:
                majority_value = counter.most_common(1)[0][0]
            rec._unified_responses[question] = [UnificatiedValueSchema(value=majority_value, strategy=self.value)]
        return records


class LabelQuestionStrategyMixin:
    def unify_responses(self, records: List[FeedbackRecord], question: Union[str, LabelQuestion, MultiLabelQuestion]):
        UnificatiedValueSchema.update_forward_refs()
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
            # only allow for submitted responses
            responses = [resp for resp in rec.responses if resp.status == "submitted"]
            # get responses with a value that is most frequent
            rec._unified_responses[question] = [
                UnificatiedValueSchema(value=resp.values[question].value, strategy=self.value) for resp in responses
            ]

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
            counter = Counter()
            # only allow for submitted responses
            responses = [resp for resp in rec.responses if resp.status == "submitted"]
            # get responses with a value that is most frequent
            for resp in responses:
                counter.update([resp.values[question].value])
            # Find the maximum count
            max_count = max(counter.values())
            # Get a list of values with the maximum count
            most_common_values = [value for value, count in counter.items() if count == max_count]
            if len(most_common_values) > 1:
                majority_value = random.choice(most_common_values)
            else:
                majority_value = counter.most_common(1)[0][0]

            rec._unified_responses[question] = [UnificatiedValueSchema(value=majority_value, strategy=self.value)]
        return rec

    @classmethod
    def _majority_weighted(self, records: List[FeedbackRecord], question: LabelQuestion):
        raise NotImplementedError("Not implemented yet")


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
            rec._unified_responses[question] = [UnificatiedValueSchema(value=majority_value, strategy=self.value)]
        return records

    @classmethod
    def _majority_weighted(self, records: List[FeedbackRecord], question: MultiLabelQuestion):
        raise NotImplementedError("Not implemented yet")


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
