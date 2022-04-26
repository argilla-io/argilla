from rubrix.client.sdk.client import AuthenticatedClient
from rubrix.client.sdk.commons.errors import ApiCompatibilityError, GenericApiError


class AbstractApi:
    def __init__(self, client: AuthenticatedClient):
        self.__client__ = client


def api_compatibility_check(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GenericApiError as gap:
            response = gap.ctx.get("response")
            if "Method Not Allowed" == response:
                raise ApiCompatibilityError()
            raise gap

    return inner
