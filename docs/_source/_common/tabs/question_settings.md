::::{tab-set}

:::{tab-item} Rating

```python
rg.RatingQuestion(
    name="rating",
    title="Rate the quality of the response:",
    description="1 = very bad - 5= very good",
    required=True,
    values=[1, 2, 3, 4, 5]
)
```

![Rating question](/_static/images/llms/questions/rating_question.png)
:::

:::{tab-item} Text

```python
rg.TextQuestion(
    name="corrected-text",
    title="Provide a correction to the response:",
    required=False,
    use_markdown=True
)
```
![Text Question](/_static/images/llms/questions/text_question.png)
:::

:::{tab-item} Label

```python
rg.LabelQuestion(
    name="relevant",
    title="Is the response relevant for the given prompt?",
    labels=["Yes","No"],
    required=True,
    visible_labels=None
)
```

![Label Question](/_static/images/llms/questions/label_question.png)
:::

:::{tab-item} Multi-label

```python
rg.MultiLabelQuestion(
    name="content_class",
    title="Does the response include any of the following?",
    description="Select all that apply",
    labels={"hate": "Hate Speech" , "sexual": "Sexual content", "violent": "Violent content", "pii": "Personal information", "untruthful": "Untruthful info", "not_english": "Not English", "inappropriate": "Inappropriate content"},
    required=False,
    visible_labels=4
)
```

![Multi-label Question](/_static/images/llms/questions/multilabel_question.png)
:::

::::