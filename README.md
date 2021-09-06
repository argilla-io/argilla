
<p align="left">
    <img src="docs/images/rubrix_logo.svg" alt="drawing" width="200" style="height: 100px"/>
</p>

<p align="left">
    <a href="https://github.com/recognai/rubrix/actions">
        <img alt="CI" src="https://github.com/recognai/rubrix/workflows/CI/badge.svg?branch=master&event=push">
    </a>
    <img alt="Codecov" src="https://img.shields.io/codecov/c/github/recognai/rubrix">
    <a href="https://pypi.org/project/rubrix/">
        <img alt="CI" src="https://img.shields.io/pypi/v/rubrix.svg?style=flat-square&logo=pypi&logoColor=white">
    </a>
    <a href="https://pypi.org/project/rubrix/">
        <img alt="CI" src="https://static.pepy.tech/personalized-badge/rubrix?period=month&units=international_system&left_color=grey&right_color=blue&left_text=pypi%20downloads/month">
    </a>
        <a href="https://hub.docker.com/r/recognai/rubrix">
        <img alt="CI" src="https://img.shields.io/docker/pulls/recognai/rubrix">
    </a>
    <a href="https://github.com/ambv/black">
        <img alt="CI" src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square">
    </a>
    <a href="https://twitter.com/recogn_ai">
        <img alt="CI" src="https://img.shields.io/twitter/follow/recogn_ai.svg?style=social&label=Follow">
    </a>
    <!--img alt="CI" src="https://img.shields.io/docker/v/recognai/rubrix?sort=semver"-->
    
</p>

## What is Rubrix?

Rubrix is a **production-ready Python framework for exploring, annotating, and managing data** in NLP projects. 

Key features:

- **Open**: Rubrix is free, open-source, and 100% compatible with major NLP libraries (Hugging Face transformers, spaCy, Stanford Stanza, Flair, etc.). In fact, you can **use and combine your preferred libraries** without implementing any specific interface.

- **End-to-end**: Most annotation tools see data collection as a one-off activity at the beginning of each project. In real-world projects, data collection is a key activity of the iterative ML development process. Once a model goes into production, you want to monitor and analyze its predictions and collect more data to improve your model over time. Rubrix is designed to close this gap, enabling you to **iterate as much you need**.

- **User and Developer Experience**: The key to sustainable NLP solutions is to make it easier for everyone to contribute to projects. *Domain experts* should feel comfortable interpreting and annotating data. *Data scientists* should feel free to experiment and iterate. *Engineers* should feel in control of data pipelines. Rubrix optimizes the experience for these core users to **make your teams more productive**. 

- **Beyond hand labeling workflows**: Classical hand labeling workflows are costly and inefficient, but human supervision is essential. Easily combine active learning, bulk-labeling, zero-shot models, and weak-supervision into **novel data annotation workflows**.


## Example

This is an example for logging model predictions from a 🤗 transformers text classification pipeline:

