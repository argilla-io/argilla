# What is Argilla?

[Argilla](https://argilla.io) is a **production-ready framework for building and improving datasets** for NLP projects.

```{admonition} Argilla on HF Spaces
:class: important

Deploy your own Argilla Server on Spaces with a few clicks:

<a  href="https://huggingface.co/new-space?template=argilla/argilla-template-space">
    <img src="https://huggingface.co/datasets/huggingface/badges/raw/main/deploy-to-spaces-lg.svg" />
</a>

```


```{admonition} Semantic Search data labelling 🆕
:class: important

🆕 Use embeddings to find the most similar records with the UI. This feature uses vector search combined with traditional search (keyword and filter based).

Get started: [Semantic Search Deep-dive guide](../guides/label_records_with_semanticsearch.ipynb)

```



<iframe width="100%" height="450" src="https://www.youtube.com/embed/jP3anvp7Rto" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Features

- **Open**: Argilla is free, open-source, and 100% compatible with major NLP libraries (Hugging Face transformers, spaCy, Stanford Stanza, Flair, etc.). In fact, you can **use and combine your preferred libraries** without implementing any specific interface.

- **End-to-end**: Most annotation tools treat data collection as a one-off activity at the beginning of each project. In real-world projects, data collection is a key activity of the iterative process of ML model development. Once a model goes into production, you want to monitor and analyze its predictions, and collect more data to improve your model over time. Argilla is designed to close this gap, enabling you to **iterate as much as you need**.

- **User and Developer Experience**: The key to sustainable NLP solutions is to make it easier for everyone to contribute to projects. *Domain experts* should feel comfortable interpreting and annotating data. *Data scientists* should feel free to experiment and iterate. *Engineers* should feel in control of data pipelines. Argilla optimizes the experience for these core users to **make your teams more productive**.

- **Beyond hand-labeling**: Classical hand labeling workflows are costly and inefficient, but having humans-in-the-loop is essential. Easily combine hand-labeling with active learning, bulk-labeling, zero-shot models, and weak-supervision in **novel data annotation workflows**.

## Use cases

* **Data labelling and curation**: collect labels to start a project from scratch or from existing live models.
* **Model monitoring and observability:** log and observe predictions of live models.
* **Evaluation**: easily compute "live" metrics from models in production, and slice evaluation datasets to test your system under specific conditions.
* **Model debugging**: log predictions during the development process to visually spot issues.
* **Explainability:** log token attributions to help you interpret model predictions.

```{include} /_common/next_steps.md
```
