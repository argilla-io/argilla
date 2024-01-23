from starlette.exceptions import HTTPException


class OAuth2Error(HTTPException):
    """Base OAuth2 exception."""


class OAuth2AuthenticationError(OAuth2Error):
    """Raised when authentication fails."""


class OAuth2InvalidRequestError(OAuth2Error):
    """Raised when request is invalid."""
