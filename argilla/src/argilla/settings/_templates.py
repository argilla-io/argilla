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

from typing import List, Optional, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from argilla.settings._resource import Settings
    from argilla.settings._field import TextField


def _get_field_type(field_type: str) -> "TextField":
    """Get the field type from the field type string."""
    from argilla import TextField, ImageField

    FIELD_MAPPING = {
        "text": TextField,
        "image": ImageField,
    }

    return FIELD_MAPPING[field_type]


class DefaultSettingsMixin:
    """Mixin class for handling default templates of the `Settings` class."""

    @classmethod
    def for_classification(
        cls: "Settings",
        labels: List[str],
        field_type: Optional[Literal["text", "image", "chat"]] = "text",
    ) -> "Settings":
        """Default settings for document classification task. Document classification template consists of a text field and a label question.

        Parameters:
        guidelines (str): Guidelines for the task.
        fields (List[Field]): List of fields.
        questions (List[QuestionType]): List of questions.
        use_chat (bool): If True, the field will be replaced with a chat field.
        """
        from argilla import Settings, LabelQuestion

        settings = Settings(
            guidelines="Select a label for the document.",
            fields=[_get_field_type(field_type)(name="text")],
            questions=[LabelQuestion(name="label", labels=labels)],
            mapping={"input": "text", "output": "label", "document": "text"},
        )

        return settings

    @classmethod
    def for_ranking(
        cls: "Settings",
        field_type: Optional[Literal["text", "image", "chat"]] = "text",
    ) -> "Settings":
        """Default settings for response ranking task. Response ranking template consists of an instruction field, two response fields, and a ranking question.

        Parameters:
        guidelines (str): Guidelines for the task.
        fields (List[Field]): List of fields.
        questions (List[QuestionType]): List of questions.
        use_chat (bool): If True, the field will be replaced with a chat field.

        """
        from argilla import Settings, RankingQuestion

        fields = [
            _get_field_type(field_type)(name="instruction"),
            _get_field_type(field_type)(name="response1"),
            _get_field_type(field_type)(name="response2"),
        ]

        settings = Settings(
            guidelines="Rank the responses.",
            fields=fields,
            questions=[RankingQuestion(name="ranking", values=["response1", "response2"])],
            mapping={
                "input": "instruction",
                "prompt": "instruction",
                "chosen": "response1",
                "rejected": "response2",
            },
        )

        return settings

    @classmethod
    def for_rating(
        cls: "Settings",
        field_type: Optional[Literal["text", "image", "chat"]] = "text",
    ) -> "Settings":
        """Default settings for response rating task. Response rating template consists of an instruction field, a response field, and a rating question.

        Parameters:
        guidelines (str): Guidelines for the task.
        fields (List[Field]): List of fields.
        questions (List[QuestionType]): List of questions.
        use_chat (bool): If True, the field will be replaced with a chat field.

        """
        from argilla import Settings, RatingQuestion

        fields = [
            _get_field_type(field_type)(name="instruction"),
            _get_field_type(field_type)(name="response"),
        ]

        settings = Settings(
            guidelines="Rate the response.",
            fields=fields,
            questions=[RatingQuestion(name="rating", values=[1, 2, 3, 4, 5])],
            mapping={
                "input": "instruction",
                "prompt": "instruction",
                "output": "response",
                "score": "rating",
            },
        )
        return settings
