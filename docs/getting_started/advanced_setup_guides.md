(advanced-setup-guides)=
# Advanced setup guides

Here we provide some setup guides for an advanced usage of Rubrix.

(setting-up-elasticsearch-via-docker)=
## Setting up Elasticsearch via docker

Setting up Elasticsearch (ES) via docker is straightforward.
Simply run the following command:

```bash
docker run -d --name elasticsearch-for-rubrix -p 9200:9200 -p 9300:9300 -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch-oss:7.10.2
```

This will create an ES docker container named *"elasticsearch-for-rubrix"* that will run in the background.

To see the logs of the container, you can run:

```bash
docker logs elasticsearch-for-rubrix
```

Or you can stop/start the container via:

```bash
docker stop elasticsearch-for-rubrix
docker start elasticsearch-for-rubrix
```

:::{warning}
Keep in mind, if you remove your container with
```bash
docker rm elasticsearch-for-rubrix
```
you will loose all your datasets in Rubrix!
:::

For more details about the ES installation with docker, see their [official documentation](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/docker.html).
For MacOS and Windows, Elasticsearch also provides [homebrew formulae](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/brew.html) and a [msi package](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/windows.html), respectively.
We recommend ES version 7.10 to work with Rubrix.


(server-configurations)=
## Server configurations

