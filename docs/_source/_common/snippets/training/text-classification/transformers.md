---
title: This is how to train your Text Classifier dataset using Transformers
description: In aliquet velit eget nisl euismod ultricies. Nam pretium tortor eu pretium lobortis.
buttonText: Learn more in the docs
buttonLink: https://docs.argilla.io/en/latest/guides/
---

```python
import spacy
import argilla as rg

nlp = spacy.load("en_core_web_sm")
nlp = rg.monitor(nlp, dataset="nlp_monitoring_spacy")

dataset.map(lambda example: {"prediction": nlp(example["text"])})
```
