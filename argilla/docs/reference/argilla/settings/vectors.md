---
hide: footer
---
# Vectors

Vector fields in Argilla are used to define the vector form of a record that will be reviewed by a user.

## Usage Examples

To define a vector field, instantiate the `VectorField` class with a name and dimensions, then pass it to the `vectors` parameter of the `Settings` class.

```python
settings = rg.Settings(
    fields=[
        rg.TextField(name="text"),
    ],
    vectors=[
        rg.VectorField(
            name="my_vector",
            dimension=768,
            title="Document Embedding",
        ),
    ],
)
```

> To add records with vectors, refer to the [`rg.Vector`](../records/vectors.md) class documentation.

---

::: src.argilla.settings._vector.VectorField
