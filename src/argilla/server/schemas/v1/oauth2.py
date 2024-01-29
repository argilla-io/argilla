from typing import List

from pydantic import BaseModel


class Provider(BaseModel):
    name: str


class Providers(BaseModel):
    items: List[Provider]


class Token(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str = "bearer"
