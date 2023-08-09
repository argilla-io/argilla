# Update a Feedback dataset
Make changes to your Feedback datasets:

## Adding more records
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

## Delete existing records

This is only possible from Argilla 1.14.0

```python
# load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")
# delete a specific record
dataset.records[0].delete()
```

You can also delete a list of records

```python
# load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")
# delete a list of records from a dataset
dataset.delete_records([record for record in dataset.records[:5]])
```

## Adding suggestions to existing records

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

## Update suggestions in existing records

```python
# load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")

for record in dataset.records:
    record.update(suggestions=[...])
```