from typing import Optional

import yaml

from .model import UserInDB
from .settings import settings


class UsersDAO:
    def __init__(self, users_file: str):
        try:
            with open(users_file) as file:
                self.__users__ = yaml.safe_load(file)
        except FileNotFoundError:
            self.__users__ = {
                "admin": {
                    "username": "admin",
                    "email": "admin@example.com",
                    "full_name": "Admin user",
                    "user_group": None,
                    "hashed_password": "$2y$12$MPcRR71ByqgSI8AaqgxrMeSdrD4BcxDIdYkr.ePQoKz7wsGK7SAca",  # 1234
                    "disabled": False,
                },
                "test": {
                    "username": "test",
                    "email": "test@example.com",
                    "full_name": "Test user",
                    "user_groups": ["test"],
                    "hashed_password": "$2y$12$MPcRR71ByqgSI8AaqgxrMeSdrD4BcxDIdYkr.ePQoKz7wsGK7SAca",  # 1234
                    "disabled": False,
                },
            }

    def get_user(self, user_name: str) -> Optional[UserInDB]:
        if user_name in self.__users__:
            return UserInDB(**self.__users__[user_name])


def create_users_dao() -> UsersDAO:
    return UsersDAO(settings.users_db)
