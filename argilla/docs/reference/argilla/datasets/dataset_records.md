---
hide: footer
---
# `rg.Dataset.records`

## Usage Examples

In most cases, you will not need to create a `DatasetRecords` object directly. Instead, you can access it via the `Dataset` object:

```python
dataset.records
```

!!! note "For user familiar with legacy approaches"
    1. `Dataset.records` object is used to interact with the records in a dataset. It interactively fetches records from the server in batches without using a local copy of the records.
    2. The `log` method of `Dataset.records` is used to both add and update records in a dataset. If the record includes a known `id` field, the record will be updated. If the record does not include a known `id` field, the record will be added.


### Adding records to a dataset

To add records to a dataset, use the `log` method. Records can be added as dictionaries or as `Record` objects. Single records can also be added as a dictionary or `Record`.

=== "As a `Record` object"

    You can also add records to a dataset by initializing a `Record` object directly.

    ```python

    records = [
        rg.Record(
            fields={
                "question": "Do you need oxygen to breathe?",
                "answer": "Yes"
            },
        ),
        rg.Record(
            fields={
                "question": "What is the boiling point of water?",
                "answer": "100 degrees Celsius"
            },
        ),
    ] # (1)

    dataset.records.log(records)
    ```

    1. This is an illustration of a definition. In a real world scenario, you would iterate over a data structure and create `Record` objects for each iteration.

=== "From a data structure"

    ```python

    data = [
        {
            "question": "Do you need oxygen to breathe?",
            "answer": "Yes",
        },
        {
            "question": "What is the boiling point of water?",
            "answer": "100 degrees Celsius",
        },
    ] # (1)

    dataset.records.log(data)
    ```

    1. The data structure's keys must match the fields or questions in the Argilla dataset. In this case, there are fields named `question` and `answer`.

=== "From a data structure with a mapping"

    ```python
    data = [
        {
            "query": "Do you need oxygen to breathe?",
            "response": "Yes",
        },
        {
            "query": "What is the boiling point of water?",
            "response": "100 degrees Celsius",
        },
    ] # (1)
    dataset.records.log(
        records=data,
        mapping={"query": "question", "response": "answer"} # (2)
    )

    ```

    1. The data structure's keys must match the fields or questions in the Argilla dataset. In this case, there are fields named `question` and `answer`.
    2. The data structure has keys `query` and `response` and the Argilla dataset has `question` and `answer`. You can use the `mapping` parameter to map the keys in the data structure to the fields in the Argilla dataset.

=== "From a Hugging Face dataset"

    You can also add records to a dataset using a Hugging Face dataset. This is useful when you want to use a dataset from the Hugging Face Hub and add it to your Argilla dataset.

    You can add the dataset where the column names correspond to the names of fields, questions, metadata or vectors in the Argilla dataset.

    If the dataset's schema does not correspond to your Argilla dataset names, you can use a `mapping` to indicate which columns in the dataset correspond to the Argilla dataset fields.

    ```python
    from datasets import load_dataset

    hf_dataset = load_dataset("imdb", split="train[:100]") # (1)

    dataset.records.log(records=hf_dataset)
    ```

    1. In this example, the Hugging Face dataset matches the Argilla dataset schema. If that is not the case, you could use the `.map` of the `datasets` library to prepare the data before adding it to the Argilla dataset.

    Here we use the `mapping` parameter to specify the relationship between the Hugging Face dataset and the Argilla dataset.

    ```python
    dataset.records.log(records=hf_dataset, mapping={"txt": "text", "y": "label"}) # (1)
    ```

    1. In this case, the `txt` key in the Hugging Face dataset corresponds to the `text` field in the Argilla dataset, and the `y` key in the Hugging Face dataset corresponds to the `label` field in the Argilla dataset.


### Updating records in a dataset

Records can also be updated using the `log` method with records that contain an `id` to identify the records to be updated. As above, records can be added as dictionaries or as `Record` objects.

=== "As a `Record` object"

    You can update records in a dataset by initializing a `Record` object directly and providing the `id` field.

    ```python

    records = [
        rg.Record(
            metadata={"department": "toys"},
            id="2" # (1)
        ),
    ]

    dataset.records.log(records)
    ```

    1. The `id` field is required to identify the record to be updated. The `id` field must be unique for each record in the dataset. If the `id` field is not provided, the record will be added as a new record.

