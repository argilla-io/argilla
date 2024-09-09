---
hide: footer
---
# `rg.Record`

The `Record` object is used to represent a single record in Argilla. It contains fields, suggestions, responses, metadata, and vectors.

## Usage Examples

### Creating a Record

To create records, you can use the `Record` class and pass it to the `Dataset.records.log` method. The `Record` class requires a `fields` parameter, which is a dictionary of field names and values. The field names must match the field names in the dataset's `Settings` object to be accepted.

```python
dataset.records.log(
    records=[
        rg.Record(
            fields={"text": "Hello World, how are you?"},
        ),
    ]
) # (1)
```

1. The Argilla dataset contains a field named `text` matching the key here.

To create records with image fields, pass the image to the record object as either a remote url, local path to an image file, or a PIL object. The field names must be defined as an `rg.ImageField`in the dataset's `Settings` object to be accepted. Images will be stored in the Argilla database and returned as rescaled PIL objects.

```python
dataset.records.log(
    records=[
        rg.Record(
            fields={"image": "https://example.com/image.jpg"}, # (1)
        ),
    ]
)
```

1. The image can be referenced as either a remote url, a local file path, or a PIL object.

!!! note
    The image will be stored in the Argilla database and can impact the dataset's storage usage. Images should be less than 5mb in size and datasets should contain less than 10,000 images.

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

For changes to take effect, the user must call the `update` method on the `Dataset` object, or pass the updated records to `Dataset.records.log`. All core record atttributes can be updated in this way. Check their respective documentation for more information: [Suggestions](suggestions.md), [Responses](responses.md), [Metadata](metadata.md), [Vectors](vectors.md).


---

::: src.argilla.records._resource.Record

