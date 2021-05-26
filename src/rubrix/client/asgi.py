import datetime
import json
import logging
import re
import threading
from queue import Queue
from typing import Any, Callable, Dict, List, Optional, Tuple

import rubrix
from rubrix import Record, TextClassificationRecord, TokenClassificationRecord
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.types import Message, Receive

_logger = logging.getLogger(__name__)
_spaces_regex = re.compile(r"\s+")


def token_classification_mapper(inputs, outputs):
    text = inputs.get("text", "")
    tokens = outputs.get("tokens") if isinstance(outputs, dict) else None
    return TokenClassificationRecord(
        text=text,
        tokens=tokens or _spaces_regex.split(text),
        prediction=[
            (entity["label"], entity["start"], entity["end"])
            for entity in (
                outputs.get("entities") if isinstance(outputs, dict) else outputs
            )
        ],
        event_timestamp=datetime.datetime.now(),
    )


def text_classification_mapper(inputs, outputs):
    return TextClassificationRecord(
        inputs=inputs,
        prediction=[
            (label, score)
            for label, score in zip(
                outputs.get("labels", []), outputs.get("probabilities", [])
            )
        ],
        event_timestamp=datetime.datetime.now(),
    )


class CachedJsonRequest(Request):
    """
    We must a cached version of incoming requests since request body cannot be read from middleware directly.
    See <https://github.com/encode/starlette/issues/847> for more information

    TODO Remove usage of CachedRequest when https://github.com/encode/starlette/pull/848 is released
    """

    @property
    def receive(self) -> Receive:
        body = None
        if hasattr(self, "_body"):
            body = self._body
        if body is not None:

            async def cached_receive() -> Message:
                return dict(type="http.request", body=body)

            return cached_receive
        return self._receive


class RubrixLogHTTPMiddleware(BaseHTTPMiddleware):
    """An standard starlette middleware that enables rubrix logs for http prediction requests"""

    def __init__(
        self,
        api_endpoint: str,
        dataset: str,
        records_mapper: Optional[Callable[[dict, dict], Record]] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._endpoint = api_endpoint
        self._dataset = dataset
        self._records_mapper = records_mapper or text_classification_mapper
        self._queue = Queue()
        self._worker_task = threading.Thread(
            target=self.__worker__, name=RubrixLogHTTPMiddleware.__name__, daemon=True
        )
        self._worker_task.start()

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if self._endpoint != request.url.path:  # Filtering endpoint path
            return await call_next(request)

        content_type = request.headers.get("Content-type", None)
        if "application/json" not in content_type:
            return await call_next(request)

        cached_request = CachedJsonRequest(
            scope=request.scope, receive=request.receive, send=request._send
        )
        # Must read body before call_next
        inputs = await cached_request.json()
        response: Response = await call_next(cached_request)
        try:
            if (
                not isinstance(response, (JSONResponse, StreamingResponse))
                or response.status_code >= 400
            ):
                return response

            new_response, outputs = await self._extract_response_content(response)
            self._queue.put_nowait((inputs, outputs, str(request.url)))
            return new_response
        except Exception as ex:
            _logger.error("Cannot log to rubrix", exc_info=ex)
            return response

    def __worker__(self):
        while True:
            try:
                inputs, outputs, url = self._queue.get()
                self._log_to_rubrix(inputs, outputs, url)
            except Exception as ex:
                # Run thread FOREVER!!!
                _logger.error("Error sending records to rubrix", exc_info=ex)
            finally:
                self._queue.task_done()

    async def _extract_response_content(
        self, response: Response
    ) -> Tuple[Response, List[Dict[str, Any]]]:
        """Extracts response body content from response and returns a new processable response"""
        body = b""
        new_response = response
        if isinstance(response, StreamingResponse):
            async for chunk in response.body_iterator:
                body += chunk
            new_response = StreamingResponse(
                content=(chunk for chunk in [body]),
                status_code=response.status_code,
                headers={k: v for k, v in response.headers.items()},
                media_type=response.media_type,
                background=response.background,
            )
        else:
            body = response.body
        return new_response, json.loads(body)

    def _log_to_rubrix(
        self,
        inputs: List[Dict[str, Any]],
        outputs: List[Dict[str, Any]],
        url: str,
        **tags
    ):
        records = [
            record
            for _inputs, _outputs in zip(inputs, outputs)
            for record in [self._records_mapper(_inputs, _outputs)]
            if record
        ]

        if records:
            for r in records:
                r.prediction_agent = url
            rubrix.log(records=records, name=self._dataset, tags=tags)
