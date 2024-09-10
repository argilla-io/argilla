---
hide: footer
---
# Distribution

Distribution settings are used to define the criteria used by the tool to automatically manage records in the dataset depending on the expected number of submitted responses per record.

## Usage Examples

The default minimum submitted responses per record is 1. If you wish to increase this value, you can define it through the `TaskDistribution` class and pass it to the `Settings` class.

```python
settings = rg.Settings(
    guidelines="These are some guidelines.",
    fields=[
        rg.TextField(
            name="text",
        ),
    ],
    questions=[
        rg.LabelQuestion(
            name="label",
            labels=["label_1", "label_2", "label_3"]
        ),
    ],
    distribution=rg.TaskDistribution(min_submitted=3)
)

dataset = rg.Dataset(
    name="my_dataset",
    settings=settings
)
```

---

::: src.argilla.settings._task_distribution.OverlapTaskDistribution
