# Export a Feedback Dataset

Your Argilla instance will always have all your datasets and annotations saved and accessible. However, if you'd like to save your dataset either locally or in the Hugging Face Hub, in this section you will find some useful methods to do just that.

```{note}
The methods mentioned in this page are only available for `FeedbackDataset`. For other types of datasets like `TextClassificationDataset`, `TokenClassificationDataset` and `Text2TextDataset` check [this guide](../../log_load_and_prepare_data.md).
```

## Pull from Argilla

The first step will be to pull a dataset from Argilla with the `FeedbackDataset.from_argilla()` method. This method will return a new instance of `FeedbackDataset` with the same guidelines, fields, questions, and records (including responses if any) as the dataset in Argilla.

```python
dataset = rg.FeedbackDataset.from_argilla("my-dataset", workspace="my-workspace")
```

At this point, you can do any post-processing you may need with this dataset e.g., [unifying responses](collect_responses.ipynb) from multiple annotators. Once you're happy with the result, you can decide on some of the following options to save it.


## Push back to Argilla

When using a `FeedbackDataset` pulled from Argilla via `FeedbackDataset.from_argilla`, you can always push the dataset back to Argilla in case you want to clone the dataset or explore it after post-processing.

::::{tab-set}

:::{tab-item} Argilla 1.14.0 or higher
```python
dataset = dataset.pull()
remote_dataset = dataset.push_to_argilla(name="my-dataset-clone", workspace="my-workspace")
```
:::

:::{tab-item} Lower than Argilla 1.14.0
```python
dataset.push_to_argilla(name="my-dataset-clone", workspace="my-workspace")
```
:::
::::

Additionally, you can still clone local `FeedbackDataset` datasets that have neither been pushed nor pulled to/from Argilla, respectively; via calling `push_to_argilla`.

```python
dataset.push_to_argilla(name="my-dataset-clone", workspace="my-workspace")
```

## Push to the Hugging Face Hub

It is also possible to save and load a `FeedbackDataset` into the Hugging Face Hub for persistence. The methods `push_to_huggingface` and `from_huggingface` allow you to push to or pull from the Hugging Face Hub, respectively.

When pushing a `FeedbackDataset` to the HuggingFace Hub, one can provide the param `generate_card` to generate and push the Dataset Card too. `generate_card` is by default `True`, so it will always be generated unless `generate_card=False` is specified.

```python
# Push to HuggingFace Hub
dataset.push_to_huggingface("argilla/my-dataset")

# Push to HuggingFace Hub as private
dataset.push_to_huggingface("argilla/my-dataset", private=True, token="...")
```

Note that the `FeedbackDataset.push_to_huggingface()` method uploads not just the dataset records, but also a configuration file named `argilla.yaml`, that contains the dataset configuration i.e. the fields, questions, and guidelines, if any. This way you can load any `FeedbackDataset` that has been pushed to the Hub back in Argilla using the `from_huggingface` method.

```python
# Load a public dataset
dataset = rg.FeedbackDataset.from_huggingface("argilla/my-dataset")

# Load a private dataset
dataset = rg.FeedbackDataset.from_huggingface("argilla/my-dataset", use_auth_token=True)
```

```{note}
The args and kwargs of `push_to_huggingface` are the args of `push_to_hub` from 🤗[Datasets](https://huggingface.co/docs/datasets/v2.12.0/en/package_reference/main_classes#datasets.Dataset.push_to_hub), and the ones of `from_huggingface` are the args of `load_dataset` from 🤗[Datasets](https://huggingface.co/docs/datasets/v2.12.0/en/package_reference/loading_methods#datasets.load_dataset).
```

## Save to disk

Additionally, due to the integration with 🤗 Datasets, you can also export the records of a `FeedbackDataset` locally in your preferred format by converting the `FeedbackDataset` to a `datasets.Dataset` first using the method `format_as("datasets")`. Then, you may export the `datasets.Dataset` to either CSV, JSON, Parquet, etc. Check all the options in the [🤗 Datasets documentation](https://huggingface.co/docs/datasets/v2.12.0/en/package_reference/main_classes#datasets.Dataset.save_to_disk).

```python
hf_dataset = dataset.format_as("datasets")

hf_dataset.save_to_disk("sharegpt-prompt-rating-mini")  # Save as a `datasets.Dataset` in the local filesystem
hf_dataset.to_csv("sharegpt-prompt-rating-mini.csv")  # Save as CSV
hf_dataset.to_json("sharegpt-prompt-rating-mini.json")  # Save as JSON
hf_dataset.to_parquet()  # Save as Parquet
```

```{note}
This workaround will just export the records into the desired format, not the dataset configuration. If you want to load the records back into Argilla, you will need to create a `FeedbackDataset` and add the records as explained [here](create_dataset.ipynb).
```