By default, the Rubrix server will look for your ES endpoint at `http://localhost:9200`.
But you can customize this by setting the `ELASTICSEARCH` environment variable.
Have a look at the list of available [environment variables](#environment-variables) to further configure the Rubrix server.

Since the Rubrix server is built on fastapi, you can launch it using **uvicorn** directly:

```bash
uvicorn rubrix:app
```

:::{note}

For Rubrix versions below 0.9 you can launch the server via
```bash
uvicorn rubrix.server.server:app
```
:::

For more details about fastapi and uvicorn, see [here](https://fastapi.tiangolo.com/deployment/manually/#run-a-server-manually-uvicorn).

Fastapi also provides beautiful REST API docs that you can check at [http://localhost:6900/api/docs](http://localhost:6900/api/docs).

### Environment variables

You can set following environment variables to further configure your server and client.

#### Server

- `ELASTICSEARCH`: URL of the connection endpoint of the Elasticsearch instance (Default: `http://localhost:9200`).

- `RUBRIX_ELASTICSEARCH_SSL_VERIFY`: If "False", disables SSL certificate verification when connection to the Elasticsearch backend.

- `RUBRIX_ELASTICSEARCH_CA_PATH`: Path to CA cert for ES host. For example: `/full/path/to/root-ca.pem` (Optional)

- `RUBRIX_NAMESPACE`: A prefix used to manage Elasticsearch indices. You can use this namespace to use the same Elasticsearch instance for several independent Rubrix instances.

- `RUBRIX_DEFAULT_ES_SEARCH_ANALYZER`: Default analyzer for textual fields excluding the metadata (Default: "standard").

- `RUBRIX_EXACT_ES_SEARCH_ANALYZER`: Default analyzer for `*.exact` fields in textual information (Default: "whitespace").

- `METADATA_FIELDS_LIMIT`: Max number of fields in the metadata (Default: 50, max: 100).

- `CORS_ORIGINS`: List of host patterns for CORS origin access.

- `DOCS_ENABLED`: If False, disables openapi docs endpoint at */api/docs*.

#### Client

- `RUBRIX_API_URL`: The default API URL when calling {meth}`rubrix.init`.

- `RUBRIX_API_KEY`: The default API key when calling {meth}`rubrix.init`.

- `RUBRIX_WORKSPACE`: The default workspace when calling {meth}`rubrix.init`.



(launching-the-web-app-via-docker)=
## Launching the web app via docker

You can use vanilla docker to run our image of the web app.
First, pull the image from the [Docker Hub](https://hub.docker.com/):

```bash
docker pull recognai/rubrix
```

Then simply run it.
Keep in mind that you need a running Elasticsearch instance for Rubrix to work.
By default, the Rubrix server will look for your Elasticsearch endpoint at `http://localhost:9200`.
But you can customize this by setting the `ELASTICSEARCH` environment variable.

```bash
docker run -p 6900:6900 -e "ELASTICSEARCH=<your-elasticsearch-endpoint>" --name rubrix recognai/rubrix
```

To find running instances of the Rubrix server, you can list all the running containers on your machine:

```bash
docker ps
```

To stop the Rubrix server, just stop the container:

```bash
docker stop rubrix
```

If you want to deploy your own Elasticsearch cluster via docker, we refer you to the excellent guide on the [Elasticsearch homepage](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html).

(launching-the-web-app-via-docker-compose)=
## Launching the web app via docker-compose

For this method you first need to install [Docker Compose](https://docs.docker.com/compose/install/).

Then, create a folder:

```bash
mkdir rubrix && cd rubrix
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

This is a convenient way because it automatically includes an [Elasticsearch](https://www.elastic.co/elasticsearch/) instance, Rubrix's main persistent layer.

:::{warning}
Keep in mind, if you execute
```bash
docker-compose down
```
you will lose all your datasets in Rubrix!
:::

### Persisting ElasticSearch data
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
      - cluster.name=es-rubrix-local
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    networks:
      - rubrix
    # Add the volume to the elasticsearch service
    volumes:
      - elasticdata:/usr/share/elasticsearch/data
  rubrix:
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


(configure-elasticsearch-role-users)=
## Configure Elasticsearch role/users

If you have an Elasticsearch instance and want to share resources with other applications, you can easily configure it for Rubrix.

All you need to take into account is:


* Rubrix will create its ES indices with the following pattern `.rubrix*`. It's recommended to create a new role (e.g., rubrix) and provide it with all privileges for this index pattern.

* Rubrix creates an index template for these indices, so you may provide related template privileges to this ES role.

Rubrix uses the `ELASTICSEARCH` environment variable to set the ES connection.

You can provide the credentials using the following scheme:

```bash
http(s)://user:passwd@elastichost
```

Below you can see a screenshot for setting up a new *rubrix* Role and its permissions:

![Rubrix Role and permissions in ES](https://user-images.githubusercontent.com/2518789/142883104-f4f20cf0-34a0-47ff-8ee3-ab9f4644271c.png)


### Change elasticsearch index analyzers

By default, for indexing text fields, Rubrix uses the `standard` analyzer for general search and the `whitespace`
analyzer for more exact queries (required by certain rules in the weak supervision module). If those analyzers
don't fit your use case, you can change them using the following environment variables:
`RUBRIX_DEFAULT_ES_SEARCH_ANALYZER` and `RUBRIX_EXACT_ES_SEARCH_ANALYZER`.

Note that provided analyzers names should be defined as built-in ones. If you want to use a
customized analyzer, you should create it inside an index_template matching Rubrix index names (`.rubrix*.records-v0),
and then provide the analyzer name using the specific environment variable.

(deploy-to-aws-instance-using-docker-machine)=
## Deploy to aws instance using docker-machine

### Setup an AWS profile

The `aws` command cli must be installed. Then, type:

```bash
aws configure --profile rubrix
```

and follow command instructions. For more details, visit [AWS official documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html).

Once the profile is created (a new entry should appear in file `~/.aws/config`), you can activate it via setting environment variable:

```bash
export AWS_PROFILE=rubrix
```

### Create docker machine (aws)

```bash
docker-machine create --driver amazonec2 \
--amazonec2-root-size 60 \
--amazonec2-instance-type t2.large \
--amazonec2-open-port 80 \
--amazonec2-ami ami-0b541372 \
--amazonec2-region eu-west-1 \
rubrix-aws
```

Available ami depends on region. The provided ami is available for eu-west regions

### Verify machine creation

```bash
$>docker-machine ls

NAME                   ACTIVE   DRIVER      STATE     URL                        SWARM   DOCKER     ERRORS
rubrix-aws             -        amazonec2   Running   tcp://52.213.178.33:2376           v20.10.7
```

### Save asigned machine ip

In our case, the assigned ip is `52.213.178.33`

### Connect to remote docker machine

To enable the connection between the local docker client and the remote daemon, we must type following command:

```bash
eval $(docker-machine env rubrix-aws)
```

### Define a docker-compose.yaml

{{ dockercomposeyaml }}

### Pull image

```bash
docker-compose pull
```

### Launch docker container

```bash
docker-compose up -d
```

### Accessing Rubrix

In our case http://52.213.178.33


(install-from-master)=
## Install from master

If you want the cutting-edge version of *Rubrix* with the latest changes and experimental features, follow the steps below in your terminal.
**Be aware that this version might be unstable!**

First, you need to install the master version of our python client:

```bash
 pip install -U git+https://github.com/recognai/rubrix.git
```

Then, the easiest way to get the master version of our web app up and running is via docker-compose:

:::{note}
For now, we only provide the master version of our web app via docker.
If you want to run the web app of the master branch **without** docker, we refer you to our [development setup](development-setup).
:::

```bash
 # get the docker-compose yaml file
 mkdir rubrix && cd rubrix
 wget -O docker-compose.yml https://raw.githubusercontent.com/recognai/rubrix/master/docker-compose.yaml
 # use the master image of the rubrix container instead of the latest
 sed -i 's/rubrix:latest/rubrix:master/' docker-compose.yml
 # start all services
 docker-compose up
 ```

If you want to use vanilla docker (and have your own Elasticsearch instance running), you can just use our master image:

```bash
docker run -p 6900:6900 -e "ELASTICSEARCH=<your-elasticsearch-endpoint>" --name rubrix recognai/rubrix:master
```
