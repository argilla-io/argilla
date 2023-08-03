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

import argilla as rg
import pytest
from argilla.client import api
from argilla.client.api import delete, get_workspace, init
from argilla.client.client import Argilla
from argilla.client.sdk.commons.errors import ForbiddenApiError
from argilla.datasets import TextClassificationSettings, TokenClassificationSettings
from argilla.datasets.__init__ import configure_dataset
from argilla.server.contexts import accounts
from argilla.server.security.model import WorkspaceUserCreate

if TYPE_CHECKING:
    from argilla.client.apis.datasets import LabelsSchemaSettings
    from argilla.server.models import User
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.parametrize(
    ("settings_", "wrong_settings"),
    [
        (
            TextClassificationSettings(label_schema={"A", "B"}),
            TokenClassificationSettings(label_schema={"PER", "ORG"}),
        ),
        (
            TokenClassificationSettings(label_schema={"PER", "ORG"}),
            TextClassificationSettings(label_schema={"A", "B"}),
        ),
        (
            TokenClassificationSettings(label_schema=[1, 2, 3]),
            TextClassificationSettings(label_schema={"A", "B"}),
        ),
    ],
)
def test_settings_workflow(
    argilla_user: "User", settings_: "LabelsSchemaSettings", wrong_settings: "LabelsSchemaSettings"
):
    dataset = "test-dataset"

    init(api_key=argilla_user.api_key, workspace=argilla_user.username)
    workspace = get_workspace()

    delete(dataset)
    configure_dataset(dataset, settings=settings_, workspace=workspace)

    current_api = api.active_api()
    datasets_api = current_api.datasets

    found_settings = datasets_api.load_settings(dataset)
    assert {label for label in found_settings.label_schema} == {str(label) for label in settings_.label_schema}

    settings_.label_schema = {"LALALA"}
    configure_dataset(dataset, settings_, workspace=workspace)

    found_settings = datasets_api.load_settings(dataset)
    assert found_settings == settings_

    with pytest.raises(ValueError, match="Task type mismatch"):
        configure_dataset(dataset, wrong_settings, workspace=workspace)


def test_list_dataset(mocked_client: "SecuredClient"):
    from argilla.client.api import active_client

    client = active_client()
    datasets = client.http_client.get("/api/datasets")

    for ds in datasets:
        assert ds["owner"] == ds["workspace"]


@pytest.mark.asyncio
async def test_delete_dataset_by_non_creator(
    mocked_client: "SecuredClient", mock_user: "User", argilla_user: "User", db: "AsyncSession"
):
    dataset = "test_delete_dataset_by_non_creator"

    for workspace in argilla_user.workspaces:
        await accounts.create_workspace_user(db, WorkspaceUserCreate(user_id=mock_user.id, workspace_id=workspace.id))

    await db.refresh(mock_user, attribute_names=["workspaces"])

    rg = Argilla()

    delete(dataset)
    rg.datasets.configure(
        dataset, settings=TextClassificationSettings(label_schema={"A", "B", "C"}), workspace=get_workspace()
    )

    api = Argilla(api_key=mock_user.api_key, workspace=get_workspace())
    with pytest.raises(ForbiddenApiError):
        api.delete(dataset)
