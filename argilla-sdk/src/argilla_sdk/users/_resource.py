# Copyright 2024-present, Argilla, Inc.
# TODO: This license is not consistent with the license used in the project.
#       Delete the inconsistent license and above line and rerun pre-commit to insert a good license.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Optional
from uuid import UUID

from argilla_sdk import Workspace
from argilla_sdk._api import UsersAPI
from argilla_sdk._models import Role, UserModel
from argilla_sdk._resource import Resource
from argilla_sdk.client import Argilla


class User(Resource):
    """Class for interacting with Argilla users in the Argilla server. User profiles \
        are used to manage access to the Argilla server and track responses to records.

    Attributes:
        username (str): The username of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        role (str): The role of the user, either 'annotator' or 'admin'.
        password (str): The password of the user.
        id (UUID): The ID of the user.
    """

    _model: UserModel
    _api: UsersAPI

    def __init__(
        self,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: Optional[str] = None,
        password: Optional[str] = None,
        client: Optional["Argilla"] = None,
        id: Optional[UUID] = None,
        _model: Optional[UserModel] = None,
    ) -> None:
        """Initializes a User object with a client and a username

        Parameters:
            username (str): The username of the user
            first_name (str): The first name of the user
            last_name (str): The last name of the user
            role (str): The role of the user, either 'annotator', admin, or 'owner'
            password (str): The password of the user. If not provided, a random password will be generated
            client (Argilla): The client used to interact with Argilla

        Returns:
            User: The initialized user object
        ```
        """
        client = client or Argilla._get_default()
        super().__init__(client=client, api=client.api.users)

        if _model is None:
            _model = UserModel(
                username=username,
                password=password or self._generate_random_password(),
                first_name=first_name or username,
                last_name=last_name,
                role=role or Role.annotator,
                id=id,
            )
            self.log(f"Initialized user with username {username}")
        self._sync(model=_model)

    def create(self) -> "User":
        """Creates the user in Argilla. After creating a user, it will be able to log in to the Argilla server.

        Returns:
            User: The user that was created in Argilla.

        """
        model_create = self.api_model()
        model = self._api.create(model_create)
        # The password is not returned in the response
        model.password = model_create.password
        self._sync(model=model)
        return self

    def delete(self) -> None:
        """Deletes the user from Argilla. After deleting a user, it will no longer be able to log in to the Argilla server."""
        super().delete()
        # exists relies on the id, so we need to set it to None
        self._model = UserModel(username=self.username)

    def exists(self) -> bool:
        """Checks if the user exists in Argilla

        Returns:
            bool: True if the user exists, False otherwise.
        """
        # TODO - Implement the exist method in the API
        return self.id is not None

    def add_to_workspace(self, workspace: "Workspace") -> "User":
        """Adds the user to a workspace. After adding a user to a workspace, it will have access to the datasets
        in the workspace.

        Args:
            workspace (Workspace): The workspace to add the user to.

        Returns:
            User: The user that was added to the workspace.
        """
        model = self._api.add_to_workspace(workspace.id, self.id)
        self._sync(model=model)
        return self

    def remove_from_workspace(self, workspace: "Workspace") -> "User":
        """Removes the user from a workspace. After removing a user from a workspace, it will no longer have access to
        the datasets in the workspace.

        Args:
            workspace (Workspace): The workspace to remove the user from.

        Returns:
            User: The user that was removed from the workspace.

        """
        model = self._api.delete_from_workspace(workspace.id, self.id)
        self._sync(model=model)

        return self

    ############################
    # Properties
    ############################
    @property
    def username(self) -> str:
        return self._model.username

    @username.setter
    def username(self, value: str) -> None:
        self._model.username = value

    @property
    def password(self) -> str:
        return self._model.password

    @password.setter
    def password(self, value: str) -> None:
        self._model.password = value

    @property
    def first_name(self) -> str:
        return self._model.first_name

    @first_name.setter
    def first_name(self, value: str) -> None:
        self._model.first_name = value

    @property
    def last_name(self) -> str:
        return self._model.last_name

    @last_name.setter
    def last_name(self, value: str) -> None:
        self._model.last_name = value

    @property
    def role(self) -> Role:
        return self._model.role

    @role.setter
    def role(self, value: Role) -> None:
        self._model.role = value

    ############################
    # Private methods
    ############################

    @staticmethod
    def _generate_random_password(n: int = 12) -> str:
        """Generates a random password for the user"""
        import random
        import string

        return "".join(random.choices(string.ascii_letters + string.digits, k=n))
