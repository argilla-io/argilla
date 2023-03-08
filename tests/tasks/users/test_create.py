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

from argilla.server.contexts import accounts
from argilla.server.models import User, UserRole
from argilla.tasks.users.create import create
from click.testing import CliRunner
from sqlalchemy.orm import Session


def test_create_passing_all_params(db: Session):
    username = "test-user"
    first_name = "First"
    role = UserRole.admin
    password = "12345678"

    cli_params = f"--first-name {first_name} --username {username} --role {role} --password {password}"
    CliRunner().invoke(create, cli_params)

    user = db.query(User).filter_by(username=username).first()
    assert user
    assert user.first_name == first_name
    assert user.role == role
    assert accounts.verify_password(password, user.password_hash)


def test_create_with_input_role(db: Session):
    username = "test-user"
    role = UserRole.admin

    cli_params = f"--username {username} --password 12345678 --first-name First"
    CliRunner().invoke(create, cli_params, input=f"{role}\n")

    user = db.query(User).filter_by(username=username).first()
    assert user
    assert user.role == role


def test_create_with_input_password(db: Session):
    username = "test-user"
    password = "12345678"

    cli_params = f"--username {username} --role admin --first-name First"
    CliRunner().invoke(create, cli_params, input=f"{password}\n{password}\n")

    user = db.query(User).filter_by(username=username).first()
    assert user
    assert accounts.verify_password(password, user.password_hash)


def test_create_with_default_role(db: Session):
    username = "test-user"
    password = "12345678"

    cli_params = f"--username {username} --password {password} --first-name First"
    CliRunner().invoke(create, cli_params, input=f"\n")

    user = db.query(User).filter_by(username=username).first()
    assert user
    assert user.role == UserRole.annotator


def test_create_with_input_username(db: Session):
    username = "test-user"
    password = "12345678"

    cli_params = f"--password {password} --first-name First"
    CliRunner().invoke(create, cli_params, input=f"{username}\n")

    assert db.query(User).filter_by(username=username).first()


def test_create_with_last_name(db: Session):
    username = "test-user"
    password = "12345678"
    last_name = "Last"

    cli_params = f"--username {username} --password {password} --role admin --first-name First --last-name {last_name}"
    CliRunner().invoke(create, cli_params)

    user = db.query(User).filter_by(username=username).first()
    assert user
    assert user.last_name == last_name


def test_create_with_invalid_username(db: Session):
    username = "Invalid-Username"
    password = "12345678"

    runner = CliRunner()
    cli_params = f"--username {username} --password {password} --role admin --first-name First"
    result = runner.invoke(create, cli_params)

    assert db.query(User).filter_by(username=username).first() is None
    assert str(result.exception) == (
        "1 validation error for UserCreate\n"
        "username\n"
        '  string does not match regex "^(?!-|_)[a-z0-9-_]+$" '
        "(type=value_error.str.regex; pattern=^(?!-|_)[a-z0-9-_]+$)"
    )


def test_create_with_invalid_password(db: Session):
    username = "username"
    password = "11"

    cli_params = f"--username {username} --password {password} --role admin --first-name First"
    result = CliRunner().invoke(create, cli_params)

    assert db.query(User).filter_by(username=username).first() is None
    assert str(result.exception) == (
        "1 validation error for UserCreate\n"
        "password\n"
        "  ensure this value has at least 8 characters "
        "(type=value_error.any_str.min_length; limit_value=8)"
    )
