import pytest
from fastapi.security import SecurityScopes

from rubrix.server.security.auth_provider.local.provider import create_local_auth_provider

localAuth = create_local_auth_provider()
security_Scopes = SecurityScopes


# Tests for function get_user via token and api key
@pytest.mark.asyncio
async def test_get_user_via_token():
    access_token = localAuth._create_access_token(username="rubrix")
    user = await localAuth.get_user(security_scopes=security_Scopes, token=access_token)
    assert user.username == "rubrix"


@pytest.mark.asyncio
async def test_get_user_via_api_key():
    user = await localAuth.get_user(security_scopes=security_Scopes,api_key="rubrix.apikey")
    assert user.username == "rubrix"


# Test for function find user by api key token
@pytest.mark.asyncio
async def test_get_user_by_api_key():
    user = await localAuth._find_user_by_api_key(api_key="rubrix.apikey")
    assert user.username == "rubrix"


# Test for function fetch token
def test_fetch_token_user():
    access_token = localAuth._create_access_token(username="rubrix")
    user = localAuth.fetch_token_user(token=access_token)
    assert user.username == "rubrix"

