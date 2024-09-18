# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from typing import TYPE_CHECKING, Optional, Callable, Union, List

import argilla as rg
from argilla import Argilla
from argilla.webhooks._resource import Webhook
from argilla.webhooks._handler import WebhookHandler

if TYPE_CHECKING:
    from fastapi import FastAPI

WEBHOOK_SERVER_URL = os.getenv("WEBHOOK_SERVER_URL", "http://localhost.org:8000")


def _webhook_url_for_func(func: Callable) -> str:
    return f"{WEBHOOK_SERVER_URL}/{func.__name__}"


def get_webhook_server() -> "FastAPI":
    from fastapi import FastAPI

    global _server
    if not _server:
        _server = FastAPI()
    return _server


def set_webhook_server(app: "FastAPI"):
    global _server

    if _server:
        raise ValueError("Server already set")

    _server = app


_server: Optional["FastAPI"] = None


def webhook_listener(
    events: Union[str, List[str]],
    description: Optional[str] = None,
    client: Optional["Argilla"] = None,
    server: Optional["FastAPI"] = None,
    raw_event: bool = False,
) -> Callable:
    client = client or rg.Argilla._get_default()
    server = server or get_webhook_server()

    if isinstance(events, str):
        events = [events]

    def decorator(func: Callable) -> Callable:
        webhook_url = _webhook_url_for_func(func)

        webhook = None
        for argilla_webhook in client.webhooks:
            if webhook_url == argilla_webhook.url:
                webhook = argilla_webhook
                break

        if webhook:
            webhook.description = description or webhook.description
            webhook.events = events
            webhook.update()
        else:
            webhook = Webhook(
                url=webhook_url,
                events=events,
                description=description or f"Webhook for {func.__name__}",
            ).create()

        request_handler = WebhookHandler(webhook).handle(func, raw_event)
        server.post(f"/{func.__name__}", tags=["Argilla Webhooks"])(request_handler)

        return request_handler

    return decorator
