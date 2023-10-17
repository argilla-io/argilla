::::{tab-set}

:::{tab-item} Feedback Task

```python
import argilla as rg

dataset = rg.FeedbackDataset(
    guidelines="Add some guidelines for the annotation team here.",
    fields=[
        rg.TextField(name="prompt", title="Human prompt"),
        rg.TextField(name="output", title="Generated output", use_markdown=True)
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
            required=False,
            use_markdown=True
        )
    ]
)

dataset.push_to_argilla(name="my_dataset", workspace="my_workspace")
```
:::

:::{tab-item} Text Classification
```python
import argilla as rg

settings = rg.TextClassificationSettings(label_schema=["A", "B", "C"])

rg.configure_dataset_settings(name="my_dataset", settings=settings)
```
:::

:::{tab-item} Token Classification
```python
import argilla as rg

settings = rg.TokenClassificationSettings(label_schema=["A", "B", "C"])

rg.configure_dataset_settings(name="my_dataset", settings=settings)
```
:::

:::{tab-item} Text2Text
Because we do not require a labeling schema for `Text2Text`, we can create a dataset by directly logging records via `rg.log()`.
:::

::::