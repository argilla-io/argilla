You can unify responses by using a `FeedbackRecord`s in combination with a `QuestionStrategy`.

::::{tab-set}

:::{tab-item} RatingQuestion

```python
from argilla import RatingQuestionStrategy, FeedbackRecord

dataset = FeedbackDataset.from_huggingface(
    repo_id="argilla/stackoverflow_feedback_demo"
)
strategy = RatingQuestionStrategy("majority") # "mean", "max", "min"
dataset.unify_responses(
    question=dataset.get_question_by_name("answer_quality")
    strategy=strategy
)
dataset.records[0].unified_responses
```

:::

:::{tab-item} LabelQuestion

```python
from argilla import RatingQuestionStrategy, FeedbackRecord

dataset = FeedbackDataset.from_huggingface(
    repo_id="argilla/stackoverflow_feedback_demo"
)
strategy = LabelQuestionStrategy("majority") # "disagreement", "majority_weighted (WIP)"
dataset.unify_responses(
    question=dataset.get_question_by_name("title_question_fit")
    strategy=strategy
)
dataset.records[0].unified_responses
```

:::


:::{tab-item} MultiLabelQuestion

```python
from argilla import RatingQuestionStrategy, FeedbackRecord

dataset = FeedbackDataset.from_huggingface(
    repo_id="argilla/stackoverflow_feedback_demo"
)
strategy = MultiLabelQuestionStrategy("majority") # "disagreement", "majority_weighted (WIP)"
dataset.unify_responses(
    question=dataset.get_question_by_name("tags")
    strategy=strategy
)
dataset.records[0].unified_responses
```

:::

::::

:::{note}
You can also pass the `question` and `strategy` as string directly.
:::