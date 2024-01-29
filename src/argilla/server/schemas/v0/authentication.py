from typing import Annotated

from fastapi import Form

from argilla.server.pydantic_v1 import BaseModel


class UserPasswordRequestForm:
    """User password request form."""

    def __init__(self, *, username: Annotated[str, Form()], password: Annotated[str, Form()]):
        self.username = username
        self.password = password


class Token(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str = "bearer"
