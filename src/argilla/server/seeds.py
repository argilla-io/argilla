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

from argilla._constants import DEFAULT_API_KEY
from argilla.server.database import SessionLocal
from argilla.server.models import User, UserRole, Workspace


def development_seeds():
    with SessionLocal() as session, session.begin():
        session.add_all(
            [
                Workspace(name="workspace-1"),
                Workspace(name="workspace-2"),
                User(
                    first_name="John",
                    last_name="Doe",
                    username="argilla",
                    role=UserRole.admin,
                    password_hash="$2y$05$eaw.j2Kaw8s8vpscVIZMfuqSIX3OLmxA21WjtWicDdn0losQ91Hw.",
                    api_key="1234",
                ),
                User(
                    first_name="Tanya",
                    last_name="Franklin",
                    username="tanya",
                    password_hash="$2y$05$eaw.j2Kaw8s8vpscVIZMfuqSIX3OLmxA21WjtWicDdn0losQ91Hw.",
                    api_key="123456",
                ),
            ]
        )


def test_seeds(db: SessionLocal):
    db.add_all(
        [
            Workspace(
                name="argilla",
                users=[
                    User(
                        first_name="Argilla",
                        username="argilla",
                        role=UserRole.admin,
                        password_hash="$2y$05$eaw.j2Kaw8s8vpscVIZMfuqSIX3OLmxA21WjtWicDdn0losQ91Hw.",
                        api_key=DEFAULT_API_KEY,
                    ),
                ],
            )
        ]
    )
    db.commit()
