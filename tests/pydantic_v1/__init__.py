from importlib import metadata

try:
    from pydantic.v1 import *  # noqa: F403
except ImportError:
    from pydantic import *  # noqa: F403

try:
    PYDANTIC_MAJOR_VERSION: int = int(metadata.version("pydantic").split(".")[0])
except metadata.PackageNotFoundError:
    PYDANTIC_MAJOR_VERSION = 0
