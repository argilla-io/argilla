(setup-and-installation)=
# Setup and installation

In this guide, we will help you to get up and running with Rubrix.
Basically, you need to:

1. Install Rubrix
2. Launch the web app
3. Start logging data

## 1. Install Rubrix

First, make sure you have Python 3.7 or above installed.

Then you can install Rubrix with `pip` or `conda`.

**with pip**

{{ '```bash\npip install "rubrix[server]{}"\n```'.format(pipversion) }}

**with conda**

{{ '```bash\nconda install -c conda-forge "rubrix-server{}"\n```'.format(pipversion) }}

(launch-the-web-app)=
## 2. Launch the web app

Rubrix uses [Elasticsearch (ES)](https://www.elastic.co/elasticsearch/) as its main persistent layer.
**If you do not have an ES instance running on your machine**, we recommend setting one up via docker:

```bash
docker run -d --name elasticsearch-for-rubrix -p 9200:9200 -p 9300:9300 -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch-oss:7.10.2
```

:::{note}
For more details about setting up ES via docker, check our [advanced setup guide](setting-up-elasticsearch-via-docker).
:::

You can start the Rubrix web app via Python.

```bash
python -m rubrix
```

Afterward, you should be able to access the web app at [http://localhost:6900/](http://localhost:6900/).
**The default username and password are** `rubrix` **and** `1234` (see the [user management guide](user-management.ipynb) to configure this).

:::{note}
You can also launch the web app via [docker](launching-the-web-app-via-docker) or [docker-compose](launching-the-web-app-via-docker-compose).
For the latter you do not need a running ES instance.
:::

## 3. Start logging data

The following code will log one record into a data set called `example-dataset`:

```python
import rubrix as rb

rb.log(
    rb.TextClassificationRecord(text="My first Rubrix example"),
    name='example-dataset'
)
```

If you now go to your Rubrix app at [http://localhost:6900/](http://localhost:6900/), you will find your first data set.

**Congratulations! You are ready to start working with Rubrix.**

## Next steps

Have a look at our [advanced setup guides](advanced-setup-guides) if you want to (among other things):

- [setup Elasticsearch (ES) via docker](setting-up-elasticsearch-via-docker)
- [configure the Rubrix server](server-configurations)
- [share an ES instance with other applications](configure-elasticsearch-role-users)
- [deploy Rubrix on an AWS instance](deploy-to-aws-instance-using-docker-machine)

To continue learning we recommend you to:

* Check our **Guides** and **Tutorials**;
* Read about Rubrix's main [concepts](concepts.md);
