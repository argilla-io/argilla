---
title: Text classification
description: When a RatingQuestion, LabelQuestion or MultiLabelQuestion is present in the datasets, we can define a TrainingTaskMappingForTextClassification to use our ArgillaTrainer integration for fine-tuning with openai”, “setfit”, “peft”, “spacy” and “transformers”.
links:
  - linkText: Argilla unification docs
    linkLink: https://docs.argilla.io/en/latest/guides/llms/practical_guides/collect_responses.html#solve-disagreements
  - linkText: Argilla fine-tuning docs
    linkLink: https://docs.argilla.io/en/latest/guides/llms/practical_guides/fine_tune_others.html#text-classification
  - linkText: ArgillaTrainer docs
    linkLink: https://docs.argilla.io/en/latest/guides/train_a_model.html#the-argillatrainer
---

```python
import argilla as rg

dataset = rg.FeedbackDataset.from_argilla(
    name="<my_dataset_name>",
    workspace="<my_workspace_name>"
)
label_unification = rg.LabelUnification(
    question=dataset.question_by_name("<my_question>"),
    strategy="majority"
)
training_task_mapping = rg.TrainingTaskMapping.for_text_classification(
    text=dataset.field_by_name("text"),
    label=label_unification
)
trainer = rg.ArgillaTrainer(
    dataset=dataset,
    training_task_mapping=training_task_mapping,
    framework="<my_framework>",
)
trainer.update_config()
trainer.train()
```