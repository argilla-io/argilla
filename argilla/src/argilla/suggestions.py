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
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

from argilla._exceptions._suggestions import RecordSuggestionsError
from argilla._models import SuggestionModel
from argilla._resource import Resource
from argilla.settings import RankingQuestion

if TYPE_CHECKING:
    from argilla import QuestionType, Record

__all__ = ["Suggestion"]


class Suggestion(Resource):
    """Class for interacting with Argilla Suggestions. Suggestions are typically model predictions for records.
    Suggestions are rendered in the user interfaces as 'hints' or 'suggestions' for the user to review and accept or reject.

    Attributes:
        question_name (str): The name of the question that the suggestion is for.
        value (str): The value of the suggestion
        score (float): The score of the suggestion. For example, the probability of the model prediction.
        agent (str): The agent that created the suggestion. For example, the model name.
        type (str): The type of suggestion, either 'model' or 'human'.
    """

    _model: SuggestionModel

    def __init__(
        self,
        question_name: str,
        value: Any,
        score: Union[float, List[float], None] = None,
        agent: Optional[str] = None,
        type: Optional[Literal["model", "human"]] = None,
        _record: Optional["Record"] = None,
    ) -> None:
        super().__init__()

        if question_name is None:
            raise ValueError("question_name is required")
        if value is None:
            raise ValueError("value is required")

        self._record = _record
        self._model = SuggestionModel(
            question_name=question_name,
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

    @property
    def record(self) -> Optional["Record"]:
        """The record that the suggestion is for."""
        return self._record

    @record.setter
    def record(self, value: "Record") -> None:
        self._record = value

    @classmethod
    def from_model(cls, model: SuggestionModel, record: "Record") -> "Suggestion":
        question = record.dataset.settings.questions[model.question_id]
        model.question_name = question.name
        model.value = cls.__from_model_value(model.value, question)

        instance = cls(question.name, model.value, _record=record)
        instance._model = model

        return instance

    def api_model(self) -> SuggestionModel:
        if self.record is None or self.record.dataset is None:
            return self._model

        question = self.record.dataset.settings.questions[self.question_name]
        if question:
            return SuggestionModel(
                value=self.__to_model_value(self.value, question),
                question_name=None if not question else question.name,
                question_id=None if not question else question.id,
                type=self._model.type,
                score=self._model.score,
                agent=self._model.agent,
                id=self._model.id,
            )
        else:
            raise RecordSuggestionsError(
                f"Record suggestion is invalid because question with name={self.question_name} does not exist in the dataset ({self.record.dataset.name}). Available questions are: {list(self.record.dataset.settings.questions._properties_by_name.keys())}"
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
