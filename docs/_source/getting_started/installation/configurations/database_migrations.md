# Database Migrations

## Migrating from old schema

For old Argilla versions, labels created from the UI were not included as part of a labeling schema. Instead, the UI used the dataset metadata index in Elastic Search to store
this information.

```{warning} Warning
From Argilla version v1.4.0, all labels will be created using the new label schema settings. Be sure to migrate datasets with labels created using the UI to the proper label schema.
```

If you want to move this info to the corresponding label schema, you can execute the next code snippet:

Here is a code snippet showing how to do it:

```python
import argilla as rg
from argilla.client import api

rg.init()
client = api.active_client()

# This metadata key was used by the UI to store created labels in datasets
CUSTOM_DATA_KEY = "rubrix.recogn.ai/ui/custom/userData.v1"
datasets = [dataset for dataset in client.http_client.get("/api/datasets") if CUSTOM_DATA_KEY in dataset["metadata"]]
print(f"Found {len(datasets)} datasets to migrate")
for ds in datasets:
    metadata = ds["metadata"]
    task = ds["task"]
    name = ds["name"]
    workspace = ds["owner"]  # owner will be replaced by `workspace` in newer versions

    if task == "TextClassification":  # Build text classification settings
        labels = metadata[CUSTOM_DATA_KEY]["labels"]
        settings = rg.TextClassificationSettings(label_schema=set(labels))
    elif task == "TokenClassification":  # Build token classification settings
        labels = metadata[CUSTOM_DATA_KEY]["entities"]
        settings = rg.TokenClassificationSettings(label_schema=set(labels))
    else:
        raise Exception(f"No labels key for task {task}. {dataset}")

    # Setting the dataset workspace to work with current dataset
    rg.set_workspace(workspace)

    # We will complete labels schema with labels found in dataset records.
    # This will avoid errors on label schema validation (when labels in records are not present in the label schema)
    metrics = client.compute_metric(name=name, metric="dataset_labels")
    for label in metrics.results["labels"]:
        settings.label_schema.add(label)
    print(f"Settings labels for dataset '{name}': {settings}")
    rg.configure_dataset(name=name, settings=settings)
```

```python
import argilla as rg
from argilla.client import api

rg.init()
rg_client = api.active_client()

new_workspace = "<put-target-workspace-here>"

empty_workspace_datasets = [
    ds["name"]
    for ds in rg_client.http_client.get("/api/datasets")
    # filtering dataset with no workspace (use `"owner"` if you're running this code with server versions <=1.3.0)
    if not ds.get("workspace", None)
]

rg.set_workspace("")  # working from the "empty" workspace

for dataset in empty_workspace_datasets:
    rg.copy(dataset, dataset, new_workspace)

# Dataset are normally copied to the provided workspace
# You should delete datasets with no workspace
# In that case, uncomment following lines
# for dataset in empty_workspace_datasets:
#    rg.delete(dataset)
```

## Reindex a dataset

Sometimes updates require us to reindex the data.

### Argilla Metrics

For our internally computed metrics, this can be done by simply, loading and logging the same records back to the same index. This is because our internal metrics are computed and updated during logging.

```python
import argilla as rg

dataset = "my-outdated-dataset"
ds = rg.load(dataset)
rg.log(ds, dataset)
```

### Elasticsearch

For Elastic indices, re-indexing requires a bit more effort. To be certain of a proper re-indexing, we requires loading the records, and storing them within a completely new index.

```python
import argilla as rg

dataset = "my-outdated-dataset"
ds = rg.load(dataset)
new_dataset = "my-new-dataset"
rg.log(ds, new_dataset)
```

#### Feedback datasets

If you are using new feedback datasets and you want to update the search engine info, you should copy your dataset:

::::{tab-set}

:::{tab-item} Argilla 1.14.0 or higher
```python
import argilla as rg

dataset = rg.FeedbackDataset.from_argilla(name="feedback-dataset")
dataset = dataset.pull()
dataset.push_to_argilla(name=f"{dataset.name}_copy")
```
:::

:::{tab-item} Lower than Argilla 1.14.0
```python
import argilla as rg

dataset = rg.FeedbackDataset.from_argilla(name="feedback-dataset")
dataset.push_to_argilla(name=f"{dataset.name}_copy")
```
:::

::::
