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

__all__ = ["WebhooksAPI"]

from typing import List

import httpx

from argilla._api._base import ResourceAPI
from argilla._exceptions import api_error_handler
from argilla._models._webhook import WebhookModel


class WebhooksAPI(ResourceAPI[WebhookModel]):
    http_client: httpx.Client
    url_stub = "/api/v1/webhooks"

    @api_error_handler
    def list(self) -> List[WebhookModel]:
        """
        Get a list of all webhooks

        Returns:
            List[WebhookModel]: List of webhooks

        """
        response = self.http_client.get(url=self.url_stub)
        response.raise_for_status()
        response_json = response.json()
        webhooks = self._model_from_jsons(json_data=response_json["items"])
        self._log_message(message=f"Got {len(webhooks)} webhooks")
        return webhooks

    @api_error_handler
    def create(self, webhook: WebhookModel) -> WebhookModel:
        """
        Create a webhook

        Args:
            webhook (WebhookModel): Webhook to create

        Returns:
            WebhookModel: Created webhook

        """
        response = self.http_client.post(
            url=self.url_stub,
            json={
                "url": webhook.url,
                "events": webhook.events,
                "description": webhook.description,
            },
        )
        response.raise_for_status()
        response_json = response.json()
        webhook = self._model_from_json(json_data=response_json)
        self._log_message(message=f"Created webhook with id {webhook.id}")
        return webhook

    @api_error_handler
    def delete(self, webhook_id: str) -> None:
        """
        Delete a webhook

        Args:
            webhook_id (str): ID of the webhook to delete

        """
        response = self.http_client.delete(url=f"{self.url_stub}/{webhook_id}")
        response.raise_for_status()
        self._log_message(message=f"Deleted webhook with id {webhook_id}")

    @api_error_handler
    def update(self, webhook: WebhookModel) -> WebhookModel:
        """
        Update a webhook

        Args:
            webhook (WebhookModel): Webhook to update

        Returns:
            WebhookModel: Updated webhook

        """
        response = self.http_client.patch(url=f"{self.url_stub}/{webhook.id}", json=webhook.model_dump())
        response.raise_for_status()
        response_json = response.json()
        webhook = self._model_from_json(json_data=response_json)
        self._log_message(message=f"Updated webhook with id {webhook.id}")
        return webhook

    @api_error_handler
    def ping(self, webhook_id: str) -> None:
        """
        Ping a webhook

        Args:
            webhook_id (str): ID of the webhook to ping

        """
        response = self.http_client.post(url=f"{self.url_stub}/{webhook_id}/ping")
        response.raise_for_status()
        self._log_message(message=f"Pinged webhook with id {webhook_id}")

    @staticmethod
    def _model_from_json(json_data: dict) -> WebhookModel:
        return WebhookModel.model_validate(json_data)

    def _model_from_jsons(self, json_data: List[dict]) -> List[WebhookModel]:
        return list(map(self._model_from_json, json_data))
