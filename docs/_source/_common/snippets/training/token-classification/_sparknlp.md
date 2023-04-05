---
title: Spark NLP
description: The ArgillaSparkNLPTrainer leverages the features of Spark NLP to train programmatically with Argilla.
links:
  - linkText: Argilla docs
    linkLink: https://docs.argilla.io/en/latest/guides/train_a_model.html
  - linkText: Spark NLP docs
    linkLink: https://spacy.io/usage/training
---

*code snippet*

```python
from argilla.training import ArgillaTrainer

trainer = ArgillaTrainer(name="<my_dataset_name>", framework="spark-nlp", train_size=0.8)
trainer.update_config(max_epochs=10)
trainer.train(path="token-classification")
records = trainer.predict("The ArgillaTrainer is great!", as_argilla_records=True)
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
