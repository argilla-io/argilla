
![](docs/images/og_rubrix.png)

<br/>

<div align="center">
    <h3><a href="https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g"> 👩🏾‍💻 Join the community on Slack</a>
    | <a href="https://docs.rubrix.ml">📚 Docs</a>
| <a href="https://github.com/recognai/rubrix/#get-started">🚀 Get started</a>
    | <a href="https://github.com/recognai/rubrix/#quick-links">🔗 Quick links</a></h3>
</div>


<br/>
<br/>

<p align="center">
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
    <!--a href="https://anaconda.org/conda-forge/rubrix">
        <img alt="CI" src="https://img.shields.io/conda/pn/conda-forge/rubrix?logo=anaconda&style=flat">
    </a-->
    <a href="https://anaconda.org/conda-forge/rubrix">
        <img alt="CI" src="https://img.shields.io/conda/vn/conda-forge/rubrix?logo=anaconda&style=flat&color=orange">
    </a>
    <a href="https://rubrix.readthedocs.io/en/stable/">
        <img alt="CI" src="https://img.shields.io/static/v1?logo=readthedocs&style=flat&color=pink&label=docs&message=rubrix">
    </a>
    <!--a href="https://github.com/ambv/black">
        <img alt="CI" src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square">
    </a-->
    <a href="https://twitter.com/rubrixml">
        <img alt="CI" src="https://img.shields.io/twitter/follow/rubrixml.svg?style=social&label=Follow">
    </a>
    <!--img alt="CI" src="https://img.shields.io/docker/v/recognai/rubrix?sort=semver"-->

</p>




## What is Rubrix?

Rubrix is a **production-ready Python framework for exploring, annotating, and managing data** in NLP projects.

Why Rubrix?

- **Open**: Rubrix is free, open-source, and 100% compatible with major NLP libraries (Hugging Face transformers, spaCy, Stanford Stanza, Flair, etc.). In fact, you can **use and combine your preferred libraries** without implementing any specific interface.

- **End-to-end**: Most annotation tools treat data collection as a one-off activity at the beginning of each project. In real-world projects, data collection is a key activity of the iterative process of ML model development. Once a model goes into production, you want to monitor and analyze its predictions, and collect more data to improve your model over time. Rubrix is designed to close this gap, enabling you to **iterate as much as you need**.

- **User and Developer Experience**: The key to sustainable NLP solutions is to make it easier for everyone to contribute to projects. _Domain experts_ should feel comfortable interpreting and annotating data. _Data scientists_ should feel free to experiment and iterate. _Engineers_ should feel in control of data pipelines. Rubrix optimizes the experience for these core users to **make your teams more productive**.

- **Beyond hand-labeling**: Classical hand labeling workflows are costly and inefficient, but having humans-in-the-loop is essential. Easily combine hand-labeling with active learning, bulk-labeling, zero-shot models, and weak-supervision in **novel data annotation workflows**.

## Example

Interactive weak supervision. Building a news classifier with user search queries:

https://user-images.githubusercontent.com/15979778/167146590-72d8f7b1-f94d-45a6-9896-1525cf949efe.mp4

