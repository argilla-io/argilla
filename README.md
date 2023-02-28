
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
<a  href="https://huggingface.co/new-space?template=argilla/argilla-template-space">
<img src="https://huggingface.co/datasets/huggingface/badges/raw/main/deploy-to-spaces-sm.svg" />
</a>
</p>

<h2 align="center">Open-source framework for data-centric NLP</h2>
<p align="center">Data Labeling for MLOps & Feedback Loops</p>

> 🆕 🔥 Deploy [Argilla on Spaces](https://huggingface.co/new-space?template=argilla/argilla-template-space)

> 🆕 🔥 Since `1.2.0` Argilla supports vector search for finding the most similar records to a given one. This feature uses vector or semantic search combined with more traditional search (keyword and filter based). Learn more on this [deep-dive guide](https://docs.argilla.io/en/latest/guides/features/semantic-search.html)


<!-- https://user-images.githubusercontent.com/25269220/200496945-7efb11b8-19f3-4793-bb1d-d42132009cbb.mp4 -->


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

- Programmatic labeling using [rules and weak supervision](https://docs.argilla.io/en/latest/guides/programmatic_labeling_with_rules.html). Built-in label models (Snorkel, Flyingsquid)
- [Bulk-labeling](https://docs.argilla.io/en/latest/reference/webapp/features.html#bulk-annotate) and [search-driven annotation](https://docs.argilla.io/en/latest/guides/features/queries.html)
- Iterate on training data with any [pre-trained model](https://docs.argilla.io/en/latest/tutorials/libraries/huggingface.html) or [library](https://docs.argilla.io/en/latest/tutorials/libraries/libraries.html)
- Efficiently review and refine annotations in the UI and with Python
- Use Argilla built-in metrics and methods for [finding label and data errors (e.g., cleanlab)](https://docs.argilla.io/en/latest/tutorials/notebooks/monitoring-textclassification-cleanlab-explainability.html)
- Simple integration with [active learning workflows](https://docs.argilla.io/en/latest/tutorials/techniques/active_learning.html)

### Monitoring

- Close the gap between production data and data collection activities
- [Auto-monitoring](https://docs.argilla.io/en/latest/guides/log_load_and_prepare_data.html) for [major NLP libraries and pipelines](https://docs.argilla.io/en/latest/tutorials/libraries/libraries.html) (spaCy, Hugging Face, FlairNLP)
- [ASGI middleware](https://docs.argilla.io/en/latest/tutorials/notebooks/deploying-texttokenclassification-fastapi.html) for HTTP endpoints
- Argilla Metrics to understand data and model issues, [like entity consistency for NER models](https://docs.argilla.io/en/latest/guides/measure_datasets_with_metrics.html)
- Integrated with Kibana for custom dashboards

### Team workspaces

- Bring different users and roles into the NLP data and model lifecycles
- Organize data collection, review and monitoring into different [workspaces](https://docs.argilla.io/en/latest/getting_started/installation/configurations/user_management.html)
- Manage workspace access for different users

## Quickstart
👋 Welcome! If you have just discovered Argilla this is the best place to get started. Argilla is composed of:

* Argilla Client: a powerful Python library for reading and writing data into Argilla, using all the libraries you love (transformers, spaCy, datasets, and any other).

* Argilla Server and UI: the API and UI for data annotation and curation.

To get started you need to:

1. Launch the Argilla Server and UI.

2. Pick a tutorial and start rocking with Argilla using Jupyter Notebooks, or Google Colab.

To get started follow the steps [on the Quickstart docs page](https://docs.argilla.io/en/latest/getting_started/quickstart.html).

> 🚒 **If you find issues, get direct support from the team and other community members on the [Slack Community](https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g)**

## Principles
-  **Open**: Argilla is free, open-source, and 100% compatible with major NLP libraries (Hugging Face transformers, spaCy, Stanford Stanza, Flair, etc.). In fact, you can **use and combine your preferred libraries** without implementing any specific interface.



-  **End-to-end**: Most annotation tools treat data collection as a one-off activity at the beginning of each project. In real-world projects, data collection is a key activity of the iterative process of ML model development. Once a model goes into production, you want to monitor and analyze its predictions, and collect more data to improve your model over time. Argilla is designed to close this gap, enabling you to **iterate as much as you need**.



-  **User and Developer Experience**: The key to sustainable NLP solutions is to make it easier for everyone to contribute to projects. _Domain experts_ should feel comfortable interpreting and annotating data. _Data scientists_ should feel free to experiment and iterate. _Engineers_ should feel in control of data pipelines. Argilla optimizes the experience for these core users to **make your teams more productive**.



-  **Beyond hand-labeling**: Classical hand labeling workflows are costly and inefficient, but having humans-in-the-loop is essential. Easily combine hand-labeling with active learning, bulk-labeling, zero-shot models, and weak-supervision in **novel data annotation workflows**.

## Contribute

We love contributors and have launched a collaboration with JustDiggit to hand out our very own bunds, to help the re-greening of sub-Saharan Africa. To help our community with the creation of contributions, we have created our [developer](https://docs.argilla.io/en/latest/community/developer_docs.html) and [contributor](https://docs.argilla.io/en/latest/community/contributing.html) docs. Additionally, you can always [schedule a meeting](https://calendly.com/argilla-office-hours/meeting-with-david-from-argilla-30m) with our Developer Advocacy team so they can get you up to speed.

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
