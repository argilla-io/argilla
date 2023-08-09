# Update a Feedback dataset
Oftentimes datasets that we have created previously need modifications or updates. In this section, we will explore some of the most common workflows to change an existing Feedback dataset in Argilla.

## Adding more records

To add a (list of) Feedback record(s) to an existing dataset you will only need to load the dataset using the Python client and use the `add_records` method as explained below:

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

From `v1.14.0` it is also possible to delete records from a Feedback dataset using the `delete` method like so:

```python
# load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")
# delete a specific record
dataset.records[0].delete()
```

If you prefer to delete a list of records, you can also achive this in this way:

```python
# load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")
# delete a list of records from a dataset
dataset.delete_records([record for record in dataset.records[:5]])
```

## Adding suggestions to existing records

You can also add suggestions to records that have been already pushed to Argilla:

::::{tab-set}

:::{tab-item} Argilla 1.14.0 or higher
```python
# load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")

for record in dataset.records:
    record.update(suggestions=[...])
```
:::

:::{tab-item} Lower than Argilla 1.14.0
```python
# load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")

for record in dataset.records:
    record.set_suggestions([...])
```
:::
::::

To learn about the schema that these suggestion should follow check [this page](create_dataset.md#add-suggestions).

## Update suggestions in existing records

Existing suggestions can also be modified and updated Argilla `v1.14.0` using the same method as the one in the section above. This will overwrite any existing suggestions.

```python
# load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")

for record in dataset.records:
    record.update(suggestions=[...])
```

To learn about the schema that these suggestion should follow check [this page](create_dataset.md#add-suggestions).