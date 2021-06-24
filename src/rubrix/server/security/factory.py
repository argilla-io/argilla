from .auth_provider.base import AuthProvider


def create_auth_provider() -> AuthProvider:
    from rubrix.server.security.auth_provider import (
        MockAuthProvider,
        create_local_auth_provider,
    )
    from rubrix.server.security.settings import AuthProviderType, SecuritySettings

    settings = SecuritySettings()

    if settings.auth_provider == AuthProviderType.local:
        return create_local_auth_provider()
    return MockAuthProvider()


auth = create_auth_provider()
