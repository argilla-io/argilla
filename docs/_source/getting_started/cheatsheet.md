# 🎼 Cheatsheet

## Installation

```{include} /_common/tabs/argilla_install_python.md
```


```{include} /_common/tabs/argilla_install.md
```

## Connect to Argilla

To get started with your data from our Python library, we first need to connect to our FastAPI server. This is done via `httpx` using an API key and a URL. Or take a more extensive look [here](/getting_started/quickstart_installation).

```{include} /_common/tabs/argilla_connect.md
```

## Configure datasets

Before getting started with any textual data project, we advise setting up annotation guidelines and a labeling schema. Need some more context? Take a look [here](/getting_started/quickstart_workflow).

```{include} /_common/tabs/dataset_settings.md
```

Note that feedback datasets support different types of questions. For more info on each of them, check out [this section](/getting_started/quickstart_workflow_feedback).

```{include} /_common/tabs/question_settings.md
```

## Create records

```{include} /_common/tabs/records_create.md
```

## Query datasets

To search your data from the UI or the Python library, you need to be able to write Lucene Query Language (LQL), which is native to Elastic Search and Open Search. To know more about querying and searching, take a look [here](/practical_guides/filter_dataset).

::::{tab-set}

:::{tab-item} text and inputs

The `text` field uses Elasticsearch's [standard analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/analysis-standard-analyzer.html) that ignores capitalization and removes most of the punctuation;
The `text.exact` field uses the [whitespace analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/analysis-whitespace-analyzer.html) that differentiates between lower and upper case, and does take into account punctuation;

- `text:dog.` or `text:fox`: matches both of the records.
- `text.exact:dog` or `text.exact:FOX`: matches none of the records.
- `text.exact:dog.` or `text.exact:fox`: matches only the first record.
- `text.exact:DOG` or `text.exact:FOX\!`: matches only the second record.

Similar reasoning holds for the `inputs` to look for records in which the *subject*-key contains the word *news*, you would search for

- `inputs.subject:news`

Again, as with the `text` field, you can also use the white space analyzer to perform more fine-grained searches by specifying the `exact` field.

- `inputs.subject.exact:NEWS`

![text2text_record](/_static/reference/webapp/features-search.png)
:::

:::{tab-item} metadata and filters

Imagine you provided the split to which the record belongs as metadata, that is `metadata={"split": "train"}` or `metadata={"split": "test"}`.
Then you could only search your training data by specifying the corresponding field in your query:

- `metadata.split:train`

Just like the metadata, you can also use the filter fields in your query.
A few examples to emulate the filters in the query string are:

- `status:Validated`
- `annotated_as:HAM`
- `predicted_by:Model A`

Ranges can be specified for date, numeric or string fields.
Inclusive ranges are specified with square brackets and exclusive ranges are with curly brackets:

- `score:[0.5 TO 0.6]`
- `score:{0.9 TO *}`
- `event_timestamp:[1984-01-01T01:01:01.000000 TO *]`
- `last_updated:{* TO 1984-01-01T01:01:01.000000}`

![text2text_record](/_static/reference/webapp/features-search.png)
:::

:::{tab-item} operators

You can combine an arbitrary amount of terms and fields in your search using the familiar boolean operators `AND`, `OR` and `NOT`.
The following examples showcase the power of these operators:

- `text:(quick AND fox)`: Returns records that contain the word *quick* and *fox*. The `AND` operator is the default operator, so `text:(quick fox)` is equivalent.
- `text:(quick OR brown)`: Returns records that contain either the word *quick* or *brown*.
- `text:(quick AND fox AND NOT news)`: Returns records that contain the words *quick* and *fox*, **and do not** contain *news*.
- `metadata.split:train AND text:fox`: Returns records that contain the word *fox* and that have the metadata *"split: train"*.
- `NOT _exists_:metadata.split` : Returns records that don't have a metadata *split*.

![text2text_record](/_static/reference/webapp/features-search.png)
:::

:::{tab-item} regex

Regular expression patterns can be embedded in the query string by wrapping them in forward slashes "/":

- `text:/joh?n(ath[oa]n)/`: Matches *jonathon*, *jonathan*, *johnathon*, and *johnathan*.

The supported regular expression syntax is explained in the official [Elasticsearch documentation](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/regexp-syntax.html).

![text2text_record](/_static/reference/webapp/features-search.png)
:::

:::{tab-item} fuzzy

You can search for terms that are similar to, but not exactly like the search terms, using the *fuzzy* operator.
This is useful to cover human misspellings:

