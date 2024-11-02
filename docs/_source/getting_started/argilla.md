# What is Argilla?

[Argilla](https://argilla.io) is an open-source data curation platform for LLMs. Using Argilla, everyone can build robust language models through faster data curation using both human and machine feedback. We provide support for each step in the MLOps cycle, from data labeling to model monitoring.

```{admonition} Argilla 2.x
:class: info
We are announcing that Argilla 1.29 is the final minor release for Argilla 1.x. Although we will continue to release bug fixes for this version, we will neither be adding nor removing any functionalities. Visit the [2.x docs](https://docs.argilla.io/)!
```

<div class="social social--sidebar" style="margin-top: 1em; display: flex; justify-content: right; gap: 8px">
    <a href="http://hf.co/join/discord" class="button--primary" target="_blank">Join<span aria-label="discord" class="discord-icon"></span>Discord</a>
    <a href="https://linkedin.com/company/argilla-io"
        class="button--primary" target="_blank">Follow on LinkedIn</a>
    <a href="https://linkedin.com/company/argilla-io"
        class="button--primary" target="_blank">Follow on Twitter</a>
    <div class="github-stars github-stars--sidebar"></div>
</div>

<div class="video-container">
    <iframe class="video" width="100%" height="450" src="https://www.youtube.com/embed/jP3anvp7Rto" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

## 📄 About The Docs

| Section                                                                         | Goal                                                              |
| ------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| [🚀 Quickstart](/getting_started/quickstart)                                    | **Install** Argilla and end-to-end **toy examples**               |
| [🎼 Cheatsheet](/getting_started/cheatsheet)                                    | Brief **code snippets** for our main functionalities              |
| [🔧 Installation](/getting_started/installation/deployments/deployments)        | **Everything deployment**: Docker, Kubernetes, Cloud and way more |
| [⚙️ Configuration](/getting_started/installation/configurations/configurations)  | User management and **deployment tweaking**                       |
| [💥 Concepts about LLMs](/conceptual_guides/llm/llm)                            | Generative AI, **ChatGPT and friends**                            |
| [🦮 Practical Guides](/practical_guides/practical_guides)                       | **Conceptual overview** of our main functionalities               |
| [🧗‍♀️ Tutorials](/tutorials_and_integrations/tutorials/tutorials)                                            | Specific **applied end-to-end examples**                          |
| [🏷️ References](/reference/python/index)                                        | Itemized information and **API docs**                             |
| [🏘️ Community](/community/contributing)                                         | Everything about for **developers and contributing**              |
| [🗺️ Roadmap](https://github.com/orgs/argilla-io/projects/10/views/1)            | Our **future plans**                                              |

## 🛠️ Project Architecture

Argilla is built on 5 core components:

- **Python SDK**: A Python SDK which is installable with `pip install argilla`. To interact with the Argilla Server and the Argilla UI. It provides an API to manage the data, configuration, and annotation workflows.
- **FastAPI Server**: The core of Argilla is a *Python FastAPI* server that manages the data, by pre-processing it and storing it in the vector database. Also, it stores application information in the relational database. It provides a REST API to interact with the data from the Python SDK and the Argilla UI. It also provides a web interface to visualize the data.
- **Relational Database**: A relational database to store the metadata of the records and the annotations. *SQLite* is used as the default built-in option and is deployed separately with the Argilla Server but a separate *PostgreSQL* can be used too.
- **Vector Database**: A vector database to store the records data and perform scalable vector similarity searches and basic document searches. We currently support *ElasticSearch* and *AWS OpenSearch* and they can be deployed as separate Docker images.
- **Vue.js UI**: A web application to visualize and annotate your data, users, and teams. It is built with *Vue.js* and is directly deployed alongside the Argilla Server within our Argilla Docker image.

## 📏 Principles

- **Open**: Argilla is free, open-source, and 100% compatible with major NLP libraries (Hugging Face transformers, spaCy, Stanford Stanza, Flair, etc.). In fact, you can **use and combine your preferred libraries** without implementing any specific interface.

- **End-to-end**: Most annotation tools treat data collection as a one-off activity at the beginning of each project. In real-world projects, data collection is a key activity of the iterative process of ML model development. Once a model goes into production, you want to monitor and analyze its predictions and collect more data to improve your model over time. Argilla is designed to close this gap, enabling you to **iterate as much as you need**.

- **User and Developer Experience**: The key to sustainable NLP solutions is to make it easier for everyone to contribute to projects. _Domain experts_ should feel comfortable interpreting and annotating data. _Data scientists_ should feel free to experiment and iterate. _Engineers_ should feel in control of data pipelines. Argilla optimizes the experience for these core users to **make your teams more productive**.

- **Beyond hand-labeling**: Classical hand-labeling workflows are costly and inefficient, but having humans in the loop is essential. Easily combine hand-labeling with active learning, bulk-labeling, zero-shot models, and weak supervision in **novel** data annotation workflows\*\*.


## ❔ FAQ

<details>
<summary>What is Argilla?</summary>
<p>

Argilla is an open-source data curation platform, designed to enhance the development of both small and large language models (LLMs). Using Argilla, everyone can build robust language models through faster data curation using both human and machine feedback. We provide support for each step in the MLOps cycle, from data labeling to model monitoring. In fact, the inspiration behind the name "Argilla" comes from the word for "clay", in Latin, Italian and even in Catalan. And just as clay has been a fundamental medium for human creativity and tool-making throughout history, we view data as the essential material for sculpting and refining models.

</p>
</details>

<details>
<summary>Does Argilla train models?</summary>
<p>

Argilla does not train models but offers tools and integrations to help you do so. With Argilla, you can easily load data and train models straightforward using a feature we call the `ArgillaTrainer`. The `ArgillaTrainer` acts as a bridge to various popular NLP libraries. It simplifies the training process by offering an easy-to-understand interface for many NLP tasks using default pre-set settings without the need of converting data from Argilla's format. You can find more information about training models with Argilla <a href="/practical_guides/fine_tune.html">here</a>.

</p>
</details>

<details>
<summary>What is the difference between old datasets and the FeedbackDataset?</summary>
<p>

The FeedbackDataset stands out for its versatility and adaptability, designed to support a wider range of NLP tasks including those centered on large language models. In contrast, older datasets, while more feature-rich in specific areas, are tailored to singular NLP tasks. However, in Argilla 2.0, the intention is to phase out the older datasets in favor of the FeedbackDataset. For a more detailed explanation, please refer to <a href="/practical_guides/choose_dataset.html">this guide</a>.

</p>
</details>

<details>
<summary>Can Argilla only be used for LLMs?</summary>
<p>

No, Argilla is a versatile tool suitable for a wide range of NLP tasks. However, we emphasize the integration with small and large language models (LLMs), reflecting confidence in the significant role that they will play in the future of NLP. In this page, you can find a list of <a href="/practical_guides/choose_dataset.html#table-comparison">supported tasks</a>.

</p>
</details>

<details>
<summary>Does Argilla provide annotation workforces?</summary>
<p>

Currently, we already have partnerships with annotation providers that ensure ethical practices and secure work environments. Feel free to schedule a meeting <a href="https://calendly.com/david-berenstein-huggingface/30min">here</a> or contact us via <a href="mailto:david@argilla.io">email</a>.

</p>
</details>

<details>
<summary>Does Argilla cost money?</summary>
<p>

No, Argilla is an open-source platform. And we plan to keep Argilla free forever. However, we do offer a commercial version of Argilla called Argilla Cloud.

</p>
</details>

<details>
<summary>What is the difference between Argilla open source and Argilla Cloud?</summary>
<p>

Argilla Cloud is the counterpart to our open-source platform, offering a Software as a Service (SaaS) model, and doesn't add extra features beyond what is available in the open-source version. The main difference is its cloud-hosting, which caters especially to large teams requiring features that aren't typically necessary for individual practitioners or small businesses. So, Argilla Cloud is a SAS plus virtual private cloud deployment, with added features specifically related to the cloud. For those interested in the different plans available under Argilla Cloud, you can find detailed information on our <a href="https://argilla.io/pricing">website</a>.

</p>
</details>

<details>
<summary>How does Argilla differ from competitors like Snorkel, Prodigy and Scale?</summary>
<p>

Argilla distinguishes itself for its focus on specific use cases and human-in-the-loop approaches. While it does offer programmatic features, Argilla's core value lies in actively involving human experts in the tool-building process, setting it apart from other competitors.

Furthermore, Argilla places particular emphasis on smooth integration with other tools in the community, particularly within the realms of MLOps and NLP. So, its compatibility with popular frameworks like SpaCy and Hugging Face makes it exceptionally user-friendly and accessible.

Finally, platforms like Snorkel, Prodigy or Scale, while more comprehensive, often require a significant commitment. Argilla, on the other hand, works more as a component within the MLOps ecosystem, allowing users to begin with specific use cases and then scale up as needed. This flexibility is particularly beneficial for users and customers who prefer to start small and expand their applications over time, as opposed to committing to an all-encompassing platform from the outset.

</p>
</details>

<details>
<summary>What is Argilla currently working on?</summary>
<p>

We are continuously working on improving Argilla's features and usability, focusing now concentrating on a three-pronged vision: the development of Argilla Core (open-source), Distilabel, and Argilla JS/TS. You can find a list of our current projects <a href="https://github.com/orgs/argilla-io/projects/10/views/1">here</a>.

</p>
</details>
</details>


## 🤝 Contribute

To help our community with the creation of contributions, we have created our [developer](https://docs.v1.argilla.io/en/latest/community/developer_docs.html) and [contributor](https://docs.v1.argilla.io/en/latest/community/contributing.html) docs. Additionally, you can always [schedule a meeting](https://calendly.com/david-berenstein-huggingface/30min) with our Developer Advocacy team so they can get you up to speed.

## 🥇 Contributors

<a  href="https://github.com/argilla-io/argilla/graphs/contributors">

<img  src="https://contrib.rocks/image?repo=argilla-io/argilla" />

</a>

```{include} /_common/next_steps.md
```

## 🗺️ Roadmap

We continuously work on updating [our plans and our roadmap](https://github.com/orgs/argilla-io/projects/10/views/1) and we love to discuss those with our community. Feel encouraged to participate.
