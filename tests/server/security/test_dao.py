import pytest

from rubrix.server.security.auth_provider.local.users.service import create_users_dao

usersDAO = create_users_dao()


# Test for function get_user class UserInDB
def test_get_user():
    user = usersDAO.get_user(user_name="rubrix")
    assert user.username == "rubrix"


# Test for function get_user_by_api_key class UserInDB
@pytest.mark.asyncio
async def test_get_user_by_api_key():
    user = await usersDAO.get_user_by_api_key(api_key="rubrix.apikey")
    assert user.username == "rubrix"
