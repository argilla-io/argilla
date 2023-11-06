# 📥 Export a dataset
​
Your Argilla instance will always have all your datasets and annotations saved and accessible. However, if you'd like to save your dataset either locally or in the Hugging Face Hub, in this section you will find some useful methods to do just that.
​
## Feedback Dataset

```{include} /_common/feedback_dataset.md
```

### Pull from Argilla
​
The first step will be to pull a dataset from Argilla with the `FeedbackDataset.from_argilla()` method. This method will return a new instance of `FeedbackDataset` with the same guidelines, fields, questions, and records (including responses if any) as the dataset in Argilla.
​
:::{note}
From Argilla 1.14.0, calling `from_argilla` will pull the `FeedbackDataset` from Argilla, but the instance will be remote, which implies that the additions, updates, and deletions of records will be pushed to Argilla as soon as they are made. This is a change from previous versions of Argilla, where you had to call `push_to_argilla` again to push the changes to Argilla.
:::
​
```python
remote_dataset = rg.FeedbackDataset.from_argilla("my-dataset", workspace="my-workspace")
local_dataset = remote_dataset.pull(max_records=100) # get first 100 records
```
​
At this point, you can do any post-processing you may need with this dataset e.g., [unifying responses](collect_responses.ipynb) from multiple annotators. Once you're happy with the result, you can decide on some of the following options to save it.
​
### Push back to Argilla
​
When using a `FeedbackDataset` pulled from Argilla via `FeedbackDataset.from_argilla`, you can always push the dataset back to Argilla in case you want to clone the dataset or explore it after post-processing.

::::{tab-set}

:::{tab-item} Argilla 1.14.0 or higher
```python
# This publishes the dataset with its records to Argilla and returns the dataset in Argilla
remote_dataset = dataset.push_to_argilla(name="my-dataset", workspace="my-workspace")
local_dataset = remote_dataset.pull(max_records=100) # get first 100 records
```
:::

