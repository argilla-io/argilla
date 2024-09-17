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

from typing import List, Optional


from argilla import Argilla
from argilla._api._webhooks import WebhookModel, WebhooksAPI
from argilla._resource import Resource


class Webhook(Resource):
    """
    Webhook resource.
    """

    _model: WebhookModel
    _api: WebhooksAPI

    def __init__(self, url: str, events: List[str], description: Optional[str] = None, _client: Argilla = None):
        client = _client or Argilla._get_default()
        api = client.api.webhooks
        events = events or []

        super().__init__(api=api, client=client)

        self._model = WebhookModel(url=url, events=list(events), description=description)

    @property
    def url(self) -> str:
        return self._model.url

    @url.setter
    def url(self, value: str):
        self._model.url = value

    @property
    def events(self) -> List[str]:
        return self._model.events

    @events.setter
    def events(self, value: List[str]):
        self._model.events = value

    @property
    def enabled(self) -> bool:
        return self._model.enabled

    @enabled.setter
    def enabled(self, value: bool):
        self._model.enabled = value

    @property
    def description(self) -> Optional[str]:
        return self._model.description

    @description.setter
    def description(self, value: Optional[str]):
        self._model.description = value

    @property
    def secret(self) -> str:
        return self._model.secret

    @classmethod
    def from_model(cls, model: WebhookModel, client: Optional["Argilla"] = None) -> "Webhook":
        instance = cls(url=model.url, events=model.events, _client=client)
        instance._model = model

        return instance
