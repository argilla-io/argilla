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
import time
import warnings
from threading import Thread
from typing import TYPE_CHECKING, Optional, Callable, Union, List

import argilla as rg
from argilla import Argilla
from argilla.webhooks._handler import WebhookHandler
from argilla.webhooks._resource import Webhook

if TYPE_CHECKING:
    from fastapi import FastAPI

__all__ = ["webhook_listener", "get_webhook_server", "set_webhook_server", "start_webhook_server"]


def _compute_default_webhook_server_url() -> str:
    """
    Compute the webhook server URL.

    Returns:
        str: The webhook server URL. If the environment variable `SPACE_HOST` is set, it will return `https://<SPACE_HOST>`.
        Otherwise, it will return the value of the environment variable `WEBHOOK_SERVER_URL` or `http://127.0.0.1:8000`.

    """
    if space_host := os.getenv("SPACE_HOST"):
        return f"https://{space_host}"

    return os.getenv("WEBHOOK_SERVER_URL", "http://127.0.0.1:8000")


def _webhook_url_for_func(func: Callable) -> str:
    """
    Compute the full webhook URL for a given function.

    Parameters:
        func (Callable): The function to compute the webhook URL for.

    Returns:
        str: The full webhook URL.

    """
    webhook_server_url = _compute_default_webhook_server_url()

    return f"{webhook_server_url}/{func.__name__}"


def webhook_listener(
    events: Union[str, List[str]],
    description: Optional[str] = None,
    client: Optional["Argilla"] = None,
    server: Optional["FastAPI"] = None,
    raw_event: bool = False,
) -> Callable:
    """
    Decorator to create a webhook listener for a function.

    Parameters:
        events (Union[str, List[str]]): The events to listen to.
        description (Optional[str]): The description of the webhook.
        client (Optional[Argilla]): The Argilla client to use. Defaults to the default client.
        server (Optional[FastAPI]): The FastAPI server to use. Defaults to the default server.
        raw_event (bool): Whether to pass the raw event to the function. Defaults to False.

    Returns:
        Callable: The decorated function.

    """

    client = client or rg.Argilla._get_default()
    server = server or get_webhook_server()

    if isinstance(events, str):
        events = [events]

    def wrapper(func: Callable) -> Callable:
        webhook_url = _webhook_url_for_func(func)

        webhook = None
        for argilla_webhook in client.webhooks:
            if argilla_webhook.url == webhook_url and argilla_webhook.events == events:
                warnings.warn(f"Found existing webhook with for URL {argilla_webhook.url}: {argilla_webhook}")
                webhook = argilla_webhook
                webhook.description = description or webhook.description
                webhook.enabled = True
                webhook.update()
                break

        if not webhook:
            webhook = Webhook(
                url=webhook_url,
                events=events,
                description=description or f"Webhook for {func.__name__}",
            ).create()

        request_handler = WebhookHandler(webhook).handle(func, raw_event)
        server.post(f"/{func.__name__}", tags=["Argilla Webhooks"])(request_handler)

        return request_handler

    return wrapper


def get_webhook_server() -> "FastAPI":
    """
    Get the current webhook server. If it does not exist, it will create one.

    Returns:
        FastAPI: The webhook server.

    """
    from fastapi import FastAPI

    global _server
    if not _server:
        _server = FastAPI()
    return _server


def set_webhook_server(app: "FastAPI"):
    """
    Set the webhook server. This should only be called once.

    Parameters:
        app (FastAPI): The webhook server.

    """
    global _server

    if _server:
        raise ValueError("Server already set")

    _server = app


class _WebhookServerRunner:
    """
    Class to run the webhook server in a separate thread.
    """

    def __init__(self, server: "FastAPI"):
        import uvicorn

        self._server = uvicorn.Server(uvicorn.Config(app=server))
        self._thread = Thread(target=self._server.run, daemon=True)

    def start(self):
        """Start the webhook server"""
        self._thread.start()
        while not self._server.started and self._thread.is_alive():
            time.sleep(1e-3)

    def stop(self):
        """Stop the webhook server"""
        self._server.should_exit = True
        self._thread.join()


def start_webhook_server():
    """Start the webhook runner."""

    global _server_runner

    if _server_runner:
        warnings.warn("Server already started")
    else:
        server = get_webhook_server()

        _server_runner = _WebhookServerRunner(server)
        _server_runner.start()


def stop_webhook_server():
    """Stop the webhook runner."""

    global _server_runner

    if not _server_runner:
        warnings.warn("Server not started")
    else:
        try:
            _server_runner.stop()
        finally:
            _server_runner = None


_server: Optional["FastAPI"] = None
_server_runner: Optional[_WebhookServerRunner] = None
