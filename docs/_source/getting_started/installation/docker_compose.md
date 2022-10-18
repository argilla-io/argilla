
# Docker-compose

This guide explains how to run the Argilla server with Elasticsearch using `docker-compose`.

(launching-the-web-app-via-docker-compose)=
## Launching the web app via docker-compose

For this method you first need to install [Docker Compose](https://docs.docker.com/compose/install/).

Then, create a folder:

```bash
mkdir argilla && cd argilla
```

and launch the docker-contained web app with the following command:

```bash
wget -O docker-compose.yml https://raw.githubusercontent.com/recognai/rubrix/master/docker-compose.yaml && docker-compose up -d
```
:::{warning}
Latest versions of docker should be executed without the dash '-', e.g:

```bash
docker compose up -d
```
:::

This is a convenient way because it automatically includes an [Elasticsearch](https://www.elastic.co/elasticsearch/) instance, Argilla's main persistent layer.

:::{warning}
Keep in mind, if you execute
```bash
docker-compose down
```
you will lose all your datasets in Argilla!
:::

## Persisting ElasticSearch data
To avoid losing all the data when the docker-compose/server goes down, you can add some persistence by mounting a
volume in the docker compose.

To this end, **modify the elasticsearch service and create a new volume** in the docker-compse.yml file:

```yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.11.1
    container_name: elasticsearch
    environment:
      - node.name=elasticsearch
      - cluster.name=es-argilla-local
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    networks:
      - argilla
    # Add the volume to the elasticsearch service
    volumes:
      - elasticdata:/usr/share/elasticsearch/data
  argilla:
    # ... here goes the rest of the docker-compose.yaml

# ...

# At the end of the file create a volume for ElasticSearch
volumes:
  elasticdata:


```

Then, even if the ElasticSearch service goes down the data will be persisted in the elasticdata volume. To check it
you can execute the command:

```bash
docker volume ls
```

Note that if you want to apply these changes, and you already have a previous docker-compose instance running, you need
to execute the **up** command again:

```bash
docker-compose up -d
```
