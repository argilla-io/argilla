## Description

[This space](https://huggingface.co/spaces/argilla/argilla-webhooks) is a basic server webhooks example to show how to set up webhook listeners using the argilla SDK.

The application defines three webhook listeners for the following events:

- Record events: `record.deleted`, `record.completed`
- Dataset events: `dataset.created`, `dataset.updated`, `dataset.deleted`, `dataset.published`
- Response events: `response.created`, `response.updated`

The events are stored in a queue and displayed in the JSON component and the incoming events is updated every second.

You can view the incoming events in the JSON component below.

This application is just a demonstration of how to use the Argilla webhook listeners. You can visit the
[Argilla documentation](https://docs.argilla.io/dev/how_to_guides/webhooks) for more information.

## Running the app

First create an HF space running the argilla server. Be sure the space is public.

Once the server is up and running, you duplicate the space and configure the following environment variables:

- `ARGILLA_API_URL`: The URL of the argilla server.
- `ARGILLA_API_KEY`: The API key to access the argilla server.

## Testing the app

Open the gradio application. You can see incoming events from the argilla server.
