---
title: This is how to train your Text Classifier dataset using spaCy
description: In aliquet velit eget nisl euismod ultricies. Nam pretium tortor eu pretium lobortis. Proin imperdiet ante erat. Vestibulum vitae faucibus felis, et posuere felis. Sed pharetra congue tristique
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
