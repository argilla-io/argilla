from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from jose import JWTError, jwt
from pydantic import BaseSettings
from rubrix.server.commons.errors import InactiveUserError, UnauthorizedError
from rubrix.server.security.auth_provider.base import (
    AuthProvider, )
from rubrix.server.security.model import Token
from rubrix.server.users.model import User
from rubrix.server.users.service import UsersService

_TOKEN_URL = "/api/security/token"
_API_KEY_URL = "/api/security/api-key"

_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=_TOKEN_URL,
)


class Settings(BaseSettings):

    """
    Attributes
    ----------

    secret_key:
        The secret key used for signed the token data

    algorithm:
        Encryption algorithm for token data

    token_expiration_in_minutes:
        The session token expiration in minutes. Default=30

    """

    secret_key: str = "secret"
    algorithm: str = "HS256"
    token_expiration_in_minutes: int = 30

    class Config:
        env_prefix = "RUBRIX_LOCAL_AUTH_"

        fields = {
            "secret_key": {"env": ["SECRET_KEY", f"{env_prefix}SECRET_KEY"]},
            "token_expiration_in_minutes": {
                "env": [
                    "TOKEN_EXPIRATION_IN_MINUTES",
                    f"{env_prefix}TOKEN_EXPIRATION_IN_MINUTES",
                ]
            },
        }


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
            _TOKEN_URL, response_model=Token, operation_id="login_for_access_token"
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

        @self.router.post(
            _API_KEY_URL,
            response_model=Token,
            operation_id="generate_user_api_key",
        )
        async def generate_user_api_key(
            user: User = Depends(self.get_user),
            access_token_expiration: Optional[timedelta] = timedelta(
                hours=730
            ),  # 1 month,
        ) -> Token:
            """

            Parameters
            ----------
            user:
                request user
            access_token_expiration:
                The access token expiration

            Returns
            -------
                An api access token for api-key purposes.

            """
            access_token = self._create_access_token(
                user.username, expires_delta=access_token_expiration
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
        token: str = Depends(_oauth2_scheme),
    ) -> User:
        """
        Fetches the user for a given token

        Parameters
        ----------
        token:
            The login token.
            fastapi injects this param from request
        Returns
        -------

        """
        user = self.fetch_token_user(token)
        if user is None:
            raise UnauthorizedError()

        if user.disabled:
            raise InactiveUserError()

        return user


def create_local_auth_provider():
    from rubrix.server.users.dao import create_users_dao
    from rubrix.server.users.service import create_users_service

    settings = Settings()
    users_dao = create_users_dao()
    users_service = create_users_service(users_dao)

    return LocalAuthProvider(users=users_service, settings=settings)
