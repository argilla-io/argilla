---
hide: footer
---

# Fields

Fields in Argilla are define the content of a record that will be reviewed by a user.

## Usage Examples

To define a field, instantiate the `TextField` class and pass it to the `fields` parameter of the `Settings` class.

```python
text_field = rg.TextField(name="text")
markdown_field = rg.TextField(name="text", use_markdown=True)
```

The `fields` parameter of the `Settings` class can accept a list of fields, like this:

```python
settings = rg.Settings(
    fields=[
        rg.TextField(name="text"),
    ],
)

data = rg.Dataset(
    name="my_dataset",
    settings=settings,
)

```

> To add records with values for fields, refer to the [`rg.Dataset.records`](../records/records.md) documentation.

---

## Class References

### `rg.TextField`

::: argilla_sdk.settings.TextField
    options:
        heading_level: 3
