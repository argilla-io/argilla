from pathlib import Path
from tests.pydantic_v1 import PYDANTIC_MAJOR_VERSION


def pytest_ignore_collect(path: Path, **kwargs) -> bool:
    """
    This function ignore server and integration related tests when pydantic v2 is detected since
    the server side is not pydantic v2 compatible
    """
    for ignore_pattern in ["**/unit/server/**", "**/integration/**"]:
        if Path(path).match(ignore_pattern):
            return PYDANTIC_MAJOR_VERSION == 2
    return False
