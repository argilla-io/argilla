# Docker

This guide explains how to launch the Elasticsearch backend and Argilla Server using `docker`. Please check the setup and installation section to understand other options.

(setting-up-elasticsearch-via-docker)=
## Elasticsearch

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

## Argilla Server and UI

You can use vanilla docker to run our image of Argilla Server.
First, pull the image from the [Docker Hub](https://hub.docker.com/):

```bash
docker pull argilla/argilla-server
```

Then simply run it.
Keep in mind that you need a running Elasticsearch instance for Argilla to work.
By default, the Argilla server will look for your Elasticsearch endpoint at `http://localhost:9200`.
But you can customize this by setting the `ELASTICSEARCH` environment variable.

```bash
docker run -p 6900:6900 -e "ELASTICSEARCH=<your-elasticsearch-endpoint>" --name argilla argilla/argilla-server
```
:::{note}
By default, telemetry is enabled. This helps us to improve our product. For more info about the metrics and disabling them check [telemetry](../../reference/telemetry.md).

:::

To find running instances of the Argilla server, you can list all the running containers on your machine:

```bash
docker ps
```

To stop the Argilla server, just stop the container:

```bash
docker stop argilla
```

If you want to deploy your own Elasticsearch cluster via docker, we refer you to the excellent guide on the [Elasticsearch homepage](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html).
