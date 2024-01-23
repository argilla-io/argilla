from typing import Any
from typing import Callable
from typing import Union


class Claims(dict):
    """Claims configuration for a single provider."""

    display_name: Union[str, Callable[[dict], Any]]
    identity: Union[str, Callable[[dict], Any]]
    picture: Union[str, Callable[[dict], Any]]
    email: Union[str, Callable[[dict], Any]]

    def __init__(self, seq=None, **kwargs) -> None:
        super().__init__(seq or {}, **kwargs)
        self["display_name"] = kwargs.get("display_name", self.get("display_name", "name"))
        self["identity"] = kwargs.get("identity", self.get("identity", "sub"))
        self["picture"] = kwargs.get("picture", self.get("picture", "picture"))
        self["email"] = kwargs.get("email", self.get("email", "email"))
