from huggingface_hub import dataset_infofrom tests.integration.conftest import client---
description: In this section, we will provide a step-by-step guide to show how to filter and query a dataset.
---

# Query and filter records

This guide provides an overview of how to query and filter a dataset in Argilla.

You can search for records in your dataset by **querying** or **filtering**. The query focuses on the content of the text field, while the filter is used to filter the records based on conditions. You can use them independently or combine multiple filters to create complex search queries. You can also export records from a dataset either as a single dictionary or a list of dictionaries.

!!! info "Main Classes"

    === "`rg.Query`"

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

    === "`rg.Similar`"

        ```python
        rg.Similar(
            name="vector",
            value=(0.1, 0.2, 0.3),
        )
        ```
        > Check the [Similar - Python Reference](../reference/argilla/search.md) to see the attributes, arguments, and methods of the `Similar` class in detail.

## Query with search terms

To search for records with terms, you can use the `Dataset.records` attribute with a query string. The search terms are used to search for records that contain the terms in the text field. You can search a single term or various terms, in the latter, all of them should appear in the record to be retrieved.

=== "Single term search"

    ```python
    import argilla as rg

    client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

    dataset = client.datasets(name="my_dataset", workspace="my_workspace")

    query = rg.Query(query="my_term")

    queried_records = dataset.records(query=query).to_list(flatten=True)
    ```

=== "Multiple terms search"

    ```python
    import argilla as rg

    client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

    dataset = client.datasets(name="my_dataset", workspace="my_workspace")

    query = rg.Query(query="my_term1 my_term2")

    queried_records = dataset.records(query=query).to_list(flatten=True)
    ```

### Advanced queries

