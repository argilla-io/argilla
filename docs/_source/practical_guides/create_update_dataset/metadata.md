# 💾 Work with metadata

## Feedback Dataset

```{include} /_common/feedback_dataset.md
```
![workflow](/_static/tutorials/end2end/base/workflow_metadata.svg)

### Define `metadata_properties`

Metadata properties allow you to configure the use of metadata information for the filtering and sorting features available in the UI and Python SDK.

You can define metadata properties using the Python SDK when [creating a FeedbackDataset](/practical_guides/create_update_dataset/create_dataset) or adding them to an already existing FeedbackDataset. They have the following arguments:

- `name`: The name of the metadata property, as it will be used internally.
- `title` (optional): The name of the metadata property, as it will be displayed in the UI. Defaults to the `name` value, but capitalized.
- `visible_for_annotators` (optional): A boolean to specify whether the metadata property will be accessible for users with an `annotator` role in the UI (`True`), or if it will only be visible for users with `owner` or `admin` roles (`False`). It is set to `True` by default.

The following arguments apply to specific metadata types:
- `values` (optional): In a `TermsMetadataProperty`, you can pass a list of valid values for this metadata property, in case you want to run any validation. If none are provided, the list of values will be computed from the values provided in the records.
- `min` (optional): In an `IntegerMetadataProperty` or a `FloatMetadataProperty`, you can pass a minimum valid value. If none is provided, the minimum value will be computed from the values provided in the records.
- `max` (optional): In an `IntegerMetadataProperty` or a `FloatMetadataProperty`, you can pass a maximum valid value. If none is provided, the maximum value will be computed from the values provided in the records.

```{include} /_common/tabs/metadata_types.md
```

#### Add `metadata_properties`

