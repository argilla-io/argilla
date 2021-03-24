from typing import Any, Dict

from pydantic import BaseModel


class ApiInfo(BaseModel):
    """Basic api info"""

    rubrix_version: str


class ApiStatus(ApiInfo):
    """The Rubrix api status model"""

    elasticsearch: Dict[str, Any]
    mem_info: Dict[str, Any]
