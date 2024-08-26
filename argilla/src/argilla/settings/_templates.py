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

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from argilla.settings._resource import Settings
    from argilla.settings._field import TextField as Field
    from argilla.settings._question import QuestionType


class DefaultSettingsMixin:
    """Mixin class for handling default templates of the `Settings` class."""

    @classmethod
    def for_document_classification(
        cls: "Settings",
        guidelines: Optional[str] = None,
        fields: Optional[List["Field"]] = None,
        questions: Optional[List["QuestionType"]] = None,
        use_chat: Optional[bool] = False,
    ) -> "Settings":
        """Default settings for document classification task. Document classification template consists of a text field and a label question.

        Parameters:
        guidelines (str): Guidelines for the task.
        fields (List[Field]): List of fields.
        questions (List[QuestionType]): List of questions.
        use_chat (bool): If True, the field will be replaced with a chat field.
        """
        from argilla import Settings, TextField, LabelQuestion

        settings = Settings(
            guidelines="Select a label for the document.",
            fields=[TextField(name="text")],
            questions=[LabelQuestion(name="label", labels=["positive", "negative"])],
        )

        return DefaultSettingsMixin._update_settings(
            settings=settings,
            guidelines=guidelines,
            fields=fields,
            questions=questions,
            use_chat=use_chat,
        )

    @classmethod
    def for_response_ranking(
        cls: "Settings",
        guidelines: Optional[str] = None,
        fields: Optional[List["Field"]] = None,
        questions: Optional[List["QuestionType"]] = None,
        use_chat: Optional[bool] = False,
    ) -> "Settings":
        """Default settings for response ranking task. Response ranking template consists of an instruction field, two response fields, and a ranking question.

        Parameters:
        guidelines (str): Guidelines for the task.
        fields (List[Field]): List of fields.
        questions (List[QuestionType]): List of questions.
        use_chat (bool): If True, the field will be replaced with a chat field.

        """
        from argilla import Settings, TextField, RankingQuestion

        settings = Settings(
            guidelines="Rank the responses.",
            fields=[TextField(name="instruction"), TextField(name="response1"), TextField(name="response2")],
            questions=[RankingQuestion(name="ranking", values=["response1", "response2"])],
        )

        return DefaultSettingsMixin._update_settings(
            settings=settings,
            guidelines=guidelines,
            fields=fields,
            questions=questions,
            use_chat=use_chat,
        )

    @classmethod
    def for_response_rating(
        cls: "Settings",
        guidelines: Optional[str] = None,
        fields: Optional[List["Field"]] = None,
        questions: Optional[List["QuestionType"]] = None,
        use_chat: Optional[bool] = False,
    ) -> "Settings":
        """Default settings for response rating task. Response rating template consists of an instruction field, a response field, and a rating question.

        Parameters:
        guidelines (str): Guidelines for the task.
        fields (List[Field]): List of fields.
        questions (List[QuestionType]): List of questions.
        use_chat (bool): If True, the field will be replaced with a chat field.

        """
        from argilla import Settings, TextField, RatingQuestion

        settings = Settings(
            guidelines="Rate the response.",
            fields=[TextField(name="instruction"), TextField(name="response")],
            questions=[RatingQuestion(name="rating", values=[1, 2, 3, 4, 5])],
        )
        return DefaultSettingsMixin._update_settings(
            settings=settings,
            guidelines=guidelines,
            fields=fields,
            questions=questions,
            use_chat=use_chat,
        )

    @staticmethod
    def _update_settings(
        settings: "Settings",
        guidelines: Optional[str] = None,
        fields: Optional[List["Field"]] = None,
        questions: Optional[List["QuestionType"]] = None,
        use_chat: Optional[bool] = False,
    ) -> "Settings":
        """Utility method to update the settings with partial values."""
        if guidelines:
            settings.guidelines = guidelines
        if fields:
            settings.fields = fields
        if questions:
            settings.questions = questions
        # if use_chat:
        #     settings.fields = [
        #         ChatField(
        #             name=field.name,
        #         )
        #         for field in settings.fields
        #     ]
        return settings
