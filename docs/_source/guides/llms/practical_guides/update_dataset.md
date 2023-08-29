# Update a Feedback Dataset

Oftentimes datasets that we have created previously need modifications or updates. In this section, we will explore some of the most common workflows to change an existing `FeedbackDataset` in Argilla.

Remember that you will need to connect to Argilla to perform any of the actions below.

```python
rg.init(
    api_url="<ARGILLA_API_URL>",
    api_key="<ARGILLA_API_KEY>
)
```

## Add records

To add a `FeedbackRecord` and/or a list of `FeedbackRecord`s to an existing dataset you will need to load the `FeedbackDataset` from Argilla first, calling `FeedbackDataset.from_argilla`, and then call the `add_records` method.

:::{note}
From Argilla 1.14.0, calling `from_argilla` will pull the `FeedbackDataset` from Argilla, but the instance will be remote, which implies that the additions, updates, and deletions of records will be pushed to Argilla as soon as they are made. This is a change from previous versions of Argilla, where you had to call `push_to_argilla` again to push the changes to Argilla.
:::

::::{tab-set}

:::{tab-item} Argilla 1.14.0 or higher
```python
# load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")
# list of Feedback records to add
new_records = [...]
# add records to the dataset
dataset.add_records(new_records)
```
:::

:::{tab-item} Lower than Argilla 1.14.0
```python
# load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")
# list of Feedback records to add
new_records = [...]
# add records to the dataset
dataset.add_records(new_records)
# push the dataset to Argilla
dataset.push_to_argilla()
```
:::
::::

To learn about the format that these records follow, check [this page](create_dataset.md#add-records) or go to our [cheatsheet](../../../getting_started/cheatsheet.md#create-records).

## Delete existing records

From `v1.14.0`, it is possible to delete records from a `FeedbackDataset` in Argilla. Remember that from 1.14.0, when pulling a `FeedbackDataset` from Argilla via the `from_argilla` method, the returned instance is a remote `FeedbackDataset`, which implies that all the additions, updates, and deletions are directly pushed to Argilla, without having to call `push_to_argilla` for those to be pushed to Argilla.

The first alternative is to call the `delete` method over a single `FeedbackRecord` in the dataset, which will delete that record from Argilla.

```python
# load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")
# delete a specific record
dataset.records[0].delete()
```

Otherwise, you can also select one or more records from the existing `FeedbackDataset` (which are `FeedbackRecord`s in Argilla) and call the `delete_records` method to delete them from Argilla.

```python
# load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")
# delete a list of records from a dataset
dataset.delete_records(list(dataset.records[:5]))
```

## Add or update suggestions in existing records

You can also add suggestions to records that have been already pushed to Argilla and from `v1.14.0` update existing ones.

:::{note}
From Argilla 1.14.0, calling `from_argilla` will pull the `FeedbackDataset` from Argilla, but the instance will be remote, which implies that the additions, updates, and deletions of records will be pushed to Argilla as soon as they are made. This is a change from previous versions of Argilla, where you had to call `push_to_argilla` again to push the changes to Argilla.
:::

::::{tab-set}

:::{tab-item} Argilla 1.14.0 or higher

You can add or update existing suggestions from Argilla `v1.14.0` using this method.

```{note}
If you include in this method a suggestion for a question that already has one, this will overwrite the previous suggestion.
```

```python
# load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")
# loop through the records and add suggestions
for record in dataset.records:
    record.update(suggestions=[...])
```
:::

:::{tab-item} Lower than Argilla 1.14.0

This method will only add suggestions to records that don't have them. To update suggestions, upgrade to `v1.14.0` or higher and follow the snippet in the other tab.

```python
# load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")
# loop through the records and add suggestions
for record in dataset.records:
    record.set_suggestions([...])
dataset.push_to_argilla()
```
:::
::::

To learn about the schema that these suggestions should follow check [this page](create_dataset.md#add-suggestions).
