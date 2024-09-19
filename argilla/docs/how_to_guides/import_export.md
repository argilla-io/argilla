---
description: In this section, we will provide a step-by-step guide to show how to import and export datasets to Python, local disk, or the Hugging Face Hub
---

# Importing and exporting datasets and records

This guide provides an overview of how to import and export your dataset or its records to Python, your local disk, or the Hugging Face Hub.

In Argilla, you can import/export two main components of a dataset:

- The dataset's complete configuration is defined in `rg.Settings`. This is useful if you want to share your feedback task or restore it later in Argilla.
- The records stored in the dataset, including `Metadata`, `Vectors`, `Suggestions`, and `Responses`. This is useful if you want to use your dataset's records outside of Argilla.

Check the [Dataset - Python Reference](../reference/argilla/datasets/datasets.md) to see the attributes, arguments, and methods of the export `Dataset` class in detail.

!!! info "Main Classes"
    === "`rg.Dataset.to_hub`"

        ```python
        rg.Dataset.to_hub(
            repo_id="<my_org>/<my_dataset>",
            with_records=True,
            generate_card=True
        )
        ```

    === "`rg.Dataset.from_hub`"

        ```python
        rg.Dataset.from_hub(
            repo_id="<my_org>/<my_dataset>",
            name="my_dataset",
            workspace="my_workspace",
            client=rg.Client(),
            with_records=True
        )
        ```

    === "`rg.Dataset.to_disk`"

        ```python
        rg.Dataset.to_disk(
            path="<path-empty-directory>",
            with_records=True
        )
        ```

    === "`rg.Dataset.from_disk`"

        ```python
        rg.Dataset.from_disk(
            path="<path-dataset-directory>",
            name="my_dataset",
            workspace="my_workspace",
            client=rg.Client(),
            with_records=True
        )
        ```

    === "`rg.Dataset.records.to_datasets()`"

        ```python
        rg.Dataset.records.to_datasets()
        ```
    === "`rg.Dataset.records.to_dict()`"

        ```python
        rg.Dataset.records.to_dict()
        ```
    === "`rg.Dataset.records.to_list()`"

        ```python
        rg.Dataset.records.to_list()
        ```

    > Check the [Dataset - Python Reference](../reference/argilla/datasets/datasets.md) to see the attributes, arguments, and methods of the export `Dataset` class in detail.

    > Check the [Record - Python Reference](../reference/argilla/records/records.md) to see the attributes, arguments, and methods of the `Record` class in detail.


## Importing and exporting datasets

First, we will go through exporting a complete dataset from Argilla. This includes the dataset's settings and records. All of these methods use the `rg.Dataset.from_*` and `rg.Dataset.to_*` methods.

### Hugging Face Hub

#### Export to Hub

You can push a dataset from Argilla to the Hugging Face Hub. This is useful if you want to share your dataset with the community or version control it. You can push the dataset to the Hugging Face Hub using the `rg.Dataset.to_hub` method.

```python
import argilla as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

dataset = client.datasets(name="my_dataset")

dataset.to_hub(repo_id="<my_org>/<my_dataset>")
```

!!! note "With or without records"
    The example above will push the dataset's `Settings` and records to the hub. If you only want to push the dataset's configuration, you can set the `with_records` parameter to `False`. This is useful if you're just interested in a specific dataset template or you want to make changes in the dataset settings and/or records.

    ```python
    dataset.to_hub(repo_id="<my_org>/<my_dataset>", with_records=False)
    ```

#### Import from Hub

You can pull a dataset from the Hugging Face Hub to Argilla. This is useful if you want to restore a dataset and its configuration. You can pull the dataset from the Hugging Face Hub using the `rg.Dataset.from_hub` method.

```python

import argilla as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

dataset = rg.Dataset.from_hub(repo_id="<my_org>/<my_dataset>")
```

The `rg.Dataset.from_hub` method loads the configuration and records from the dataset repo. If you only want to load records, you can pass a `datasets.Dataset` object to the `rg.Dataset.log` method. This enables you to configure your own dataset and reuse existing Hub datasets. See the [guide on records](record.md) for more information.


