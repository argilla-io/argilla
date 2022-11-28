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
import datetime
import json
import logging
import re
from typing import Any, Callable, Dict, List, Optional, Tuple

from argilla.monitoring.base import BaseMonitor

try:
    import starlette
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "'starlette' must be installed to use the middleware feature! "
        "You can install 'starlette' with the command: `pip install starlette>=0.13.0`"
    )
else:
    from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
    from starlette.requests import Request
    from starlette.responses import JSONResponse, Response, StreamingResponse
    from starlette.types import Message, Receive

from argilla.client.models import (
    Record,
    TextClassificationRecord,
    TokenClassificationRecord,
)

_logger = logging.getLogger(__name__)
_default_tokenization_pattern = re.compile(r"\W+")


def token_classification_mapper(inputs, outputs):
    if isinstance(inputs, str):
        text = inputs
    elif isinstance(inputs, dict):
        text = inputs.get("text", "")
    else:
        text = ""
    tokens = outputs.get("tokens") if isinstance(outputs, dict) else None
    return TokenClassificationRecord(
        text=text,
        tokens=tokens or _default_tokenization_pattern.split(text),
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
                outputs.get("labels", []), outputs.get("scores", [])
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


class ArgillaLogHTTPMiddleware(BaseHTTPMiddleware):
    """An standard starlette middleware that enables argilla logs for http prediction requests"""

    def __init__(
        self,
        api_endpoint: str,
        dataset: str,
        records_mapper: Optional[Callable[[dict, dict], Record]],
        sample_rate: float = 1.0,
        log_interval: float = 1.0,
        agent: Optional[str] = None,
        tags: Dict[str, str] = None,
        *args,
        **kwargs
    ):
        BaseHTTPMiddleware.__init__(self, *args, **kwargs)

        self._endpoint = api_endpoint
        self._dataset = dataset
        self._records_mapper = records_mapper
        self._monitor_cfg = dict(
            dataset=dataset,
            sample_rate=sample_rate,
            log_interval=log_interval,
            agent=agent,
            tags=tags,
        )
        self._monitor: Optional[BaseMonitor] = None

    def init(self):
        if self._monitor:
            return
        from argilla.client.api import active_api

        self._monitor = BaseMonitor(
            self,
            api=active_api(),
            **self._monitor_cfg,
        )
        self._monitor._prepare_log_data = self._prepare_argilla_data

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        self.init()

        if self._endpoint != request.url.path:  # Filtering endpoint path
            return await call_next(request)

        cached_request = CachedJsonRequest(
            scope=request.scope,
            receive=request.receive,
            send=request._send,
        )

        try:
            # Must obtain input parameters from request
            if cached_request.method in ["POST", "PUT"]:
                content_type = request.headers.get("Content-type", None)
                if content_type is None:
                    if "application/json" not in content_type:
                        return await call_next(request)
                inputs = await cached_request.json()
            elif cached_request.method == "GET":
                inputs = cached_request.query_params._dict
            else:
                raise NotImplementedError(
                    "Only request methods POST, PUT and GET are implemented."
                )

            # Must obtain response from request
            response: Response = await call_next(cached_request)
            if (
                not isinstance(response, (JSONResponse, StreamingResponse))
                or response.status_code >= 400
            ):
                return response

            new_response, outputs = await self._extract_response_content(response)
            self._monitor.send_records(inputs=inputs, outputs=outputs)
            return new_response
        except Exception as ex:
            _logger.error("Cannot log to argilla", exc_info=ex)
            return await call_next(request)

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

    def _prepare_argilla_data(
        self, inputs: List[Dict[str, Any]], outputs: List[Dict[str, Any]], **tags
    ):
        # using the base monitor, we only need to provide the input data to the rg.log function
        # and the monitor will handle the sample rate, queue and argilla interaction
        try:
            records = self._records_mapper(inputs, outputs)
            assert records, ValueError(
                "The records_mapper returns and empty record list."
            )
            if not isinstance(records, list):
                records = [records]
        except Exception as ex:
            records = []
            _logger.error(
                "Cannot log to argilla. Error in records mapper.", exc_info=ex
            )

        for record in records:
            if self._monitor.agent is not None and not record.prediction_agent:
                record.prediction_agent = self._monitor.agent

        return dict(
            records=records or [],
            name=self._dataset,
            tags=tags,
        )
