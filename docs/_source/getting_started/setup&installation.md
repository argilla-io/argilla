(setup-and-installation)=
# Setup and installation

In this guide, we will help you to get up and running with Argilla.
Basically, you need to:

1. Install Argilla
2. Launch the web app
3. Start logging data

## 1. Install Argilla

First, make sure you have Python 3.7 or above installed.

Then you can install Argilla with `pip` or `conda`.

**with pip**

{{ '```bash\npip install "argilla[server]{}"\n```'.format(pipversion) }}

**with conda**

{{ '```bash\nconda install -c conda-forge "argilla-server{}"\n```'.format(pipversion) }}

(launch-the-web-app)=
## 2. Launch the web app

Argilla uses [Elasticsearch (ES)](https://www.elastic.co/elasticsearch/) as its main persistent layer.
**If you do not have an ES instance running on your machine**, we recommend setting one up via docker:

```bash
docker run -d --name elasticsearch-for-argilla -p 9200:9200 -p 9300:9300 -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch-oss:7.10.2
```

:::{note}
For more details about setting up ES via docker, check our [advanced setup guide](setting-up-elasticsearch-via-docker).
:::

You can start the Argilla web app via Python.

```bash
python -m argilla
```

Afterward, you should be able to access the web app at [http://localhost:6900/](http://localhost:6900/).
**The default username and password are** `argilla` **and** `1234` (see the [user management guide](user-management.ipynb) to configure this).

:::{note}
You can also launch the web app via [docker](launching-the-web-app-via-docker) or [docker-compose](launching-the-web-app-via-docker-compose).
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

**Congratulations! You are ready to start working with Argilla.**

## Next steps

Have a look at our [advanced setup guides](advanced-setup-guides) if you want to (among other things):

- [setup Elasticsearch (ES) via docker](setting-up-elasticsearch-via-docker)
- [configure the Argilla server](server-configurations)
- [share an ES instance with other applications](configure-elasticsearch-role-users)
- [deploy Argilla on an AWS instance](deploy-to-aws-instance-using-docker-machine)

To continue learning we recommend you to:

* Check our **Guides** and **Tutorials**;
* Read about Argilla's main [concepts](concepts.md);
