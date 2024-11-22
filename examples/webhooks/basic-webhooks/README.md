## Description

This is a basic webhook example to show how to configure webhook listeners using the argilla SDK

The application defines three webhook listeners for the following events:

- Record events: `record.deleted`, `record.completed`
- Dataset events: `dataset.created`, `dataset.updated`, `dataset.published`, `dataset.deleted`
- Response events: `response.created`, `response.updated`

You can visit the [Argilla documentation](https://docs.argilla.io/dev/how_to_guides/webhooks) for more information.

## Running the app

This example is intended to be used locally. You can check [this space](https://huggingface.co/spaces/argilla/argilla-webhooks)
for a remote example.

First, you must start the argilla server. We recommend you to use the docker installation. You can run the following commands to start the argilla server:
```bash
mkdir argilla && cd argilla
curl https://raw.githubusercontent.com/argilla-io/argilla/main/examples/deployments/docker/docker-compose.yaml -o docker-compose.yaml
docker compose up -d
```

For more information on how to install the argilla server, please refer to the [argilla documentation](https://docs.argilla.io/latest/getting_started).

Once the argilla server is up and running, start the webhook server by running the following command:

```bash
ARGILLA_API_KEY=argilla.apikey \
WEBHOOK_SERVER_URL=http://host.docker.internal:8000 \
uvicorn main:server
```

The `ARGILLA_API_KEY` environment variable should be set to the API key of the argilla server.
The `WEBHOOK_SERVER_URL` environment variable should be set to the URL where the webhook server is running.
In this case, we are using `http://host.docker.internal:8000` because the webhook calls will be done inside a docker container.

The application will remove all existing webhook listeners and create new ones for the events mentioned above.

## Testing the app

When you start working with the argilla server, you can see the logs in the webhook server.
You can test the webhook listeners by creating, updating, and deleting datasets, responses and records in the argilla server.
