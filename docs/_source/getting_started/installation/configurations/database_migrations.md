# Database Migrations

## Argilla server database migrations

Since Argilla 1.6.0, the information about users and workspaces, and the data of the `FeedbackDataset`s is stored in an SQL database (SQLite or PostgreSQL). That being said,
every release of Argilla may require a database migration to update the database schema to the new version. This section explains how to perform the database migrations.

In order to apply the migrations, a connection to the database needs to be established. In the case that SQLite is used, then the only way to apply the migrations is by
executing the migration command from the same machine where the Argilla server is running. In the case that PostgreSQL is used, then the migration command can be executed
from any machine that has access to the PostgreSQL database setting the `ARGILLA_DATABASE_URL` environment variable to the URL of the database.

### Listing the available database revisions/migrations

To list the available database revisions/migrations, the `argilla server database revisions` command can be used. This command will list the different revisions to which
the database can be migrated. As several revisions could be generated for a single release, the command will also show the latest revision that was generated for each release.

```bash
argilla server database revisions
```
```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.

Tagged revisions
-----------------
• 1.7 (revision: '1769ee58fbb4')
• 1.8 (revision: 'ae5522b4c674')
• 1.11 (revision: '3ff6484f8b37')
• 1.13 (revision: '1e629a913727')

Alembic revisions
-----------------
3fc3c0839959 -> 1e629a913727 (head), fix suggestions type enum values
8c574ada5e5f -> 3fc3c0839959, create suggestions table
3ff6484f8b37 -> 8c574ada5e5f, update_enum_columns
ae5522b4c674 -> 3ff6484f8b37, add record metadata column
e402e9d9245e -> ae5522b4c674, create fields table
8be56284dac0 -> e402e9d9245e, create responses table
3a8e2f9b5dea -> 8be56284dac0, create records table
b9099dc08489 -> 3a8e2f9b5dea, create questions table
1769ee58fbb4 -> b9099dc08489, create datasets table
82a5a88a3fa5 -> 1769ee58fbb4, create workspaces_users table
74694870197c -> 82a5a88a3fa5, create workspaces table
<base> -> 74694870197c, create users table

Current revision
----------------
Current revision(s) for sqlite:////Users/gabrielmbmb/.argilla/argilla.db?check_same_thread=False:
Rev: 1e629a913727 (head)
Parent: 3fc3c0839959
Path: /Users/gabrielmbmb/Source/Argilla/argilla/src/argilla/server/alembic/versions/1e629a913727_fix_suggestions_type_enum_values.py

    fix suggestions type enum values

    Revision ID: 1e629a913727
    Revises: 3fc3c0839959
    Create Date: 2023-07-24 12:47:11.715011
```

### Apply the latest migration

If the `migrate` command is called without any argument, then the latest migration will be applied.

```bash
argilla server database migrate
```

### Apply a specific migration

The `migrate` command can also be used to apply a specific migration. To do so, the `--revision` option needs to be provided with the name of the revision or the Argilla
version to which the database will be migrated.

```bash
argilla server database migrate migrate --revision 1.7
```

:::{warning}
Applying a revision that is older than the current revision of the database will revert the database to the state of that revision, which means that the data could be lost.
:::

## Migrating from the old schema

For old Argilla versions, labels created from the UI were not included as part of a labeling schema. Instead, the UI used the dataset metadata index in Elastic Search to store
this information.

```{warning} Warning
From Argilla version v1.4.0, all labels will be created using the new label schema settings. Be sure to migrate datasets with labels created using the UI to the proper label schema.
```

If you want to move this info to the corresponding label schema, you can execute the next code snippet:


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

Sometimes, updates require us to reindex the data.

### Argilla Metrics

For our internally computed metrics, this can be done by simply, loading and logging the same records back to the same index. This is because our internal metrics are computed and updated during logging.

```python
import argilla as rg

dataset = "my-outdated-dataset"
ds = rg.load(dataset)
rg.log(ds, dataset)
```

### Elasticsearch

For Elastic indices, re-indexing requires a bit more effort. To be certain of a proper re-indexing, we require loading the records and storing them within a completely new index.

```python
import argilla as rg

dataset = "my-outdated-dataset"
ds = rg.load(dataset)
new_dataset = "my-new-dataset"
rg.log(ds, new_dataset)
```

### Feedback datasets

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

Additionally from Argilla version `1.21.0` a CLI task is available to reindex all feedback datasets into search engine:

::::{tab-set}

:::{tab-item} Argilla 1.21.0 or higher
```sh
argilla server search-engine reindex
```
:::

::::

Or alternatively reindex only a specific feedback dataset providing an id:

::::{tab-set}

:::{tab-item} Argilla 1.21.0 or higher
```sh
argilla server search-engine reindex --feedback-dataset-id 08476931-ac30-4eec-9a35-bb59b48aea91
```
:::

::::

You can set the `REINDEX_DATASETS` environment variable to `true` to reindex the datasets.

:::

::::
