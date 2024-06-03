::::{tab-set}

:::{tab-item} Label

```python
rg.LabelQuestion(
    name="relevant",
    title="Is the response relevant for the given prompt?",
    labels={"YES": "Yes", "NO": "No"}, # or ["YES","NO"]
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
    labels={"hate": "Hate Speech" , "sexual": "Sexual content", "violent": "Violent content", "pii": "Personal information", "untruthful": "Untruthful info", "not_english": "Not English", "inappropriate": "Inappropriate content"}, # or ["hate", "sexual", "violent", "pii", "untruthful", "not_english", "inappropriate"]
    required=False,
    visible_labels=4,
    labels_order="natural"
)
```

![Multi-label Question](/_static/images/llms/questions/multilabel_question.png)
:::

:::{tab-item} Ranking

```python
rg.RankingQuestion(
    name="preference",
    title="Order replies based on your preference",
    description="1 = best, 3 = worst. Ties are allowed.",
    required=True,
    values={"reply-1": "Reply 1", "reply-2": "Reply 2", "reply-3": "Reply 3"} # or ["reply-1", "reply-2", "reply-3"]
)
```

![Ranking question](/_static/images/llms/questions/ranking_question.png)
:::

:::{tab-item} Rating

```python
rg.RatingQuestion(
    name="quality",
    title="Rate the quality of the response:",
    description="1 = very bad - 5= very good",
    required=True,
    values=[1, 2, 3, 4, 5]
)
```

![Rating question](/_static/images/llms/questions/rating_question.png)
:::

:::{tab-item} Span

```python
rg.SpanQuestion(
    name="entities",
    title="Highlight the entities in the text:",
    labels={"PER": "Person", "ORG": "Organization", "EVE": "Event"},
    # or ["PER", "ORG", "EVE"],
    field="text",
    required=True,
    allow_overlapping=False
)
```

![Span question](/_static/images/llms/questions/span_question.png)
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

::::
