from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from rubrix.server.commons.errors import InactiveUserError, UnauthorizedError
from rubrix.server.users.model import MOCK_USER, User
from rubrix.server.users.service import UsersService, create_users_service

from .model import Token
from .settings import settings as security_settings

router = APIRouter(tags=["security"], prefix="/security")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/security/token", auto_error=security_settings.enable_security
)


async def fetch_user_for_token(
    token: str = Depends(oauth2_scheme),
    service: UsersService = Depends(create_users_service),
) -> User:
    """
    Fetches the user for a given token

    Parameters
    ----------
    token:
        The login token.
        fastapi injects this param from request
    service:
        Users service for user authentication.
        fastapi injects this param from application

    Returns
    -------

    """
    if not security_settings.enable_security:
        return MOCK_USER

    user = service.fetch_token_user(token)
    if user is None:
        raise UnauthorizedError()
    return user


async def get_current_active_user(current_user: User = Depends(fetch_user_for_token)):
    """
    Get the current active user

    Parameters
    ----------
    current_user:
        The current user. Param injected by fastapi

    Returns
    -------
        The current user if active.
        Raises an InactiveUserError exception, otherwise

    """
    if current_user.disabled:
        raise InactiveUserError()
    return current_user


@router.post("/token", response_model=Token, operation_id="login_for_access_token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    users: UsersService = Depends(create_users_service),
) -> Token:
    """
    Login access token api endpoint

    Parameters
    ----------
    form_data:
        The user/password form
    users:
        The users service

    Returns
    -------
        Logging token if user is properly authenticated.
        Unauthorized exception otherwise

    """
    user = users.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise UnauthorizedError()
    access_token_expires = timedelta(
        minutes=security_settings.token_expiration_in_minutes
    )
    access_token = users.create_access_token(
        user.username, expires_delta=access_token_expires
    )
    return Token(access_token=access_token)


@router.post("/api-key", response_model=Token, operation_id="generate_user_api_key")
async def generate_user_api_key(
    user: User = Depends(get_current_active_user),
    users: UsersService = Depends(create_users_service),
) -> Token:
    """

    Parameters
    ----------
    user:
        request user
    users:
        The users service


    Returns
    -------
        An api access token for api-key purposes.

    """
    # TODO: configurable expiration
    access_token_expires = timedelta(hours=730)  # 1 month
    access_token = users.create_access_token(
        user.username, expires_delta=access_token_expires
    )
    return Token(access_token=access_token)
