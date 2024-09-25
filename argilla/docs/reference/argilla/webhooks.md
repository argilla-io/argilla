---
hide: footer
---

# `argilla.webhooks`

Webhooks are a way for web applications to notify each other when something happens. For example, you might want to be
notified when a new dataset is created in Argilla.

## Usage Examples

To listen for incoming webhooks, you can use the `webhook_listener` decorator function to register a function to be called
when a webhook is received:

```python
from argilla.webhooks import webhook_listener

@webhook_listener(events="dataset.created")
async def my_webhook_listener(dataset):
    print(dataset)
```

To manually create a new webhook, instantiate the `Webhook` object with the client and the name:

```python
webhook = rg.Webhook(
    url="https://somehost.com/webhook",
    events=["dataset.created"],
    description="My webhook"
)
webhook.create()
```

To retrieve a list of existing webhooks, use the `client.webhooks` attribute:

```python
for webhook in client.webhooks():
    print(webhook)
```

---

::: src.argilla.webhooks._resource.Webhook
    options:
        heading_level: 4

::: src.argilla.webhooks._helpers.webhook_listener
    options:
        heading_level: 4
        hide: footer

::: src.argilla.webhooks._helpers.get_webhook_server
    options:
        heading_level: 4
        hide: footer

::: src.argilla.webhooks._helpers.set_webhook_server
    options:
        heading_level: 4
        hide: footer

::: src.argilla.webhooks._handler.WebhookHandler
    options:
        heading_level: 4
        hide: footer

::: src.argilla.webhooks._event.WebhookEvent
    options:
        heading_level: 4
        hide: footer

::: src.argilla.webhooks._event.DatasetEvent
    options:
        heading_level: 4
        hide: footer

::: src.argilla.webhooks._event.RecordEvent
    options:
        heading_level: 4
        hide: footer

::: src.argilla.webhooks._event.UserResponseEvent
    options:
        heading_level: 4
        hide: footer

