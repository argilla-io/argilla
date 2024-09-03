---
description: In this guide we will show you how to use the Image Field in Argilla to create records with images.
---

# Images in Argilla datasets

In Argilla, you can create records with images using the `rg.ImageField` class. This class is used to define fields in a dataset's settings that will contain images. `ImageField` fields can be used to store image URLs or data URIs, and a dataset can have multiple image fields or a combination of image and text fields.

!!! info "Main Class"

    === `rg.ImageField`

        ```python
        rg.ImageField(
            name="image"
        )
        ```

    === `rg.Record`

        ```python
        rg.Record(
            fields={"image": "https://example.com/image.jpg"},
        )
        ```

## Define an Image Field

To define an image field, instantiate the `ImageField` class and pass it to the `rg.Settings` class.

```python
settings = rg.Settings(
    fields=[
        rg.ImageField(name="image"),
    ],
)
```

## Adding Records with Image Fields

To add records with image fields, pass the remote URL or data URI of the image to the records object. The field names must match those defined as an `rg.ImageField` in the dataset's `Settings` object to be accepted.

```python
dataset.records.log(
    records=[
        rg.Record(
            fields={"image": "https://example.com/image.jpg"},
        ),
        rg.Record(
            fields={"image": "data:image/png;base64,iV..."}, # (1)
        ),
    ]
)
```

1. The image can be referenced as either a remote URL or a data URI.