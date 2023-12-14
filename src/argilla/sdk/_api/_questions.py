import dataclasses
import datetime
from typing import Any, ClassVar, Dict, List, Literal, NamedTuple, Optional, Union
from uuid import UUID

import httpx

from argilla import sdk as sdk


@dataclasses.dataclass
class TextQuestionSettings:
    type: ClassVar[Literal["text"]] = "text"
    use_markdown: bool

    def to_dict(self):
        return {
            "type": self.type,
            "use_markdown": self.use_markdown,
        }


@dataclasses.dataclass
class RatingQuestionSettings:
    @dataclasses.dataclass
    class Option:
        value: int

        def to_dict(self) -> Dict[str, Any]:
            return {"value": self.value}

    type: ClassVar[Literal["rating"]] = "rating"
    options: List[Option]

    def __post_init__(self):
        for index, option in enumerate(self.options):
            if isinstance(option, dict):
                self.options[index] = self.Option(**option)

    def to_dict(self):
        return {
            "type": self.type,
            "options": [option.to_dict() for option in self.options],
        }

    @classmethod
    def build(cls, min_value: int, max_value: int) -> "RatingQuestionSettings":
        return cls(options=[cls.Option(value=value) for value in range(min_value, max_value + 1)])


@dataclasses.dataclass
class LabelQuestionSettings:
    @dataclasses.dataclass
    class Option:
        value: str
        text: str
        description: Optional[str] = None

        def to_dict(self) -> Dict[str, Any]:
            return {
                "value": self.value,
                "text": self.text,
                "description": self.description,
            }

    type: ClassVar[Literal["label_selection"]] = "label_selection"
    options: List[Option]
    visible_options: Optional[int] = None

    def __post_init__(self):
        for index, option in enumerate(self.options):
            if isinstance(option, dict):
                self.options[index] = self.Option(**option)

    def to_dict(self):
        return {
            "type": self.type,
            "options": [option.to_dict() for option in self.options],
            "visible_options": self.visible_options,
        }

    @classmethod
    def build(cls, options: List[str]) -> "LabelQuestionSettings":
        return cls(options=[cls.Option(value=option, text=option) for option in options])


@dataclasses.dataclass
class MultiLabelQuestionSettings:
    @dataclasses.dataclass
    class Option:
        value: str
        text: str
        description: Optional[str] = None

        def to_dict(self) -> Dict[str, Any]:
            return {
                "value": self.value,
                "text": self.text,
                "description": self.description,
            }

    type: ClassVar[Literal["multi_label_selection"]] = "multi_label_selection"
    options: List[Option]
    visible_options: Optional[int] = None

    def __post_init__(self):
        for index, option in enumerate(self.options):
            if isinstance(option, dict):
                self.options[index] = self.Option(**option)

    def to_dict(self):
        return {
            "type": self.type,
            "options": [option.to_dict() for option in self.options],
            "visible_options": self.visible_options,
        }

    @classmethod
    def build(cls, options: List[str]) -> "MultiLabelQuestionSettings":
        return cls(options=[cls.Option(value=option, text=option) for option in options])


QuestionSettings = Union[
    RatingQuestionSettings, LabelQuestionSettings, MultiLabelQuestionSettings, TextQuestionSettings
]

_QUESTION_SETTINGS_TYPE_TO_CLASS = {
    question_class.type: question_class for question_class in QuestionSettings.__args__  # noqa
}


class Question(NamedTuple):
    id: UUID
    name: str
    title: str
    description: str
    required: bool

    settings: QuestionSettings

    inserted_at: datetime.datetime
    updated_at: datetime.datetime

    client: httpx.Client

    dataset_id: Optional[UUID] = None

    @classmethod
    def list(cls, dataset_id: UUID) -> List["Question"]:
        client = sdk.default_http_client

        response = client.get(f"/api/v1/datasets/{dataset_id}/questions")
        response.raise_for_status()

        json_response = response.json()
        return [cls._construct_question_from_server_question(question) for question in json_response["items"]]

    @classmethod
    def get(cls, question_id: UUID) -> "Question":
        client = sdk.default_http_client

        response = client.get(f"/api/v1/questions/{question_id}")

        response.raise_for_status()
        return cls._construct_question_from_server_question(response.json())

    @classmethod
    def by_name(cls, dataset_id: UUID, name: str) -> "Question":
        # TODO: Maybe we should support an query parameter for this?
        questions = cls.list(dataset_id)
        for question in questions:
            if question.name == name:
                return question

    @classmethod
    def create(
        cls, dataset_id: UUID, name: str, title: str, description: str, required: bool, settings: QuestionSettings
    ) -> "Question":
        client = sdk.default_http_client

        response = client.post(
            f"/api/v1/datasets/{dataset_id}/questions",
            json={
                "name": name,
                "title": title,
                "description": description,
                "required": required,
                "settings": settings.to_dict(),
            },
        )

        response.raise_for_status()
        return cls._construct_question_from_server_question(response.json())

    def update(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        settings: Optional[QuestionSettings] = None,
    ) -> "Question":
        client = self.client

        title = title or self.title
        description = description or self.description
        settings = settings or self.settings

        response = client.patch(
            f"/api/v1/questions/{self.id}",
            json={
                "title": title,
                "description": description,
                "settings": settings.to_dict(),
            },
        )

        response.raise_for_status()
        return self._construct_question_from_server_question(response.json())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "required": self.required,
            "settings": self.settings.to_dict(),
            "inserted_at": self.inserted_at,
            "updated_at": self.updated_at,
            "dataset_id": self.dataset_id,
        }

    @classmethod
    def _construct_question_from_server_question(cls, data: Dict[str, Any]):
        client = sdk.default_http_client

        question_class = _QUESTION_SETTINGS_TYPE_TO_CLASS[data["settings"].pop("type")]
        data["settings"] = question_class(**data["settings"])  # noqa

        return cls(**data, client=client)
