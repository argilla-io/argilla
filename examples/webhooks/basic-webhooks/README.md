---
title: Argilla Webhooks
emoji: 🦀
colorFrom: pink
colorTo: pink
sdk: gradio
sdk_version: 4.44.1
app_file: app.py
pinned: false
---

## Description

This space is a basic server webhooks example to show how to set up webhook listeners using the argilla SDK.

The application defines three webhook listeners for the following events:

- Record events: `record.deleted`, `record.completed`
- Dataset events: `dataset.created`, `dataset.updated`, `dataset.deleted`, `dataset.published`
- Response events: `response.created`, `response.updated`

The events are stored in a queue and displayed in the JSON component and the incoming events is updated every second.

You can view the incoming events in the JSON component below.

This application is just a demonstration of how to use the Argilla webhook listeners. You can visit the
[Argilla documentation](https://docs.argilla.io/dev/how_to_guides/webhooks) for more information.

The space is located at https://huggingface.co/spaces/argilla/argilla-webhooks

## Running the app

First create an HF space running the argilla server. Once the server is up and running, you must define the following environment variables:

- `ARGILLA_API_URL`: The URL of the argilla server.
- `ARGILLA_API_KEY`: The API key to access the argilla server.

Now, you can run the app just running the following command:

```bash
python app.py
```

## Testing the app

Open the gradio application. You can see incoming events from the argilla server.