- `text:quikc~`: Matches quick and quikc.

![text2text_record](/_static/reference/webapp/features-search.png)
:::

:::{tab-item} wildcards

Wildcard searches can be run on individual search terms, using `?` to replace a single character, and `*` to replace zero or more characters:

- `text:(qu?ck bro*)`
- `text.exact:"Lazy Dog*"`: Matches, for example, *"Lazy Dog"*, *"Lazy Dog."*, or *"Lazy Dogs"*.
- `inputs.\*:news`: Searches all input fields for the word *news*.

![text2text_record](/_static/reference/webapp/features-search.png)
:::

::::

## Semantic search

Semantic search or vector search is an amazingly powerful tool to sift through text based on sensical intuition instead of keywords. We use the native Elastic Search vector support to empower our users to navigate their records. Want to know more about this? Take a look [here](/tutorials/techniques/semantic_search).

::::{tab-set}

:::{tab-item} Create Records
```python
import argilla as rg

# We allow for a maximum of 5 vectors.
record = rg.TextClassificationRecord(
    text="Hello world, I am a vector record!",
    vectors= {"my_vector_name": [0, 42, 1984]}
)
rg.log(name="dataset", records=record)
```
:::

:::{tab-item} Query Records
```python
import argilla as rg

# We return the 50 most similar records
records = rg.load(name="dataset", vector=("my_vector_name", [0, 43, 1985]))
```
:::

::::

<a href="https://docs.v1.argilla.io/en/latest/guides/label_records_with_semanticsearch.html"><img src="https://docs.v1.argilla.io/en/latest/_images/features-similaritysearch.png" width="100%"></a>

## Weak supervision

Weak supervision for NLP is like teaching a model with "approximate" answers instead of perfect ones. It uses clever tricks and shortcuts to avoid the need for labor-intensive labeling. It's like giving the model training wheels to learn on its own. While it's not as accurate as traditional supervision, it allows training on a much larger scale. Want to know more, look [here](/tutorials/techniques/weak_supervision).

::::{tab-set}

:::{tab-item} Create, update and delete Rules
```python
from argilla.labeling.text_classification import add_rules, delete_rules, Rule, update_rules

# Create
rule = Rule(query="positive impact", label="optimism")
add_rules(dataset="my_dataset", rules=[rule])

# Update
rule.label = "pessimism"
update_rules(dataset="my_dataset", rules=[rule])

# Delete
delete_rules(dataset="my_dataset", rules=[rule])
```
:::

:::{tab-item} Analyze: WeakLabels
```python
from argilla.labeling.text_classification import WeakLabels, load_rules

rules = load_rules("my_dataset")

weak_labels = WeakLabels(
    rules=rules,
    dataset="my_dataset"
)

weak_labels.summary()
```
:::

:::{tab-item} Predict: MajorityVoter
```python
from argilla.labeling.text_classification import MajorityVoter, #Snorkel, #FlyingSquid

majority_model = MajorityVoter(weak_labels)
majority_model.score(output_str=True)
records_for_training = majority_model.predict()

# optional: log the records to a new dataset in Argilla
rg.log(records_for_training, name="majority_voter_results")
```
:::

::::

<a href="https://docs.v1.argilla.io/en/latest/guides/programmatic_labeling_with_rules.html"><img src="https://docs.v1.argilla.io/en/latest/_images/features-weak-labelling.png" width="100%"></a>

## Train Models

We love our open-source training libraries as much as you do, so we provide integrations with all of them to limit the time you spend on data preparation and have more fun with actual training. We support `spacy`, `transformers`, `setfit`, `openai`, `autotrain`, and way more. Want to get to know all support? Train/fine-tune a model from a `FeedbackDataset` as explained [here](/practical_guides/fine_tune.md#feedback-dataset), or either a `TextClassificationDataset` or a `TokenClassificationDataset`[here](/practical_guides/fine_tune.md#other-datasets).

```python
from argilla.training import ArgillaTrainer

trainer = ArgillaTrainer(
    name="my_dataset",
    workspace="my_workspace",
    framework="my_framework",
    model="my_framework_model",
    train_size=0.8,
    seed=42,
    limit=10,
    query="my-query"
)
trainer.update_config() # see usage below
trainer.train()
records = trainer.predict(["my-text"], as_argilla_records=True)
```

```{include} /_common/tabs/train_update_config.md
```

<a href="https://argilla.io/blog/introducing-argilla-trainer"><img src="https://argilla.io/blog/introducing-argilla-trainer/train.png" width="100%"></a>