(setup-and-installation)=
# Setup and installation

In this guide, we will help you to get up and running with Argilla.
Basically, you need to:

1. Install Argilla
2. Launch the web app
3. Start logging data

## 1. Install Argilla

First, make sure you have Python 3.7 or above installed.

Then you can install Argilla with `pip`:

{{ '```bash\npip install "argilla[server]{}"\n```'.format(pipversion) }}

## 2. Install Elasticsearch or Opensearch
You need to launch Argilla's database. Argilla supports to backend databases: Elasticsearch and Opensearch.

If you don’t have Elasticsearch (ES) or Opensearch running we recommend you to install [Docker Desktop](https://www.docker.com/products/docker-desktop/) for your plattform.

<div class="alert alert-info">

Note

Check the [setup and installation section](./installation/installation.md) for further options and configurations regarding Elasticsearch and Opensearch.
</div>

Now you can launch Elasticsearch or Opensearch using `docker compose` as follows:

### Opensearch
You can launch Opensearch with Docker as follows:
```bash

mkdir argilla & cd argilla
wget https://raw.githubusercontent.com/argilla-io/argilla/main/docker-compose.opensearch.yaml
docker-compose up -d

```

Alternatively, you can download the [docker-compose](https://raw.githubusercontent.com/argilla-io/argilla/main/docker-compose.opensearch.yaml) manually and then run:

```bash

docker-compose -f docker-compose.opensearch.yaml up

```

### Elasticsearch
You can launch Elasticsearch with Docker as follows:
```bash

mkdir argilla & cd argilla
wget https://raw.githubusercontent.com/argilla-io/argilla/main/docker-compose.elasticsearch.yaml
docker-compose up -d

```
Alternatively, you can download the [docker-compose](https://raw.githubusercontent.com/argilla-io/argilla/main/docker-compose.elasticsearch.yaml) manually and then run:

```bash

docker-compose -f docker-compose.elasticsearch.yaml up

```


(launch-the-web-app)=
## 3. Launch Argilla Server


You can start the Argilla Server and UI by running:

```bash

python -m argilla

```

Afterward, you should be able to access the Argilla UI at [http://localhost:6900/](http://localhost:6900/).
**The default username and password are** `argilla` **and** `1234` (see the [user management guide](user-management.ipynb) to configure this).

:::{note}
You can also launch the Argilla Server and UI using [docker](launching-the-web-app-via-docker) or [docker-compose](launching-the-web-app-via-docker-compose).
For the latter you do not need a running ES instance.
:::

## 3. Start logging data

The following code will log one record into a data set called `example-dataset`:

```python
import argilla as rg

rg.log(
    rg.TextClassificationRecord(text="My first Argilla example"),
    name='example-dataset'
)
```

If you now go to your Argilla app at [http://localhost:6900/](http://localhost:6900/), you will find your first data set.


```{toctree}
:maxdepth: 2
:hidden:

deployments/deployments.md
configurations/configurations.md
```