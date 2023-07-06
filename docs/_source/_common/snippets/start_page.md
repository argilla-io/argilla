::::{tab-set}

:::{tab-item} Feedback datasets

```python
# install datasets library with pip install datasets
import argilla as rg
from datasets import load_dataset

# load an Argilla Feedback dataset from the Hugging Face hub
dataset = rg.FeedbackDataset.from_huggingface("argilla/oasst_response_quality", split="train")

# push the dataset to Argilla
dataset.push_to_argilla("oasst_response_quality")
```
:::

:::{tab-item} Other datasets

```python
# install datasets library with pip install datasets
import argilla as rg
from datasets import load_dataset

# load dataset from the hub
dataset = load_dataset("argilla/gutenberg_spacy-ner", split="train")

# read in dataset, assuming its a dataset for token classification
dataset_rg = rg.read_datasets(dataset, task="TokenClassification")

# log the dataset
rg.log(dataset_rg, "gutenberg_spacy-ner")
```
:::
::::