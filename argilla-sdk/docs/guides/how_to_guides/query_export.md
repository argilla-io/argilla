---
description: In this section, we will provide a step-by-step guide to show how to filter and query a dataset.
---

# Query, filter, and export records

This guide provides an overview of how to query and filter a dataset in Argilla and export records.

You can search for records in your dataset by **querying** or **filtering**. The query focuses on the content of the text field, while the filter is used to filter the records based on conditions. You can use them independently or combine multiple filters to create complex search queries. You can also export records from a dataset either as a single dictionary or a list of dictionaries.

!!! info "Main Classes"

    === "`rg.query`"

        ```python
        rg.Query(
            query="query",
            filter=filter
        )
        ```
        > Check the [Query - Python Reference](../../reference/argilla_sdk/search.md) to see the attributes, arguments, and methods of the `Query` class in detail.

    === "`rg.Filter`"

        ```python
        rg.Filter(
            [
                ("field", "==", "value"),
            ]
        )
        ```
        > Check the [Filter - Python Reference](../../reference/argilla_sdk/search.md) to see the attributes, arguments, and methods of the `Filter` class in detail.

## Query with search terms

To search for records with terms, you can use the `Dataset.records` attribute with a query string. The search terms are used to search for records that contain the terms in the text field. You can search a single term or various terms, in the latter, all of them should appear in the record to be retrieved.

=== "Single search term"

    ```python
    import argilla_sdk as rg

    client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

    workspace = client.workspaces("my_workspace")

    dataset = client.datasets(name="my_dataset", workspace=workspace)

    query = rg.Query(query="my_term")

    queried_records = list(dataset.records(query=query))
    ```

=== "Multiple search term"

    ```python
    import argilla_sdk as rg

    client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

    workspace = client.workspaces("my_workspace")

    dataset = client.datasets(name="my_dataset", workspace=workspace)

    query = rg.Query(query="my_term1 my_term2")

    queried_records = list(dataset.records(query=query))
    ```

## Filter by conditions

You can use the `Filter` class to define the conditions and pass them to the `Dataset.records` attribute to fetch records based on the conditions. Conditions include "==", ">=", "<=", or "in". Conditions can be combined with dot notation to filter records based on metadata, suggestions, or responses. You can use a single condition or multiple conditions to filter records.

| operator | description |
|----------|-------------|
| `==`     | The `field` value is equal to the `value` |
| `>=`     | The `field` value is greater than or equal to the `value` |
| `<=`     | The `field` value is less than or equal to the `value` |
| `in`     | TThe `field` value is included in a list of values |

=== "Single condition"

    ```python
    import argilla_sdk as rg

    client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

    workspace = client.workspaces("my_workspace")

    dataset = client.datasets(name="my_dataset", workspace=workspace)

    filter_label = rg.Filter(("label", "==", "positive"))

    filtered_records = list(dataset.records(query=rg.Query(filter=filter_label)))
    ```

=== "Multiple conditions"

    ```python
    import argilla_sdk as rg

    client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

    workspace = client.workspaces("my_workspace")

    dataset = client.datasets(name="my_dataset", workspace=workspace)

    filters = rg.Filter(
        [
            ("label.suggestion", "==", "positive"),
            ("metadata.count", ">=", 10),
            ("metadata.count", "<=", 20),
            ("label", "in", ["positive", "negative"])
        ]
    )

    filtered_records = list(dataset.records(
        query=rg.Query(filter=filters)),
        with_suggestions=True
    )
    ```

## Filter by status

You can filter records based on their status. The status can be `pending`, `draft`, `submitted`, or `discarded`.

```python
import argilla_sdk as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

workspace = client.workspaces("my_workspace")

dataset = client.datasets(name="my_dataset", workspace=workspace)

status_filter = rg.Query(
    filter = rg.Filter(("status", "==", "submitted"))
)

filtered_records = list(dataset.records(status_filter))
```

## Query and filter a dataset

As mentioned, you can use a query with a search term and a filter or various filters to create complex search queries.

```python
import argilla_sdk as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

workspace = client.workspaces("my_workspace")

dataset = client.datasets(name="my_dataset", workspace=workspace)

query_filter = rg.Query(
    query="my_term",
    filter= rg.Filter(
        [
            ("label.suggestion", "==", "positive"),
            ("metadata.count", ">=", 10),
        ]
    )
)

queried_filtered_records = list(dataset.records(
    query=query_filter,
    with_metadata=True,
    with_suggestions=True
    )
)
```

## Export records to a dictionary

Records can be exported from `Dataset.records` as a dictionary. The `to_dict` method can be used to export records as a dictionary. You can specify the orientation of the dictionary output. You can also decide if to flatten or not the dictionary.

=== "
```python
import argilla_sdk as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

workspace = client.workspaces("my_workspace")

dataset = client.datasets(name="my_dataset", workspace=workspace)

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

## Export records to a list

Records can be exported from `Dataset.records` as a list of dictionaries. The `to_list` method can be used to export records as a list of dictionaries. You can decide if to flatten it or not.

```python
import argilla_sdk as rg

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
