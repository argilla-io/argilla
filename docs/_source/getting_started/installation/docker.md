# Docker

Here we provide some setup guides for an advanced usage of Argilla.

(setting-up-elasticsearch-via-docker)=
## Setting up Elasticsearch

Setting up Elasticsearch (ES) via docker is straightforward.
Simply run the following command:

```bash
docker run -d --name elasticsearch-for-argilla -p 9200:9200 -p 9300:9300 -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch-oss:7.10.2
```

This will create an ES docker container named *"elasticsearch-for-argilla"* that will run in the background.

To see the logs of the container, you can run:

```bash
docker logs elasticsearch-for-argilla
```

Or you can stop/start the container via:

```bash
docker stop elasticsearch-for-argilla
docker start elasticsearch-for-argilla
```

:::{warning}
Keep in mind, if you remove your container with
```bash
docker rm elasticsearch-for-argilla
```
you will loose all your datasets in Argilla!
:::

For more details about the ES installation with docker, see their [official documentation](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/docker.html).
For MacOS and Windows, Elasticsearch also provides [homebrew formulae](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/brew.html) and a [msi package](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/windows.html), respectively.
We recommend ES version 7.10 to work with Argilla.


(server-configurations)=
## Server configurations

By default, the Argilla server will look for your ES endpoint at `http://localhost:9200`.
But you can customize this by setting the `ELASTICSEARCH` environment variable.
Have a look at the list of available [environment variables](#environment-variables) to further configure the Argilla server.

Since the Argilla server is built on fastapi, you can launch it using **uvicorn** directly:

```bash
uvicorn argilla:app
```

:::{note}

For Argilla versions below 0.9 you can launch the server via
```bash
uvicorn argilla.server.server:app
```
:::

For more details about fastapi and uvicorn, see [here](https://fastapi.tiangolo.com/deployment/manually/#run-a-server-manually-uvicorn).

Fastapi also provides beautiful REST API docs that you can check at [http://localhost:6900/api/docs](http://localhost:6900/api/docs).

### Environment variables

You can set following environment variables to further configure your server and client.

#### Server

- `ELASTICSEARCH`: URL of the connection endpoint of the Elasticsearch instance (Default: `http://localhost:9200`).

- `ARGILLA_ELASTICSEARCH_SSL_VERIFY`: If "False", disables SSL certificate verification when connection to the Elasticsearch backend.

- `ARGILLA_ELASTICSEARCH_CA_PATH`: Path to CA cert for ES host. For example: `/full/path/to/root-ca.pem` (Optional)

- `ARGILLA_NAMESPACE`: A prefix used to manage Elasticsearch indices. You can use this namespace to use the same Elasticsearch instance for several independent Argilla instances.

- `ARGILLA_DEFAULT_ES_SEARCH_ANALYZER`: Default analyzer for textual fields excluding the metadata (Default: "standard").

- `ARGILLA_EXACT_ES_SEARCH_ANALYZER`: Default analyzer for `*.exact` fields in textual information (Default: "whitespace").

- `METADATA_FIELDS_LIMIT`: Max number of fields in the metadata (Default: 50, max: 100).

- `CORS_ORIGINS`: List of host patterns for CORS origin access.

- `DOCS_ENABLED`: If False, disables openapi docs endpoint at */api/docs*.

#### Client

- `ARGILLA_API_URL`: The default API URL when calling {meth}`argilla.init`.

- `ARGILLA_API_KEY`: The default API key when calling {meth}`argilla.init`.

- `ARGILLA_WORKSPACE`: The default workspace when calling {meth}`argilla.init`.



(launching-the-web-app-via-docker)=
## Launching the web app

You can use vanilla docker to run our image of the web app.
First, pull the image from the [Docker Hub](https://hub.docker.com/):

```bash
docker pull argilla/argilla
```

Then simply run it.
Keep in mind that you need a running Elasticsearch instance for Argilla to work.
By default, the Argilla server will look for your Elasticsearch endpoint at `http://localhost:9200`.
But you can customize this by setting the `ELASTICSEARCH` environment variable.

```bash
docker run -p 6900:6900 -e "ELASTICSEARCH=<your-elasticsearch-endpoint>" --name argilla argilla/argilla
```

To find running instances of the Argilla server, you can list all the running containers on your machine:

```bash
docker ps
```

To stop the Argilla server, just stop the container:

```bash
docker stop argilla
```

If you want to deploy your own Elasticsearch cluster via docker, we refer you to the excellent guide on the [Elasticsearch homepage](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html).
