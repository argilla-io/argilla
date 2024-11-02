---
hide: footer
---
# `rg.Query`

To collect records based on searching criteria, you can use the `Query` and `Filter` classes. The `Query` class is used to define the search criteria, while the `Filter` class is used to filter the search results. `Filter` is passed to a `Query` object so you can combine multiple filters to create complex search queries. A `Query` object can also be passed to `Dataset.records` to fetch records based on the search criteria.

## Usage Examples

### Searching for records with terms

To search for records with terms, you can use the `Dataset.records` attribute with a query string. The search terms are used to search for records that contain the terms in the text field.

```python
for record in dataset.records(query="paris"):
    print(record)

```

### Filtering records by conditions

Argilla allows you to filter records based on conditions. You can use the `Filter` class to define the conditions and pass them to the `Dataset.records` attribute to fetch records based on the conditions. Conditions include "==", ">=", "<=", or "in". Conditions can be combined with dot notation to filter records based on metadata, suggestions, or responses.

```python

# create a range from 10 to 20
range_filter = rg.Filter(
    [
        ("metadata.count", ">=", 10),
        ("metadata.count", "<=", 20)
    ]
)

# query records with metadata count greater than 10 and less than 20
query = rg.Query(filters=range_filter, query="paris")

# iterate over the results
for record in dataset.records(query=query):
    print(record)
```


---

::: src.argilla.records._search.Query

::: src.argilla.records._search.Filter

::: src.argilla.records._search.Similar