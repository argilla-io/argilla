
<h1 align="center">
  <a href=""><img src="https://github.com/dvsrepo/imgs/raw/main/rg.svg" alt="Argilla" width="150"></a>
  <br>
  Argilla
  <br>
</h1>
<p align="center">
<a  href="https://pypi.org/project/rubrix/">
<img  alt="CI"  src="https://img.shields.io/pypi/v/rubrix.svg?style=flat-square&logo=pypi&logoColor=white">
</a>
<a  href="https://anaconda.org/conda-forge/rubrix">
<img  alt="CI"  src="https://img.shields.io/conda/vn/conda-forge/rubrix?logo=anaconda&style=flat&color=orange">
</a>
<img  alt="Codecov" src="https://img.shields.io/codecov/c/github/recognai/rubrix">
<a href="https://pepy.tech/project/rubrix">
<img  alt="CI"  src="https://static.pepy.tech/personalized-badge/rubrix?period=month&units=international_system&left_color=grey&right_color=blue&left_text=pypi%20downloads/month">
</a>
</p>

<h2 align="center">Open-source framework for data-centric NLP</h2>
<p align="center">Data Labeling + Data Curation + Inference Store</p>
<p align="center">Designed for MLOps & Feedback Loops</p>

https://user-images.githubusercontent.com/15979778/167146590-72d8f7b1-f94d-45a6-9896-1525cf949efe.mp4


<br>

<p align="center">
<a  href="https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g">
<img src="https://img.shields.io/badge/JOIN US ON SLACK-4A154B?style=for-the-badge&logo=slack&logoColor=white" />
</a>
<img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" />
<img src="https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white" />
</p>

<br>

<h3>
<p align="center">
<a href="#">Documentation</a> | </span>
<a href="#key-features">Key Features</a> <span> | </span>
<a href="#quickstart">Quickstart</a> <span> | </span>
<a href="#principles">Principles</a> | </span>
<a href="#FAQ">FAQ</a>
</p>
</h3>

## Key Features

### Advanced NLP labeling

- Programmatic labeling using Weak Supervision. Built-in label models (Snorkel, Flyingsquid)
- Bulk-labeling and search-driven annotation
- Iterate on training data with any pre-trained model or library
- Efficiently review and refine annotations in the UI and with Python
- Use Argilla built-in metrics and methods for finding label and data errors (e.g., cleanlab)
- Simple integration with active learning workflows

### Monitoring

- Close the gap between production data and data collection activities
- Auto-monitoring for major NLP libraries and pipelines (spaCy, Hugging Face, FlairNLP)
- ASGI middleware for HTTP endpoints
- Argilla Metrics to understand data and model issues, like entity consistency for NER models
- Integrated with Kibana for custom dashboards

### Team workspaces

- Bring different users and roles into the NLP data and model lifecycles
- Organize data collection, review and monitoring into different workspaces
- Manage workspace access for different users

## Quickstart
Argilla is composed of a `Python Server` with Elasticsearch as the database layer, and a `Python Client` to create and manage datasets.

To get started you need to **install the client and the server** with `pip`:
```bash

pip install "argilla[server]"

```
<details>
<summary>
or conda:
</summary>

```bash

pip install "argilla[server]"

```

</details>

Then you need to **run [Elasticsearch (ES)](https://www.elastic.co/elasticsearch)**.

The simplest way is to use`Docker` by running:

```bash

docker run -d --name es-for-argilla -p 9200:9200 -p 9300:9300 -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch-oss:7.10.2

```
> :information_source: **Check [the docs](https://rubrix.readthedocs.io/en/stable/getting_started/setup%26installation.html) for further options and configurations for Elasticsearch.**

Finally you can **launch the server**:

```bash

python -m argilla

```
> :information_source:  The most common error message after this step is related to the Elasticsearch instance not running. Make sure your Elasticsearch instance is running on http://localhost:9200/. If you already have an Elasticsearch instance or cluster, you can set point the server to its URL by using [ENV variables](#)


🎉 You can now access Argilla UI pointing your browser at http://localhost:6900/.

**The default username and password are**  `argilla`  **and**  `1234`.

To upload your first dataset you can run from your terminal:

@TODO give a one-liner or something else to create a data. Or provide a command which creates one or several demo datasets.


> 🚒 **If you find issues, get direct support from the team and other community members on the [Slack Community](https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g)**


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
To get started we highly recommend using Jupyter Notebooks so you might want to install Jupyter Lab or use Jupiter support for VS Code for example.

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

Check out our [cookbook](https://rubrix.readthedocs.io/en/stable/guides/cookbook.html) and our [tutorials](https://rubrix.readthedocs.io/en/stable) on how Argilla integrates with these frameworks.


If you want to train a Hugging Face transformer or spaCy NER model, we provide a neat shortcut to [prepare your dataset for training](https://rubrix.readthedocs.io/en/stable/reference/python/python_client.html#rubrix.client.datasets.DatasetForTextClassification.prepare_for_training).
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
<a  href="https://github.com/recognai/rubrix/graphs/contributors">

<img  src="https://contrib.rocks/image?repo=recognai/rubrix" />

</a>