:::{tab-item} Lower than Argilla 1.14.0
```python
# This publishes the dataset with its records to Argilla and turns the dataset object into a dataset in Argilla
dataset.push_to_argilla(name="my-dataset", workspace="my-workspace")
```
:::
::::
​
Additionally, you can still clone local `FeedbackDataset` datasets that have neither been pushed nor pulled to/from Argilla, respectively; via calling `push_to_argilla`.
​
```python
dataset.push_to_argilla(name="my-dataset-clone", workspace="my-workspace")
```
​
### Push to the Hugging Face Hub
​
It is also possible to save and load a `FeedbackDataset` into the Hugging Face Hub for persistence. The methods `push_to_huggingface` and `from_huggingface` allow you to push to or pull from the Hugging Face Hub, respectively.
​
When pushing a `FeedbackDataset` to the HuggingFace Hub, one can provide the param `generate_card` to generate and push the Dataset Card too. `generate_card` is by default `True`, so it will always be generated unless `generate_card=False` is specified.
​
```python
# Push to HuggingFace Hub
dataset.push_to_huggingface("argilla/my-dataset")
​
# Push to HuggingFace Hub as private
dataset.push_to_huggingface("argilla/my-dataset", private=True, token="...")
```
​
Note that the `FeedbackDataset.push_to_huggingface()` method uploads not just the dataset records, but also a configuration file named `argilla.yaml`, that contains the dataset configuration i.e. the fields, questions, and guidelines, if any. This way you can load any `FeedbackDataset` that has been pushed to the Hub back in Argilla using the `from_huggingface` method.
​
```python
# Load a public dataset
dataset = rg.FeedbackDataset.from_huggingface("argilla/my-dataset")
​
# Load a private dataset
dataset = rg.FeedbackDataset.from_huggingface("argilla/my-dataset", use_auth_token=True)
```
​
```{note}
The args and kwargs of `push_to_huggingface` are the args of `push_to_hub` from 🤗[Datasets](https://huggingface.co/docs/datasets/v2.12.0/en/package_reference/main_classes#datasets.Dataset.push_to_hub), and the ones of `from_huggingface` are the args of `load_dataset` from 🤗[Datasets](https://huggingface.co/docs/datasets/v2.12.0/en/package_reference/loading_methods#datasets.load_dataset).
```
​
### Save to disk
​
Additionally, due to the integration with 🤗 Datasets, you can also export the records of a `FeedbackDataset` locally in your preferred format by converting the `FeedbackDataset` to a `datasets.Dataset` first using the method `format_as("datasets")`. Then, you may export the `datasets.Dataset` to either CSV, JSON, Parquet, etc. Check all the options in the 🤗[Datasets documentation](https://huggingface.co/docs/datasets/v2.12.0/en/package_reference/main_classes#datasets.Dataset.save_to_disk).
​
```python
hf_dataset = dataset.format_as("datasets")
​
hf_dataset.save_to_disk("sharegpt-prompt-rating-mini")  # Save as a `datasets.Dataset` in the local filesystem
hf_dataset.to_csv("sharegpt-prompt-rating-mini.csv")  # Save as CSV
hf_dataset.to_json("sharegpt-prompt-rating-mini.json")  # Save as JSON
hf_dataset.to_parquet()  # Save as Parquet
```
​
```{note}
This workaround will just export the records into the desired format, not the dataset configuration. If you want to load the records back into Argilla, you will need to create a `FeedbackDataset` and add the records as explained [here](/practical_guides/create_dataset.md).
```
​
## Other datasets
​
```{include} /_common/other_datasets.md
```
​
### Pull from Argilla
​
You can simply load the dataset from Argilla using the `rg.load()` function.
​
```python
import argilla as rg
​
# load your annotated dataset from the Argilla web app
dataset_rg = rg.load("my_dataset")
```
​
For easiness and manageability, Argilla offers transformations to Hugging Face Datasets and Pandas DataFrame.
```python
# export your Argilla Dataset to a datasets Dataset
dataset_ds = dataset_rg.to_datasets()
```
```python
# export to a pandas DataFrame
df = dataset_rg.to_pandas()
```

### Push back to Argilla

When using other datasets pulled from Argilla via `rg.load`, you can always push the dataset back to Argilla. This can be done using the `rg.log()` function, just like you did when pushing records for the first time to Argilla. If the records don't exist already in the dataset, these will be added to it, otherwise, the existing records will be updated.

```python
import argilla as rg

dataset_rg = rg.load("my_dataset")

# loop through the records and change them

rg.log(dataset_rg, name="my_dataset")
```
​
### Push to the Hugging Face Hub

You can push your dataset in the form of a Hugging Face Dataset directly to the hub. Just use the `to_datasets()` transformation as explained in the previous section and push the dataset:
​
```python
# push the dataset to the Hugging Face Hub
dataset_ds.push_to_hub("my_dataset")
```
​
### Save to disk
Your dataset will always be safe and accessible from Argilla, but in case you need to share or save it somewhere else, here are a couple of options.
​
Alternatively, you can save the dataset locally. To do that, we recommend formatting the dataset as a [Hugging Face Dataset](https://huggingface.co/docs/datasets/v2.12.0/en/package_reference/main_classes#datasets.Dataset.save_to_disk) or [Pandas DataFrame](https://pandas.pydata.org/docs/reference/io.html) first and use the methods native to these libraries to export as CSV, JSON, Parquet, etc.
​
```python
# save locally using Hugging Face datasets
​
import argilla as rg
​
# load your annotated dataset from the Argilla web app
dataset_rg = rg.load("my_dataset")
​
# export your Argilla Dataset to a datasets Dataset
dataset_ds = dataset_rg.to_datasets()
​
dataset_ds.save_to_disk("my_dataset")  # Save as a `datasets.Dataset` in the local filesystem
dataset_ds.to_csv("my_dataset.csv")  # Save as CSV
dataset_ds.to_json("my_dataset.json")  # Save as JSON
dataset_ds.to_parquet()  # Save as Parquet
```
​
```python
# save locally using Pandas DataFrame
import argilla as rg
​
# load your annotated dataset from the Argilla web app
dataset_rg = rg.load("my_dataset")
​
# export your Argilla Dataset to a Pandas DataFrame
df = dataset_rg.to_pandas()
​
df.to_csv("my_dataset.csv")  # Save as CSV
df.to_json("my_dataset.json")  # Save as JSON
df.to_parquet("my_dataset.parquet")  # Save as Parquet
```