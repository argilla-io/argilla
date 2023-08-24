# 🧑‍💻 Manage Data

This guide showcases some features of the `Dataset` classes in the Argilla client.
The Dataset classes are lightweight containers for Argilla records. These classes facilitate importing from and exporting to different formats (e.g., `pandas.DataFrame`, `datasets.Dataset`) as well as sharing and versioning Argilla datasets using the Hugging Face Hub.

For each record type there's a corresponding Dataset class called `DatasetFor<RecordType>`.
You can look up their API in the [reference section](../reference/python/python_client.rst#module-argilla.client.datasets)

```{note}
For information on how to manage data for the new Feedback Task datasets, check our [How-to guides](../guides/llms/practical_guides/practical_guides.md) that explain how to import/export data, configure this type of dataset and more!
```

## Argilla Records

The main component of the Argilla data model is called a record. A dataset in Argilla is a collection of these records.
Records can be of different types depending on the currently supported tasks:

 1. `TextClassificationRecord`
 2. `TokenClassificationRecord`
 3. `Text2TextRecord`

The most critical attributes of a record that are common to all types are:

 - `text`: The input text of the record (Required);
 - `annotation`: Annotate your record in a task-specific manner (Optional);
 - `prediction`: Add task-specific model predictions to the record (Optional);
 - `metadata`: Add some arbitrary metadata to the record (Optional);

Some other cool attributes for a record are:

 - `vectors`: Input vectors to enable [semantic search](label_records_with_semanticsearch.html).
 - `explanation`: Token attributions for [highlighting text](log_model_explanations.html).

In Argilla, records are created programmatically using the [client library](../reference/python/python_client.rst) within a Python script, a [Jupyter notebook](https://jupyter.org/), or another IDE.


Let's see how to create and upload a basic record to the Argilla web app  (make sure Argilla is already installed on your machine as described in the [setup guide](../getting_started/quickstart_installation.html)):

### Create records

We support different tasks within the Argilla eco-system focused on NLP: `Text Classification`, `Token Classification` and `Text2Text`.


::::{tab-set}

:::{tab-item} Text Classification

```python
import argilla as rg

rec = rg.TextClassificationRecord(
    text="beautiful accomodations stayed hotel santa... hotels higer ranked website.",
    prediction=[("price", 0.75), ("hygiene", 0.25)],
    annotation="price"
)
rg.log(records=rec, name="my_dataset")
```
![single_textclass_record](/_static/reference/webapp/features-single_textclass_record.png)
:::

:::{tab-item} Text Classification (multi-label)
```python
import argilla as rg

rec = rg.TextClassificationRecord(
    text="damn this kid and her fancy clothes makes me feel like a bad parent.",
    prediction=[("admiration", 0.75), ("annoyance", 0.25)],
    annotation=["price", "annoyance"],
    multi_label=True
)
rg.log(records=rec, name="my_dataset")
```
![multi_textclass_record](/_static/reference/webapp/features-multi_textclass_record.png)
:::


:::{tab-item} Token Classification
```python
import argilla as rg

record = rg.TokenClassificationRecord(
    text="Michael is a professor at Harvard",
    tokens=["Michael", "is", "a", "professor", "at", "Harvard"],
    prediction=[("NAME", 0, 7, 0.75), ("LOC", 26, 33, 0.8)],
    annotation=[("NAME", 0, 7), ("LOC", 26, 33)],
)
rg.log(records=rec, name="my_dataset")
```
![tokclass_record](/_static/reference/webapp/features-tokclass_record.png)
:::

:::{tab-item} Text2Text
```python
import argilla as rg

record = rg.Text2TextRecord(
    text="A giant giant spider is discovered... how much does he make in a year?",
    prediction=["He has 3*4 trees. So he has 12*5=60 apples."],
)
rg.log(records=rec, name="my_dataset")
```

![text2text_record](/_static/reference/webapp/features-text2text_record.png)
:::

::::

### Special Metadata Fields

To facilitate some customization for the usage of metadata fields, we also added some custom metadata fields.

#### Protected fields

By adding a leading underscore `_` to a random metadata field, we can refrain Argilla from indexing it, which allows us to store the additional info in Elastic without performance loss. So, these metadata fields won't be used in queries or filters by adding an underscore at the start e.g. `_my_field`.

#### Image support

You can pass a URL in the metadata field `_image_url` and the image will be rendered in the Argilla UI. You can use this in the Text Classification and the Token Classification tasks. These images need to be hosted on a publicly available URL, or private file servers like NGINX, or Minio.

## Argilla Datasets
### Create a Dataset

The records classes correspond to 3 equivalent datasets:

 1. `DatasetForTextClassification`
 2. `DatasetForTokenClassification`
 3. `DatasetForText2Text`

Under the hood the Dataset classes store the records in a simple Python list. Therefore, working with a Dataset class is not very different from working with a simple list of records, but before creating a dataset we should first define dataset settings and a labeling schema.

Argilla datasets have certain *settings* that you can configure via the `rg.*Settings` classes, for example `rg.TextClassificationSettings`. The Dataset classes do some extra checks for you, to make sure you do not mix record types when appending or indexing into a dataset.

### Define a labeling schema
You can define a labeling schema for your Argilla dataset, which fixes the allowed labels for your predictions and annotations.
Once you set a labeling schema, each time you log to the corresponding dataset, Argilla will perform validations of the added predictions and annotations to make sure they comply with the schema.
You can set your labels using the code below or from the [Dataset settings page](../reference/webapp/pages.md#dataset-settings) in the UI.

If you forget to define a labeling schema, Argilla will aggregate the labels it finds in the dataset automatically, but you will need to validate it. To do this, go to your [Dataset settings page](../reference/webapp/pages.md#dataset-settings) and click _Save schema_.

![Schema not saved](/_static/images/guides/guides-define_schema.png)

::::{tab-set}

:::{tab-item} Text Classification
```python
import argilla as rg

settings = rg.TextClassificationSettings(label_schema=["A", "B", "C"])

rg.configure_dataset(name="my_dataset", settings=settings)
```
:::

:::{tab-item} Token Classification
```python
import argilla as rg

settings = rg.TokenClassificationSettings(label_schema=["A", "B", "C"])

rg.configure_dataset(name="my_dataset", settings=settings)
```
:::

:::{tab-item} Text2Text
Because we do not require a labeling schema for `Text2Text`, we can create a dataset by directly logging records via `rg.log()`.
:::

::::
## Log data

Argilla currently gives users several ways to log model predictions besides the `rg.log` async method.

### Using `rg.log`

For this example we show how to use `rg.log` to create records that will be logged into an existing dataset, with an [existing labeling schema](#define-a-labeling-schema). Note that, this needs to be defined before logging data into a dataset.

```python
import argilla as rg

# create a record with correct annotation
valid_record = rg.TextClassificationRecord(text="text", annotation="A")
dataset_rg = rg.DatasetForTextClassification([valid_record])
rg.log(dataset_rg, "my_dataset") or rg.log(valid_record, "my_dataset")
# processed 1 record(s)

# Logging to the newly created dataset triggers the validation checks and prohibits label B
invalid_record = rg.TextClassificationRecord(text="text", annotation="D")
invalid_dataset_rg = rg.DatasetForTextClassification([invalid_record])
rg.log(invalid_dataset_rg, "my_dataset") or rg.log(invalid_record, "my_dataset")
# BadRequestApiError: Argilla server returned an error with http status: 400
```

### Using `rg.monitor`

For widely-used libraries Argilla includes an "auto-monitoring" option via the `rg.monitor` method. Currently supported libraries are Hugging Face Transformers and spaCy, if you'd like to see another library supported feel free to add a discussion or issue on GitHub.

`rg.monitor` will wrap HF and spaCy pipelines so every time you call them, the output of these calls will be logged into the dataset of your choice, as a background process, in a non-blocking way. Additionally, `rg.monitor` will add several tags to your dataset such as the library build version, the model name, the language, etc. This should also work for custom (private) pipelines, not only the Hub's or official spaCy models.

It is worth noting that this feature is useful beyond monitoring, and can be used for data collection (e.g., bootstrapping data annotation with pre-trained pipelines), model development (e.g., error analysis), and model evaluation (e.g., combined with data annotation to obtain evaluation metrics).

```python
import argilla as rg

# using spaCy
import spacy
nlp = spacy.load("en_core_web_sm")
nlp = rg.monitor(nlp, dataset="nlp_monitoring_spacy", sample_rate=1.0)
nlp("I want to monitor this TokenClassification text!")

# using transformers
from transformers import pipeline
nlp = pipeline("sentiment-analysis", return_all_scores=True, padding=True, truncation=True)
nlp = rg.monitor(nlp, dataset="nlp_monitoring", sample_rate=1.0)
nlp("I want to monitor this TextClassification text!")

# using flAIr
from flair.data import Sentence
from flair.models import SequenceTagger
tagger = rg.monitor(SequenceTagger.load("flair/ner-english"), dataset="flair-example", sample_rate=1.0)
sentence = Sentence("I want to monitor this TokenClassification text!")
tagger.predict(sentence)
```

### Using ASGI middleware

For using the ASGI middleware, see this [tutorial](/tutorials/notebooks/deploying-texttokenclassification-fastapi.ipynb).

## Load Data

It is very straightforward to simply load a dataset. This can be done using `rg.load`. Additionally, you can check our [query page](query_datasets.html) for custom info about querying and you can check our [vector page](label_records_with_semanticsearch.html) for info about vector search.

```python
import argilla as rg

dataset_rg = rg.load(
    name="my_dataset",
    query="my AND query",
    limit=42,
    vectors=("vector1", [0, 42, 1957]),
    sort=[("event_timestamp", "desc")]
)
```

## Update Data

It is possible to update records from your Argilla datasets using our Python API. This approach works the same way as an upsert in a normal database, based on the record `id`. You can update any arbitrary parameters and they will be over-written if you use the `id` of the original record.

```python
import argilla as rg

# read all records in the dataset or define a specific search via the `query` parameter
record = rg.load("my_first_dataset")

# modify first record metadata (if no previous metadata dict you might need to create it)
record[0].metadata["my_metadata"] = "im a new value"

# log record to update it, this will keep everything but add my_metadata field and value
rg.log(name="my_first_dataset", records=record[0])
```

## Import and export Data

When you have your data in a [_pandas DataFrame_](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) or a [_datasets Dataset_](https://huggingface.co/docs/datasets/access.html), we provide some neat shortcuts to import this data into a Argilla Dataset.
You have to make sure that the data follows the record model of a specific task, otherwise you will get validation errors.
Columns in your DataFrame/Dataset that are not supported or recognized, will simply be ignored.

The record models of the tasks are explained in the [reference section](../reference/python/python_client.rst#module-argilla.client.models).

<div class="alert alert-info">

Note

Due to it's pyarrow nature, data in a `datasets.Dataset` has to follow a slightly different model, that you can look up in the examples of the `Dataset*.from_datasets` [docstrings](../reference/python/python_client.rst#argilla.client.datasets.DatasetForTokenClassification.from_datasets).

</div>

### Pandas

```python
import argilla as rg

# import data from a pandas DataFrame
dataset_rg = rg.read_pandas(my_dataframe, task="TextClassification")
# or
dataset_rg = rg.DatasetForTextClassification.from_pandas(my_dataframe)

# export back to a pandas DataFrame
dataset_rg.to_pandas()
```

### Datasets library

We also provide helper arguments you can use to read almost arbitrary datasets for a given task from the [Hugging Face Hub](https://huggingface.co/datasets).

```python
import argilla as rg
from datasets import load_dataset

my_dataset = load_dataset("argilla/news", split="test")

# import data from a datasets Dataset
dataset_rg = rg.read_datasets(my_dataset, task="TextClassification")
# or
dataset_rg = rg.DatasetForTextClassification.from_datasets(my_dataset)

# export back to a datasets
dataset_rg.to_datasets()
```

Additionally, we can choose to map certain input arguments of the Argilla records to columns of the given dataset.
Let's have a look at a few examples:

```python
import argilla as rg
from datasets import load_dataset

# the "poem_sentiment" dataset has columns "verse_text" and "label"
dataset_rg = rg.DatasetForTextClassification.from_datasets(
    dataset=load_dataset("poem_sentiment", split="test"),
    text="verse_text",
    annotation="label",
)

# the "snli" dataset has the columns "premise", "hypothesis" and "label"
dataset_rg = rg.DatasetForTextClassification.from_datasets(
    dataset=load_dataset("snli", split="test"),
    inputs=["premise", "hypothesis"],
    annotation="label",
)

# the "conll2003" dataset has the columns "id", "tokens", "pos_tags", "chunk_tags" and "ner_tags"
rg.DatasetForTokenClassification.from_datasets(
    dataset=load_dataset("conll2003", split="test"),
    tags="ner_tags",
)

# the "xsum" dataset has the columns "id", "document" and "summary"
rg.DatasetForText2Text.from_datasets(
    dataset=load_dataset("xsum", split="test"),
    text="document",
    annotation="summary",
)
```

You can also use the shortcut `rg.read_datasets(dataset=..., task=..., **kwargs)` where the keyword arguments are passed on to the corresponding `from_datasets()` method.

### Hugging Face hub

You can easily share your Argilla dataset with your community via the Hugging Face Hub.
For this you just need to export your Argilla Dataset to a `datasets.Dataset` and [push it to the hub](https://huggingface.co/docs/datasets/upload_dataset.html?highlight=push_to_hub#upload-from-python):

```python
import argilla as rg

# load your annotated dataset from the Argilla web app
dataset_rg = rg.load("my_dataset")

# export your Argilla Dataset to a datasets Dataset
dataset_ds = dataset_rg.to_datasets()

# push the dataset to the Hugging Face Hub
dataset_ds.push_to_hub("my_dataset")
```

Afterward, your community can easily access your annotated dataset and log it directly to the Argilla web app:

```python
from datasets import load_dataset

# download the dataset from the Hugging Face Hub
dataset_ds = load_dataset("user/my_dataset", split="train")

# read in dataset, assuming its a dataset for text classification
dataset_rg = rg.read_datasets(dataset_ds, task="TextClassification")

# log the dataset to the Argilla web app
rg.log(dataset_rg, "dataset_by_user")
```