If you need more complex searches, you can use [Elasticsearch's simple query string syntax](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-simple-query-string-query.html#simple-query-string-syntax). Here is a summary of the different available operators:

| operator     | description                 | example                                                               |
| ------------ | --------------------------- | --------------------------------------------------------------------- |
|`+` or `space`| **AND**: search both terms  | `argilla + distilabel` or `argilla distilabel`</br> return records that include the terms "argilla" and "distilabel"|
|`|`           | **OR**: search either term  | `argilla | distilabel` </br> returns records that include the term "argilla" or "distilabel"|
|`-`           | **Negation**: exclude a term| `argilla -distilabel` </br> returns records that contain the term "argilla" and don't have the term "distilabel"|
|`*`           | **Prefix**: search a prefix | `arg*`</br> returns records with any words starting with "arg-"|
|`"`           | **Phrase**: search a phrase | `"argilla and distilabel"` </br> returns records that contain the phrase "argilla and distilabel"|
|`(` and `)`   | **Precedence**: group terms | `(argilla | distilabel) rules` </br> returns records that contain either "argilla" or "distilabel" and "rules"|
|`~N`          | **Edit distance**: search a term or phrase with an edit distance| `argilla~1` </br> returns records that contain the term "argilla" with an edit distance of 1, e.g. "argila"|

!!! tip
    To use one of these characters literally, escape it with a preceding backslash `\`, e.g. `"1 \+ 2"` would match records where the phrase "1 + 2" is found.

## Filter by conditions

You can use the `Filter` class to define the conditions and pass them to the `Dataset.records` attribute to fetch records based on the conditions. Conditions include "==", ">=", "<=", or "in". Conditions can be combined with dot notation to filter records based on metadata, suggestions, or responses. You can use a single condition or multiple conditions to filter records.

| operator | description                                               |
| -------- | --------------------------------------------------------- |
| `==`     | The `field` value is equal to the `value`                 |
| `>=`     | The `field` value is greater than or equal to the `value` |
| `<=`     | The `field` value is less than or equal to the `value`    |
| `in`     | The `field` value is included in a list of values        |

=== "Single condition"

    ```python
    import argilla as rg

    client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

    dataset = client.datasets(name="my_dataset", workspace="my_workspace")

    filter_label = rg.Filter(("label", "==", "positive"))

    filtered_records = dataset.records(query=rg.Query(filter=filter_label)).to_list(
        flatten=True
    )
    ```

=== "Multiple conditions"

    ```python
    import argilla as rg

    client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

    dataset = client.datasets(name="my_dataset", workspace="my_workspace")

    filters = rg.Filter(
        [
            ("label.suggestion", "==", "positive"),
            ("metadata.count", ">=", 10),
            ("metadata.count", "<=", 20),
            ("label", "in", ["positive", "negative"])
        ]
    )

    filtered_records = dataset.records(
        query=rg.Query(filter=filters), with_suggestions=True
    ).to_list(flatten=True)
    ```

### Available fields

You can filter records based on the following fields:


| field                   | description                                                                    | example                                                        |
|-------------------------|--------------------------------------------------------------------------------|----------------------------------------------------------------|
| `id`                    | The record id                                                                  | `("id", "in", ["1","2","3"])`                                  |
| `_server_id`            | The internal record id. This value must be a valida UUID                       | `("_server_id", "==", "ba69a996-85c2-4af0-a473-23138929641b")` |
| `inserted_at`           | The date and time the record was inserted. You can pass a datetime or a string | `("inserted_at" ">=", "2024-10-10")`                           |
| `updated_at`            | The date and time the record was updated.                                      | `("updated_at" ">=", "2024-10-10")`                            |
| `status`                | The record status, which can be `pending` or `completed`.                      | `("status", "==", "completed")`                                |
| `response.status`       | The response status, which can be `draft`, `submitted`, or `discarded`.        | `("response.status", "==", "submitted")`                       |
| `metadata.<name>`       | Filter by a metadata property                                                  | `("metadata.split", "==", "train")`                            |
| `<question>.suggestion` | Filter by a question suggestion value                                          | `("label.sugggestion", "==", "positive")`                      |
| `<question>.score`      | Filter by a suggestion score                                                   | `("label.score", "<=", "0.9")`                                 |
| `<question>.agent`      | Filter by a suggestion agent                                                   | `("label.agent", "<=", "ChatGPT4.0")`                          |
| `<question>.response`   | Filter by a question response                                                  | `("label.response", "==", "negative")`                         |


## Filter by status

You can filter records based on record or response status. Record status can be `pending` or `completed`, and response status can be `draft`, `submitted`, or `discarded`.

```python
import argilla as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

dataset = client.datasets(name="my_dataset", workspace="my_workspace")

status_filter = rg.Query(
    filter=rg.Filter(
        [
            ("status", "==", "completed"),
            ("response.status", "==", "discarded")
        ]
    )
)

filtered_records = dataset.records(status_filter).to_list(flatten=True)
```

## Similarity search

You can search for records that are similar to a given vector. You can use the `Similar` class to define the vector and pass it as part of the query argument to the `Dataset.records`.

```python

import argilla as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

dataset = client.datasets(name="my_dataset", workspace="my_workspace")


similar_filter = rg.Query(
    similar=rg.Similar(
        name="vector", value=(0.1, 0.2, 0.3),
    )
)

filtered_records = dataset.records(similar_filter).to_list(flatten=True)
```

!!! Note
    The `Similar` search expects a vector field definition as part of the dataset settings. If the dataset does not have a vector field, the search will return an error.
    Vist the [Vectors](./dataset.md#vectors) section for more details on how to define a vector field.

## Query and filter a dataset

As mentioned, you can use a query with a search term and a filter or various filters to create complex search queries.

```python
import argilla as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

dataset = client.datasets(name="my_dataset", workspace="my_workspace")

query_filter = rg.Query(
    query="my_term",
    filter=rg.Filter(
        [
            ("label.suggestion", "==", "positive"),
            ("metadata.count", ">=", 10),
        ]
    )
)

queried_filtered_records = dataset.records(
    query=query_filter,
    with_metadata=True,
    with_suggestions=True
).to_list(flatten=True)
```
