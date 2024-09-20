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
import argilla as rg

settings = rg.Settings(
    guidelines="Select the sentiment of the prompt.",
    fields=[rg.TextField(name="prompt", use_markdown=True)],
    questions=[rg.LabelQuestion(name="sentiment", labels=["positive", "negative"])],
)

dataset = rg.Dataset(name="sentiment_analysis", settings=settings)

# Create the dataset on the server
dataset.create()

```

To define the settings for fields, questions, metadata, vectors, or distribution, refer to the [`rg.TextField`](fields.md), [`rg.LabelQuestion`](questions.md), [`rg.TermsMetadataProperty`](metadata_property.md), and [`rg.VectorField`](vectors.md), [`rg.TaskDistribution`](task_distribution.md) class documentation.

### Creating settings using built in templates

Argilla provides built-in templates for creating settings for common dataset types. To use a template, use the class methods of the `Settings` class. There are three built-in templates available for classification, ranking, and rating tasks. Template settings also include default guidelines and mappings.

#### Classification Task

You can define a classification task using the `rg.Settings.for_classification` class method. This will create a dataset with a text field and a label question. You can select field types using the `field_type` parameter with `image` or `text`.

```python
settings = rg.Settings.for_classification(labels=["positive", "negative"]) # (1)
```

This will return a `Settings` object with the following settings:

```python
settings = Settings(
    guidelines="Select a label for the document.",
    fields=[rg.TextField(field_type)(name="text")],
    questions=[LabelQuestion(name="label", labels=labels)],
    mapping={"input": "text", "output": "label", "document": "text"},
)
```

#### Ranking Task

You can define a ranking task using the `rg.Settings.for_ranking` class method. This will create a dataset with a text field and a ranking question.

```python
settings = rg.Settings.for_ranking()
```

This will return a `Settings` object with the following settings:

```python
settings = Settings(
    guidelines="Rank the responses.",
    fields=[
        rg.TextField(name="instruction"),
        rg.TextField(name="response1"),
        rg.TextField(name="response2"),
    ],
    questions=[RankingQuestion(name="ranking", values=["response1", "response2"])],
    mapping={
        "input": "instruction",
        "prompt": "instruction",
        "chosen": "response1",
        "rejected": "response2",
    },
)
```

#### Rating Task

You can define a rating task using the `rg.Settings.for_rating` class method. This will create a dataset with a text field and a rating question.

```python
settings = rg.Settings.for_rating()
```

This will return a `Settings` object with the following settings:

```python
settings = Settings(
    guidelines="Rate the response.",
    fields=[
        rg.TextField(name="instruction"),
        rg.TextField(name="response"),
    ],
    questions=[RatingQuestion(name="rating", values=[1, 2, 3, 4, 5])],
    mapping={
        "input": "instruction",
        "prompt": "instruction",
        "output": "response",
        "score": "rating",
    },
)
```

---

::: src.argilla.settings._resource.Settings
