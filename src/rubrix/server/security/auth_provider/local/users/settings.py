"""
User environment variables settings definition
"""
from pydantic import BaseSettings


class UsersSettings(BaseSettings):
    """
    The Api users settings

    Attributes
    ----------

    users_db:
        Database users file.

    """


settings = UsersSettings()
