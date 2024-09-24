---
description: In this section, we will provide a step-by-step guide to create a webhook in Argilla.
---

# Use Argilla webhooks

This guide provides an overview of how to create and use webhooks in Argilla.

A **webhook** allows an application to submit real-time information to other applications whenever a specific event occurs. Unlike traditional APIs, you won’t need to poll for data very frequently in order to get it in real time. This makes webhooks much more efficient for both the provider and the consumer.

## Creating a webhook listener in Argilla

The python SDK provides a simple way to create a webhook in Argilla. It allows you to focus on the use case of the webhook and not on the implementation details. You only need to create your event handler function with the `webhook_listener` decorator.

```python
import argilla as rg

from datetime import datetime
from argilla import webhook_listener

@webhook_listener(events="dataset.created")
async def my_webhook_handler(dataset: rg.Dataset, type: str, timestamp: datetime):
    print(dataset, type, timestamp)
```

In the example above, we have created a webhook that listens to the `dataset.created` event.
> You can find the list of events in the [Events](#events) section.

The python SDK will automatically create a webhook in Argilla and listen to the specified event. When the event is triggered,
the `my_webhook_handler` function will be called with the event data. The SDK will also parse the incoming webhook event into
a proper resource object (`rg.Dataset`, `rg.Record`, and `rg.Response`). The SDK will also take care of request authentication and error handling.

## Running the webhook server

Under the hood, the SDK uses the `FastAPI` framework to create the webhook server and the POST endpoint to receive the webhook events.

To run the webhook, you need to define the webhook server in your code and start it using the `uvicorn` command.

```python
from argilla import get_webhook_server

server = get_webhook_server()
```

```bash
uvicorn my_webhook:server
```

You can explore the Swagger UI to explore your defined webhooks by visiting `http://localhost:8000/docs`.


The `uvicorn` command will start the webhook server on the default port `8000`.

By default, the Python SDK will register the webhook using the server URL `http://127.0.0.1:8000/`. If you want to use a different server URL, you can set the `WEBHOOK_SERVER_URL` environment variable.

```bash
export WEBHOOK_SERVER_URL=http://my-webhook-server.com
```

All incoming webhook events will be sent to the specified server URL.

## Webhooks management

The Python SDK provides a simple way to manage webhooks in Argilla. You can create, list, update, and delete webhooks using the SDK.

### Create a webhook

To create a new webhook in Argilla, you can define it in the `Webhook` class and then call the `create` method.

```python
import argilla as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

webhook = rg.Webhook(
    url="https://my-webhook-server.com",
    events=["dataset.created"],
    description="My webhook"
)

webhook.create()

```

### List webhooks

You can list all the existing webhooks in Argilla by accessing the `webhooks` attribute on the Argilla class and iterating over them.

```python
import argilla as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

for webhook in client.webhooks:
    print(webhook)

```

### Update a webhook

You can update a webhook using the `update` method.

```python
import argilla as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

webhook = rg.Webhook(
    url="http://127.0.0.1:8000",
    events=["dataset.created"],
    description="My webhook"
).create()

webhook.events = ["dataset.updated"]
webhook.update()

```
> You should use IP address instead of localhost since the webhook validation expect a Top Level Domain (TLD) in the URL.

### Delete a webhook

You can delete a webhook using the `delete` method.

```python
import argilla as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

for webhook in client.webhooks:
    webhook.delete()

```

## Deploying a webhooks server in a Hugging Face Space

You can deploy your webhook in a Hugging Face Space. You can visit this [link](https://huggingface.co/spaces/frascuchon/argilla-webhooks/tree/main)
to expore an example of a webhook server deployed in a Hugging Face Space.


## Events

The following is a list of events that you can listen to in Argilla, grouped by resource type.

### Dataset events

- `dataset.created`: The Dataset resource was created.
- `dataset.updated`: The Dataset resource was updated.
- `dataset.deleted`: The Dataset resource was deleted.
- `dataset.published`: The Dataset resource was published.

### Record events
- `record.created`: The Record resource was created.
- `record.updated`: The Record resource was updated.
- `record.deleted`: The Record resource was deleted.
- `record.completed`: The Record resource was completed (status="completed").

### Response events
- `response.created`: The Response resource was created.
- `response.updated`: The Response resource was updated.
- `response.deleted`: The Response resource was deleted.