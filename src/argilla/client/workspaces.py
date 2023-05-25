#  coding=utf-8
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

import warnings
from typing import TYPE_CHECKING, Optional

import argilla as rg

if TYPE_CHECKING:
    from argilla.client.api import Argilla


class Workspace:
    """The `Workspace` class is used to manage workspaces in Argilla. The main
    purpose of this class is to ease the conversion from name to ID, since the
    workspace name is known to the user while the ID is not. Also, it helps checking
    whether the workspace exists or not.

    Args:
        name: the name of the workspace to be managed. If not provided, the current
            workspace will be used.
        id: the ID of the workspace to be managed.

    Raises:
        ValueError: if the workspace does not exist in the current Argilla account.

    Examples:
        >>> from argilla import rg
        >>> workspace = rg.Workspace.from_name("my-workspace")
        >>> workspace.id
    """

    def __init__(self, name: str, *, id: Optional[str] = None) -> None:
        """Initializes a new `Workspace` instance using the provided name. If no name
        is provided, the current workspace will be used.

        Args:
            name: the name of the workspace to be managed. If not provided, the current
                workspace will be used.
            id: the ID of the workspace to be managed.
        """
        self.name = name
        self.id = id or None

        if self.id is None:
            warnings.warn(
                f"The `rg.Workspace` doesn't exist yet, you need to create it in advance. Otherwise, use `rg.Workspace.from_name` to make sure that the workspace exists."
            )

    @classmethod
    def from_name(cls, name: str) -> "Workspace":
        """Class method to create a new `rg.Workspace` instance using the provided
        name, if it exists.

        Args:
            name: the name of the workspace to be managed.

        Returns:
            A new `rg.Workspace` instance.

        Raises:
            ValueError: if the workspace does not exist in the current Argilla account.
        """
        client: "Argilla" = rg.active_client()
        for workspace in client.list_workspaces():
            if workspace.name == name:
                return cls(name, id=workspace.id)
        raise ValueError(f"Workspace {name} not found in the current Argilla account.")
