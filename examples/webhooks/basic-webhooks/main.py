import os
from datetime import datetime

import argilla as rg

# Environment variables with defaults
API_KEY = os.environ.get("ARGILLA_API_KEY", "argilla.apikey")
API_URL = os.environ.get("ARGILLA_API_URL", "http://localhost:6900")

# Initialize Argilla client
client = rg.Argilla(api_key=API_KEY, api_url=API_URL)

# Show the existing webhooks in the argilla server
for webhook in client.webhooks:
    print(webhook.url)


# Create a webhook listener using the decorator
# This decorator will :
# 1. Create the webhook in the argilla server
# 2. Create a POST endpoint in the server
# 3. Handle the incoming requests to verify the webhook signature
# 4. Ignoring the events other than the ones specified in the `events` argument
# 5. Parse the incoming request and call the decorated function with the parsed data
#
# Each event will be passed as a keyword argument to the decorated function depending on the event type.
# The event types are:
# - record: created, updated, deleted and completed
# - response: created, updated, deleted
# - dataset: created, updated, published, deleted
# Related resources will be passed as keyword arguments to the decorated function
# (for example the dataset for a record-related event, or the record for a response-related event)
# When a resource is deleted
@rg.webhook_listener(events=["record.created", "record.completed"])
async def listen_record(
    record: rg.Record, dataset: rg.Dataset, type: str, timestamp: datetime
):
    print(f"Received record event of type {type} at {timestamp}")

    action = "completed" if type == "record.completed" else "created"
    print(f"A record with id {record.id} has been {action} for dataset {dataset.name}!")


@rg.webhook_listener(events="response.updated")
async def trigger_something_on_response_updated(response: rg.UserResponse, **kwargs):
    print(
        f"The user response {response.id} has been updated with the following responses:"
    )
    print([response.serialize() for response in response.responses])


@rg.webhook_listener(events=["dataset.created", "dataset.updated", "dataset.published"])
async def with_raw_payload(
    type: str,
    timestamp: datetime,
    dataset: rg.Dataset,
    **kwargs,
):
    print(f"Event type {type} at {timestamp}")
    print(dataset.settings)


@rg.webhook_listener(events="dataset.deleted")
async def on_dataset_deleted(
    data: dict,
    **kwargs,
):
    print(f"Dataset {data} has been deleted!")


# Set the webhook server. The server is a FastAPI instance, so you need to expose it in order to run it using uvicorn:
# ```bash
# uvicorn main:webhook_server --reload
# ```

server = rg.get_webhook_server()
