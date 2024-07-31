---
title: spaCy
description: The ArgillaSpacyTrainer leverages the features of spaCy to train programmatically with Argilla.
links:
  - linkText: Argilla docs
    linkLink: https://docs.v1.argilla.io/en/practical_guides/fine_tune.html#token-classification
  - linkText: spaCy docs
    linkLink: https://spacy.io/usage/training
---

*code snippet*

```python
from argilla.training import ArgillaTrainer

trainer = ArgillaTrainer(
    name="<my_dataset_name>",
    workspace="<my_workspace_name>",
    framework="spacy",
    train_size=0.8
)
trainer.update_config(max_epochs=10)
trainer.train(output_dir="token-classification")
records = trainer.predict("The ArgillaTrainer is great!", as_argilla_records=True)
```

*update training config*

```python
# `spacy.training`
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
