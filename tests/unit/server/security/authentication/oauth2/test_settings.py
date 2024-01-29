import pytest

from argilla.server.security.authentication.oauth2 import OAuth2Settings


class TestOAuth2Settings:
    def test_configure_unsupported_provider(self):
        with pytest.raises(ValueError):
            OAuth2Settings.from_dict({"providers": [{"name": "unsupported"}]})

    def test_configure_github_provider(self):
        settings = OAuth2Settings.from_dict(
            {
                "providers": [
                    {
                        "name": "github",
                        "client_id": "github_client_id",
                        "client_secret": "github_client_secret",
                        "scope": "user:email",
                    }
                ]
            }
        )
        github_provider = settings.providers["github"]

        assert github_provider.name == "github"
        assert github_provider.client_id == "github_client_id"
        assert github_provider.client_secret == "github_client_secret"
        assert github_provider.scope == ["user:email"]

    def test_configure_huggingface_provider(self):
        settings = OAuth2Settings.from_dict(
            {
                "providers": [
                    {
                        "name": "huggingface",
                        "client_id": "huggingface_client_id",
                        "client_secret": "huggingface_client_secret",
                        "scope": "openid profile email"
                    }
                ]
            }
        )
        huggingface_provider = settings.providers["huggingface"]

        assert huggingface_provider.name == "huggingface"
        assert huggingface_provider.client_id == "huggingface_client_id"
        assert huggingface_provider.client_secret == "huggingface_client_secret"
        assert huggingface_provider.scope == ["openid", "profile", "email"]
