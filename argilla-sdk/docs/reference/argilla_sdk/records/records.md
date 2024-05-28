# `rg.Record`

The `Record` object is used to represent a single record in Argilla. It contains fields, suggestions, responses, metadata, and vectors.

## Usage Examples

### Creating a Record

To add records, you can pass dictionaries to the `Dataset.records.add` method. Argilla will instantiate the `Record` class based on the input data and `mapping` property. The input data keys must match the names in `rg.Settings` object, or be mapped via the dictionary passed to the `mapping` parameter.

```python
dataset.records.add(
    records=[
    {
        "question": "What is the capital of France?",
        "answer": "Paris"
    },
])
```

You can also create `Record` objects directly and pass them to the same method.

```python
records = [
        rg.Record(
            fields={"text": "Hello World, how are you?"},
            responses=[rg.Response("label", "positive", user_id=user_id)],
        ),
    ]
dataset.records.add(records=records)
```

### Accessing Record Attributes

The `Record` object has suggestions, responses, metadata, and vectors attributes that can be accessed directly whilst iterating over records in a dataset.

```python
for record in dataset.records(
    with_suggestions=True,
    with_responses=True,
    with_metadata=True,
    with_vectors=True
    ):
    print(record.suggestions)
    print(record.responses)
    print(record.metadata)
    print(record.vectors)
```

Record properties can also be updated whilst iterating over records in a dataset.

```python
for record in dataset.records(with_metadata=True):
    record.metadata = {"department": "toys"}
```

For changes to take effect, the user must call the `update` method on the `Dataset` object.


---

## Class Reference

### `rg.Record`

::: argilla_sdk.records.Record
    options:
        heading_level: 3