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

import factory
from argilla.server.models import (
    Dataset,
    Field,
    FieldType,
    Question,
    QuestionType,
    Record,
    Response,
    User,
    UserRole,
    Workspace,
    WorkspaceUser,
)

from tests.database import TestSession


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = TestSession
        sqlalchemy_session_persistence = "flush"


class WorkspaceUserFactory(BaseFactory):
    class Meta:
        model = WorkspaceUser


class WorkspaceFactory(BaseFactory):
    class Meta:
        model = Workspace

    name = factory.Sequence(lambda n: f"workspace-{n}")


class UserFactory(BaseFactory):
    class Meta:
        model = User

    first_name = factory.Faker("first_name")
    username = factory.Sequence(lambda n: f"username-{n}")
    api_key = factory.Sequence(lambda n: f"api-key-{n}")
    password_hash = "$2y$05$eaw.j2Kaw8s8vpscVIZMfuqSIX3OLmxA21WjtWicDdn0losQ91Hw."


class OwnerFactory(UserFactory):
    role = UserRole.owner


class AdminFactory(UserFactory):
    role = UserRole.admin


class AnnotatorFactory(UserFactory):
    role = UserRole.annotator


class DatasetFactory(BaseFactory):
    class Meta:
        model = Dataset

    name = factory.Sequence(lambda n: f"dataset-{n}")
    workspace = factory.SubFactory(WorkspaceFactory)


class RecordFactory(BaseFactory):
    class Meta:
        model = Record

    fields = {
        "text": "This is a text",
        "sentiment": "neutral",
    }
    external_id = factory.Sequence(lambda n: f"external-id-{n}")
    dataset = factory.SubFactory(DatasetFactory)


class ResponseFactory(BaseFactory):
    class Meta:
        model = Response

    record = factory.SubFactory(RecordFactory)
    user = factory.SubFactory(UserFactory)


class FieldFactory(BaseFactory):
    class Meta:
        model = Field

    name = factory.Sequence(lambda n: f"field-{n}")
    title = "Field Title"
    dataset = factory.SubFactory(DatasetFactory)


class TextFieldFactory(FieldFactory):
    settings = {"type": FieldType.text.value}


class QuestionFactory(BaseFactory):
    class Meta:
        model = Question

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        default_settings = cls.settings.copy()
        settings = kwargs.get("settings", {})
        if settings:
            default_settings.update(settings)
            kwargs["settings"] = default_settings
        return super()._create(model_class, *args, **kwargs)

    name = factory.Sequence(lambda n: f"question-{n}")
    title = "Question Title"
    description = "Question Description"
    dataset = factory.SubFactory(DatasetFactory)
    settings = {}


class TextQuestionFactory(QuestionFactory):
    settings = {"type": QuestionType.text.value}


class RatingQuestionFactory(QuestionFactory):
    settings = {
        "type": QuestionType.rating.value,
        "options": [
            {"value": 1},
            {"value": 2},
            {"value": 3},
            {"value": 4},
            {"value": 5},
            {"value": 6},
            {"value": 7},
            {"value": 8},
            {"value": 9},
            {"value": 10},
        ],
    }


class LabelSelectionQuestionFactory(QuestionFactory):
    settings = {
        "type": QuestionType.label_selection.value,
        "options": [
            {"value": "option1", "text": "Option 1"},
            {"value": "option2", "text": "Option 2"},
            {"value": "option3", "text": "Option 3"},
        ],
    }


class MultiLabelSelectionQuestionFactory(QuestionFactory):
    settings = {
        "type": QuestionType.multi_label_selection.value,
        "options": [
            {"value": "option1", "text": "Option 1"},
            {"value": "option2", "text": "Option 2"},
            {"value": "option3", "text": "Option 3"},
        ],
    }


class RankingQuestionFactory(QuestionFactory):
    settings = {
        "type": QuestionType.ranking.value,
        "options": [
            {"value": "completion-a", "text": "Completion A"},
            {"value": "completion-b", "text": "Completion B"},
            {"value": "completion-c", "text": "Completion C"},
        ],
    }
