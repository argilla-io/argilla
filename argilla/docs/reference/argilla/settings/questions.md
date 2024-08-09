---
hide: footer
---

# Questions

Argilla uses questions to gather the feedback. The questions will be answered by users or models.

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

## `rg.LabelQuestion`

::: src.argilla.settings._question.LabelQuestion


## `rg.MultiLabelQuestion`

::: src.argilla.settings._question.MultiLabelQuestion


## `rg.RankingQuestion`

::: src.argilla.settings._question.RankingQuestion

## `rg.TextQuestion`

::: src.argilla.settings._question.TextQuestion


## `rg.RatingQuestion`

::: src.argilla.settings._question.RatingQuestion


## `rg.SpanQuestion`

::: src.argilla.settings._question.SpanQuestion
