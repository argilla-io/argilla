---
title: spaCy
description: The ArgillaSpacyTrainer leverages the features of spaCy to train programmatically with Argilla.
links:
  - linkText: Argilla docs
    linkLink: https://docs.argilla.io/en/latest/guides/
  - linkText: spaCy docs
    linkLink: https://spacy.io/usage/training
---

*code snippet*
```python
from argilla.training import ArgillaTrainer

trainer = ArgillaTrainer(name="<my_dataset_name>", framework="spacy", train_size=0.8)
trainer.update_config(max_epochs=10)
trainer.train(path="token-classification")
records = trainer.predict("I live in Barcelona.", as_argilla_records=True)
```

*config options*
```bash
[training]
dev_corpus = "corpora.dev"
train_corpus = "corpora.train"
seed = ${system.seed}
gpu_allocator = ${system.gpu_allocator}
dropout = 0.1
accumulate_gradient = 1
patience = 1600
max_epochs = 0
max_steps = 20000
eval_frequency = 200
frozen_components = []
annotating_components = []
before_to_disk = null
before_update = null
```
