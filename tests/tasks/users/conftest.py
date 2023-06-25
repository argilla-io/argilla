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

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pytest_mock import MockerFixture
    from sqlalchemy.orm import Session


@pytest.fixture(autouse=True)
def mock_session_local(mocker: "MockerFixture", db: "Session") -> None:
    mocker.patch.object(db, "close", side_effect=lambda: None)
    mocker.patch("argilla.tasks.users.create.SessionLocal", return_value=db)
    mocker.patch("argilla.tasks.users.update.SessionLocal", return_value=db)
    mocker.patch("argilla.tasks.users.create_default.SessionLocal", return_value=db)
    mocker.patch("argilla.tasks.users.migrate.SessionLocal", return_value=db)
