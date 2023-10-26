from typing import Optional

from pydantic import BaseModel


class VectorSettings(BaseModel):
    name: str
    dimensions: int
    # TODO Uncomment when is supported
    # title: Optional[str] = None


