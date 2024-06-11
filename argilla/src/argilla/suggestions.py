# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Any, Optional, Literal, Union, List, TYPE_CHECKING, Dict
from uuid import UUID

from argilla._models import SuggestionModel
from argilla._resource import Resource
from argilla.settings import RankingQuestion

if TYPE_CHECKING:
    from argilla import QuestionType, Record, Dataset

__all__ = ["Suggestion"]


class Suggestion(Resource):
    """Class for interacting with Argilla Suggestions. Suggestions are typically model predictions for records.
    Suggestions are rendered in the user interfaces as 'hints' or 'suggestions' for the user to review and accept or reject.

    Attributes:
        value (str): The value of the suggestion.add()
        question_name (str): The name of the question that the suggestion is for.
        type (str): The type of suggestion, either 'model' or 'human'.
        score (float): The score of the suggestion. For example, the probability of the model prediction.
        agent (str): The agent that created the suggestion. For example, the model name.
        question_id (UUID): The ID of the question that the suggestion is for.

    """

    _model: SuggestionModel

    def __init__(
        self,
        question_name: str,
        value: Any,
        score: Union[float, List[float], None] = None,
        agent: Optional[str] = None,
        type: Optional[Literal["model", "human"]] = None,
        id: Optional[UUID] = None,
        question_id: Optional[UUID] = None,
        _record: Optional["Record"] = None,
    ) -> None:
        super().__init__()

        if question_name is None:
            raise ValueError("question_name is required")
        if value is None:
            raise ValueError("value is required")

        self.record = _record
        self._model = SuggestionModel(
            id=id,
            question_name=question_name,
            question_id=question_id,
            value=value,
            type=type,
            score=score,
            agent=agent,
        )

    ##############################
    # Properties
    ##############################

    @property
    def value(self) -> Any:
        """The value of the suggestion."""
        return self._model.value

    @property
    def question_name(self) -> Optional[str]:
        """The name of the question that the suggestion is for."""
        return self._model.question_name

    @question_name.setter
    def question_name(self, value: str) -> None:
        self._model.question_name = value

    @property
    def question_id(self) -> Optional[UUID]:
        """The ID of the question that the suggestion is for."""
        return self._model.question_id

    @question_id.setter
    def question_id(self, value: UUID) -> None:
        self._model.question_id = value

    @property
    def type(self) -> Optional[Literal["model", "human"]]:
        """The type of suggestion, either 'model' or 'human'."""
        return self._model.type

    @property
    def score(self) -> Optional[Union[float, List[float]]]:
        """The score of the suggestion."""
        return self._model.score

    @score.setter
    def score(self, value: float) -> None:
        self._model.score = value

    @property
    def agent(self) -> Optional[str]:
        """The agent that created the suggestion."""
        return self._model.agent

    @agent.setter
    def agent(self, value: str) -> None:
        self._model.agent = value

    @classmethod
    def from_model(cls, model: SuggestionModel, dataset: "Dataset") -> "Suggestion":
        question = dataset.settings.question_by_id(model.question_id)
        model.question_name = question.name
        model.value = cls.__from_model_value(model.value, question)

        return cls(**model.model_dump())

    def api_model(self) -> SuggestionModel:
        if self.record is None or self.record.dataset is None:
            return self._model

        question = self.record.dataset.settings.question_by_name(self.question_name)
        return SuggestionModel(
            value=self.__to_model_value(self.value, question),
            question_name=self.question_name,
            question_id=self.question_id or question.id,
            type=self._model.type,
            score=self._model.score,
            agent=self._model.agent,
            id=self._model.id,
        )

    @classmethod
    def __to_model_value(cls, value: Any, question: "QuestionType") -> Any:
        if isinstance(question, RankingQuestion):
            return cls.__ranking_to_model_value(value)
        return value

    @classmethod
    def __from_model_value(cls, value: Any, question: "QuestionType") -> Any:
        if isinstance(question, RankingQuestion):
            return cls.__ranking_from_model_value(value)
        return value

    @classmethod
    def __ranking_from_model_value(cls, value: List[Dict[str, Any]]) -> List[str]:
        return [v["value"] for v in value]

    @classmethod
    def __ranking_to_model_value(cls, value: List[str]) -> List[Dict[str, str]]:
        return [{"value": str(v)} for v in value]
