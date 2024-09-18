---
hide: footer
---
# `rg.Vector`

A vector is a numerical representation of a `Record` field or attribute, usually the record's text. Vectors can be used to search for similar records via the UI or SDK. Vectors can be added to a record directly or as a dictionary with a key that the matches `rg.VectorField` name.

## Usage Examples

To use vectors within a dataset, you must define a vector field in the dataset settings. The vector field is a list of vector fields that can be attached to a record. The following example demonstrates how to add vectors to a dataset and how to access vectors from a record object:

```python
import argilla as rg

dataset = Dataset(
    name="dataset_with_metadata",
    settings=Settings(
        fields=[TextField(name="text")],
        questions=[LabelQuestion(name="label", labels=["positive", "negative"])],
        vectors=[
            VectorField(name="vector_name"),
        ],
    ),
)
dataset.create()
```

Then, you can add records to the dataset with vectors that correspond to the vector field defined in the dataset settings:

```python
dataset.records.log(
    [
        {
            "text": "Hello World, how are you?",
            "vector_name": [0.1, 0.2, 0.3]
        }
    ]
)
```

Vectors can be passed using a mapping, where the key is the key in the data source and the value is the name in the dataset's setting's `rg.VectorField` object. For example, the following code adds a record with a vector using a mapping:

```python
dataset.records.log(
    [
        {
            "text": "Hello World, how are you?",
            "x": [0.1, 0.2, 0.3]
        }
    ],
    mapping={"x": "vector_name"}
)
```

Or, vectors can be instantiated and added to a record directly, like this:

```python
dataset.records.log(
    [
        rg.Record(
            fields={"text": "Hello World, how are you?"},
            vectors=[rg.Vector("embedding", [0.1, 0.2, 0.3])],
        )
    ]
)
```

---

::: src.argilla.vectors.Vector

