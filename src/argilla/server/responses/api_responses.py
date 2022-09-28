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

from starlette.responses import JSONResponse, StreamingResponse
from starlette.types import Send

from argilla.server.errors import APIErrorHandler


class StreamingResponseWithErrorHandling(StreamingResponse):
    async def stream_response(self, send: Send) -> None:
        try:
            return await super().stream_response(send)
        except Exception as ex:
            json_response: JSONResponse = (
                await APIErrorHandler.common_exception_handler(send, error=ex)
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": json_response.body,
                    "more_body": False,
                }
            )
