---
description: In this section, we will provide a step-by-step guide to show how to import and export datasets to Python, local disk, or the Hugging Face Hub
---

# Importing and exporting datasets and records

This guide provides an overview of how to import and export your dataset or its records to Python, your local disk, or the Hugging Face Hub.

In Argilla, you can import/export two main components of a dataset:
- The dataset's complete configuration defined in `rg.Settings`. This is useful if your want to share your feedback task or restore it later in Argilla.
- The records stored in the dataset, including `Metadata`, `Vectors`, `Suggestions`, and `Responses`. This is useful if you want to use your dataset's records outside of Argilla.

Check the [Dataset - Python Reference](../reference/argilla/datasets/dataset.md) to see the attributes, arguments, and methods of the export `Dataset` class in detail.

## Export an `rg.Dataset` from Argilla

First, we will go through exporting a complete dataset from Argilla. This includes the dataset's setting and records. All of these methods use the `rg.Dataset.from_*` and `rg.Dataset.to_*` methods.

### Push an Argilla dataset to the Hugging Face Hub

You can push a dataset from Argilla to the Hugging Face Hub. This is useful if you want to share your dataset with the community or version control it. You can push the dataset to the Hugging Face Hub using the `rg.Dataset.to_hub` method.

```python
import argilla as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")
dataset = client.datasets(name="my_dataset")
dataset.to_hub(repo_id="<repo_id>")
```

!!! note "With or without records"
    The example above will push the dataset's `Settings` and records to the hub. If you only want to push the dataset's configuration, you can set the `with_records` parameter to `False`. This is useful if you're just interested in a specific dataset template or you want to make changes in the dataset settings and/or records.

    ```python
    dataset.to_hub(repo_id="<repo_id>", with_records=False)
    ```
    With the dataset's configuration you could then make changes to the dataset's settings, or add records via the `datasets` package.

    ```python
    hf_dataset = load_dataset("<repo_id>")
    dataset.log(hf_dataset)
    ```

### Pull an Argilla dataset from the Hugging Face Hub

You can pull a dataset from the Hugging Face Hub to Argilla. This is useful if you want to restore a dataset and its configuration. You can pull the dataset from the Hugging Face Hub using the `rg.Dataset.from_hub` method.

```python

import argilla as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")
dataset = rg.Dataset.from_hub(repo_id="<repo_id>")
```

Note that this approach loads the configuration from the repo and stores the records. If you only want to load records, use the `load_dataset` method of the `datasets` package, and pass the dataset to `rg.Dataset.log` method. This enables you to configure your own dataset and reuse existing Hub datasets. See the [guide on records](record.md) for more information.

### Saving an Argilla dataset to local disk

You can save a dataset from Argilla to your local disk. This is useful if you want to back up your dataset. You can use the `rg.Dataset.to_disk` method.

```python
import argilla as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")
dataset = client.datasets(name="my_dataset", workspace=workspace)

dataset.to_disk(path="path/to/dataset")
```

This will save the dataset's configuration and records to the specified path. If you only want to save the dataset's configuration, you can set the `with_records` parameter to `False`.

```python
dataset.to_disk(path="path/to/dataset", with_records=False)
```

### Loading an Argilla dataset from local disk

You can load a dataset from your local disk to Argilla. This is useful if you want to restore a dataset's configuration. You can use the `rg.Dataset.from_disk` method.

```python
import argilla as rg

dataset = rg.Dataset.from_disk(path="path/to/dataset")
```

!!! note "Directing the dataset to a workspace and name"
    You can also specify the workspace and name of the dataset when loading it from the disk.

    ```python
    dataset = rg.Dataset.from_disk(path="path/to/dataset", target_workspace=workspace, target_name="my_dataset")
    ```

## Export only records from Argilla Datasets

The records alone can be exported from a dataset in Argilla.  This is useful if you want to process the records in Python, export them to a different platform, or use them in model training. All of these methods use the `rg.Dataset.records` attribute.

The records can be exported as a dictionary, a list of dictionaries, or to a `Dataset` of the `datasets` package.

To import records to a dataset, used the `rg.Datasets.records.log` method. Their is a guide on how to do this in the [Record - Python Reference](record.md).

=== "To the `datasets` package"


    Records can be exported from `Dataset.records` to the `datasets` package. The `to_dataset` method can be used to export records to the `datasets` package. You can specify the name of the dataset and the split to export the records.

    ```python
    import argilla as rg

    client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")
    dataset = client.datasets(name="my_dataset")

    # Export records as a dictionary
    exported_ds = dataset.records.to_datasets()
    ```

=== "To a Python dictionary"

    Records can be exported from `Dataset.records` as a dictionary. The `to_dict` method can be used to export records as a dictionary. You can specify the orientation of the dictionary output. You can also decide if to flatten or not the dictionary.

    ```python
    import argilla as rg

    client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")
    dataset = client.datasets(name="my_dataset")

    # Export records as a dictionary
    exported_records = dataset.records.to_dict()
    # {'fields': [{'text': 'Hello'},{'text': 'World'}], suggestions': [{'label': {'value': 'positive'}}, {'label': {'value': 'negative'}}]

    # Export records as a dictionary with orient=index
    exported_records = dataset.records.to_dict(orient="index")
    # {"uuid": {'fields': {'text': 'Hello'}, 'suggestions': {'label': {'value': 'positive'}}}, {"uuid": {'fields': {'text': 'World'}, 'suggestions': {'label': {'value': 'negative'}}},

    # Export records as a dictionary with flatten=false
    exported_records = dataset.records.to_dict(flatten=True)
    # {"text": ["Hello", "World"], "label.suggestion": ["greeting", "greeting"]}
    ```

=== "To a python list"

    Records can be exported from `Dataset.records` as a list of dictionaries. The `to_list` method can be used to export records as a list of dictionaries. You can decide if to flatten it or not.

    ```python
    import argilla as rg

    client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

    workspace = client.workspaces("my_workspace")

    dataset = client.datasets(name="my_dataset", workspace=workspace)

    # Export records as a list of dictionaries
    exported_records = dataset.records.to_list()
    # [{'fields': {'text': 'Hello'}, 'suggestion': {'label': {value: 'greeting'}}}, {'fields': {'text': 'World'}, 'suggestion': {'label': {value: 'greeting'}}}]

    # Export records as a list of dictionaries with flatten=False
    exported_records = dataset.records.to_list(flatten=True)
    # [{"text": "Hello", "label": "greeting"}, {"text": "World", "label": "greeting"}]
    ```
