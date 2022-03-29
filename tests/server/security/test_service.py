import pytest

from rubrix.server.security.auth_provider.local.users.dao import create_users_dao
from rubrix.server.security.auth_provider.local.users.service import UsersService

usersService = UsersService.get_instance(users=create_users_dao())


def test_authenticate_user():
    user = usersService.authenticate_user(username="rubrix", password="1234")
    assert user.username == "rubrix"


def test_get_user():
    user = usersService.get_user(username="rubrix")
    assert user.username == "rubrix"


@pytest.mark.asyncio
async def test_find_user_by_api_key():
    user = await usersService.find_user_by_api_key(api_key="rubrix.apikey")
    assert user.username == "rubrix"
