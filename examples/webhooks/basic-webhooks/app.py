import os
from datetime import datetime
from queue import Queue

import argilla as rg
import gradio as gr

client = rg.Argilla()

server = rg.get_webhook_server()
incoming_events = Queue()

# Set up the webhook listeners

# Delete all existing webhooks
for webhook in client.webhooks:
    print(f"Deleting webhook: {webhook.url}")
    webhook.delete()


# Create a webhook for record events
@rg.webhook_listener(events=["record.deleted", "record.completed"])
async def record_events(record: rg.Record, type: str, timestamp: datetime):
    print(f"Received event type {type} at {timestamp}: ", record)

    incoming_events.put({"event": type, "data": record})


# Create a webhook for dataset events
@rg.webhook_listener(
    events=[
        "dataset.created",
        "dataset.updated",
        "dataset.deleted",
        "dataset.published",
    ]
)
async def dataset_events(dataset: rg.Dataset, type: str, timestamp: datetime):
    print(f"Received event type {type} at {timestamp}: ", dataset)

    incoming_events.put({"event": type, "data": dataset})


# Create a webhook for response events
@rg.webhook_listener(events=["response.created", "response.updated"])
async def response_events(response: rg.UserResponse, type: str, timestamp: datetime):
    print(f"Received event type {type} at {timestamp}: ", response)

    incoming_events.put({"event": type, "data": response})


def read_next_event():
    event = incoming_events.get()

    return event


with gr.Blocks() as demo:
    argilla_server = client.http_client.base_url
    gr.Markdown("## Argilla Events")
    gr.Markdown(f"""
        This demo shows the incoming events from the [Argilla Server]({argilla_server}).

        The application defines three webhook listeners for the following events:
        - Record events: `record.created`, `record.updated`, `record.deleted`, `record.completed`
        - Dataset events: `dataset.created`, `dataset.updated`, `dataset.deleted`, `dataset.published`
        - Response events: `response.created`, `response.updated`

        The events are stored in a queue and displayed in the JSON component and the incoming events is updated every second.

        You can view the incoming events in the JSON component below.

        This application is just a demonstration of how to use the Argilla webhook listeners.

        You can visit the [Argilla documentation](https://docs.argilla.io/dev/how_to_guides/webhooks) for more information.
    """)
    json_component = gr.JSON(label="Incoming argilla events:", value={})
    gr.Timer(1, active=True).tick(read_next_event, outputs=json_component)

gr.mount_gradio_app(server, demo, path="/")

# Start the FastAPI server
import uvicorn

uvicorn.run(server, host="0.0.0.0", port=7860)
