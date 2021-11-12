from typing import List, Optional

from pydantic import BaseModel


class User(BaseModel):
    """User data model"""

    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    workspaces: List[str] = None