![Rubrix Intro](https://github.com/recognai/rubrix-materials/raw/main/zeroshot.gif)


```python
from transformers import pipeline
from datasets import load_dataset
import rubrix as rb

model = pipeline('zero-shot-classification', model="typeform/squeezebert-mnli")

dataset = load_dataset("ag_news", split='test[0:100]')

# Our labels are: ['World', 'Sports', 'Business', 'Sci/Tech']
labels = dataset.features["label"].names

for record in dataset:
    prediction = model(record['text'], labels)

    item = rb.TextClassificationRecord(
        inputs=record["text"],
        prediction=list(zip(prediction['labels'], prediction['scores'])),
        annotation=labels[record["label"]]
    )

    rb.log(item, name="ag_news_zeroshot")
```

## Components

Rubrix is composed of:

- a **Python library** to bridge data and models, which you can install via `pip`.
- a **web application** to explore and label data, which you can launch using Docker or directly with Python.

![](docs/images/rubrix_intro.svg)

## Quick links

| Doc | Description |
|---|---|
| 🚶 **[First steps](https://rubrix.rtfd.io/en/stable/index.html#first-steps-with-rubrix)**    | New to Rubrix and want to get started? |
| 👩‍🏫 **[Concepts](https://rubrix.rtfd.io/en/stable/getting_started/concepts.html)**   | Want to know more about Rubrix concepts? |
| 🛠️ **[Setup and install](https://rubrix.rtfd.io/en/stable/getting_started/setup%26installation.html)**  | How to configure and install Rubrix |
| 🗒️ **[Tasks](https://rubrix.rtfd.io/en/stable/getting_started/supported_tasks.html)**  | What can you use Rubrix for? |
| 📱 **[UI reference](https://rubrix.rtfd.io/en/stable/reference/rubrix_webapp_reference.html)** | How to use the web-app for data exploration and annotation |
| 🐍 **[Python API docs](https://rubrix.rtfd.io/en/stable/reference/python_client_api.html)** | How to use the Python classes and methods |
| 👩‍🍳 **[Rubrix cookbook](https://rubrix.rtfd.io/en/stable/guides/cookbook.html)**   | How to use Rubrix with your favourite libraries (`flair`, `stanza`...)  |
| 👋 **[Community forum](https://github.com/recognai/rubrix/discussions)**   | Ask questions, share feedback, ideas and suggestions  |
| 🤗 **[Hugging Face tutorial](https://rubrix.rtfd.io/en/stable/tutorials/01-huggingface.html)** | Using Rubrix with 🤗`transformers` and `datasets` |
| 💫 **[spaCy tutorial](https://rubrix.rtfd.io/en/stable/tutorials/02-spacy.html)** | Using `spaCy` with Rubrix for NER projects |
| 🐠 **[Weak supervision tutorial](https://rubrix.rtfd.io/en/stable/tutorials/04-snorkel.html)** | How to leverage weak supervision with `snorkel` & Rubrix |
| 🤔 **[Active learning tutorial](https://rubrix.rtfd.io/en/stable/tutorials/05-active_learning.html)** | How to use active learning with `modAL` & Rubrix |
| 🧪 **[Knowledge graph tutorial](https://rubrix.rtfd.io/en/stable/tutorials/03-kglab_pytorch_geometric.html)** | How to use Rubrix with `kglab` & `pytorch_geometric` |

## Get started

To get started you need to follow three steps:

1. Install the Python client
2. Launch the web app
3. Start logging data
   
### 1. Install the Python client

You can install the Python client with `pip`:

```bash
pip install rubrix
```

### 2. Launch the web app

There are two ways to launch the webapp:

- a) Using [docker-compose](https://docs.docker.com/compose/) (**recommended**).
- b) Executing the server code manually

#### a) Using docker-compose (recommended)

Create a folder:

```bash
mkdir rubrix && cd rubrix
```

and launch the docker-contained web app with the following command:

```bash
wget -O docker-compose.yml https://git.io/rb-docker && docker-compose up
```

This is the recommended way because it automatically includes an
[Elasticsearch](https://www.elastic.co/elasticsearch/) instance, Rubrix's main persistence layer.

#### b) Executing the server code manually

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
But you can customize this by setting the ``ELASTICSEARCH`` environment variable.

### 3. Start logging data

The following code will log one record into a data set called `example-dataset`:

```python
import rubrix as rb

rb.log(
    rb.TextClassificationRecord(inputs="My first Rubrix example"),
    name='example-dataset'
)
```

If you go to your Rubrix app at http://localhost:6900/, you should see your first dataset.
**The default username and password are ``rubrix`` and ``1234``**.
You can also check the REST API docs at http://localhost:6900/api/docs.

Congratulations! You are ready to start working with Rubrix.

To better understand what's possible take a look at Rubrix's [Cookbook](https://rubrix.rtfd.io/en/stable/guides/cookbook.html)

## Community
As a new open-source project, we are eager to hear your thoughts, fix bugs, and help you get started. Feel free to use the Discussion forum or the Issues and we'll be pleased to help out.