If you want to add metadata properties when creating a dataset, you can pass them as a list of `MetadataProperty` instances to the `metadata_properties` argument of the `FeedbackDataset` constructor as shown [here](/practical_guides/create_update_dataset/create_dataset.md#create-the-dataset). If you want to add metadata properties to an existing dataset, you can use the `add_metadata_properties` method. For an end-to-end example, check our [tutorial on adding metadata](/tutorials_and_integrations/tutorials/feedback/end2end_examples/add-metadata-003.ipynb).

```python
metadata_property = rg.TermsMetadataProperty(
    name="groups",
    title="Annotation groups",
    values=["group-a", "group-b", "group-c"]
)
dataset.add_metadata_property(metadata_property)
```

Once the metadata properties were added, you can check their definition using `metadata_property_by_name`.

```python
dataset.metadata_property_by_name("groups")
# rg.TermsMetadataProperty(
#     name="groups",
#     title="Annotation groups",
#     values=["group-a", "group-b", "group-c"]
# )
```

#### Update `metadata_properties`

You can update the metadata properties for a `FeedbackDataset`, via assignment. If the dataset was already pushed to Argilla and you are working with a `RemoteFeedbackDataset`, you can update them using the `update_metadata_properties` method.

```{note}
The dataset not yet pushed to Argilla or pulled from HuggingFace Hub is an instance of `FeedbackDataset` whereas the dataset pulled from Argilla is an instance of `RemoteFeedbackDataset`.
```

```python
metadata_config = dataset.metadata_property_by_name("groups")
metadata_config.title = "Teams"
dataset.update_metadata_properties(metadata_config)
```

#### Delete `metadata_properties`

If you need to delete metadata properties from an already configured `FeedbackDataset`, you can use the `delete_metadata_properties` method.

```python
dataset.delete_metadata_properties(metadata_properties="groups")
```

### Format `metadata`

Record metadata can include any information about the record that is not part of the fields in the form of a dictionary. If you want the metadata to correspond with the metadata properties configured for your dataset so that these can be used for filtering and sorting records, make sure that the key of the dictionary corresponds with the metadata property `name`. When the key doesn't correspond, this will be considered extra metadata that will get stored with the record (as long as `allow_extra_metadata` is set to `True` for the dataset), but will not be usable for filtering and sorting. For any metadata property, you can define a single metadata value in the form of a string or integer, or multiple metadata values in the form of a list of strings or integers.

::::{tab-set}

:::{tab-item} Single Metadata

```python
record = rg.FeedbackRecord(
    fields={...},
    metadata={"source": "encyclopedia", "text_length":150}
)
```
:::

:::{tab-item} Multiple Metadata
```python
record = rg.FeedbackRecord(
    fields={...},
    metadata={"source": ["encyclopedia", "wikipedia"], "text_length":150}
)
```

:::

::::

#### Add `metadata`

Once the `metadata_properties` were defined, to add metadata to the records, it slightly depends on whether you are using a `FeedbackDataset` or a `RemoteFeedbackDataset`. For an end-to-end example, check our [tutorial on adding metadata](/tutorials_and_integrations/tutorials/feedback/end2end_examples/add-metadata-003.ipynb). Remember that you can either define a single metadata value for a metadata property or aggregate metadata values for the `TermsMetadataProperty` in the form of a list for the cases where one record falls into multiple metadata categories.

```{note}
The dataset not yet pushed to Argilla or pulled from HuggingFace Hub is an instance of `FeedbackDataset` whereas the dataset pulled from Argilla is an instance of `RemoteFeedbackDataset`. The difference between the two is that the former is a local one and the changes made on it stay locally. On the other hand, the latter is a remote one and the changes made on it are directly reflected on the dataset on the Argilla server, which can make your process faster.
```

::::{tab-set}

:::{tab-item} Local dataset
```python
for record in dataset.records:
    record.metadata["my_metadata"] = "new_metadata"
```
:::

:::{tab-item} Remote dataset
```python
modified_records = []
for record in dataset.records:
    record.metadata["my_metadata"] = "new_metadata"
    modified_records.append(record)
dataset.update_records(modified_records)
```
:::

::::

```{note}
You can also follow the same strategy to modify existing metadata.
```

### Add Text Descriptives

You can easily add text descriptives to your records or datasets using the `TextDescriptivesExtractor` based on the [TextDescriptives](https://github.com/HLasse/TextDescriptives) library, which will add the corresponding metadata properties and metadata automatically. The `TextDescriptivesExtractor` can be used on a `FeedbackDataset` or a `RemoteFeedbackDataset` and accepts the following arguments:

- `model` (optional): The language of the spacy model that will be used. Defaults to `en`. Check [here](https://spacy.io/usage/models) the available languages and models.
- `metrics` (optional): A list of metrics to extract. The default extracted metrics are: `n_tokens`, `n_unique_tokens`, `n_sentences`, `perplexity`, `entropy`, and `flesch_reading_ease`. You can select your metrics according to the following groups `descriptive_stats`, `readability`, `dependency_distance`, `pos_proportions`, `coherence`, `quality`, and `information_theory`. For more information about each group, check this documentation [page](https://hlasse.github.io/TextDescriptives/descriptivestats.html).
- `visible_for_annotators` (optional): Whether the extracted metrics should be visible to annotators. Defaults to `True`.
- `show_progress` (optional): Whether to show a progress bar when extracting metrics. Defaults to `True`.

For a practical example, check our [tutorial on adding text descriptives as metadata](/tutorials_and_integrations/integrations/add_text_descriptives_as_metadata.ipynb).

::::{tab-set}

:::{tab-item} Dataset

This can be used to update the dataset and configuration with `MetadataProperties` for `Fields` in a `FeedbackDataset` or a `RemoteFeedbackDataset`.

```python
from argilla.client.feedback.integrations.textdescriptives import TextDescriptivesExtractor

dataset = ... # FeedbackDataset or RemoteFeedbackDataset

tde = TextDescriptivesExtractor(
    model="en",
    metrics=None,
    visible_for_annotators=True,
    show_progress=True,
)

dataset = tde.update_dataset(
    dataset=dataset
    fields=None # None means using all fields
    update_records=True # Also, update the records in the dataset
    overwrite=False # Whether to overwrite existing vectors
)
```
:::

:::{tab-item} Records

This can be used to update the records with `Metadata` values for `Fields` in a list of `FeedbackRecords`.

```python
from argilla.client.feedback.integrations.textdescriptives import TextDescriptivesExtractor

records = [...] # FeedbackRecords or RemoteFeedbackRecords

tde = TextDescriptivesExtractor(
    model="en",
    metrics=None,
    visible_for_annotators=True,
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

### Add `metadata`

You can add metadata to a `TextClassificationRecord`, `TokenClassificationRecord` or `Text2TextRecord`. The metadata is a dictionary with the name as the key and the metadata as the value.

```python
rg.TokenClassificationRecord(
    text=" ".join(tokens),
    tokens=tokens,
    metadata={"my_metadata": metadata},
)

```

You can easily add metadata to a record by modifying the `metadata` dictionary. This can also be used to modify existing metadata.

```python
dataset = rg.load("my_dataset")
modified_records = []
for record in dataset:
    record.metadata["my_metadata"] = "my_value"
    modified_records.append(record)
rg.log(name="my_dataset", records=modified_records)
```
