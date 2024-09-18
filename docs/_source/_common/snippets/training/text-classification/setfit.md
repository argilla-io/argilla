---
title: SetFit
description: The ArgillaSetFitTrainer leverages the features of SetFit to train programmatically with Argilla.
links:
  - linkText: Argilla docs
    linkLink: https://docs.v1.argilla.io/en/latest/practical_guides/fine_tune.html#text-classification
  - linkText: SetFit docs
    linkLink: https://github.com/huggingface/setfit
---

*code snippet*

```python
from argilla.training import ArgillaTrainer

trainer = ArgillaTrainer(
    name="<my_dataset_name>",
    workspace="<my_workspace_name>",
    framework="setfit",
    train_size=0.8
)
trainer.update_config(num_iterations=10)
trainer.train(output_dir="text-classification")
records = trainer.predict("The ArgillaTrainer is great!", as_argilla_records=True)
```

*update training config*

```python
trainer.update_config(
    dev_corpus = "corpora.dev",
    train_corpus = "corpora.train",
    seed = 42,
    gpu_allocator = 0,
    accumulate_gradient = 1,
    patience = 1600,
    max_epochs = 0,
    max_steps = 20000,
    eval_frequency = 200,
    frozen_components = [],
    annotating_components = [],
    before_to_disk = None,
    before_update = None
)
```
