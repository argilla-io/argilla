---
title: Transformers
description: The ArgillaTransformersTrainer leverages the features of transformers to train programmatically with Argilla.
links:
  - linkText: Argilla docs
    linkLink: https://docs.argilla.io/en/latest/guides/
  - linkText: Transformers docs
    linkLink: https://spacy.io/usage/training
---

```python
from argilla.training import ArgillaTrainer

trainer = ArgillaTrainer(name="<my_dataset_name>", framework="transformers", train_size=0.8)
trainer.update_config(max_epochs=10)
trainer.train(path="text2text")
records = trainer.predict("I live in Barcelona.", as_argilla_records=True)
```
