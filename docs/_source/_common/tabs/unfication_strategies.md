::::{tab-set}

:::{tab-item} LabelQuestion

```python
from argilla import LabelQuestionStrategy, FeedbackDataset

dataset = FeedbackDataset.from_huggingface(
    repo_id="argilla/stackoverflow_feedback_demo"
)
strategy = LabelQuestionStrategy("majority") # "disagreement", "majority_weighted (WIP)"
dataset.compute_unified_responses(
    question=dataset.question_by_name("title_question_fit"),
    strategy=strategy,
)
dataset.records[0].unified_responses
```

:::


:::{tab-item} MultiLabelQuestion

```python
from argilla import MultiLabelQuestionStrategy, FeedbackDataset

dataset = FeedbackDataset.from_huggingface(
    repo_id="argilla/stackoverflow_feedback_demo"
)
strategy = MultiLabelQuestionStrategy("majority") # "disagreement", "majority_weighted (WIP)"
dataset.compute_unified_responses(
    question=dataset.question_by_name("tags"),
    strategy=strategy,
)
dataset.records[0].unified_responses
```

:::

:::{tab-item} RankingQuestion

```python
from argilla import RankingQuestionStrategy, FeedbackDataset

dataset = FeedbackDataset.from_huggingface(
    repo_id="argilla/stackoverflow_feedback_demo"
)
strategy = RankingQuestionStrategy("majority") # "mean", "max", "min"
dataset.compute_unified_responses(
    question=dataset.question_by_name("relevance_ranking"),
    strategy=strategy,
)
dataset.records[0].unified_responses
```

:::

:::{tab-item} RatingQuestion

```python
from argilla import RatingQuestionStrategy, FeedbackDataset

dataset = FeedbackDataset.from_huggingface(
    repo_id="argilla/stackoverflow_feedback_demo"
)
strategy = RatingQuestionStrategy("majority") # "mean", "max", "min"
dataset.compute_unified_responses(
    question=dataset.question_by_name("answer_quality"),
    strategy=strategy,
)
dataset.records[0].unified_responses
```

:::

::::

:::{note}
You can also pass the `question` and `strategy` as string directly.
:::