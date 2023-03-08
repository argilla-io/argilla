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

from argilla._constants import DEFAULT_API_KEY, DEFAULT_PASSWORD, DEFAULT_USERNAME
from argilla.server.contexts import accounts
from argilla.server.models import User, UserRole
from argilla.tasks.users.create_default import create_default
from click.testing import CliRunner
from sqlalchemy.orm import Session


def test_create_default(db: Session):
    result = CliRunner().invoke(create_default)

    assert result.exit_code == 0
    assert result.output != ""
    assert db.query(User).count() == 1

    default_user = db.query(User).filter_by(username=DEFAULT_USERNAME).first()
    assert default_user
    assert default_user.role == UserRole.admin
    assert default_user.api_key == DEFAULT_API_KEY
    assert accounts.verify_password(DEFAULT_PASSWORD, default_user.password_hash)
    assert [ws.name for ws in default_user.workspaces] == [DEFAULT_USERNAME]


def test_create_default_quiet(db: Session):
    result = CliRunner().invoke(create_default, ["--quiet"])

    assert result.exit_code == 0
    assert result.output == ""
