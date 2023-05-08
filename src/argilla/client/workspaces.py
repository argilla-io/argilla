#  coding=utf-8
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

from typing import TYPE_CHECKING, Optional

import argilla as rg

if TYPE_CHECKING:
    from argilla.client.api import Argilla


class Workspace:
    def __init__(self, name: Optional[str] = None) -> None:
        self.client: "Argilla" = rg.active_client()

        self.name = name or self.client.get_workspace()
        self.id = None
        for workspace in self.client.list_workspaces():
            if workspace.name == self.name:
                self.id = workspace.id
                break
        if self.id is None:
            raise ValueError(f"Workspace {self.name} not found in the current Argilla account.")
