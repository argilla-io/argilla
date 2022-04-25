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
from typing import Union

from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.types import Scope


class RewriteStaticFiles(StaticFiles):
    """Simple server rewrite implementation for SPI apps"""

    async def get_response(self, path: str, scope: Scope) -> Response:
        try:
            response = await super().get_response(path, scope)
            return await self._handle_response(response, scope)
        except HTTPException as ex:
            return await self._handle_response(ex, scope)

    async def _handle_response(
        self, response_or_error: Union[Response, HTTPException], scope
    ):
        if self.html and (response_or_error.status_code == 404):
            return await super().get_response(path="", scope=scope)
        if isinstance(response_or_error, HTTPException):
            raise response_or_error
        return response_or_error
