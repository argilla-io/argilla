---
hide: footer
---

# Questions

Questions in Argilla are the questions that will be answered as feedback. They are used to define the questions that will be answered by users or models.

## Usage Examples

To define a label question, for example, instantiate the `LabelQuestion` class and pass it to the `Settings` class.

```python
label_question = rg.LabelQuestion(name="label", labels=["positive", "negative"])

settings = rg.Settings(
    fields=[
        rg.TextField(name="text"),
    ],
    questions=[
        label_question,
    ],
)

```

Questions can be combined in extensible ways based on the type of feedback you want to collect. For example, you can combine a label question with a text question to collect both a label and a text response.

```python
label_question = rg.LabelQuestion(name="label", labels=["positive", "negative"])
text_question = rg.TextQuestion(name="response")

settings = rg.Settings(
    fields=[
        rg.TextField(name="text"),
    ],
    questions=[
        label_question,
        text_question,
    ],
)

dataset = rg.Dataset(
    name="my_dataset",
    settings=settings,
)


```

> To add records with responses to questions, refer to the [`rg.Response`](../records/responses.md) class documentation.


---

## Class References

### `rg.LabelQuestion`

::: argilla_sdk.settings.LabelQuestion
    options:
        heading_level: 3

### `rg.MultiLabelQuestion`

::: argilla_sdk.settings.MultiLabelQuestion
    options:
        heading_level: 3

### `rg.RankingQuestion`

::: argilla_sdk.settings.RankingQuestion
    options:
        heading_level: 3

### `rg.TextQuestion`

::: argilla_sdk.settings.TextQuestion
    options:
        heading_level: 3

### `rg.RatingQuestion`

::: argilla_sdk.settings.RatingQuestion
    options:
        heading_level: 3

### `rg.SpanQuestion`

::: argilla_sdk.settings.SpanQuestion
    options:
        heading_level: 3