=== "From a data structure"

    You can also update records in a dataset by providing the `id` field in the data structure.

    ```python

    data = [
        {
            "metadata": {"department": "toys"},
            "id": "2" # (1)
        },
    ]

    dataset.records.log(data)
    ```

    1. The `id` field is required to identify the record to be updated. The `id` field must be unique for each record in the dataset. If the `id` field is not provided, the record will be added as a new record.


=== "From a data structure with a mapping"

    You can also update records in a dataset by providing the `id` field in the data structure and using a mapping to map the keys in the data structure to the fields in the dataset.

    ```python
    data = [
        {
            "metadata": {"department": "toys"},
            "my_id": "2" # (1)
        },
    ]

    dataset.records.log(
        records=data,
        mapping={"my_id": "id"} # (2)
    )

    ```

    1. The `id` field is required to identify the record to be updated. The `id` field must be unique for each record in the dataset. If the `id` field is not provided, the record will be added as a new record.
    2. Let's say that your data structure has keys `my_id` instead of `id`. You can use the `mapping` parameter to map the keys in the data structure to the fields in the dataset.

=== "From a Hugging Face dataset"

    You can also update records to an Argilla dataset using a Hugging Face dataset. To update records, the Hugging Face dataset must contain an `id` field to identify the records to be updated, or you can use a mapping to map the keys in the Hugging Face dataset to the fields in the Argilla dataset.

    ```python
    from datasets import load_dataset

    hf_dataset = load_dataset("imdb", split="train[:100]") # (1)

    dataset.records.log(records=hf_dataset, mapping={"uuid": "id"}) # (2)
    ```

    1. In this example, the Hugging Face dataset matches the Argilla dataset schema.
    2. The `uuid` key in the Hugging Face dataset corresponds to the `id` field in the Argilla dataset.

### Adding and updating records with images

Argilla datasets can contain image fields. You can add images to a dataset by passing the image to the record object as either a remote URL, a local path to an image file, or a PIL object. The field names must be defined as an `rg.ImageField` in the dataset's `Settings` object to be accepted. Images will be stored in the Argilla database and returned using the data URI schema.

!!! note "As PIL objects"
    To retrieve the images as rescaled PIL objects, you can use the `to_datasets` method when exporting the records, as shown in this [how-to guide](../../../how_to_guides/import_export.md).


=== "From a data structure with remote URLs"

    ```python
    data = [
        {
            "image": "https://example.com/image1.jpg",
        },
        {
            "image": "https://example.com/image2.jpg",
        },
    ]

    dataset.records.log(data)
    ```

=== "From a data structure with local files or PIL objects"

    ```python
    import os
    from PIL import Image

    image_dir = "path/to/images"

    data = [
        {
            "image": os.path.join(image_dir, "image1.jpg"), # (1)
        },
        {
            "image": Image.open(os.path.join(image_dir, "image2.jpg")), # (2)
        },
    ]

    dataset.records.log(data)
    ```

    1. The image is a local file path.
    2. The image is a PIL object.

=== "From a Hugging Face dataset"

    Hugging Face datasets can be passed directly to the `log` method. The image field must be defined as an `Image` in the dataset's features.

    ```python
    hf_dataset = load_dataset("ylecun/mnist", split="train[:100]")
    dataset.records.log(records=hf_dataset)
    ```

    If the image field is not defined as an `Image` in the dataset's features, you can cast the dataset to the correct schema before adding it to the Argilla dataset. This is only necessary if the image field is not defined as an `Image` in the dataset's features, and is not one of the supported image types by Argilla (URL, local path, or PIL object).

    ```python
    hf_dataset = load_dataset("<my_custom_dataset>") # (1)
    hf_dataset = hf_dataset.cast(
        features=Features({"image": Image(), "label": Value("string")}),
    )
    dataset.records.log(records=hf_dataset)
    ```

    1. In this example, the Hugging Face dataset matches the Argilla dataset schema but the image field is not defined as an `Image` in the dataset's features.


### Iterating over records in a dataset

`Dataset.records` can be used to iterate over records in a dataset from the server. The records will be fetched in batches from the server::

```python
for record in dataset.records:
    print(record)

# Fetch records with suggestions and responses
for record in dataset.records(with_suggestions=True, with_responses=True):
    print(record.suggestions)
    print(record.responses)

# Filter records by a query and fetch records with vectors
for record in dataset.records(query="capital", with_vectors=True):
    print(record.vectors)
```

Check out the [`rg.Record`](../records/records.md) class reference for more information on the properties and methods available on a record and the [`rg.Query`](../search.md) class reference for more information on the query syntax.

---

::: src.argilla.records._dataset_records.DatasetRecords
