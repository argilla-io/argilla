::::{tab-set}

:::{tab-item} Feedback Task
:sync: feedbacktask

```python
import argilla as rg

dataset = rg.create_feedback_dataset(
    name="my_dataset",
    workspace="my_workspace",
    guidelines="Add some guidelines for the annotation team here.",
    fields=[
        rg.TextField(name="prompt", title="Human prompt"),
        rg.TextField(name="output", title="Generated output")
    ],
    questions =[
        rg.RatingQuestion(
            name="rating",
            title="Rate the quality of the response:",
            description="1 = very bad - 5= very good",
            required=True,
            values=[1,2,3,4,5]
        ),
        rg.TextQuestion(
            name="corrected-text",
            title="Provide a correction to the response:",
            required=False
        )
    ]
)
```
:::

:::{tab-item} Text Classification
:sync: textclass
```python
import argilla as rg

settings = rg.TextClassificationSettings(label_schema=["A", "B", "C"])

rg.configure_dataset(name="my_dataset", settings=settings)
```
:::

:::{tab-item} Token Classification
:sync: tokenclass
```python
import argilla as rg

settings = rg.TokenClassificationSettings(label_schema=["A", "B", "C"])

rg.configure_dataset(name="my_dataset", settings=settings)
```
:::

:::{tab-item} Text2Text
:sync: text2text
Because we do not require a labeling schema for `Text2Text`, we can create a dataset by directly logging records via `rg.log()`.
:::

::::