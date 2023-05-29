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
from argilla.server.database import SessionLocal
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
from sqlalchemy import orm

Session = orm.scoped_session(SessionLocal)


class WorkspaceUserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = WorkspaceUser
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"


class WorkspaceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Workspace
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"workspace-{n}")


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"

    first_name = factory.Faker("first_name")
    username = factory.Sequence(lambda n: f"username-{n}")
    api_key = factory.Sequence(lambda n: f"api-key-{n}")
    password_hash = "$2y$05$eaw.j2Kaw8s8vpscVIZMfuqSIX3OLmxA21WjtWicDdn0losQ91Hw."


class AdminFactory(UserFactory):
    role = UserRole.admin


class AnnotatorFactory(UserFactory):
    role = UserRole.annotator


class DatasetFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Dataset
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"dataset-{n}")
    workspace = factory.SubFactory(WorkspaceFactory)


class RecordFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Record
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"

    fields = {
        "text": "This is a text",
        "sentiment": "neutral",
    }
    external_id = factory.Sequence(lambda n: f"external-id-{n}")
    dataset = factory.SubFactory(DatasetFactory)


class ResponseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Response
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"

    record = factory.SubFactory(RecordFactory)
    user = factory.SubFactory(UserFactory)


class FieldFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Field
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"field-{n}")
    title = "Field Title"
    dataset = factory.SubFactory(DatasetFactory)


class TextFieldFactory(FieldFactory):
    settings = {"type": FieldType.text.value}


class QuestionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Question
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"question-{n}")
    title = "Question Title"
    dataset = factory.SubFactory(DatasetFactory)


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
