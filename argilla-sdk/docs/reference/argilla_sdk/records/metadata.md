---
hide: footer
---
# `metadata`

Metadata in argilla is a dictionary that can be attached to a record. It is used to store additional information about the record that is not part of the record's fields or responses. For example, the source of the record, the date it was created, or any other information that is relevant to the record. Metadata can be added to a record directly or as valules within a dictionary.

## Usage Examples

To use metadata within a dataset, you must define a metadata property in the dataset settings. The metadata property is a list of metadata properties that can be attached to a record. The following example demonstrates how to add metadata to a dataset and how to access metadata from a record object:

```python
import argilla_sdk as rg

dataset = Dataset(
    name="dataset_with_metadata",
    settings=Settings(
        fields=[TextField(name="text")],
        questions=[LabelQuestion(name="label", labels=["positive", "negative"])],
        metadata=[
            rg.TermsMetadataProperty(name="category", options=["A", "B", "C"]),
        ],
    ),
)
dataset.create()
```

Then, you can add records to the dataset with metadata that corresponds to the metadata property defined in the dataset settings:

```python
dataset_with_metadata.records.log(
    [
        {"text": "text", "label": "positive", "category": "A"},
        {"text": "text", "label": "negative", "category": "B"},
    ]
)
```