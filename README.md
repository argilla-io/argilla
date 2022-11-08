
<h1 align="center">
  <a href=""><img src="https://github.com/dvsrepo/imgs/raw/main/rg.svg" alt="Argilla" width="150"></a>
  <br>
  Argilla
  <br>
</h1>
<p align="center">
<a  href="https://pypi.org/project/argilla/">
<img  alt="CI"  src="https://img.shields.io/pypi/v/argilla.svg?style=flat-square&logo=pypi&logoColor=white">
</a>
<!--a  href="https://anaconda.org/conda-forge/rubrix">
<img  alt="CI"  src="https://img.shields.io/conda/vn/conda-forge/rubrix?logo=anaconda&style=flat&color=orange">
</!a-->
<img alt="Codecov" src="https://codecov.io/gh/argilla-io/argilla/branch/main/graph/badge.svg?token=VDVR29VOMG"/>
<a href="https://pepy.tech/project/argilla">
<img  alt="CI"  src="https://static.pepy.tech/personalized-badge/argilla?period=month&units=international_system&left_color=grey&right_color=blue&left_text=pypi%20downloads/month">
</a>
</p>

<h2 align="center">Open-source framework for data-centric NLP</h2>
<p align="center">Data Labeling + Data Curation + Inference Store</p>
<p align="center">Designed for MLOps & Feedback Loops</p>


https://user-images.githubusercontent.com/25269220/200496945-7efb11b8-19f3-4793-bb1d-d42132009cbb.mp4

<br>

<p align="center">
<a  href="https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g">
<img src="https://img.shields.io/badge/JOIN US ON SLACK-4A154B?style=for-the-badge&logo=slack&logoColor=white" />
</a>
<a href="https://linkedin.com/company/argilla-io">
<img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" />
</a>
<a  href="https://twitter.com/argilla_io">
<img src="https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white" />
</a>
</p>

<br>

<h3>
<p align="center">
<a href="https://docs.argilla.io">Documentation</a> | </span>
<a href="#key-features">Key Features</a> <span> | </span>
<a href="#quickstart">Quickstart</a> <span> | </span>
<a href="#principles">Principles</a> | </span>
<a href="docs/_source/community/migration-rubrix.md">Migration from Rubrix</a> | </span>
<a href="#faq">FAQ</a>
</p>
</h3>

## Key Features

### Advanced NLP labeling

