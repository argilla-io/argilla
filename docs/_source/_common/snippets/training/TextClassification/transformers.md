---
title: spaCy
description: Lorem ipsum
documentationLink: https://docs.argilla.io/en/latest/guides/
task: TextClassification
---

# header

```python
import spacy
import argilla as rg

nlp = spacy.load("en_core_web_sm")
nlp = rg.monitor(nlp, dataset="nlp_monitoring_spacy")

dataset.map(lambda example: {"prediction": nlp(example["text"])})
```
