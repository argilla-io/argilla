# 🎫 Work with vectors

## Feedback Dataset

```{include} /_common/feedback_dataset.md
```

![workflow](/_static/tutorials/end2end/base/workflow_vectors.svg)


### Define `vectors_settings`

To use the similarity search in the UI and the Python SDK, you will need to configure vector settings. These are defined using the SDK as a list of up to 5 vectors when [creating a FeedbackDataset](/practical_guides/create_update_dataset/create_dataset) or adding them to an already existing FeedbackDataset. They have the following arguments:

- `name`: The name of the vector, as it will appear in the records.
- `dimensions`: The dimensions of the vectors used in this setting.
- `title` (optional): A name for the vector to display in the UI for better readability.

```python
vectors_settings = [
    rg.VectorSettings(
        name="my_vector",
        dimensions=768
    ),
    rg.VectorSettings(
        name="my_other_vector",
        title="Another Vector", # optional
        dimensions=768
    )
]
```

#### Add `vectors_settings`

If you want to add vector settings when creating a dataset, you can pass them as a list of `VectorSettings` instances to the `vector_settings` argument of the `FeedbackDataset` constructor as shown [here](/practical_guides/create_update_dataset/create_dataset.md#create-the-dataset).
For an end-to-end example, check our [tutorial on adding vectors](/tutorials_and_integrations/tutorials/feedback/end2end_examples/add-vectors-004.ipynb).

```python
vector_settings = rg.VectorSettings(
    name="sentence_embeddings",
    title="Sentence Embeddings",
    dimensions=384
)
dataset.add_vector_settings(vector_settings)
```

Once the vector settings are added, you can check their definition using `vector_settings_property_by_name`.

```python
dataset.vector_settings_property_by_name("sentence_embeddings")
# rg.VectorSettings(
#     name="sentence_embeddings",
#     title="Sentence Embeddings",
#     dimensions=768
# )
```

#### Update `vectors_settings`

You can update the vector settings for a `FeedbackDataset`, via assignment. If the dataset was already pushed to Argilla and you are working with a `RemoteFeedbackDataset`, you can update them using the `update_vector_settings` method.

```{note}
The dataset not yet pushed to Argilla or pulled from HuggingFace Hub is an instance of `FeedbackDataset` whereas the dataset pulled from Argilla is an instance of `RemoteFeedbackDataset`.
```

```python
vector_config = dataset.vector_settings_by_name("sentence_embeddings")
vector_config.title = "Embeddings"
dataset.update_vectors_settings(vector_config)
```

#### Delete `vectors_settings`

If you need to delete vector settings from an already configured `FeedbackDataset`, you can use the `delete_vector_settings` method.

```python
dataset.delete_vectors_settings("sentence_embeddings")
```

### Format `vectors`
You can associate vectors, like text embeddings, to your records. This will enable the [semantic search](filter_dataset.md#semantic-search) in the UI and the Python SDK. These are saved as a dictionary, where the keys correspond to the `name`s of the vector settings that were configured for your dataset and the value is a list of floats. Make sure that the length of the list corresponds to the dimensions set in the vector settings.

```{hint}
Vectors should have the following format `List[float]`. If you are using numpy arrays, simply convert them using the method `.tolist()`.
```

```python
record = rg.FeedbackRecord(
    fields={...},
    vectors={"my_vector": [...], "my_other_vector": [...]}
)
```

#### Add `vectors`

Once the `vector_settings` were defined, to add vectors to the records, it slightly depends on whether you are using a `FeedbackDataset` or a `RemoteFeedbackDataset`. For an end-to-end example, check our [tutorial on adding vectors](/tutorials_and_integrations/tutorials/feedback/end2end_examples/add-vectors-004.ipynb).

```{note}
The dataset not yet pushed to Argilla or pulled from HuggingFace Hub is an instance of `FeedbackDataset` whereas the dataset pulled from Argilla is an instance of `RemoteFeedbackDataset`. The difference between the two is that the former is a local one and the changes made on it stay locally. On the other hand, the latter is a remote one and the changes made on it are directly reflected on the dataset on the Argilla server, which can make your process faster.
```

::::{tab-set}

:::{tab-item} Local dataset
```python
for record in dataset.records:
    record.vectors["my_vectors"] = [0.1, 0.2, 0.3, 0.4]
```
:::

:::{tab-item} Remote dataset
```python
modified_records = []
for record in dataset.records:
    record.vectors["my_vectors"] = [0.1, 0.2, 0.3, 0.4]
    modified_records.append(record)
dataset.update_records(modified_records)
```
:::

::::

```{note}
You can also follow the same strategy to modify existing vectors.
```

### Add Sentence Transformers `vectors`

You can easily add semantic embeddings to your records or datasets using the `SentenceTransformersExtractor` based on the [sentence-transformers](https://sbert.net/) library. This extractor is available in the Python SDK and can be used to configure settings for a dataset and extract embeddings from a list of records. The `SentenceTransformersExtractor` has the following arguments:

- `model_name`: The name of the model to use for extracting embeddings. You can find a list of available models [here](https://www.sbert.net/docs/pretrained_models.html).
- `show_progress` (optional): Whether to show a progress bar when extracting metrics. Defaults to `True`.

For a practical example, check our [tutorial on adding sentence transformer embeddings as vectors](/tutorials_and_integrations/integrations/add_sentence_transformers_embeddings_as_vectors.ipynb).

::::{tab-set}

:::{tab-item} Dataset

This can be used to update the dataset and configuration with `VectorSettings` for `Fields` in a `FeedbackDataset` or a `RemoteFeedbackDataset`.

```python
from argilla.client.feedback.integrations.sentencetransformers import SentenceTransformersExtractor

dataset = ... # FeedbackDataset or RemoteFeedbackDataset

tde = SentenceTransformersExtractor(
    model="TaylorAI/bge-micro-v2",
    show_progress=True,
)

dataset = tde.update_dataset(
    dataset=dataset,
    fields=None, # None means using all fields
    update_records=True, # Also, update the records in the dataset
    overwrite=False, # Whether to overwrite existing vectors
)
```
:::

:::{tab-item} Records

This can be used to update the records with `vector` values for `Fields` in a list of `FeedbackRecords`.

```python
from argilla.client.feedback.integrations.textdescrisentencetransformersptives import SentenceTransformersExtractor

records = [...] # FeedbackRecords or RemoteFeedbackRecords

tde = SentenceTransformersExtractor(
    model="TaylorAI/bge-micro-v2",
    show_progress=True,
)

records = tde.update_records(
    records=records,
    fields=None # None means using all fields
    overwrite=False # Whether to overwrite existing vectors
)
```

:::

::::

## Other datasets

```{include} /_common/other_datasets.md
```

### Add `vectors`

You can add vectors to a `TextClassificationRecord`, `TokenClassificationRecord` or `Text2TextRecord`. The vectors is a dictionary with the name as the key and the vectors as the value.

```python
record = rg.TokenClassificationRecord(
    text = "Michael is a professor at Harvard",
    tokens = ["Michael", "is", "a", "professor", "at", "Harvard"],
    vectors = {
        "bert_base_uncased": [3.2, 4.5, 5.6, 8.9]
        }
)

```