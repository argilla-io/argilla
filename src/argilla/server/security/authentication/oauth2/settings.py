import os
from typing import List, Optional

from argilla.server.security.authentication.oauth2.client_provider import OAuth2ClientProvider
from social_core.backends.open_id_connect import OpenIdConnectAuth

__all__ = ["OAuth2Settings"]


class OAuth2Settings:
    def __init__(
        self,
        enabled: bool = True,
        allow_http: bool = False,
        providers: List["OAuth2ClientProvider"] = None,
    ):
        self.enabled = enabled
        self.allow_http = allow_http
        self._providers = providers or []

        if self.allow_http:
            # See https://stackoverflow.com/questions/27785375/testing-flask-oauthlib-locally-without-https
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    @property
    def providers(self) -> dict:
        return {provider.name: provider for provider in self._providers}

    @classmethod
    def defaults(cls) -> "OAuth2Settings":
        from dotenv import load_dotenv

        load_dotenv()
        return cls(providers=[HuggingfaceClientProvider()])


class HuggingfaceClientProvider(OAuth2ClientProvider):
    """Specialized HuggingFace OAuth2 provider."""

    class HuggingfaceOpenId(OpenIdConnectAuth):
        """Huggingface OpenID Connect authentication backend."""

        name = "huggingface"

        OIDC_ENDPOINT = "https://huggingface.co"
        AUTHORIZATION_URL = "https://huggingface.co/oauth/authorize"
        ACCESS_TOKEN_URL = "https://huggingface.co/oauth/token"

        def oidc_endpoint(self) -> str:
            return self.OIDC_ENDPOINT

    def __init__(
        self,
        *,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            name=self.HuggingfaceOpenId.name,
            backend_class=self.HuggingfaceOpenId,
            client_id=client_id or os.getenv("OAUTH2_HF_CLIENT_ID", client_id),
            client_secret=client_secret or os.getenv("OAUTH2_HF_CLIENT_SECRET", client_secret),
            redirect_uri=redirect_uri
            or os.getenv("OAUTH2_HF_REDIRECT_URI"),  # THis should be the same for all providers
            scope=["openid", "profile"],
            claims={"username": "preferred_username", "first_name": "name"},
        )
