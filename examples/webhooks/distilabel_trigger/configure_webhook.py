import os

import argilla as rg
from argilla._api._webhooks import WebhookModel
from standardwebhooks.webhooks import Webhook

WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL", "http://localhost.org:8000")


def configure_webhook(client: rg.Argilla, path: str) -> Webhook:
    # Configure the webhook
    for wh_model in client.api.webhooks.list():
        client.api.webhooks.delete(wh_model.id)

    model = WebhookModel(
        url=f"{WEBHOOK_BASE_URL}{path}",
        events=["record.completed"],
        description="Webhook for record completion",
    )

    webhook_model = client.api.webhooks.create(model)
    webhook = Webhook(whsecret=webhook_model.secret)

    return webhook