- Programmatic labeling using [weak supervision](https://docs.argilla.io/en/latest/guides/techniques/weak_supervision.html). Built-in label models (Snorkel, Flyingsquid)
- [Bulk-labeling](https://docs.argilla.io/en/latest/reference/webapp/features.html#bulk-annotate) and [search-driven annotation](https://docs.argilla.io/en/latest/guides/features/queries.html)
- Iterate on training data with any [pre-trained model](https://docs.argilla.io/en/latest/tutorials/libraries/huggingface.html) or [library](https://docs.argilla.io/en/latest/tutorials/libraries/libraries.html)
- Efficiently review and refine annotations in the UI and with Python
- Use Argilla built-in metrics and methods for [finding label and data errors (e.g., cleanlab)](https://docs.argilla.io/en/latest/tutorials/notebooks/monitoring-textclassification-cleanlab-explainability.html)
- Simple integration with [active learning workflows](https://docs.argilla.io/en/latest/tutorials/techniques/active_learning.html)

### Monitoring

- Close the gap between production data and data collection activities
- [Auto-monitoring](https://docs.argilla.io/en/latest/guides/steps/3_deploying.html) for [major NLP libraries and pipelines](https://docs.argilla.io/en/latest/tutorials/libraries/libraries.html) (spaCy, Hugging Face, FlairNLP)
- [ASGI middleware](https://docs.argilla.io/en/latest/tutorials/notebooks/deploying-texttokenclassification-fastapi.html) for HTTP endpoints
- Argilla Metrics to understand data and model issues, [like entity consistency for NER models](https://docs.argilla.io/en/latest/guides/steps/4_monitoring.html)
- Integrated with Kibana for custom dashboards

### Team workspaces

- Bring different users and roles into the NLP data and model lifecycles
- Organize data collection, review and monitoring into different [workspaces](https://docs.argilla.io/en/latest/getting_started/installation/user_management.html#workspace)
- Manage workspace access for different users

## Quickstart
Argilla is composed of a `Python Server` with Elasticsearch as the database layer, and a `Python Client` to create and manage datasets.

To get started you need to **install the client and the server** with `pip`:
```bash

pip install "argilla[server]"

```

Then you need to **run [Elasticsearch (ES)](https://www.elastic.co/elasticsearch)**.

The simplest way is to use`Docker` by running:

```bash

docker run -d --name es-for-argilla -p 9200:9200 -p 9300:9300 -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch-oss:7.10.2

```
> :information_source: **Check [the docs](https://docs.argilla.io/en/latest/getting_started/quickstart.html) for further options and configurations for Elasticsearch.**

Finally you can **launch the server**:

```bash

python -m argilla

```
> :information_source:  The most common error message after this step is related to the Elasticsearch instance not running. Make sure your Elasticsearch instance is running on http://localhost:9200/. If you already have an Elasticsearch instance or cluster, you point the server to its URL by using [ENV variables](#)


🎉 You can now access Argilla UI pointing your browser at http://localhost:6900/.

**The default username and password are**  `argilla`  **and**  `1234`.

Your workspace will contain no datasets. So let's use the `datasets` library to create our first datasets!

First, you need to install `datasets`:
```bash

pip install datasets

```

Then go to your Python IDE of choice and run:
```python

import pandas as pd
import argilla as rg
from datasets import load_dataset

# load dataset from the hub
dataset = load_dataset("argilla/gutenberg_spacy-ner", split="train")

# read in dataset, assuming its a dataset for text classification
dataset_rg = rg.read_datasets(dataset, task="TokenClassification")

# log the dataset to the Argilla web app
rg.log(dataset_rg, "gutenberg_spacy-ner")

# load dataset from json
my_dataframe = pd.read_json(
    "https://raw.githubusercontent.com/recognai/datasets/main/sst-sentimentclassification.json")

# convert pandas dataframe to DatasetForTextClassification
dataset_rg = rg.DatasetForTextClassification.from_pandas(my_dataframe)

# log the dataset to the Argilla web app
rg.log(dataset_rg, name="sst-sentimentclassification")
```

This will create two datasets which you can use to do a quick tour of the core features of Argilla.

> 🚒 **If you find issues, get direct support from the team and other community members on the [Slack Community](https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g)**

For getting started with your own use cases, [go to the docs](https://docs.argilla.io).
## Principles
-  **Open**: Argilla is free, open-source, and 100% compatible with major NLP libraries (Hugging Face transformers, spaCy, Stanford Stanza, Flair, etc.). In fact, you can **use and combine your preferred libraries** without implementing any specific interface.



-  **End-to-end**: Most annotation tools treat data collection as a one-off activity at the beginning of each project. In real-world projects, data collection is a key activity of the iterative process of ML model development. Once a model goes into production, you want to monitor and analyze its predictions, and collect more data to improve your model over time. Argilla is designed to close this gap, enabling you to **iterate as much as you need**.



-  **User and Developer Experience**: The key to sustainable NLP solutions is to make it easier for everyone to contribute to projects. _Domain experts_ should feel comfortable interpreting and annotating data. _Data scientists_ should feel free to experiment and iterate. _Engineers_ should feel in control of data pipelines. Argilla optimizes the experience for these core users to **make your teams more productive**.



-  **Beyond hand-labeling**: Classical hand labeling workflows are costly and inefficient, but having humans-in-the-loop is essential. Easily combine hand-labeling with active learning, bulk-labeling, zero-shot models, and weak-supervision in **novel data annotation workflows**.

## FAQ

### What is Argilla?
Argilla is an open-source MLOps tool for building and managing data for Natural Language Processing.

### What can I use Argilla for?
Argilla is useful if you want to:

- create a dataset for training a model.

- evaluate and improve an existing model.

- monitor an existing model to improve it over time and gather more training data.

### What do I need to start using Argilla?
You need to have a running instance of Elasticsearch and install the Argilla Python library.
The library is used to read and write data into Argilla.

### How can I "upload" data into Argilla?
Currently, the only way to upload data into Argilla is by using the Python library.

This is based on the assumption that there's rarely a perfectly prepared dataset in the format expected by the data annotation tool.

Argilla is designed to enable fast iteration for users that are closer to data and models, namely data scientists and NLP/ML/Data engineers.

If you are familiar with libraries like Weights & Biases or MLFlow, you'll find Argilla `log` and `load` methods intuitive.

That said, Argilla gives you different shortcuts and utils to make loading data into Argilla a breeze, such as the ability to read datasets directly from the Hugging Face Hub.

In summary, the recommended process for uploading data into Argilla would be following:

1. Install Argilla Python library,

2. Open a Jupyter Notebook,

3. Make sure you have a Argilla server instance up and running,

4. Read your source dataset using Pandas, Hugging Face datasets, or any other library,

5. Do any data preparation, pre-processing, or pre-annotation with a pretrained model, and

6. Transform your dataset rows/records into Argilla records and log them into a dataset using `rb.log`. If your dataset is already loaded as a Hugging Face dataset, check the `read_datasets` method to make this process even simpler.

### How can I train a model
The training datasets created with Argilla are model agnostic.

You can choose one of many amazing frameworks to train your model, like [transformers](https://huggingface.co/docs/transformers/), [spaCy](https://spacy.io/), [flair](https://github.com/flairNLP/flair) or [sklearn](https://scikit-learn.org).

Check out our [deep dives](https://docs.argilla.io/en/latest/guides/guides.html) and our [tutorials](https://docs.argilla.io/en/latest/tutorials/tutorials.html) on how Argilla integrates with these frameworks.


If you want to train a Hugging Face transformer or spaCy NER model, we provide a neat shortcut to [prepare your dataset for training](https://docs.argilla.io/en/latest/guides/features/datasets.html#Prepare-dataset-for-training).
### Can Argilla share the Elasticsearch Instance/cluster?
Yes, you can use the same Elasticsearch instance/cluster for Argilla and other applications.
You only need to perform some configuration, check the Advanced installation guide in the docs.
### How to solve an exceeded flood-stage watermark in Elasticsearch?
By default, Elasticsearch is quite conservative regarding the disk space it is allowed to use.

If less than 5% of your disk is free, Elasticsearch can enforce a read-only block on every index, and as a consequence, Argilla stops working.

To solve this, you can simply increase the watermark by executing the following command in your terminal:

```bash

curl -X PUT "localhost:9200/_cluster/settings?pretty" -H 'Content-Type: application/json' -d'{"persistent": {"cluster.routing.allocation.disk.watermark.flood_stage":"99%"}}'

```
## Contributors
<a  href="https://github.com/argilla-io/argilla/graphs/contributors">

<img  src="https://contrib.rocks/image?repo=argilla-io/argilla" />

</a>
