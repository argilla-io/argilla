from pydantic import BaseModel


class Token(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str = "bearer"
