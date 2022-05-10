from types import TracebackType
from typing import Optional, Tuple, Type

from rubrix.client.sdk.client import AuthenticatedClient
from rubrix.client.sdk.commons.errors import ApiCompatibilityError, GenericApiError


class AbstractApi:
    def __init__(self, client: AuthenticatedClient):
        self.__client__ = client


class _ApiCompatibilityContextManager:
    def __init__(self, min_version: Tuple[int, int, int]):
        self._min_version = min_version

    def __enter__(self):
        # TODO: If a client is provided, check minimal version against the server version
        pass

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        if not exc_val:
            return

        if isinstance(exc_val, GenericApiError):
            response = exc_val.ctx.get("response")
            if "Method Not Allowed" == response:
                raise ApiCompatibilityError(
                    ".".join(map(str, self._min_version))
                ) from exc_val
            raise exc_val


def api_compatibility(
    min_version: Tuple[int, int, int], client: Optional[AuthenticatedClient] = None
):
    """
    Handles problems related to server API compatibility.

    Args:
        min_version: the minimal version that the Rubrix client can work with
        client: An http client abstraction connecting to server instance. If provided, some extra
            checks could be applied

    """
    return _ApiCompatibilityContextManager(min_version=min_version)
