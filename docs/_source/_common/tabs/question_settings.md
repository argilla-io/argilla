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
:::

:::{tab-item} Text

```python
rg.TextQuestion(
    name="corrected-text",
    title="Provide a correction to the response:",
    required=False
)
```
:::

:::{tab-item} Label

```python
rg.LabelQuestion(
    name="truthfulness",
    title="Is this text truthful?",
    description="Select 'No' if the text contains any information that not real or is incorrect, otherwise select 'Yes'.",
    required=True,
    labels=["Yes", "No"],
    visible_labels=2
)
```
:::

:::{tab-item} Multi-label

```python
rg.MultiLabelQuestion(
    name="content_class",
    title="Does the text contain any of the following?",
    description="Select all that apply",
    required=True,
    labels=["Hate speech", "Sexual content", "Violent content", "PII"],
    visible_labels=2
)
```
:::

::::