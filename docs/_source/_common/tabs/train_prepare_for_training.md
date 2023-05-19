::::{tab-set}

:::{tab-item} OpenAI
:sync: openai

```python
import argilla as rg

dataset_rg = rg.load("<my_dataset>")
dataset_rg.prepare_for_training(framework="openai", train_size=1)
# [{'promt': 'My title', 'completion': ' My content'}]
```
:::

:::{tab-item} Setfit
:sync: setfit

```python
import argilla as rg

dataset_rg = rg.load("<my_dataset>")
dataset_rg.prepare_for_training(framework="setfit", train_size=1)
# {'title': 'My title', 'content': 'My content', 'label': 0}
```
:::

:::{tab-item} spaCy
:sync: spacy

```python
import argilla as rg
import spacy

nlp = spacy.blank("en")

dataset_rg = rg.load("<my_dataset>")
dataset_rg.prepare_for_training(framework="spacy", lang=nlp, train_size=1)
# <spacy.tokens._serialize.DocBin object at 0x280613af0>
```
:::

:::{tab-item} Transformers
:sync: transformers

```python
import argilla as rg

dataset_rg = rg.load("<my_dataset>")
dataset_rg.prepare_for_training(framework="transformers", train_size=1)
# {'title': 'My title', 'content': 'My content', 'label': 0}
```
:::

:::{tab-item} SpanMarker
:sync: spanmarker

```python
import argilla as rg

dataset_rg = rg.load("<my_dataset>")
dataset_rg.prepare_for_training(framework="span_marker", train_size=1)
# {'title': 'My title', 'content': 'My content', 'label': 0}
```
:::

:::{tab-item} Spark NLP
:sync: sparknlp

```python
import argilla as rg

dataset_rg = rg.load("<my_dataset>")
dataset_rg.prepare_for_training(framework="spark-nlp", train_size=1)
# <pd.DataFrame>
```
:::

::::