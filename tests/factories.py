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
    Annotation,
    Dataset,
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


class DatasetFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Dataset
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"dataset-{n}")
    workspace = factory.SubFactory(WorkspaceFactory)


class AnnotationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Annotation
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"annotation-{n}")
    title = "Annotation Title"
    dataset = factory.SubFactory(DatasetFactory)


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
