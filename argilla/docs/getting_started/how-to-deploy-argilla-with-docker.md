---
description: Deploy Argilla with Docker
---
This guide describes how to deploy the Argilla Server with `docker compose`. This is useful if you want to deploy Argilla locally, and/or have full control over the configuration the server, database, and search engine (Elasticsearch).

First, you need to install `docker` on your machine and make sure you can run `docker compose`.

Then, create a folder (you can modify the folder name):

```console
mkdir argilla && cd argilla
```

Download `docker-compose.yaml`:

```console
wget -O docker-compose.yaml https://raw.githubusercontent.com/argilla-io/argilla/main/examples/deployments/docker/docker-compose.yaml
```

Generate a 32 character random string with:

```console
openssl rand -hex 32
```

Copy the value and modify the following line of your local `docker-compose.yaml`:

```yaml
environment:
  ARGILLA_HOME_PATH: /var/lib/argilla
  ARGILLA_ELASTICSEARCH: http://elasticsearch:9200
  ARGILLA_AUTH_SECRET_KEY: <add_generated_key_here>
```

Run to deploy the server on `http://localhost:6900`:
```console
docker compose up -d
```
Once is completed, go this URL with your browser: [http://localhost:6900](http://localhost:6900) and you should see the Argilla login page.

If it's not available, check the logs:

```console
docker compose logs -f
```

Most of the deployment issues are related to ElasticSearch. [Join Hugging Face Discord's server](http://hf.co/join/discord) and ask for support on the Argilla channel.
