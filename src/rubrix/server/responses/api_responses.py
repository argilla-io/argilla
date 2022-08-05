from starlette.responses import JSONResponse, StreamingResponse
from starlette.types import Send

from rubrix.server.errors import APIErrorHandler


class StreamingResponseWithErrorHandling(StreamingResponse):

    async def stream_response(self, send: Send) -> None:
        try:
            return await super().stream_response(send)
        except Exception as ex:
            json_response: JSONResponse = await APIErrorHandler.common_exception_handler(send, error=ex)
            await send({"type": "http.response.body", "body": json_response.body, "more_body": False})