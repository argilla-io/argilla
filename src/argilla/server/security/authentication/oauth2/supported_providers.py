from social_core.backends.github import GithubOAuth2
from social_core.backends.open_id_connect import OpenIdConnectAuth

from argilla.server.security.authentication.claims import Claims
from argilla.server.security.authentication.oauth2.client_provider import OAuth2ClientProvider


class HuggingfaceOpenId(OpenIdConnectAuth):
    """Huggingface OpenID Connect authentication backend."""

    name = "huggingface"

    OIDC_ENDPOINT = "https://huggingface.co"
    AUTHORIZATION_URL = "https://huggingface.co/oauth/authorize"
    ACCESS_TOKEN_URL = "https://huggingface.co/oauth/token"

    def oidc_endpoint(self) -> str:
        return self.OIDC_ENDPOINT


class GitHubClientProvider(OAuth2ClientProvider):
    claims = Claims(picture="avatar_url", identity=lambda user: f"{user.provider}:{user.id}", username="login")
    backend_class = GithubOAuth2
    name = "github"


class HuggingfaceClientProvider(OAuth2ClientProvider):
    """Specialized HuggingFace OAuth2 provider."""

    claims = Claims(username="preferred_username")
    backend_class = HuggingfaceOpenId
    name = "huggingface"


_providers = [GitHubClientProvider, HuggingfaceClientProvider]

ALL_SUPPORTED_OAUTH2_PROVIDERS = {provider_class.name: provider_class for provider_class in _providers}