Check the [tutorial](https://rubrix.readthedocs.io/en/master/tutorials/weak-supervision-with-rubrix.html) for more details.


## Features

### Advanced NLP labeling

- Programmatic labeling using Weak Supervision. Built-in label models (Snorkel, Flyingsquid)
- Bulk-labeling and search-driven annotation
- Iterate on training data with any pre-trained model or library
- Efficiently review and refine annotations in the UI and with Python
- Use Rubrix built-in metrics and methods for finding label and data errors (e.g., cleanlab)
- Simple integration with active learning workflows

### Monitoring

- Close the gap between production data and data collection activities
- Auto-monitoring for major NLP libraries and pipelines (spaCy, Hugging Face, FlairNLP)
- ASGI middleware for HTTP endpoints
- Rubrix Metrics to understand data and model issues, like entity consistency for NER models
- Integrated with Kibana for custom dashboards

### Team workspaces

- Bring different users and roles into the NLP data and model lifecycles
- Organize data collection, review and monitoring into different workspaces
- Manage workspace access for different users

## Get started

Getting started with Rubrix is as easy as:

```bash
pip install "rubrix[server]"
```

If you don't have [Elasticsearch (ES)](https://www.elastic.co/elasticsearch) running, make sure you have `Docker` installed and run:

> :information_source: **Check [our documentation](https://rubrix.readthedocs.io/en/stable/getting_started/setup%26installation.html) for further options and configurations regarding Elasticsearch.**

```bash
docker run -d --name elasticsearch-for-rubrix -p 9200:9200 -p 9300:9300 -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch-oss:7.10.2
```

Then simply run:

```bash
python -m rubrix
```

Afterward, you should be able to access the web app at http://localhost:6900/.
**The default username and password are** `rubrix` **and** `1234`.

> 🆕 **Rubrix Cloud Beta**: Use Rubrix on a scalable cloud infrastructure without installing the server. [Join the waiting list](https://www.rubrix.ml/rubrix-cloud/)

The following code will log one record into a dataset called `example-dataset`:

```python
import rubrix as rb

rb.log(
    rb.TextClassificationRecord(text="My first Rubrix example"),
    name='example-dataset'
)
```

If you go to your Rubrix web app at http://localhost:6900/, you should see your first dataset.

**Congratulations! You are ready to start working with Rubrix.** You can continue reading for a working example below.

To better understand what's possible take a look at Rubrix's [Cookbook](https://rubrix.rtfd.io/en/stable/guides/cookbook.html)

## Quick links

| Doc                                                                                                                     | Description                                                            |
| ----------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| 🚶 **[First steps](https://rubrix.rtfd.io/en/stable/index.html#first-steps-with-rubrix)**                               | New to Rubrix and want to get started?                                 |
| 👩‍🏫 **[Concepts](https://rubrix.rtfd.io/en/stable/getting_started/concepts.html)**                                       | Want to know more about Rubrix concepts?                               |
| 🛠️ **[Setup and install](https://rubrix.rtfd.io/en/stable/getting_started/setup%26installation.html)**                  | How to configure and install Rubrix                                    |
| 🗒️ **[Tasks](https://rubrix.rtfd.io/en/stable/getting_started/supported_tasks.html)**                                   | What can you use Rubrix for?                                           |
| 📱 **[Web app reference](https://rubrix.readthedocs.io/en/stable/reference/webapp/index.html)**                         | How to use the web-app for data exploration and annotation             |
| 🐍 **[Python client API](https://rubrix.readthedocs.io/en/stable/reference/python/index.html)**                         | How to use the Python classes and methods                              |
| 👩‍🍳 **[Rubrix cookbook](https://rubrix.rtfd.io/en/stable/guides/cookbook.html)**                                         | How to use Rubrix with your favourite libraries (`flair`, `stanza`...) |
| 👋 **[Community forum](https://github.com/recognai/rubrix/discussions)**                                                | Ask questions, share feedback, ideas and suggestions                   |
| 🤗 **[Hugging Face tutorial](https://rubrix.readthedocs.io/en/master/tutorials/01-labeling-finetuning.html)**           | Using `Hugging Face` transformers with Rubrix for text classification  |
| 💫 **[spaCy tutorial](https://rubrix.rtfd.io/en/stable/tutorials/02-spacy.html)**                                       | Using `spaCy` with Rubrix for NER projects                             |
| 🐠 **[Weak supervision tutorial](https://rubrix.readthedocs.io/en/master/tutorials/weak-supervision-with-rubrix.html)** | How to leverage weak supervision with `snorkel` & Rubrix               |
| 🤔 **[Active learning tutorial](https://rubrix.rtfd.io/en/stable/tutorials/05-active_learning.html)**                   | How to use active learning with `modAL` & Rubrix                       |

## Example

Let's see Rubrix in action with a quick example: _Bootstraping data annotation with a zero-shot classifier_

**Why**:

- The availability of pre-trained language models with zero-shot capabilities means you can, sometimes, accelerate your data annotation tasks by pre-annotating your corpus with a pre-trained zeroshot model.
- The same workflow can be applied if there is a pre-trained "supervised" model that fits your categories but needs fine-tuning for your own use case. For example, fine-tuning a sentiment classifier for a very specific type of message.

**Ingredients**:

- A zero-shot classifier from the 🤗 Hub: `typeform/distilbert-base-uncased-mnli`
- A dataset containing news
- A set of target categories: `Business`, `Sports`, etc.

**What are we going to do**:

1. Make predictions and log them into a Rubrix dataset.
2. Use the Rubrix web app to explore, filter, and annotate some examples.
3. Load the annotated examples and create a training set, which you can then use to train a supervised classifier.

### 1. Predict and log

Let's load the zero-shot pipeline and the dataset (we are using the AGNews dataset for demonstration, but this could be your own dataset). Then, let's go over the dataset records and log them using `rb.log()`. This will create a Rubrix dataset, accesible from the web app.

```python
from transformers import pipeline
from datasets import load_dataset
import rubrix as rb

model = pipeline('zero-shot-classification', model="typeform/distilbert-base-uncased-mnli")

dataset = load_dataset("ag_news", split='test[0:100]')

labels = ['World', 'Sports', 'Business', 'Sci/Tech']

records = []
for item in dataset:
    prediction = model(item['text'], labels)

    records.append(
        rb.TextClassificationRecord(
            text=item["text"],
            prediction=list(zip(prediction['labels'], prediction['scores']))
        )
    )

rb.log(records, name="news_zeroshot")
```

### 2. Explore, Filter and Label

Now let's access our Rubrix dataset and start annotating data. Let's filter the records predicted as `Sports` with high probability and use the bulk-labeling feature for labeling 5 records as `Sports`:

![](docs/images/zero_shot_example.png)

### 3. Load and create a training set

After a few iterations of data annotation, we can load the Rubrix dataset and create a training set to train or fine-tune a supervised model.

```python
# load the Rubrix dataset as a pandas DataFrame
rb_df = rb.load(name='news_zeroshot')

# filter annotated records
rb_df = rb_df[rb_df.status == "Validated"]

# select text input and the annotated label
train_df = pd.DataFrame({
    "text": rb_df.text,
    "label": rb_df.annotation,
})
```

## Architecture

Rubrix main components are:

- **Rubrix Python client**: Python client to log, load, copy and delete Rubrix datasets.
- **Rubrix server**: FastAPI REST service for reading and writing data.
- **Elasticsearch**: The storage layer and search engine powering the API and the web app.
- **Rubrix web app**: Easy-to-use web application for data exploration and annotation.

![](docs/images/rubrix_intro.svg)


## FAQ

### What is Rubrix?

Rubrix is an open-source MLOps tool for building and managing training data for Natural Language Processing.

### What can I use Rubrix for?

Rubrix is useful if you want to:

- create a data set for training a model.
- evaluate and improve an existing model.
- monitor an existing model to improve it over time and gather more training data.

### What do I need to start using Rubrix?

You need to have a running instance of Elasticsearch and install the Rubrix Python library.

The library is used to read and write data into Rubrix.
To get started we highly recommend using Jupyter Notebooks so you might want to install Jupyter Lab or use Jupiter support for VS Code for example.

### How can I "upload" data into Rubrix?

Currently, the only way to upload data into Rubrix is by using the Python library.
This is based on the assumption that there's rarely a perfectly prepared dataset in the format expected by the data annotation tool.

Rubrix is designed to enable fast iteration for users that are closer to data and models, namely data scientists and NLP/ML/Data engineers.
If you are familiar with libraries like Weights & Biases or MLFlow, you'll find Rubrix `log` and `load` methods intuitive.
That said, Rubrix gives you different shortcuts and utils to make loading data into Rubrix a breeze, such as the ability to read datasets directly from the Hugging Face Hub.

In summary, the recommended process for uploading data into Rubrix would be following:

(1) Install Rubrix Python library,

(2) Open a Jupyter Notebook,

(3) Make sure you have a Rubrix server instance up and running,

(4) Read your source dataset using Pandas, Hugging Face datasets, or any other library,

(5) Do any data preparation, pre-processing, or pre-annotation with a pretrained model, and

(6) Transform your dataset rows/records into Rubrix records and log them into a Rubrix dataset using `rb.log`. If your dataset is already loaded as a Hugging Face dataset, check the `read_datasets` method to make this process even simpler.

### How can I train a model

The training datasets curated with Rubrix are model agnostic.
You can choose one of many amazing frameworks to train your model, like [transformers](https://huggingface.co/docs/transformers/), [spaCy](https://spacy.io/), [flair](https://github.com/flairNLP/flair) or [sklearn](https://scikit-learn.org).
Check out our [cookbook](https://rubrix.readthedocs.io/en/stable/guides/cookbook.html) and our [tutorials](https://rubrix.readthedocs.io/en/stable) on how Rubrix integrates with these frameworks.

If you want to train a Hugging Face transformer, we provide a neat shortcut to [prepare your Rubrix dataset for training](https://rubrix.readthedocs.io/en/stable/reference/python/python_client.html#rubrix.client.datasets.DatasetForTextClassification.prepare_for_training).

### Can Rubrix share the Elasticsearch Instance/cluster?

Yes, you can use the same Elasticsearch instance/cluster for Rubrix and other applications.
You only need to perform some configuration, check the Advanced installation guide in the [docs](https://docs.rubrix.ml/).

### How to solve an exceeded flood-stage watermark in Elasticsearch?

By default, Elasticsearch is quite conservative regarding the disk space it is allowed to use.
If less than 5% of your disk is free, Elasticsearch can enforce a read-only block on every index, and as a consequence, Rubrix stops working.
To solve this, you can simply increase the watermark by executing the following command in your terminal:

```bash
curl -X PUT "localhost:9200/_cluster/settings?pretty" -H 'Content-Type: application/json' -d'{"persistent": {"cluster.routing.allocation.disk.watermark.flood_stage":"99%"}}'
```

## Community

As a new open-source project, we are eager to hear your thoughts, fix bugs, and help you get started.
Feel free to [join us on Slack](https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g), use the [Discussion forum](https://github.com/recognai/rubrix/discussions) or [open Issues](https://github.com/recognai/rubrix/issues) and we'll be pleased to help out.

## Contributors

<a href="https://github.com/recognai/rubrix/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=recognai/rubrix" />
</a>
