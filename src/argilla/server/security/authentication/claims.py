#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from typing import Any, Callable, Union


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
