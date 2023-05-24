---
title: AutoTrain (code)
description: Use Argilla, Datasets and Hugging Face AutoTrain Advanced with the ArgillaTrainer.
links:
  - linkText: Tutorial
    linkLink: https://www.argilla.io/blog/argilla-meets-autotrain/
  - linkText: AutoTrain Advanced docs
    linkLink: https://github.com/huggingface/autotrain-advanced
  - linkText: AutoTrain Advanced blog
    linkLink: https://huggingface.co/autotrain
---

*code snippet*

```python
from argilla.training import ArgillaTrainer

trainer = ArgillaTrainer(
    name="<my_dataset_name>",
    workspace="<my_workspace_name>",
    framework="autotrain",
    train_size=0.8
)
trainer.update_config(num_iterations=10)
trainer.train(output_dir="text-classification")
records = trainer.predict("The ArgillaTrainer is great!", as_argilla_records=True)
```

*update training config*

```python
trainer.update_config(
    training_file = None,
    validation_file = None,
    model = "curie,
    n_epochs = 4,
    batch_size = None,
    learning_rate_multiplier = 0.1,
    prompt_loss_weight = 0.1,
    compute_classification_metrics = False,
    classification_n_classes = None,
    classification_positive_class = None,
    classification_betas = None,
    suffix = None
)
```
