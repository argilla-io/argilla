from typing import Callable, Optional
from typing import Sequence
from typing import Type
from typing import Union

from social_core.backends.oauth import BaseOAuth2

from .claims import Claims

BackendFactory = Callable[[], BaseOAuth2]

class OAuth2Client:
    """OAuth2 client configuration for a single provider."""

    backend: Type[BaseOAuth2]
    backend_factory: Optional[BackendFactory] = None
    client_id: str
    client_secret: str
    redirect_uri: Optional[str]
    scope: Optional[Sequence[str]]
    claims: Optional[Union[Claims, dict]]



    def __init__(
            self,
            *,
            backend: Type[BaseOAuth2],
            client_id: str,
            client_secret: str,
            redirect_uri: Optional[str] = None,
            scope: Optional[Sequence[str]] = None,
            claims: Optional[Union[Claims, dict]] = None,
            backend_factory: Optional[BackendFactory] = None,
    ) -> None:
        self.backend = backend
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope or []
        self.claims = Claims(claims)
        self.backend_factory = backend_factory
