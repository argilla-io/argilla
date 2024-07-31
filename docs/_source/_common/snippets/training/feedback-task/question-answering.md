---
title: Question Answering
description: When two TextFields and a TextQuestion are present in the datasets, we can define a TrainingTaskForQuestionAnswering to use our ArgillaTrainer integration for fine-tuning with "transformers".
links:
  - linkText: Practical guide to Question Answering
    linkLink: https://docs.v1.argilla.io/en/latest/practical_guides/fine_tune.html#question-answering
---

```python
from argilla.feedback import ArgillaTrainer, FeedbackDataset, TrainingTask

dataset = FeedbackDataset.from_argilla(
    name="<my_dataset_name>",
    workspace="<my_workspace_name>"
)
task = TrainingTask.for_question_answering(
    question=dataset.field_by_name("<my_field>"),
    context=dataset.field_by_name("<my_field>"),
    answer=dataset.question_by_name("<my_field>"),
)
trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="transformers",
)
trainer.update_config()
trainer.train()
```