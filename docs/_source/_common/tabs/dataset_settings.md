::::{tab-set}

:::{tab-item} Text Classification
:sync: textclass
```python
import argilla as rg

settings = rg.TextClassificationSettings(label_schema=["A", "B", "C"])

rg.configure_dataset(name="my_dataset", settings=settings)
```
:::

:::{tab-item} Token Classification
:sync: tokenclass
```python
import argilla as rg

settings = rg.TokenClassificationSettings(label_schema=["A", "B", "C"])

rg.configure_dataset(name="my_dataset", settings=settings)
```
:::

:::{tab-item} Text2Text
:sync: text2text
Because we do not require a labeling schema for `Text2Text`, we can create a dataset by directly logging records via `rg.log()`.
:::

::::