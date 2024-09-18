---
title: Sentence Similarity
description: When we have two TextFields in the datasets and potentially a LabelQuestion or RankingQuestion, we can define a TrainingTaskForSentenceSimilarity to use our ArgillaTrainer integration for fine-tuning with "sentence-transformers" to train a model for sentence similarity to optimize Retrieval Augmented Generation tasks (RAG) with better retrieval and reranking.
links:
  - linkText: Practical guide to Sentence Similarity
    linkLink: https://docs.v1.argilla.io/en/latest/practical_guides/fine_tune.html#sentence-similarity
---

```python
from argilla.feedback import ArgillaTrainer, FeedbackDataset, TrainingTask

dataset = FeedbackDataset.from_argilla(
    name="<my_dataset_name>",
    workspace="<my_workspace_name>"
)
task = TrainingTask.for_question_answering(
    texts=[dataset.field_by_name("premise"), dataset.field_by_name("hypothesis")],
    label=dataset.question_by_name("label")
)
trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="sentence-transformers",
)
trainer.update_config()
trainer.train()
```