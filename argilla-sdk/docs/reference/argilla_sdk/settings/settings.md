---
hide: footer
---
# `rg.Settings`

`rg.Settings` is used to define the setttings of an Argilla `Dataset`. The settings can be used to configure the
behavior of the dataset, such as the fields, questions, guidelines, metadata, and vectors. The `Settings` class is
passed to the `Dataset` class and used to create the dataset on the server. Once created, the settings of a dataset
cannot be changed.

## Usage Examples

### Creating a new dataset with settings

To create a new dataset with settings, instantiate the `Settings` class and pass it to the `Dataset` class.

```python
import argilla_sdk as rg

settings = rg.Settings(
    guidelines="Select the sentiment of the prompt.",
    fields=[rg.TextField(name="prompt", use_markdown=True)],
    questions=[rg.LabelQuestion(name="sentiment", labels=["positive", "negative"])],
)

dataset = rg.Dataset(name="sentiment_analysis", settings=settings)

# Create the dataset on the server
dataset.create()

```

> To define the settings for fields, questions, metadata, or vectors, refer to the [`rg.TextField`](fields.md), [`rg.LabelQuestion`](questions.md), [`rg.TermsMetadataProperty`](metadata_property.md), and [`rg.VectorField`](vectors.md) class documentation.

---

## Class Reference

### `rg.Settings`

::: argilla_sdk.settings.Settings
    options:
        heading_level: 3