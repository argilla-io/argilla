import yaml
from rubrix.server.security.auth_provider.local.settings import settings
from typing import Dict, Optional

from .model import UserInDB

_DEFAULT_USER = UserInDB(
    username="rubrix",
    hashed_password=settings.default_password,
    api_key=settings.default_apikey,
)


class UsersDAO:
    def __init__(self, users_file: str):
        self.__users__: Dict[str, UserInDB] = {}
        try:
            with open(users_file) as file:
                user_list = [
                    UserInDB(**user_data) for user_data in yaml.safe_load(file)
                ]
                self.__users__ = {user.username: user for user in user_list}
        except FileNotFoundError:
            self.__users__ = {_DEFAULT_USER.username: _DEFAULT_USER}

    def get_user(self, user_name: str) -> Optional[UserInDB]:
        """Fetch user info for a given user name"""
        if user_name in self.__users__:
            return self.__users__[user_name]

    async def get_user_by_api_key(self, api_key: str) -> Optional[UserInDB]:
        """Find a user for a given api key"""
        for user in self.__users__.values():
            if api_key == user.api_key:
                return user


_instance: Optional[UsersDAO] = None


def create_users_dao() -> UsersDAO:
    """Creates a user DAO instance based on local file user yaml db"""
    global _instance

    if _instance is None:
        _instance = UsersDAO(settings.users_db_file)
    return _instance
