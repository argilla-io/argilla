try:
    from pydantic.v1.generics import *  # noqa: F403
except ImportError:
    from pydantic.generics import *  # noqa: F403

