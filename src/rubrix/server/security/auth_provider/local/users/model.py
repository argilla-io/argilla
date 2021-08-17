from rubrix.server.security.model import User


class UserInDB(User):
    """Internal user model"""

    hashed_password: str
    api_key: str
