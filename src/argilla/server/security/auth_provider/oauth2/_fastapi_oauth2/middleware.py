from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from fastapi.security.utils import get_authorization_scheme_param
from jose.exceptions import JOSEError
from jose.jwt import decode as jwt_decode
from jose.jwt import encode as jwt_encode
from starlette.authentication import AuthCredentials
from starlette.authentication import AuthenticationBackend
from starlette.authentication import BaseUser
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.types import ASGIApp
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send

from .claims import Claims
from .config import OAuth2Config
from .core import OAuth2Core


class Auth(AuthCredentials):
    """Extended auth credentials schema based on Starlette AuthCredentials."""

    ssr: bool
    http: bool
    secret: str
    expires: int
    algorithm: str
    scopes: List[str]
    provider: OAuth2Core
    clients: Dict[str, OAuth2Core]

    @classmethod
    def jwt_encode(cls, data: dict) -> str:
        return jwt_encode(data, cls.secret, algorithm=cls.algorithm)

    @classmethod
    def jwt_decode(cls, token: str) -> dict:
        return jwt_decode(token, cls.secret, algorithms=[cls.algorithm])

    @classmethod
    def jwt_create(cls, token_data: dict) -> str:
        expire = datetime.utcnow() + timedelta(seconds=cls.expires)
        return cls.jwt_encode({**token_data, "exp": expire})


class User(BaseUser, dict):
    """Extended user schema based on Starlette BaseUser."""

    __slots__ = ("display_name", "identity", "picture", "email")

    @property
    def is_authenticated(self) -> bool:
        return bool(self)

    def use_claims(self, claims: Claims) -> "User":
        for attr, item in claims.items():
            self[attr] = self.__getprop__(item)
        return self

    def __getprop__(self, item, default="") -> Any:
        if callable(item):
            return item(self)
        return self.get(item, default)

    __getattr__ = __getprop__


class OAuth2Backend(AuthenticationBackend):
    """Authentication backend for AuthenticationMiddleware."""

    def __init__(
            self,
            config: OAuth2Config,
            callback: Callable[[Auth, User], Union[Awaitable[None], None]] = None,
    ) -> None:
        Auth.ssr = config.enable_ssr
        Auth.http = config.allow_http
        Auth.secret = config.jwt_secret
        Auth.expires = config.jwt_expires
        Auth.algorithm = config.jwt_algorithm
        Auth.clients = {
            client.backend.name: OAuth2Core(client)
            for client in config.clients
        }
        self.callback = callback

    async def authenticate(self, request: Request) -> Optional[Tuple[Auth, User]]:
        authorization = request.headers.get(
            "Authorization",
            request.cookies.get("Authorization"),
        )
        scheme, param = get_authorization_scheme_param(authorization)

        if not scheme or not param:
            return Auth(), User()

        user = User(Auth.jwt_decode(param))
        print(Auth.jwt_decode(param))
        auth = Auth(user.pop("scope", []))
        auth.provider = auth.clients.get(user.get("provider"))
        claims = auth.provider.claims if auth.provider else {}

        # Call the callback function on authentication
        if callable(self.callback):
            coroutine = self.callback(auth, user.use_claims(claims))
            if issubclass(type(coroutine), Awaitable):
                await coroutine
        return auth, user.use_claims(claims)


class OAuth2Middleware:
    """Wrapper for the Starlette AuthenticationMiddleware."""

    auth_middleware: AuthenticationMiddleware = None

    def __init__(
            self,
            app: ASGIApp,
            config: Union[OAuth2Config, dict],
            callback: Callable[[Auth, User], Union[Awaitable[None], None]] = None,
            **kwargs,  # AuthenticationMiddleware kwargs
    ) -> None:
        """Initiates the middleware with the given configuration.

        :param app: FastAPI application instance
        :param config: middleware configuration
        :param callback: callback function to be called after authentication
        """
        if isinstance(config, dict):
            config = OAuth2Config(**config)
        elif not isinstance(config, OAuth2Config):
            raise TypeError("config is not a valid type")
        self.default_application_middleware = app
        self.auth_middleware = AuthenticationMiddleware(app, backend=OAuth2Backend(config, callback), **kwargs)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            try:
                return await self.auth_middleware(scope, receive, send)
            except (JOSEError, Exception) as e:
                middleware = PlainTextResponse(str(e), status_code=401)
                return await middleware(scope, receive, send)
        await self.default_application_middleware(scope, receive, send)
