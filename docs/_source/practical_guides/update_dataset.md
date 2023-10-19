# 💫 Update a dataset

## Feedback Dataset

```{include} /_common/feedback_dataset.md
```

Oftentimes datasets that we have created previously need modifications or updates. In this section, we will explore some of the most common workflows to change an existing `FeedbackDataset` in Argilla.

Remember that you will need to connect to Argilla to perform any of the actions below.

```python
rg.init(
    api_url="<ARGILLA_API_URL>",
    api_key="<ARGILLA_API_KEY>
)
```

### Add or delete metadata properties
If you want to add a metadata property to an existing dataset, you can do so with the `add_metadata_property` method like so:
```python
ds = rg.FeedbackDataset.from_argilla("my_dataset", workspace="my_workspace")
ds.add_metadata_property(
    rg.TermsMetadataProperty(
        name="my-property",
        title="My property",
        visible_for_annotators=True
    )
)
```

If you want to delete an existing metadata property:
```python
ds = rg.FeedbackDataset.from_argilla("my_dataset", workspace="my_workspace")
mp = ds.metadata_property_by_name("library-version")
ds.delete_metadata_properties(mp)
```

### Add records

To add a `FeedbackRecord` and/or a list of `FeedbackRecord`s to an existing dataset you will need to load the `FeedbackDataset` from Argilla first, calling `FeedbackDataset.from_argilla`, and then call the `add_records` method.

:::{note}
From Argilla 1.14.0, calling `from_argilla` will pull the `FeedbackDataset` from Argilla, but the instance will be remote, which implies that the additions, updates, and deletions of records will be pushed to Argilla as soon as they are made. This is a change from previous versions of Argilla, where you had to call `push_to_argilla` again to push the changes to Argilla.
:::

::::{tab-set}

:::{tab-item} Argilla 1.14.0 or higher

```python
# Load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")
# List of Feedback records to add
new_records = [...]
# Add records to the dataset
dataset.add_records(new_records)
```

:::

:::{tab-item} Lower than Argilla 1.14.0

```python
# Load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")
# List of Feedback records to add
new_records = [...]
# Add records to the dataset
dataset.add_records(new_records)
# Push the dataset to Argilla
dataset.push_to_argilla()
```

:::

::::

To learn about the format that these records follow, check [this page](create_dataset.md#add-records) or go to our [cheatsheet](/getting_started/cheatsheet.md#create-records).

### Delete existing records

From `v1.14.0`, it is possible to delete records from a `FeedbackDataset` in Argilla. Remember that from 1.14.0, when pulling a `FeedbackDataset` from Argilla via the `from_argilla` method, the returned instance is a remote `FeedbackDataset`, which implies that all the additions, updates, and deletions are directly pushed to Argilla, without having to call `push_to_argilla` for those to be pushed to Argilla.

::::{tab-set}

:::{tab-item} Single record
The first alternative is to call the `delete` method over a single `FeedbackRecord` in the dataset, which will delete that record from Argilla.

```python
# Load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")
# Delete a specific record
dataset.records[0].delete()
```
:::

:::{tab-item} Multiple records
Otherwise, you can also select one or more records from the existing `FeedbackDataset` (which are `FeedbackRecord`s in Argilla) and call the `delete_records` method to delete them from Argilla.

```python
# Load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")
# Delete a list of records from a dataset
dataset.delete_records(list(dataset.records[:5]))
```
:::

::::

### Update existing records

It is possible add, update and delete attributes of existing records such as suggestions and metadata by simply modifying the records and saving the changes with the `update_records` method. This is an example of how you would do this:

```python
# Load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")
# Loop through the records and make modifications
for record in dataset.records:
    # e.g. adding /modifying a metadata field
    record.metadata["my_metadata"] = "new_metadata"
    # e.g. removing all suggestions
    record.suggestions = []
    record.update()
```

## Other datasets

```{include} /_common/other_datasets.md
```
### Add records
Records can be added to your dataset by logging them using the `rg.log()` function, just like you did when pushing records for the first time to Argilla (as explained [here](/practical_guides/create_dataset.md#id4)). If the records don't exist already in the dataset, these will be added to it.

### Delete existing records
You can delete records by passing their `id` into the `rg.delete_records()` function or using a query that matches the records. Learn more [here](/reference/python/python_client.rst#argilla.delete_records).

::::{tab-set}

:::{tab-item} Delete by id
```python
## Delete by id
import argilla as rg
rg.delete_records(name="example-dataset", ids=[1,3,5])
```
:::
:::{tab-item} Delete by query
```python
## Discard records by query
import argilla as rg
rg.delete_records(name="example-dataset", query="metadata.code=33", discard_only=True)
```
:::
::::

### Update existing records

It is possible to update records from your Argilla datasets using our Python API. This approach works the same way as an upsert in a normal database, based on the record `id`. You can update any arbitrary parameters and they will be over-written if you use the `id` of the original record.

```python
import argilla as rg

# Read all records in the dataset or define a specific search via the `query` parameter
record = rg.load("my_first_dataset")

# Modify first record metadata (if no previous metadata dict, you might need to create it)
record[0].metadata["my_metadata"] = "I'm a new value"

# Log record to update it, this will keep everything but add my_metadata field and value
rg.log(name="my_first_dataset", records=record[0])
```