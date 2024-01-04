try:
    from pydantic.v1.errors import *  # noqa: F403
except ImportError:
    from pydantic.errors import *  # noqa: F403

