::::{tab-set}

:::{tab-item} OpenAI

```python
import argilla as rg

dataset_rg = rg.load("<my_dataset>")
dataset_rg.prepare_for_training(framework="openai", train_size=1)
# [{'promt': 'My title', 'completion': ' My content'}]
```
:::

:::{tab-item} AutoTrain

```python
import argilla as rg

dataset_rg = rg.load("<my_dataset>")
dataset_rg.prepare_for_training(framework="autotrain", train_size=1)
# {'title': 'My title', 'content': 'My content', 'label': 0}
```
:::

:::{tab-item} Setfit

```python
import argilla as rg

dataset_rg = rg.load("<my_dataset>")
dataset_rg.prepare_for_training(framework="setfit", train_size=1)
# {'title': 'My title', 'content': 'My content', 'label': 0}
```
:::

:::{tab-item} spaCy

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

```python
import argilla as rg

dataset_rg = rg.load("<my_dataset>")
dataset_rg.prepare_for_training(framework="transformers", train_size=1)
# {'title': 'My title', 'content': 'My content', 'label': 0}
```
:::

:::{tab-item} Peft (LoRA)

```python
import argilla as rg

dataset_rg = rg.load("<my_dataset>")
dataset_rg.prepare_for_training(framework="peft", train_size=1)
# {'title': 'My title', 'content': 'My content', 'label': 0}
```
:::

:::{tab-item} SpanMarker

```python
import argilla as rg

dataset_rg = rg.load("<my_dataset>")
dataset_rg.prepare_for_training(framework="span_marker", train_size=1)
# {'title': 'My title', 'content': 'My content', 'label': 0}
```
:::

:::{tab-item} Spark NLP

```python
import argilla as rg

dataset_rg = rg.load("<my_dataset>")
dataset_rg.prepare_for_training(framework="spark-nlp", train_size=1)
# <pd.DataFrame>
```
:::

::::