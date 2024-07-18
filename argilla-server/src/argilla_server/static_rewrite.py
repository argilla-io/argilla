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
import os
import stat
from typing import Union

import anyio
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.responses import FileResponse, RedirectResponse, Response
from starlette.types import Scope


class RewriteStaticFiles(StaticFiles):
    """Simple server rewrite implementation for SPI apps"""

    async def get_response(self, path: str, scope: Scope) -> Response:
        try:
            response = await self._get_response_internal(path, scope)
            if response.status_code == 307:
                return RedirectResponse(url=f"{scope['path']}/")
            return await self._handle_response(response, scope)
        except HTTPException as ex:
            return await self._handle_response(ex, scope)

    async def _handle_response(
        self,
        response_or_error: Union[Response, HTTPException],
        scope,
    ):
        if self.html and (response_or_error.status_code == 404):
            return await super().get_response(path="index.html", scope=scope)
        if isinstance(response_or_error, HTTPException):
            raise response_or_error
        return response_or_error

    async def _get_response_internal(self, path: str, scope: Scope) -> Response:
        """
        Returns an HTTP response, given the incoming path, method and request headers.

        This method is the same as the one in the parent class, but it handles folder path
        without trailing slash differently. Instead of returning a 307 response, it returns
        a 200 response with the content of the folder index file.
        """
        if scope["method"] not in ("GET", "HEAD"):
            raise HTTPException(status_code=405)

        try:
            full_path, stat_result = await anyio.to_thread.run_sync(self.lookup_path, path)
        except PermissionError:
            raise HTTPException(status_code=401)
        except OSError:
            raise

        if stat_result and stat.S_ISREG(stat_result.st_mode):
            # We have a static file to serve.
            return self.file_response(full_path, stat_result, scope)

        elif stat_result and stat.S_ISDIR(stat_result.st_mode) and self.html:
            # We're in HTML mode, and have got a directory URL.
            # Check if we have 'index.html' file to serve.
            index_path = os.path.join(path, "index.html")
            full_path, stat_result = await anyio.to_thread.run_sync(self.lookup_path, index_path)
            if stat_result is not None and stat.S_ISREG(stat_result.st_mode):
                return self.file_response(full_path, stat_result, scope)

        if self.html:
            # Check for '404.html' if we're in HTML mode.
            full_path, stat_result = await anyio.to_thread.run_sync(self.lookup_path, "404.html")
            if stat_result and stat.S_ISREG(stat_result.st_mode):
                return FileResponse(full_path, stat_result=stat_result, status_code=404)
        raise HTTPException(status_code=404)
