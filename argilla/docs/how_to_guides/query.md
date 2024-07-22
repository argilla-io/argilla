---
description: In this section, we will provide a step-by-step guide to show how to filter and query a dataset.
---

# Query and filter records

This guide provides an overview of how to query and filter a dataset in Argilla.

You can search for records in your dataset by **querying** or **filtering**. The query focuses on the content of the text field, while the filter is used to filter the records based on conditions. You can use them independently or combine multiple filters to create complex search queries. You can also export records from a dataset either as a single dictionary or a list of dictionaries.

!!! info "Main Classes"

    === "`rg.query`"

        ```python
        rg.Query(
            query="query",
            filter=filter
        )
        ```
        > Check the [Query - Python Reference](../reference/argilla/search.md) to see the attributes, arguments, and methods of the `Query` class in detail.

    === "`rg.Filter`"

        ```python
        rg.Filter(
            [
                ("field", "==", "value"),
            ]
        )
        ```
        > Check the [Filter - Python Reference](../reference/argilla/search.md) to see the attributes, arguments, and methods of the `Filter` class in detail.

## Query with search terms

To search for records with terms, you can use the `Dataset.records` attribute with a query string. The search terms are used to search for records that contain the terms in the text field. You can search a single term or various terms, in the latter, all of them should appear in the record to be retrieved.

=== "Single search term"

    ```python
    import argilla as rg

    client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

    workspace = client.workspaces("my_workspace")

    dataset = client.datasets(name="my_dataset", workspace=workspace)

    query = rg.Query(query="my_term")

    queried_records = list(dataset.records(query=query))
    ```

=== "Multiple search term"

    ```python
    import argilla as rg

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
    import argilla as rg

    client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

    workspace = client.workspaces("my_workspace")

    dataset = client.datasets(name="my_dataset", workspace=workspace)

    filter_label = rg.Filter(("label", "==", "positive"))

    filtered_records = list(dataset.records(query=rg.Query(filter=filter_label)))
    ```

=== "Multiple conditions"

    ```python
    import argilla as rg

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

You can filter records based on record or response status. Record status can be `pending` or `completed` and response status can be `pending`, `draft`, `submitted`, or `discarded`.

```python
import argilla as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

workspace = client.workspaces("my_workspace")

dataset = client.datasets(name="my_dataset", workspace=workspace)

status_filter = rg.Query(
    filter=rg.Filter(
        [
            ("status", "==", "completed"),
            ("response.status", "==", "discarded")
        ]
    )
)

filtered_records = list(dataset.records(status_filter))
```

## Query and filter a dataset

As mentioned, you can use a query with a search term and a filter or various filters to create complex search queries.

```python
import argilla as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

workspace = client.workspaces("my_workspace")

dataset = client.datasets(name="my_dataset", workspace=workspace)

query_filter = rg.Query(
    query="my_term",
    filter=rg.Filter(
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