!!! note "With or without records"

    The example above will pull the dataset's `Settings` and records from the hub. If you only want to pull the dataset's configuration, you can set the `with_records` parameter to `False`. This is useful if you're just interested in a specific dataset template or you want to make changes in the records.

    ```python
    dataset = rg.Dataset.from_hub(repo_id="<my_org>/<my_dataset>", with_records=False)
    ```

    You could then log the dataset's records using the `load_dataset` method of the `datasets` package and pass the dataset to the `rg.Dataset.log` method.

    ```python
    hf_dataset = load_dataset("<my_org>/<my_dataset>")
    dataset.records.log(hf_dataset) # (1)
    ```

    1. You could also use the `mapping` parameter to map record field names to argilla field and question names.

    ```python

#### Import settings from Hub

When importing datasets from the hub, Argilla will load settings from the hub in three ways:

1. If the dataset was pushed to hub by Argilla, then the settings will be loaded from the hub via the configuration file.
2. If the dataset was loaded by another source, then Argilla will define the settings based on the dataset's features in `datasets.Features`. For example, creating a `TextField` for a text feature or a `LabelQuestion` for a label class.
3. You can pass a custom `rg.Settings` object to the `rg.Dataset.from_hub` method via the `settings` parameter. This will override the settings loaded from the hub.

```python
settings = rg.Settings(
    fields=[rg.TextField(name="text")],
    questions=[rg.TextQuestion(name="answer")]
) # (1)

dataset = rg.Dataset.from_hub(repo_id="<my_org>/<my_dataset>", settings=settings)
```

1. The settings that you pass to the `rg.Dataset.from_hub` method will override the settings loaded from the hub, and need to align with the dataset being loaded.

### Local Disk

#### Export to Disk

You can save a dataset from Argilla to your local disk. This is useful if you want to back up your dataset. You can use the `rg.Dataset.to_disk` method. We recommend you to use an empty directory.

```python
import argilla as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

dataset = client.datasets(name="my_dataset")

dataset.to_disk(path="<path-empty-directory>")
```

This will save the dataset's configuration and records to the specified path. If you only want to save the dataset's configuration, you can set the `with_records` parameter to `False`.

```python
dataset.to_disk(path="<path-empty-directory>", with_records=False)
```

#### Import from Disk

You can load a dataset from your local disk to Argilla. This is useful if you want to restore a dataset's configuration. You can use the `rg.Dataset.from_disk` method.

```python
import argilla as rg

dataset = rg.Dataset.from_disk(path="<path-dataset-directory>")
```

!!! note "Directing the dataset to a name and workspace"
    You can also specify the name and workspace of the dataset when loading it from the disk.

    ```python
    dataset = rg.Dataset.from_disk(path="<path-dataset-directory>", name="my_dataset", workspace="my_workspace")
    ```

## Importing and exporting records

The records alone can be exported from a dataset in Argilla.  This is useful if you want to process the records in Python, export them to a different platform, or use them in model training. All of these methods use the `rg.Dataset.records` attribute.

### Export records

The records can be exported as a dictionary, a list of dictionaries, or a `Dataset` of the `datasets` package.

!!! note "With images"
    If your dataset includes images, the recommended approach for exporting records is to use the `to_datasets` method, which exports the images as rescaled PIL objects. With other methods, the images will be exported using the data URI schema.

=== "To a python dictionary"

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

    # Export records as a dictionary with flatten=True
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

    # Export records as a list of dictionaries with flatten=True
    exported_records = dataset.records.to_list(flatten=True)
    # [{"text": "Hello", "label": "greeting"}, {"text": "World", "label": "greeting"}]
    ```

=== "To the `datasets` package"


    Records can be exported from `Dataset.records` to the `datasets` package. The `to_dataset` method can be used to export records to the `datasets` package. You can specify the name of the dataset and the split to export the records.

    ```python
    import argilla as rg

    client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")
    dataset = client.datasets(name="my_dataset")

    # Export records as a dictionary
    exported_dataset = dataset.records.to_datasets()
    ```

### Import records

To import records to a dataset, use the `rg.Datasets.records.log` method. There is a guide on how to do this in [How-to guides - Record](./record.md), or you can check the [Record - Python Reference](../reference/argilla/records/records.md).