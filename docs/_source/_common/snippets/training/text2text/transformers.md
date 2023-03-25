---
title: Transformers
description: The ArgillaTransformersTrainer leverages the features of transformers to train programmatically with an integration with Argilla.
links:
  - linkText: Learn more in the docs
    linkLink: https://docs.argilla.io/en/latest/guides/
  - linkText: Other link
    linkLink: https://docs.argilla.io/en/latest/guides/
---

```python
import spacy
import argilla as rg

nlp = spacy.load("en_core_web_sm")
nlp = rg.monitor(nlp, dataset="nlp_monitoring_spacy")

dataset.map(lambda example: {"prediction": nlp(example["text"])})
```
