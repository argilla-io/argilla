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

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from jose import JWTError, jwt

from argilla.server.errors import InactiveUserError, UnauthorizedError
from argilla.server.security.auth_provider.base import (
    AuthProvider,
    api_key_header,
    old_api_key_header,
)
from argilla.server.security.auth_provider.local.users.service import UsersService
from argilla.server.security.model import Token, User

from .settings import Settings, settings

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.token_api_url, auto_error=False)


class LocalAuthProvider(AuthProvider):
    def __init__(
        self,
        users: UsersService,
        settings: Settings,
    ):
        self.users = users
        self.router = APIRouter(tags=["security"])
        self.settings = settings

        @self.router.post(
            settings.token_api_url,
            response_model=Token,
            operation_id="login_for_access_token",
        )
        async def login_for_access_token(
            form_data: OAuth2PasswordRequestForm = Depends(),
        ) -> Token:
            """
            Login access token api endpoint

            Parameters
            ----------
            form_data:
                The user/password form

            Returns
            -------
                Logging token if user is properly authenticated.
                Unauthorized exception otherwise

            """
            user = self.users.authenticate_user(form_data.username, form_data.password)
            if not user:
                raise UnauthorizedError()
            access_token_expires = timedelta(
                minutes=self.settings.token_expiration_in_minutes
            )
            access_token = self._create_access_token(
                user.username, expires_delta=access_token_expires
            )
            return Token(access_token=access_token)

    def _create_access_token(
        self, username: str, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Creates an access token

        Parameters
        ----------
        username:
            The user name
        expires_delta:
            Token expiration

        Returns
        -------
            An access token string
        """
        to_encode = {
            "sub": username,
        }
        if expires_delta:
            to_encode["exp"] = datetime.utcnow() + expires_delta

        return jwt.encode(
            to_encode,
            self.settings.secret_key,
            algorithm=self.settings.algorithm,
        )

    def fetch_token_user(self, token: str) -> Optional[User]:
        """
        Fetch the user for a given access token

        Parameters
        ----------
        token:
            The access token

        Returns
        -------
            An User instance if a valid token was provided. None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=[self.settings.algorithm],
            )
            username: str = payload.get("sub")
            if username:
                return self.users.get_user(username=username)
        except JWTError:
            return None

    async def get_user(
        self,
        security_scopes: SecurityScopes,
        api_key: Optional[str] = Depends(api_key_header),
        old_api_key: Optional[str] = Depends(old_api_key_header),
        token: Optional[str] = Depends(_oauth2_scheme),
    ) -> User:
        """
        Fetches the user for a given token

        Parameters
        ----------
        api_key:
            The apikey header info if provided
        old_api_key:
            Same as api key but for old clients
        token:
            The login token.
            fastapi injects this param from request
        Returns
        -------

        """
        user = await self._find_user_by_api_key(
            api_key
        ) or await self._find_user_by_api_key(old_api_key)
        if user:
            return user
        if token:
            user = self.fetch_token_user(token)
        if user is None:
            raise UnauthorizedError()

        if user.disabled:
            raise InactiveUserError()

        return user

    async def _find_user_by_api_key(self, api_key) -> User:
        return await self.users.find_user_by_api_key(api_key)


def create_local_auth_provider():
    from .users.dao import create_users_dao

    settings = Settings()

    users_service = UsersService.get_instance(
        users=create_users_dao(),
    )

    return LocalAuthProvider(users=users_service, settings=settings)
