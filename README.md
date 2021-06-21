<p align="center">
    <img src="docs/images/rubrix_logo.svg" alt="drawing" width="225"/>
</p>

# Open-source tool for tracking, exploring and iterating on data for AI

<p align="center">
    <a href="https://github.com/recognai/rubrix/actions">
        <img alt="CI" src="https://github.com/recognai/rubrix/workflows/CI/badge.svg?branch=master&event=push">
    </a>
    <!--a href="https://github.com/recognai/rubrix/blob/master/LICENSE">
        <img alt="GitHub" src="https://img.shields.io/github/license/recognai/rubrix.svg?color=blue">
    </a-->
</p>


[Rubrix](https://rubrix.ml) is a tool for tracking and iterating on data for artificial intelligence projects. Rubrix focuses on enabling novel, human in the loop workflows involving data scientists, subject matter experts and ML/data engineers. 

![](docs/images/rubrix_intro.svg)

With Rubrix, you can:

- **Monitor** the predictions of deployed models.
- **Collect** ground-truth data for starting up a project or evolving an existing one.
- **Iterate** on ****ground-truth data**** and predictions to debug, track and improve your models over time.
- **Build** custom ****applications and dashboards**** on top of your model predictions.

We've tried to make working with Rubrix easy and fun, while keeping it scalable and flexible. Rubrix is composed of:

- a **web application and a REST API**, which you can launch using Docker or build it yourself.
- a **Python library** to bridge data and models, which you can install via `pip`.

For further information, please visit the [documentation](https://docs.rubrix.ml/en/stable/)

# Get started

To get started you need to follow three steps:

1. Install the Python client
2. Launch the web app
3. Start logging data
   
## 1. Install the Python client

You can install the Rubrix Python client via

```python
pip install rubrix
```

## 2. Launch the webapp

There are two ways to launch the webapp:

- Using [docker-compose](https://docs.docker.com/compose/) (**recommended**).
- Executing the server code manually

### Using docker-compose (recommended)

Create a folder:

```bash
mkdir rubrix && cd rubrix
```

and launch the docker-contained web app with the following command:

```bash
wget -O docker-compose.yml https://raw.githubusercontent.com/recognai/rubrix/master/docker-compose.yaml && docker-compose up
```

This is the recommended way because it automatically includes an
[Elasticsearch](https://www.elastic.co/elasticsearch/) instance, Rubrix's main persistent layer.

### Executing the server code manually

When executing the server code manually you need to provide an [Elasticsearch](https://www.elastic.co/elasticsearch/) instance yourself.

1. First you need to install
   [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/install-elasticsearch.html)
   (we recommend version 7.10) and launch an Elasticsearch instance.
   For MacOS and Windows there are
   [Homebrew formulae](https://www.elastic.co/guide/en/elasticsearch/reference/7.13/brew.html) and a
   [msi package](https://www.elastic.co/guide/en/elasticsearch/reference/current/windows.html), respectively.
2. Install the Rubrix Python library together with its server dependencies:

```bash
pip install rubrix[server]
```

3. Launch a local instance of the Rubrix web app

```bash
python -m rubrix.server
```

By default, the Rubrix server will look for your Elasticsearch endpoint at ``http://localhost:9200``.
If you want to customize this, you can set the ``ELASTICSEARCH`` environment variable pointing to your endpoint.

## 3. Start logging data

The following code will log one record into the `example-dataset` dataset: 

```python
import rubrix as rb

rb.log(
    rb.TextClassificationRecord(inputs="my first rubrix example"),
    name='example-dataset'
)

```

```bash
BulkResponse(dataset='example-dataset', processed=1, failed=0)
```

If you go to your Rubrix app at [http://localhost:6900/](http://localhost:6900/), you should see your first dataset.

Congratulations! You are ready to start working with Rubrix with your own data. To better understand what's possible take a look at our [Cookbook](https://docs.rubrix.ml/en/stable/guides/cookbook.html)
