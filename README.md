
<h1 align="center">
  <a href=""><img src="https://github.com/dvsrepo/imgs/raw/main/rg.svg" alt="Argilla" width="150"></a>
  <br>
  ✨ Argilla ✨
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

<h2 align="center">Open-source feedback layer for LLMs</h2>
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
<a href="https://docs.argilla.io">📄 Documentation</a> | </span>
<a href="#-quickstart">🚀 Quickstart</a> <span> | </span>
<a href="#-cheatsheet">🎼 Cheatsheet</a> <span> | </span>
<a href="#-project-architecture">🛠️ Architecture</a> <span> | </span>
<a href="#-contribute">🤝 Contribute</a>
</p>
</h3>

## What is Argilla?

Argilla is an open-source platform for data-centric LLM development. Integrates human and model feedback loops for continuous LLM refinement and oversight.

With Argilla's Python SDK and adaptable UI, you can create human and model-in-the-loop workflows for:

* Supervised fine-tuning
* Preference tuning (RLHF, DPO, RLAIF, and more)
* Small, specialized NLP models
* Scalable evaluation.

## 🚀 Quickstart

There are different options to get started:

1. Take a look at our [quickstart page](https://docs.argilla.io/en/latest/getting_started/quickstart.html) 🚀

2. Start contributing by looking at our [contributor guidelines](##🤝-contribute) 🤝

3. Skip some steps with our [cheatsheet](##🎼-cheatsheet) 🎼

## 🎼 Cheatsheet

This cheatsheet is a quick reference to the most common commands and workflows. For more detailed information, please refer to our [documentation](https://docs.argilla.io/en/latest/getting_started/quickstart.html).

<details>
<summary><a href="https://docs.argilla.io/en/latest/getting_started/installation/deployments/docker.html">pip install argilla</a></summary>
<p>

First things first! You can <a href="https://docs.argilla.io/en/develop/getting_started/installation/deployments/python.html">install Argilla</a> from pypi.

```bash
pip install argilla
```

</p>
</details>

<details>
<summary><a href="https://docs.argilla.io/en/latest/getting_started/installation/deployments/docker.html">Deploy Locally</a></summary>
<p>

```bash
docker run -d --name argilla -p 6900:6900 argilla/argilla-quickstart:latest
```

</p>
</details>

<details>
<summary><a href="https://docs.argilla.io/en/develop/getting_started/installation/deployments/huggingface-spaces.html">Deploy on Hugging Face Hub</a></summary>
<p>

HuggingFace Spaces now have persistent storage and this is supported from Argilla 1.11.0 onwards, but you will need to manually activate it via the HuggingFace Spaces settings. Otherwise, unless you're on a paid space upgrade, after 48 hours of inactivity the space will be shut off and you will lose all the data. To avoid losing data, we highly recommend using the persistent storage layer offered by HuggingFace.

After this, we can connect to our server.

<a href="https://docs.argilla.io/en/develop/getting_started/installation/deployments/huggingface-spaces.html"><img src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/spaces-argilla-embed-space.png" width="100%"></a>

</p>
</details>

<details>
<summary><a href="https://docs.argilla.io/en/latest/getting_started/cheatsheet.html#connect-to-argilla">Connect to the Server</a></summary>
<p>
Once you have deployed Argilla, we will connect to the server.

```python
import argilla as rg

rg.init(
    api_url="argilla-api-url", # e.g. http://localhost:6900 or https://[your-owner-name]-[your_space_name].hf.space
    api_key="argilla-api-key" # e.g. "owner.apikey"
    workspace="argilla-workspace" # e.g. "admin"
)
```

After this, you can start using Argilla, so you can create a dataset and add records to it. We use the FeedbackDataset as an example, but you can use any of the other datasets available in Argilla. You can find more information about the different datasets <a href="https://docs.argilla.io/en/latest/practical_guides/choose_dataset.html">here</a>.

</p>
</details>

<details>
<summary><a href="https://docs.argilla.io/en/latest/practical_guides/create_update_dataset/create_dataset.html">Configure datasets</a></summary>
<p>

```python
import argilla as rg

dataset = rg.FeedbackDataset(
    guidelines="Please, read the question carefully and try to answer it as accurately as possible.",
    fields=[
        rg.TextField(name="question"),
        rg.TextField(name="answer"),
    ],
    questions=[
        rg.RatingQuestion(
            name="answer_quality",
            description="How would you rate the quality of the answer?",
            values=[1, 2, 3, 4, 5],
        ),
        rg.TextQuestion(
            name="answer_correction",
            description="If you think the answer is not accurate, please, correct it.",
            required=False,
        ),
    ]
)
remote_dataset = dataset.push_to_argilla(name="my-dataset", workspace="my-workspace")
```

<a href="https://docs.argilla.io/en/latest/practical_guides/create_dataset.html"><img src="https://docs.argilla.io/en/latest/_images/snapshot-feedback-demo.png" width="100%"></a>

</p>
</details>

<details>
<summary><a href="https://docs.argilla.io/en/latest/practical_guides/records.html">Add records</a></summary>
<p>

```python
import argilla as rg

record = rg.FeedbackRecord(
    fields={
        "question": "Why can camels survive long without water?",
        "answer": "Camels use the fat in their humps to keep them filled with energy and hydration for long periods of time."
    },
    metadata={"source": "encyclopedia"},
    external_id='rec_1'
)
remote_dataset.add_records(record)
```

And that's it, you now have your first dataset ready. You can begin annotating it or embark on other related tasks.

<a href="https://docs.argilla.io/en/latest/practical_guides/records.html"><img src="https://docs.argilla.io/en/latest/_images/features-annotate.png" width="100%"></a>

</p>
</details>


<details>
<summary><a href="https://docs.argilla.io/en/latest/practical_guides/filter_dataset.html">Query datasets</a></summary>
<p>

```python
import argilla as rg

filtered_dataset = dataset.filter_by(response_status="submitted")
```

<a href="https://docs.argilla.io/en/latest/practical_guides/filter_dataset.html"><img src="https://docs.argilla.io/en/latest/_images/features-search.png" width="100%">

</p>
</details>

<details>
<summary><a href="https://docs.argilla.io/en/latest/practical_guides/filter_dataset.html">Semantic search</a></summary>
<p>

```python
import argilla as rg

# using text embeddings
similar_records =  ds.find_similar_records(
    vector_name="my_vector",
    value=embedder_model.embeddings("My text is here")
    # value=embedder_model.embeddings("My text is here").tolist() # for numpy arrays
)

# using another record
similar_records =  ds.find_similar_records(
    vector_name="my_vector",
    record=ds.records[0],
    max_results=5
)
```

<a href="https://docs.argilla.io/en/latest/practical_guides/filter_dataset.html"><img src="https://docs.argilla.io/en/latest/_images/features-similaritysearch.png" width="100%"></a>

</p>
</details>

<details>
<summary><a href="https://docs.argilla.io/en/latest/tutorials/techniques/weak_supervision.html">Weak supervision</a></summary>
<p>

```python
from argilla.labeling.text_classification import add_rules, Rule

rule = Rule(query="positive impact", label="optimism")
add_rules(dataset="go_emotion", rules=[rule])
```

<a href="https://docs.argilla.io/en/latest/tutorials/techniques/weak_supervision.html"><img src="https://docs.argilla.io/en/latest/_images/features-weak-labelling.png" width="100%"></a>

<!-- <tr>
<td>
<a href="https://argilla.io/blog/introducing-argilla-trainer">Active Learning</a>
</td>
<td>

```python
from argilla_plugins import classy_learner

plugin = classy_learner(name="plugin-test")
plugin.start()
```

<video src="https://share.descript.com/view/nvlUjF8tNcZ"/>
</td>
</tr> -->

</p>
</details>

<details>
<summary><a href="https://docs.argilla.io/en/latest/practical_guides/fine_tune.html">Train models</a></summary>
<p>

```python
from argilla.training import ArgillaTrainer

trainer = ArgillaTrainer(
    name="my_dataset",
    workspace="my_workspace",
    framework="my_framework",
    model="my_framework_model",
    train_size=0.8,
    seed=42,
    limit=10,
    query="my-query"
)
trainer.update_config() # see usage below
trainer.train()
records = trainer.predict(["my-text"], as_argilla_records=True)
```

<a href="https://docs.argilla.io/en/latest/practical_guides/fine_tune.html"><img src="https://argilla.io/blog/introducing-argilla-trainer/train.png" width="100%"></a>

</p>
</details>

## 🛠️ Project Architecture

Argilla is built on 5 core components:

<details>
<summary><strong>Python SDK</strong></summary>
<p>

A Python SDK which is installable with `pip install argilla`. To interact with the Argilla Server and the Argilla UI. It provides an API to manage the data, configuration and annotation workflows.

</p>
</details>

<details>
<summary><strong>FastAPI Server</strong></summary>
<p>

The core of Argilla is a <strong>Python FastAPI</strong> server that manages the data, by pre-processing it and storing it in the vector database. Also, it stores application information in the relational database. It provides a REST API to interact with the data from the Python SDK and the Argilla UI. It also provides a web interface to visualize the data.

</p>
</details>

<details>
<summary><strong>Relational Database</strong></summary>
<p>

A relational database to store the metadata of the records and the annotations. <strong>SQLite</strong> is used as the default built-in option and is deployed separately with the Argilla Server but a separate <strong>PostgreSQL</strong> can be used too.

</p>
</details>
<details>
<summary><strong>Vector Database</strong></summary>
<p>

A vector database to store the records data and perform scalable vector similarity searches and basic document searches. We currently support <strong>ElasticSearch</strong> and <strong>AWS OpenSearch</strong> and they can be deployed as separate Docker images.

</p>
</details>

<details>
<summary><strong>Vue.js UI</strong></summary>
<p>

A web application to visualize and annotate your data, users and teams. It is built with <strong>Vue.js</strong> and is directly deployed alongside the Argilla Server within our Argilla Docker image.

</p>
</details>


## 📏 Principles

Argilla is a tool that is in continuous development, with the aim of always offering better workflows and methods for various NLP tasks. To achieve this, it is based on several principles that define its functionality and scope.

<details>
<summary><strong>Open</strong></summary>
<p>

Argilla is free, open-source, and 100% compatible with major NLP libraries (Hugging Face transformers, spaCy, Stanford Stanza, Flair, etc.). In fact, you can <strong>use and combine your preferred libraries</strong> without implementing any specific interface.

</p>
</details>

<details>
<summary><strong>End-to-end</strong></summary>
<p>

Most annotation tools treat data collection as a one-off activity at the beginning of each project. In real-world projects, data collection is a key activity of the iterative process of ML model development. Once a model goes into production, you want to monitor and analyze its predictions and collect more data to improve your model over time. Argilla is designed to close this gap, enabling you to <strong>iterate as much as you need</strong>.

</p>
</details>

<details>
<summary><strong>User and Developer Experience</strong></summary>
<p>

The key to sustainable NLP solutions are to make it easier for everyone to contribute to projects. <em>Domain experts</em> should feel comfortable interpreting and annotating data. <em>Data scientists</em> should feel free to experiment and iterate. <em>Engineers</em> should feel in control of data pipelines. Argilla optimizes the experience for these core users to <strong>make your teams more productive</strong>.

</p>
</details>

<details>
<summary><strong>Beyond hand-labeling</strong></summary>
<p>

Classical hand-labeling workflows are costly and inefficient, but having humans in the loop is essential. Easily combine hand-labeling with active learning, bulk-labeling, zero-shot models, and weak supervision in <strong>novel data annotation workflows</strong>.

</p>
</details>


## ❔ Frequently Asked Questions

Below, you can find answers to some of the most common questions about Argilla. For more information, refer to our [documentation](https://docs.argilla.io/en/develop/index.html).

<details>
<summary><strong>What is Argilla?</strong></summary>
<p>

Argilla is an open-source data curation platform, designed to enhance the development of both small and large language models (LLMs). Using Argilla, everyone can build robust language models through faster data curation using both human and machine feedback. We provide support for each step in the MLOps cycle, from data labeling to model monitoring. In fact, the inspiration behind the name "Argilla" comes from the word for "clay", in Latin, Italian and even in Catalan. And just as clay has been a fundamental medium for human creativity and tool-making throughout history, we view data as the essential material for sculpting and refining models.

</p>
</details>

<details>
<summary><strong>Does Argilla train models?</strong></summary>
<p>

Argilla does not train models but offers tools and integrations to help you do so. With Argilla, you can easily load data and train models straightforward using a feature we call the `ArgillaTrainer`. The `ArgillaTrainer` acts as a bridge to various popular NLP libraries. It simplifies the training process by offering an easy-to-understand interface for many NLP tasks using default pre-set settings without the need of converting data from Argilla's format. You can find more information about training models with Argilla <a href="https://docs.argilla.io/en/latest/practical_guides/fine_tune.html">here</a>.

</p>
</details>

<details>
<summary><strong>What is the difference between old datasets and the FeedbackDataset?</strong></summary>
<p>

The FeedbackDataset stands out for its versatility and adaptability, designed to support a wider range of NLP tasks including those centered on large language models. In contrast, older datasets, while more feature-rich in specific areas, are tailored to singular NLP tasks. However, in Argilla 2.0, the intention is to phase out the older datasets in favor of the FeedbackDataset. For a more detailed explanation, please refer to <a href="https://docs.argilla.io/en/latest/practical_guides/choose_dataset.html">this guide</a>.

</p>
</details>

<details>
<summary><strong>Can Argilla only be used for LLMs?</strong></summary>
<p>

No, Argilla is a versatile tool suitable for a wide range of NLP tasks. However, we emphasize the integration with small and large language models (LLMs), reflecting confidence in the significant role that they will play in the future of NLP. In this page, you can find a list of <a href="https://docs.argilla.io/en/latest/practical_guides/choose_dataset.html">supported tasks</a>.

</p>
</details>

<details>
<summary><strong>Does Argilla provide annotation workforces?</strong></summary>
<p>

Currently, we already have partnerships with annotation providers that ensure ethical practices and secure work environments. Feel free to schedule a meeting <a href="https://calendly.com/argilla-office-hours/30min">here</a> or contact us via <a href="mailto:david@argilla.io">email</a>.

</p>
</details>

<details>
<summary><strong>Does Argilla cost money?</strong></summary>
<p>

No, Argilla is an open-source platform. And we plan to keep Argilla free forever. However, we do offer a commercial version of Argilla called Argilla Cloud.

</p>
</details>

<details>
<summary><strong>What is the difference between Argilla open source and Argilla Cloud?</strong></summary>
<p>

Argilla Cloud is the counterpart to our open-source platform, offering a Software as a Service (SaaS) model, and doesn't add extra features beyond what is available in the open-source version. The main difference is its cloud-hosting, which caters especially to large teams requiring features that aren't typically necessary for individual practitioners or small businesses. So, Argilla Cloud is a SAS plus virtual private cloud deployment, with added features specifically related to the cloud. For those interested in the different plans available under Argilla Cloud, you can find detailed information on our <a href="https://argilla.io/pricing">website</a>.

</p>
</details>

<details>
<summary><strong>How does Argilla differ from competitors like Snorkel, Prodigy and Scale?</strong></summary>
<p>

Argilla distinguishes itself for its focus on specific use cases and human-in-the-loop approaches. While it does offer programmatic features, Argilla's core value lies in actively involving human experts in the tool-building process, setting it apart from other competitors.

Furthermore, Argilla places particular emphasis on smooth integration with other tools in the community, particularly within the realms of MLOps and NLP. So, its compatibility with popular frameworks like SpaCy and Hugging Face makes it exceptionally user-friendly and accessible.

Finally, platforms like Snorkel, Prodigy or Scale, while more comprehensive, often require a significant commitment. Argilla, on the other hand, works more as a component within the MLOps ecosystem, allowing users to begin with specific use cases and then scale up as needed. This flexibility is particularly beneficial for users and customers who prefer to start small and expand their applications over time, as opposed to committing to an all-encompassing platform from the outset.

</p>
</details>

<details>
<summary><strong>What is Argilla currently working on?</strong></summary>
<p>

We are continuously working on improving Argilla's features and usability, focusing now concentrating on a three-pronged vision: the development of Argilla Core (open-source), Distilabel, and Argilla JS/TS. You can find a list of our current projects <a href="https://github.com/orgs/argilla-io/projects/10/views/1">here</a>.

</p>
</details>

## 🤝 Contribute

We love contributors and have launched a [collaboration with JustDiggit](https://argilla.io/blog/introducing-argilla-community-growers) to hand out our very own bunds and help the re-greening of sub-Saharan Africa. To help our community with the creation of contributions, we have created our [developer](https://docs.argilla.io/en/latest/community/developer_docs.html) and [contributor](https://docs.argilla.io/en/latest/community/contributing.html) docs. Additionally, you can always [schedule a meeting](https://calendly.com/argilla-office-hours/30min) with our Developer Advocacy team so they can get you up to speed.

## 🥇 Contributors

<a  href="https://github.com/argilla-io/argilla/graphs/contributors">

<img  src="https://contrib.rocks/image?repo=argilla-io/argilla" />

</a>

## 🏘️ Community

🏘️ Attend our [online bi-weekly community meetup](https://lu.ma/embed-checkout/evt-IQtRiSuXZCIW6FB).

🙋‍♀️ Join the Argilla community on [Slack](https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g) and get direct support from the community.

⭐ Argilla [Github repo](https://github.com/argilla-io/argilla) to stay updated about new releases and tutorials.

🎁 We've just printed stickers! Would you like some? [Order stickers for free](https://tally.so/r/nr5gg2).

## 🗺️ Roadmap

We continuously work on updating [our plans and our roadmap](https://github.com/orgs/argilla-io/projects/10/views/1) and we love to discuss those with our community. Feel encouraged to participate.

