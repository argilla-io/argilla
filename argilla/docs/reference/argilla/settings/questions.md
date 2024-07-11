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

::: src.argilla.settings._question.LabelQuestion
    options:
        heading_level: 3

### `rg.MultiLabelQuestion`

::: src.argilla.settings._question.MultiLabelQuestion
    options:
        heading_level: 3

### `rg.RankingQuestion`

::: src.argilla.settings._question.RankingQuestion
    options:
        heading_level: 3

### `rg.TextQuestion`

::: src.argilla.settings._question.TextQuestion
    options:
        heading_level: 3

### `rg.RatingQuestion`

::: src.argilla.settings._question.RatingQuestion
    options:
        heading_level: 3

### `rg.SpanQuestion`

::: src.argilla.settings._question.SpanQuestion
    options:
        heading_level: 3