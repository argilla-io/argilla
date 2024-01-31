# 🔦 Semantic Search

This guide gives an overview of the semantic search features. Since `1.19.0` Argilla supports adding vectors to Feedback Datasets (other datasets include this feature since `1.2.0`) which can then be used for finding the most similar records to a given one. This feature uses vector or semantic search combined with more traditional search (keyword and filter-based).

Vector search leverages machine learning to capture rich semantic features by embedding items (text, video, images, etc.) into a vector space, which can be then used to find "semantically" similar items.

In this guide, you'll find how to:

- Set up your Elasticsearch or Opensearch endpoint with vector search support.
- Encode text into vectors for Argilla records.
- Use semantic search.

The next section gives a general overview of how semantic search works in Argilla.

## How it works

Semantic search in Argilla works as follows:

1. One or several vectors can be included in the `vectors` field of Argilla Records. The `vectors` field accepts a dictionary where `keys` represent the names and `values` contain the actual vectors. This is the case because certain use cases might require using several vectors. Note that for a `FeedbackDataset` you will also need to [configure `VectorSettings`](/practical_guides/create_update_dataset/create_dataset.md#define-vectors) in your dataset.
2. The vectors are stored at indexing time, once the records are logged with `add_records` or `update_records` in a `FeedbackDataset`, or with `rg.log` in older datasets.
3. If you have stored vectors in your dataset, you can use the semantic search feature in Argilla UI and the Python SDK.

In future versions, embedding services might be developed to facilitate steps 1 and 2 and associate vectors to records automatically.

```{note}

It's completely up to the user which encoding or embedding mechanism to use for producing these vectors. In the "Encode text fields" section of this document you will find several examples and details about this process, using open-source libraries (e.g., Hugging Face) as well as paid services (e.g., Cohere or OpenAI).

Currently, Argilla uses vector search only for searching similar records (nearest neighbors) of a given vector. This can be leveraged from Argilla UI as well as the Python Client. In the future, vector search could be leveraged as well for free text queries using Argilla UI.

```

## Setup vector search support

In order to use this feature you should use Elasticsearch at least version `8.5.x`or Opensearch `2.4.0`. We provide pre-configured docker-compose files in the root of Argilla's [Github repository](https://github.com/argilla-io/argilla).

```{warning}
If you had Argilla running with Elasticsearch 7.1.0 you need to migrate to at least version 8.5.x. Please check the section "[Migrating from Elasticsearch 7.1.0 to 8.5](#Migrate-from-7.1.0-to-8.5)".
```

### Elasticsearch backend

If you don't have another instance of Elasticsearch or Opensearch running, or don't want to keep previous Argilla datasets, you can launch a clean instance of Elasticsearch by downloading the [docker-compose.elasticsearch.yaml](https://raw.githubusercontent.com/argilla-io/argilla/develop/docker/docker-compose.elasticsearch.yaml) and running:

```bash
docker-compose -f docker-compose.elasticsearch.yaml up
```

#### Migrate from 7.1.0 to 8.5

```{warning}

If you had Argilla running with Elasticsearch 7.1.0 you need to migrate to at least version 8.5.x. Before following the process described below, please read the official [Elasticsearch Migration Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/migrating-8.5.html) carefully.
```

In order to migrate from Elasticsearch 7.1.0 and keep your datasets you can follow this process:

1. Stop your current Elasticsearch service (we assume a migration for a `docker-compose` setup).
2. Set the Elasticsearch image to 7.17.x in your `docker-compose`.
3. Start the Elasticsearch service again.
4. Once is up and running, stop it again and set the Elasticsearch image to 8.5.x
5. Finally, start again the Elasticsearch service. Data should be migrated properly.

Once the service is up you can launch the Argilla Server with `python -m argilla server start`.

### Opensearch backend

If you don't have another instance of Elasticsearch or Opensearch running, or don't want to keep previous Argilla datasets, you can launch a clean instance of Opensearch by downloading the [docker-compose.opensearch.yaml file](https://raw.githubusercontent.com/argilla-io/argilla/develop/docker/docker-compose.opensearch.yaml) and running:

```bash
docker-compose -f docker-compose.opensearch.yaml up
```

Once the service is up you can launch the Argilla Server with `ARGILLA_SEARCH_ENGINE=opensearch python -m argilla server start`.

:::{warning}
For vector search in OpenSearch, the filtering applied is using a `post_filter` step, since there is a bug that makes queries fail using filtering + knn from Argilla.
See https://github.com/opensearch-project/k-NN/issues/1286

This may result in unexpected results when combining filtering with vector search with this engine.
:::

## Add vectors to your data

The first and most important thing to do before leveraging semantic search is to turn text into a numerical representation: a vector. In practical terms, you can think of a vector as an array or list of numbers. You can associate this list of numbers with an Argilla Record by using the aforementioned `vectors` field. But the question is: **how do you create these vectors?**

Over the years, many approaches have been used to turn text into numerical representations. The goal is to "encode" meaning, context,  topics, etc.. This can be used to find "semantically" similar text. Some of these approaches are *LSA* (Latent Semantic Analysis), *tf-idf*, *LDA* (Latent Dirichlet Allocation), or *doc2Vec*. More recent methods fall in the category of "neural" methods, which leverage the power of large neural networks to *embed* text into dense vectors (a large array of real numbers). These methods have demonstrated a great ability to capture semantic features. These methods are powering a new wave of technologies that fall under categories like neural search, semantic search, or vector search. Most of these methods involve using a large language model to encode the full context of a textual snippet, such as a sentence, a paragraph, and more lately larger documents.

```{note}

In the context of Argilla, we intentionally use the term `vector` in favor of `embedding` to emphasize that users can leverage methods other than neural, which might be cheaper to compute or be more useful for their use cases.
```

In the next sections, we show how to encode text using different models and services and how to add them to Argilla records.

```{warning}

If you run into issues when logging records with large vectors using `rg.log`, we recommend you to use a smaller `chunk_size` as shown in the following examples.
```

### Sentence Transformers

SentenceTransformers is a Python framework for state-of-the-art sentence, text and image embeddings. There are dozens of [pre-trained models available](https://huggingface.co/models?pipeline_tag=sentence-similarity&sort=downloads) on the Hugging Face Hub.

Given its fundamental and open source versatile nature, we have decided to add a native integration with SentenceTransformers. This integration allows you to easily add embeddings to your records or datasets using the `SentenceTransformersExtractor` based on the [sentence-transformers](https://sbert.net/) library. This integration can be found [here](/practical_guides/create_update_dataset/vectors.md).

### OpenAI `Embeddings`

OpenAI provides an API endpoint called [Embeddings](https://beta.openai.com/docs/api-reference/embeddings) to get a vector representation of a given input that can be easily consumed by machine learning models and algorithms.

```{warning}

Due to the vector dimension limitation of Elasticsearch and Opensearch Lucene-based engines, currently, you can only use the `text-similarity-ada-001` model which produces vectors of `1024` dimensions.

```

The code below will load a dataset from the Hub, encode the `text` field, and create the `vectors` field which will contain only one key (`openai`) using the Embeddings endpoint.

To run the code below you need to install `openai` and `datasets` with pip: `pip install openai datasets`.

You also need to setup your OpenAI API key as shown below.

```python
import openai
from datasets import load_dataset

openai.api_key = "<your api key goes here>"

# Load dataset
dataset = load_dataset("banking77", split="test")

def get_embedding(texts, model="text-similarity-ada-001"):
    response = openai.Embedding.create(input = texts, model=model)
    vectors = [item["embedding"] for item in response["data"]]
    return vectors

# Encode text. Get only 500 vectors for testing, remove the select to do the full dataset
dataset = dataset.select(range(500)).map(lambda batch: {"vectors": get_embedding(batch["text"])}, batch_size=16, batched=True)

# Turn vectors into a dictionary
dataset = dataset.map(
    lambda r: {"vectors": {"text-similarity-ada-001": r["vectors"]}}
)
```

### Cohere `Co.Embed`

[Cohere Co.Embed](https://docs.cohere.ai/reference/embed) is an API endpoint by Cohere that takes a piece of text and turns it into a vector embedding.

```{warning}

Due to the vector dimension limitation of Elasticsearch and Opensearch Lucene-based engines, currently, you can only use the `small` model which produces vectors of `1024` dimensions.
```

The code below will load a dataset from the Hub, encode the `text` field, and create the `vectors` field which will contain only one key (`cohere`) using the Embeddings endpoint.

To run the code below you need to install `cohere` and `datasets` with pip: `pip install cohere datasets`.

You also need to set up your Cohere API key as shown below.

```python
import cohere

api_key = "<your api key goes here>"
co = cohere.Client(api_key)

# Load dataset
dataset = load_dataset("banking77", split="test")

def get_embedding(texts):
    return co.embed(texts, model="small").embeddings

# Encode text. Get only 1000 vectors for testing, remove the select to do the full dataset
dataset = dataset.select(range(1000)).map(lambda batch: {"vectors": get_embedding(batch["text"])}, batch_size=16, batched=True)

# Turn vectors into a dictionary
dataset = dataset.map(
    lambda r: {"vectors": {"cohere-embed": r["vectors"]}}
)
```

## Configure your dataset

Our dataset now contains a `vectors` field with the embedding vector generated by our preferred model. This dataset can be transformed into an Argilla Dataset in the following ways:

::::{tab-set}
:::{tab-item} FeedbackDataset

Let's first configure a Feedback Dataset that includes vector settings:

```python
import argilla as rg

local_ds = rg.FeedbackDataset(
    fields=[
        rg.TextField(name="text")
    ],
    questions=[
        rg.MultiLabelQuestion(
            name="topic",
            title="Select the topics mentioned in the text:",
            labels=dataset.info.features['label'].names, #these are the labels in the original dataset
        )
    ],
    vectors_settings=[
        rg.VectorSettings(name=key, dimensions=len(value))
        for key,value in dataset[0]["vectors"].items()
    ]
)
remote_ds = local_ds.push_to_argilla("banking77", workspace="admin")
```

Now we can create records and add them to the dataset:

```python
records = [
    rg.FeedbackRecord(
        fields={"text": rec["text"]},
        vectors=rec["vectors"]
    )
    for rec in dataset
]
remote_ds.add_records(records)
```

:::
:::{tab-item} Older datasets

You can use the `DatasetForTextClassification.from_datasets` method. Then, this dataset can be logged into Argilla as follows:

```python
import argilla as rg

rg_ds = rg.DatasetForTextClassification.from_datasets(dataset, annotation="label")

rg.log(
    name="banking77",
    records=rg_ds,
    chunk_size=50,
)
```

:::
::::

## Use semantic search

This section introduces how to use the semantic search feature from Argilla UI and Argilla Python client.

### Argilla UI

::::{tab-set}
:::{tab-item} FeedbackDataset

```{include} /_common/ui_feedback_semantic_search.md
```

:::
:::{tab-item} Older datasets
Within the Argilla UI, it is possible to select a record that has an attached vector to start semantic searching by clicking the "Find similar" button. After labeling, the "Remove similar record filter" button can be pressed to close the specific search and continue with your labeling session.

![Screenshot of Argilla UI](/_static/reference/webapp/features-similaritysearch.png)
:::
::::

### Argilla Python client

To find records similar to a given vector, first we need to produce that vector of reference. Let's see how we can do that with the different frameworks that we used before:

```{warning}
In order to get good results, make sure you are using the same encoder model for generating the vector used for the query. For example, if your dataset has been encoded with the `bge-small-en` model from sentence transformers, make sure to use the same model for encoding the text to be used for querying. Another option is to use an existing record in your dataset, which already contains a vector.
```

::::{tab-set}

:::{tab-item} Sentence Transformers

```python
from sentence_transformers import SentenceTransformer

encoder = SentenceTransformer("BAAI/bge-small-en", device="cpu")

vector = encoder.encode("I lost my credit card. What should I do?").tolist()
```

:::

:::{tab-item} OpenAI Embeddings

```python
vector = openai.Embedding.create(
    input = ["I lost my credit card. What should I do?"],
    model="text-similarity-ada-001"
)["data"][0]["embedding"]
```

:::

:::{tab-item} Cohere co.Embed

```python
vector = co.embed(["I lost my credit card. What should I do?"], model="small").embeddings[0]
```

:::

::::

Now that we have our reference vector, we can do a semantic search in the Python SDK:

::::{tab-set}

:::{tab-item} Feedback Datasets

```{include} /_common/sdk_feedback_semantic_search.md
```

:::

:::{tab-item} Older datasets

The `rg.load` method includes a `vector` parameter which can be used to retrieve similar records to a given vector, and a `limit` parameter to indicate the number of records to be retrieved. This parameter accepts a tuple with the key of the target vector (this should match with one of the keys of the `vectors` dictionary) and the query vector itself.

In addition, the `vector` param can be combined with the `query` param to combine vector search with traditional search.

```python
ds = rg.load(
    name="banking77-openai",
    vector=("my-vector-name", vector),
    limit=20,
    query="annotated_as:card_arrival"
)
```

:::

::::
