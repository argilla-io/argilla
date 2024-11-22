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
    print("Deleting webhook with url", webhook.url)
    webhook.delete()


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
@rg.webhook_listener(events=["record.deleted", "record.completed"])
async def records_listener(record: rg.Record, type: str, timestamp: datetime):
    print(f"Received event of type {type} at {timestamp} for record {record}")


@rg.webhook_listener(events=["response.created", "response.updated"])
async def responses_listener(response: rg.UserResponse, type: str, timestamp: datetime):
    print(f"Received event of type {type} at {timestamp} for response {response}")


@rg.webhook_listener(
    events=[
        "dataset.created",
        "dataset.updated",
        "dataset.published",
        "dataset.deleted",
    ]
)
async def datasets_listener(type: str, timestamp: datetime, dataset: rg.Dataset):
    print(f"Received event of type {type} at {timestamp} for dataset {dataset}")


# Set the webhook server. The server is a FastAPI instance, so you need to expose it in order to run it using uvicorn:
# ```bash
# uvicorn main:server --reload
# ```

server = rg.get_webhook_server()
