Use a `Feedbackdataset` directly:

```python
from argilla import FeedbackDataset

dataset = Feedbackdataset(...)
dataset.unify_responses(question="question_name", strategy="majority")
dataset.records[0].unified_response
```

Or, you can use `FeedbackRecord`s in combination with a `QuestionStrategy`.

::::{tab-set}

:::{tab-item} RatingQuestion

```python
from argilla import RatingQuestion, RatingQuestionStrategy, FeedbackRecord

records = [FeedbackRecord(...)]
strategy = RatingQuestionStrategy("majority") # "mean", "max", "min"
records = strategy.unify_responses(records, question=RatingQuestion(...))
records[0].unified_response
```

:::

:::{tab-item} LabelQuestion

```python
from argilla import LabelQuestion, LabelQuestionStrategy, FeedbackRecord

records = [FeedbackRecord(...)]
strategy = LabelQuestionStrategy("majority") # "disagreement", "majority_weighted (WIP)"
records = strategy.unify_responses(records, question=LabelQuestion(...))
records[0].unified_response
```

:::


:::{tab-item} MultiLabelQuestion

```python
from argilla import MultiLabelQuestion, MultiLabelQuestionStrategy, FeedbackRecord

records = [FeedbackRecord(...)]
strategy = MultiLabelQuestionStrategy("majority") # "disagreement", "majority_weighted (WIP)"
records = strategy.unify_responses(records, question=MultiLabelQuestion(...))
records[0].unified_response
```

:::

::::