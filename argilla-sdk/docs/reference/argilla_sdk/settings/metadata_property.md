---
hide: footer
---

# Metadata Properties

Metadata properties are used to define metadata fields in a dataset. Metadata fields are used to store additional information about the records in the dataset. For example, the category of a record, the price of a product, or any other information that is relevant to the record.

## Usage Examples

### Defining Metadata Property for a dataset

We define metadata properties via type specific classes. The following example demonstrates how to define metadata properties as either a float, integer, or terms metadata property:

`TermsMetadataProperty` is used to define a metadata field with a list of options. For example, a color field with options red, blue, and green. `FloatMetadataProperty` and `IntegerMetadataProperty` is used to define a metadata field with a float value. For example, a price field with a minimum value of 0.0 and a maximum value of 100.0.


```python
import argilla_sdk as rg

# Define metadata properties as terms
metadata_field = rg.TermsMetadataProperty(
    name="color",
    options=["red", "blue", "green"],
    title="Color",
)

# Define metadata properties as float
float_ metadata_field = rg.FloatMetadataProperty(
    name="price",
    min=0.0,
    max=100.0,
    title="Price",
)

# Define metadata properties as integer
int_metadata_field = rg.IntegerMetadataProperty(
    name="quantity",
    min=0,
    max=100,
    title="Quantity",
)
```

Metadata properties can be added to a dataset settings object:

```python

dataset = rg.Dataset(
    name="my_dataset",
    settings=rg.Settings(
        fields=[
            rg.TextField(name="text"),
        ],
        metadata=[
            metadata_field,
            float_metadata_field,
            int_metadata_field,
        ],
    ),
)
```

> To add records with metadata, refer to the [`rg.Metadata`](../records/metadata.md) class documentation.

---

## Class References

### `rg.FloatMetadataProperty`

::: argilla_sdk.settings.FloatMetadataProperty
    options:
        heading_level: 3

### `rg.IntegerMetadataProperty`

::: argilla_sdk.settings.IntegerMetadataProperty
    options:
        heading_level: 3

### `rg.TermsMetadataProperty`

::: argilla_sdk.settings.TermsMetadataProperty
    options:
        heading_level: 3