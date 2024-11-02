---
title: Text classification
description: When a RatingQuestion, LabelQuestion or MultiLabelQuestion is present in the datasets, we can define a TrainingTaskForTextClassification to use our ArgillaTrainer integration for fine-tuning with "openai", "setfit", "peft", "spacy" and "transformers".
links:
  - linkText: Argilla unification docs
    linkLink: https://docs.v1.argilla.io/en/latest/practical_guides/collect_responses.html#solve-disagreements
  - linkText: Practical guide to Text Classification
    linkLink: https://docs.v1.argilla.io/en/latest/practical_guides/fine_tune.html#text-classification
---

```python
from argilla.feedback import ArgillaTrainer, FeedbackDataset, TrainingTask

dataset = FeedbackDataset.from_argilla(
    name="<my_dataset_name>",
    workspace="<my_workspace_name>"
)
task = TrainingTask.for_text_classification(
    text=dataset.field_by_name("<my_field>"),
    label=dataset.question_by_name("<my_question>")
)
trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="<my_framework>",
)
trainer.update_config()
trainer.train()
```