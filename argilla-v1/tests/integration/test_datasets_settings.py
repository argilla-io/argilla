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

from typing import TYPE_CHECKING, Optional, Union
from uuid import uuid4

import pytest
from argilla_server.contexts import accounts
from argilla_v1 import Workspace
from argilla_v1.client import singleton
from argilla_v1.client.api import get_workspace
from argilla_v1.client.client import Argilla
from argilla_v1.client.sdk.commons.errors import ForbiddenApiError
from argilla_v1.client.singleton import init
from argilla_v1.datasets import (
    TextClassificationSettings,
    TokenClassificationSettings,
    configure_dataset,
    configure_dataset_settings,
    load_dataset_settings,
)

from tests.integration.utils import delete_ignoring_errors

if TYPE_CHECKING:
    from argilla_server.models import User
    from argilla_v1.client.apis.datasets import LabelsSchemaSettings
    from sqlalchemy.ext.asyncio import AsyncSession

    from .helpers import SecuredClient


@pytest.mark.parametrize(
    ("settings_", "wrong_settings"),
    [
        (
            TextClassificationSettings(label_schema=["A", "B"]),
            TokenClassificationSettings(label_schema=["PER", "ORG"]),
        ),
        (
            TokenClassificationSettings(label_schema=["PER", "ORG"]),
            TextClassificationSettings(label_schema=["A", "B"]),
        ),
        (
            TokenClassificationSettings(label_schema=[1, 2, 3]),
            TextClassificationSettings(label_schema=["A", "B"]),
        ),
    ],
)
def test_settings_workflow(
    argilla_user: "User", settings_: "LabelsSchemaSettings", wrong_settings: "LabelsSchemaSettings"
):
    dataset = "test-dataset"

    init(api_key=argilla_user.api_key, workspace=argilla_user.username)
    workspace = get_workspace()

    delete_ignoring_errors(dataset)
    configure_dataset(dataset, settings=settings_, workspace=workspace)

    current_api = singleton.active_api()
    datasets_api = current_api.datasets

    found_settings = datasets_api.load_settings(dataset)
    assert {label for label in found_settings.label_schema} == {str(label) for label in settings_.label_schema}

    settings_.label_schema = ["LALALA"]
    configure_dataset(dataset, settings_, workspace=workspace)

    found_settings = datasets_api.load_settings(dataset)
    assert found_settings == settings_

    with pytest.raises(ValueError, match="Task type mismatch"):
        configure_dataset(dataset, wrong_settings, workspace=workspace)


@pytest.mark.parametrize(
    "settings, workspace",
    [
        (TextClassificationSettings(label_schema={"A", "B"}), None),
        (TextClassificationSettings(label_schema={"D", "E"}), "admin"),
        (TokenClassificationSettings(label_schema={"PER", "ORG"}), None),
        (TokenClassificationSettings(label_schema={"CAT", "DOG"}), "admin"),
    ],
)
def test_configure_dataset_settings_twice(
    owner: "User",
    argilla_user: "User",
    settings: Union[TextClassificationSettings, TokenClassificationSettings],
    workspace: Optional[str],
) -> None:
    if not workspace:
        workspace_name = argilla_user.username
    else:
        init(api_key=owner.api_key)
        workspace = Workspace.create(name=workspace)
        workspace.add_user(argilla_user.id)
        workspace_name = workspace.name

    init(api_key=argilla_user.api_key, workspace=argilla_user.username)
    dataset_name = f"test-dataset-{uuid4()}"
    # This will create the dataset
    configure_dataset_settings(dataset_name, settings=settings, workspace=workspace_name)
    # This will update the dataset and what describes the issue https://github.com/argilla-io/argilla/issues/3505
    configure_dataset_settings(dataset_name, settings=settings, workspace=workspace_name)

    found_settings = load_dataset_settings(dataset_name, workspace_name)
    assert {label for label in found_settings.label_schema} == {str(label) for label in settings.label_schema}


@pytest.mark.parametrize(
    "settings",
    [
        TextClassificationSettings(label_schema={"A", "B"}),
        TokenClassificationSettings(label_schema={"PER", "ORG"}),
    ],
)
def test_configure_dataset_deprecation_warning(
    argilla_user: "User", settings: Union[TextClassificationSettings, TokenClassificationSettings]
) -> None:
    init(api_key=argilla_user.api_key, workspace=argilla_user.username)

    dataset_name = f"test-dataset-{uuid4()}"
    workspace_name = get_workspace()

    with pytest.warns(DeprecationWarning, match="This method is deprecated. Use configure_dataset_settings instead."):
        configure_dataset(dataset_name, settings=settings, workspace=workspace_name)


def test_list_dataset(mocked_client: "SecuredClient"):
    from argilla_v1.client.singleton import active_client

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
        await accounts.create_workspace_user(db, {"workspace_id": workspace.id, "user_id": mock_user.id})

    await db.refresh(mock_user, attribute_names=["workspaces"])

    rg = Argilla()

    delete_ignoring_errors(dataset)
    rg.datasets.configure(
        dataset, settings=TextClassificationSettings(label_schema={"A", "B", "C"}), workspace=get_workspace()
    )

    api = Argilla(api_key=mock_user.api_key, workspace=get_workspace())
    with pytest.raises(ForbiddenApiError):
        api.delete(dataset)
