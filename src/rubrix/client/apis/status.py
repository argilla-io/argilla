import dataclasses
from types import TracebackType
from typing import ContextManager, Optional, Type

from packaging.version import parse
from pydantic import BaseModel

from rubrix.client.apis import AbstractApi
from rubrix.client.sdk.client import AuthenticatedClient
from rubrix.client.sdk.commons.errors import ApiCompatibilityError


@dataclasses.dataclass(frozen=True)
class ApiInfo:

    rubrix_version: str


class Status(AbstractApi):
    class _ApiInfo(BaseModel):
        rubrix_version: str

    def get_info(self) -> ApiInfo:
        """
        Get the connected API info

        """

        response = self.__client__.get("/api/_info")
        api_info = self._ApiInfo.parse_obj(response)
        return ApiInfo(rubrix_version=api_info.rubrix_version)


class _ApiCompatibilityContextManager(ContextManager):
    def __init__(self, client: AuthenticatedClient, min_version: str):
        self._min_version = parse(min_version)
        self._status_api = Status(client=client) if client else None

    def __enter__(self):
        if self._status_api:
            api_info = self._status_api.get_info()
            api_version = parse(api_info.rubrix_version)
            if api_version.is_devrelease:
                api_version = parse(api_version.base_version)
            if not api_version >= self._min_version:
                raise ApiCompatibilityError(str(self._min_version))
        pass

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        pass


def api_compatibility(api: AbstractApi, min_version: str):
    """
    Handles problems related to server API compatibility.

    Args:
        api: The api component where apply the api compatibility
        min_version: the minimal version that the Rubrix client can work with

    """
    return _ApiCompatibilityContextManager(
        min_version=min_version, client=api.__client__
    )
