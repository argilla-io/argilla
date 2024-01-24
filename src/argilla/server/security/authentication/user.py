from typing import Any

from starlette.authentication import BaseUser

from .claims import Claims


class User(BaseUser, dict):
    __slots__ = ("display_name", "identity", "picture", "email", "username")

    @property
    def is_authenticated(self) -> bool:
        return bool(self)

    def use_claims(self, claims: Claims) -> "User":
        for attr, item in claims.items():
            self[attr] = self.__getprop__(item)
        return self

    def __getprop__(self, item, default="") -> Any:
        if callable(item):
            return item(self)
        return self.get(item, default)

    __getattr__ = __getprop__
