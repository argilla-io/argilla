::::{tab-set}

:::{tab-item} Feedback datasets

```python
# install datasets library with pip install datasets
import argilla as rg
from datasets import load_dataset

# load an Argilla Feedback Dataset from the Hugging Face Hub
# look for other datasets at https://huggingface.co/datasets?other=argilla
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



Welcome the user, explain how is easy is to get started, and explain how to get started step-by-step, and making sure the code snippets we suggest really work (at least in most cases).
We should avoid as much as possible requiring external deps.
The steps can be something like:
Open a notebook or Colab (we can even add the link to open a colab)
Install the argilla client with pip
Connect to the server with init, I guess we can't be 100% sure about the api_url but we can explain. For the api_key, explain the user where to get it in the UI with a link.
Setup and create your first dataset with records. We can use something that's really easy, doesn't require deps (if possible) and gets the user a first taste of how a simple dataset looks like.
Explain next steps, as you mentioned pointing to end to end examples



Improve No dataset page to transform it into an onboarding page for first time users (developers)

es, you can think about a good onboarding message from a data science perspective according to the outline in the issues.


David Berenstein
:spiral_calendar_pad:  5 hours ago
Ideally align with the QuickStarts on the docs as well : )


David Berenstein
:spiral_calendar_pad:  5 hours ago
So you can start work on this.


David Berenstein
:spiral_calendar_pad:  5 hours ago
Feel free to iterate with Natalia and Amelie.