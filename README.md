# Rubrix
> Open-source tool for tracking and evolving data for AI

<p align="center">
    <a href="https://github.com/recognai/rubrix/actions">
        <img alt="CI" src="https://github.com/recognai/rubrix/workflows/CI/badge.svg?branch=master&event=push">
    </a>
    <!--a href="https://github.com/recognai/rubrix/blob/master/LICENSE">
        <img alt="GitHub" src="https://img.shields.io/github/license/recognai/rubrix.svg?color=blue">
    </a-->
</p>


Rubrix is a tool for tracking and iterating on data for artificial intelligence projects. Rubrix focuses on enabling novel, human in the loop workflows involving data scientists, subject matter experts and ML/data engineers.

With Rubrix, you can:

- **Monitor** the predictions of deployed models.
- **Collect** ground-truth data for starting up a project or evolving an existing one.
- **Iterate** on ****ground-truth data**** and predictions to debug, track and improve your models over time.
- **Build** custom ****applications and dashboards**** on top of your model predictions.

We've tried to make working with Rubrix easy and fun, while keeping it scalable and flexible. Rubrix is composed of:

- a **web application and a REST API**, which you can launch using Docker or build it yourself.
- a **Python library** to bridge data and models, which you can install via `pip`.

## Quick links

- Get started with the [installation guide](#markdown-header-get-started)
- Check out the [Tutorials](https://github.com/recognai/rubrix/tree/master/docs/tutorials)

## Use cases

- **Model monitoring and observability:** log and observe predictions of live models.
- **Ground-truth data collection**: collect labels to start a project from scratch or from existing live models.
- **Evaluation**: easily compute "live" metrics from models in production, and slice evaluation datasets to test your system under specific conditions.
- **Model debugging**: log predictions during the development process to visually spot issues.
- **Explainability:** log things like token attributions to understand your model predictions.
- **App development:** get a powerful search-based API on top of your model predictions and ground truth data.

## Design principles

Rubrix design is:

- **Agnostic**: you can use Rubrix with any library or framework, no need to implement any interface or modify your existing toolbox and workflows.
- **Flexible:**  Rubrix does not make any strong assumption about your input data, so you can log and structure your data as it fits your use case.
- **Minimalistic:** Rubrix is built around a small set of concepts and methods

## Main concepts

### Dataset

A dataset is a collection of records.

### Record

A record is a data item composed of **inputs** and optionally, **predictions and/or annotations.**

### Task

A task defines the objective and shape of predictions and annotations inside a record

### Annotation

An annotation is a piece information assigned to a record, a label, token-level tags, or a set of labels, and typically by a human agent.

### Prediction

A prediction is a piece information assigned to a record, a label or a set of labels and typically by a machine process.

### Methods

#### `rb.log`



```python
rb.log(
    rb.TextClassificationRecord(
        inputs={"text": "my first rubrix example"},
        prediction=[('spam', 0.8), ('ham', 0.2)]
    ),
    name='example-dataset'
)
```

<details>
<summary>Show docstring</summary>
<p>

```python
Signature:
rb.log(
    records: Union[rubrix.client.models.TextClassificationRecord, rubrix.client.models.TokenClassificationRecord, Iterable[Union[rubrix.client.models.TextClassificationRecord, rubrix.client.models.TokenClassificationRecord]]],
    name: str,
    tags: Union[Dict[str, str], NoneType] = None,
    metadata: Union[Dict[str, Any], NoneType] = None,
    chunk_size: int = 500,
)
Docstring:
Register a set of logs into Rubrix

Parameters
----------
records:
    The data record object or list.
name:
    The dataset name
tags:
    A set of tags related to dataset. Optional
metadata:
    A set of extra info for dataset. Optional
chunk_size:
    The default chunk size for data bulk
File:      ~/recognai/rubrix/venv/lib/python3.8/site-packages/rubrix/__init__.py
Type:      function
```

</p>
</details>


#### `rb.load`

```python
rb.load(name='example-dataset')
```

<details>
<summary>Show docstring</summary>
<p>

```python
Signature:
rb.load(
    name: str,
    snapshot: Union[str, NoneType] = None,
    ids: Union[List[Union[str, int]], NoneType] = None,
    limit: Union[int, NoneType] = None,
) -> pandas.core.frame.DataFrame
Docstring:
Load datase/snapshot data as a huggingface dataset

Parameters
----------
name:
    The dataset name
snapshot:
    The dataset snapshot id. Optional
ids:
    If provided, load dataset records with given ids.
    Won't apply for snapshots
limit:
    The number of records to retrieve

Returns
-------
    A pandas Dataframe
File:      ~/recognai/rubrix/venv/lib/python3.8/site-packages/rubrix/__init__.py
Type:      function
```

</p>
</details>

#### `rb.snapshots`

```python
rb.snapshots(name='example-dataset')
```

<details>
<summary>Show docstring</summary>
<p>

```python
Signature: rb.snapshots(dataset: str) -> List[rubrix.sdk.models.dataset_snapshot.DatasetSnapshot]
Docstring:
Retrieve dataset snapshots

Parameters
----------
dataset:
    The dataset name

Returns
-------
File:      ~/recognai/rubrix/venv/lib/python3.8/site-packages/rubrix/__init__.py
Type:      function
```


</p>
</details>

#### `rb.delete`

```python
rb.delete(name='example-dataset')
```

<details>
<summary>Show docstring</summary>
<p>


```python
Signature: rb.delete(name: str) -> None
Docstring:
Delete a dataset with given name

Parameters
----------
name:
    The dataset name
File:      ~/recognai/rubrix/venv/lib/python3.8/site-packages/rubrix/__init__.py
Type:      function
```

</p>
</details>

#### `rb.init`

```python
rb.init(api_url='http://localhost:9090', api_key='4AkeAPIk3Y')
```

<details>
<summary>Show docstring</summary>
<p>

```python
Signature:
rb.init(
    api_url: Union[str, NoneType] = None,
    api_key: Union[str, NoneType] = None,
    timeout: int = 60,
)
Docstring:
Client setup function.

Calling the RubrixClient init function.
Passing an api_url disables environment variable reading, which will provide
default values.

Parameters
----------
api_url : str
    Address from which the API is serving. It will use the default UVICORN address as default
api_key: str
    Authentification api key. A non-secured log will be considered the default case. Optional
timeout : int
    Seconds to considered a connection timeout. Optional
File:      ~/recognai/rubrix/venv/lib/python3.8/site-packages/rubrix/__init__.py
Type:      function
```

</p>
</details>

# Get started

## 1. Launch your Rubrix app

### 1a. Using Docker and docker-compose

```bash
wget -O docker-compose.yml https://raw.githubusercontent.com/recognai/rubrix/master/docker-compose.yaml && docker-compose up
```
### 1b. With a local or remote Elasticsearch instance

1. ([https://www.elastic.co/guide/en/elasticsearch/reference/7.12/install-elasticsearch.html](Install) and) launch your Elasticsearch instance. 

2. Install the Rubrix Python library with server code `pip install rubrix[server]==0.1.0b2`.

3. Launch a local instance of Rubrix app: `python -m rubrix.server`. 

To see if everything went as expected go to [http://localhost:6900/](http://localhost:6900/).

You can also view the API docs at [http://localhost:6900/api/docs](http://localhost:6900/api/docs).
## 2. Install the Rubrix Python library:

If you are using a local installation (1b), you can skip this part.

```bash
pip install rubrix==0.1.0b2
```

## 3. Start logging data

The following code will log one record into the `example-dataset` dataset: 

```python
import rubrix as rb

rb.log(
    rb.TextClassificationRecord(inputs={"text": "my first rubrix example"}),
    name='example-dataset'
)

```

```bash
BulkResponse(dataset='example-dataset', processed=1, failed=0)
```

If you go to your Rubrix app at [http://localhost:6900/](http://localhost:6900/), you should see your first dataset.

Congratulations! You are ready to start working with Rubrix with your own data. To better understand what's possible take a look at our tutorials at: [https://github.com/recognai/rubrix/tree/master/docs/tutorials](https://github.com/recognai/rubrix/tree/master/docs/tutorials)

## Supported tasks

### Text classification

According to the amazing NLP Progress resource by Seb Ruder:

> Text classification is the task of assigning a sentence or document an appropriate category. The categories depend on the chosen dataset and can range from topics.

[http://nlpprogress.com/english/text_classification.html](http://nlpprogress.com/english/text_classification.html)

Rubrix is flexible with input and output shapes, which means you can model many related tasks like for example:

- **Sentiment analysis** ([http://nlpprogress.com/english/sentiment_analysis.html](http://nlpprogress.com/english/sentiment_analysis.html))
- **Natural Language Inference** ([http://nlpprogress.com/english/natural_language_inference.html](http://nlpprogress.com/english/natural_language_inference.html))
- **Relationship Extraction** ([http://nlpprogress.com/english/relationship_extraction.html](http://nlpprogress.com/english/relationship_extraction.html))
- **Stance detection** ([http://nlpprogress.com/english/stance_detection.html](http://nlpprogress.com/english/stance_detection.html))
- **Multi-label text classification**
- **Node classification in knowledge graphs**.

### Token classification

The most well-known task in this category is probably Named Entity Recognition:

> Named entity recognition (NER) is the task of tagging entities in text with their corresponding type. Approaches typically use BIO notation, which differentiates the beginning (B) and the inside (I) of entities. O is used for non-entity tokens.

[http://nlpprogress.com/english/named_entity_recognition.html](http://nlpprogress.com/english/named_entity_recognition.html)

Rubrix is flexible with input and output shapes, which means you can model related tasks like for example:

- Named entity recognition
- Part of speech tagging
- Key phrase extraction (https://paperswithcode.com/task/keyword-extraction)
- Slot filling

## Planned tasks
### Natural language processing

- Text2Text, covering summarization, machine translation, natural language generation, etc.
- Question answering

### Image

- Image classification
- Image captioning

### Speech

- Speech2Text
