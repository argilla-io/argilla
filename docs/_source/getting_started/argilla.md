# What is Argilla?

[Argilla](https://argilla.io) is an open-source data curation platform for LLMs. Using Argilla, everyone can build robust language models through faster data curation using both human and machine feedback. We provide support for each step in the MLOps cycle, from data labeling to model monitoring.

<div class="social social--sidebar" style="margin-top: 1em; display: flex; justify-content: right; gap: 8px">
    <a href="https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g"
        class="button--primary" target="_blank">Join <span aria-label="slack" class="slack-icon"></span></a>
    <a href="https://linkedin.com/company/argilla-io"
        class="button--primary" target="_blank">Follow on LinkedIn</a>
    <a href="https://linkedin.com/company/argilla-io"
        class="button--primary" target="_blank">Follow on Twitter</a>
    <div class="github-stars github-stars--sidebar"></div>
</div>

<iframe width="100%" height="450" src="https://www.youtube.com/embed/jP3anvp7Rto" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>


https://demo.argilla.io/datasets
## 🎼 Cheatsheet

### Deployments

::::{tab-set}

:::{tab-item} Docker
```bash
docker run -d --name argilla -p 6900:6900 argilla/argilla-quickstart:latest
```
:::

:::{tab-item} Docker Compose
```
wget -O docker-compose.yaml https://raw.githubusercontent.com/argilla-io/argilla/main/docker-compose.yaml && docker-compose up -d
```
:::

:::{tab-item} Hugging Face Spaces
<a  href="https://huggingface.co/new-space?template=argilla/argilla-template-space">
    <img src="https://huggingface.co/datasets/huggingface/badges/raw/main/deploy-to-spaces-lg.svg" />
</a>
:::

::::

### Configure Dataset

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
Because we do not require a labeling schema, we can create a dataset by directly logging records as shown below.
:::

::::

### Create Records


::::{tab-set}

:::{tab-item} Text Classification
```python
:sync: textclass
import argilla as rg

rec = rg.TextClassificationRecord(
    text="beautiful accomodations stayed hotel santa... hotels higer ranked website.",
    prediction=[("price", 0.75), ("hygiene", 0.25)],
    annotation="price"
)
rg.log(records=rec, name="my_dataset")
```
![single_textclass_record](../../_static/reference/webapp/features-single_textclass_record.png)
:::

:::{tab-item} Text Classification (multi-label)
:sync: textclass
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
![multi_textclass_record](../../_static/reference/webapp/features-multi_textclass_record.png)
:::


:::{tab-item} Token Classification
:sync: tokenclass
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
![tokclass_record](../../_static/reference/webapp/features-tokclass_record.png)
:::

:::{tab-item} Text2Text
:sync: text2text
```python
import argilla as rg

record = rg.Text2TextRecord(
    text="A giant giant spider is discovered... how much does he make in a year?",
    prediction=["He has 3*4 trees. So he has 12*5=60 apples."],
)
rg.log(records=rec, name="my_dataset")
```

![text2text_record](../../_static/reference/webapp/features-text2text_record.png)
:::

::::



### Query datasets


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

![text2text_record](../../_static/reference/webapp/features-search.png)
:::

:::{tab-item} metadata and filters

Imagine you provided the split to which the record belongs to as metadata, that is `metadata={"split": "train"}` or `metadata={"split": "test"}`.
Then you could only search your training data by specifying the corresponding field in your query:

- `metadata.split:train`

Just like the metadata, you can also use the filter fields in you query.
A few examples to emulate the filters in the query string are:

- `status:Validated`
- `annotated_as:HAM`
- `predicted_by:Model A`

Ranges can be specified for date, numeric or string fields.
Inclusive ranges are specified with square brackets and exclusive ranges with curly brackets:

- `score:[0.5 TO 0.6]`
- `score:{0.9 TO *}`
- `event_timestamp:[1984-01-01T01:01:01.000000 TO *]`
- `last_updated:{* TO 1984-01-01T01:01:01.000000}`

![text2text_record](../../_static/reference/webapp/features-search.png)
:::

:::{tab-item} operators

You can combine an arbitrary amount of terms and fields in your search using the familiar boolean operators `AND`, `OR` and `NOT`.
Following examples showcase the power of these operators:

- `text:(quick AND fox)`: Returns records that contain the word *quick* and *fox*. The `AND` operator is the default operator, so `text:(quick fox)` is equivalent.
- `text:(quick OR brown)`: Returns records that contain either the word *quick* or *brown*.
- `text:(quick AND fox AND NOT news)`: Returns records that contain the words *quick* and *fox*, **and do not** contain *news*.
- `metadata.split:train AND text:fox`: Returns records that contain the word *fox* and that have a metadata *"split: train"*.
- `NOT _exists_:metadata.split` : Returns records that don't have a metadata *split*.

![text2text_record](../../_static/reference/webapp/features-search.png)
:::

:::{tab-item} regex

Regular expression patterns can be embedded in the query string by wrapping them in forward slashes "/":

- `text:/joh?n(ath[oa]n)/`: Matches *jonathon*, *jonathan*, *johnathon*, and *johnathan*.

The supported regular expression syntax is explained on the official [Elasticsearch documentation](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/regexp-syntax.html).

![text2text_record](../../_static/reference/webapp/features-search.png)
:::

:::{tab-item} fuzzy

You can search for terms that are similar to, but not exactly like the search terms, using the *fuzzy* operator.
This is useful to cover human misspellings:

- `text:quikc~`: Matches quick and quikc.

![text2text_record](../../_static/reference/webapp/features-search.png)
:::

:::{tab-item} wildcards

Wildcard searches can be run on individual search terms, using `?` to replace a single character, and `*` to replace zero or more characters:

- `text:(qu?ck bro*)`
- `text.exact:"Lazy Dog*"`: Matches, for example, *"Lazy Dog"*, *"Lazy Dog."*, or *"Lazy Dogs"*.
- `inputs.\*:news`: Searches all input fields for the word *news*.

![text2text_record](../../_static/reference/webapp/features-search.png)
:::

::::



### Semantic search

```python
import argilla as rg

record = rg.TextClassificationRecord(
    text="Hello world, I am a vector record!",
    vectors= {"my_vector_name": [0, 42, 1984]}
)
rg.log(name="dataset", records=record)
rg.load(name="dataset", vector=("my_vector_name", [0, 43, 1985]))
```

<a href="https://docs.argilla.io/en/latest/guides/label_records_with_semanticsearch.html"><img src="https://docs.argilla.io/en/latest/_images/features-similaritysearch.png" width="100%"></a>

### Weak supervision

```python
from argilla.labeling.text_classification import add_rules, Rule

rule = Rule(query="positive impact", label="optimism")
add_rules(dataset="go_emotion", rules=[rule])
```

<a href="https://docs.argilla.io/en/latest/guides/programmatic_labeling_with_rules.html"><img src="https://docs.argilla.io/en/latest/_images/features-weak-labelling.png" width="100%"></a>

### Train Models


```python
from argilla.training import ArgillaTrainer

trainer = ArgillaTrainer(name="news", workspace="recognai", framework="setfit")
trainer.train()
```

<a href="https://argilla.io/blog/introducing-argilla-trainer"><img src="https://argilla.io/blog/introducing-argilla-trainer/train.png" width="100%"></a>


## 📏 Principles
-  **Open**: Argilla is free, open-source, and 100% compatible with major NLP libraries (Hugging Face transformers, spaCy, Stanford Stanza, Flair, etc.). In fact, you can **use and combine your preferred libraries** without implementing any specific interface.



-  **End-to-end**: Most annotation tools treat data collection as a one-off activity at the beginning of each project. In real-world projects, data collection is a key activity of the iterative process of ML model development. Once a model goes into production, you want to monitor and analyze its predictions and collect more data to improve your model over time. Argilla is designed to close this gap, enabling you to **iterate as much as you need**.



-  **User and Developer Experience**: The key to sustainable NLP solutions are to make it easier for everyone to contribute to projects. _Domain experts_ should feel comfortable interpreting and annotating data. _Data scientists_ should feel free to experiment and iterate. _Engineers_ should feel in control of data pipelines. Argilla optimizes the experience for these core users to **make your teams more productive**.



-  **Beyond hand-labeling**: Classical hand-labeling workflows are costly and inefficient, but having humans in the loop is essential. Easily combine hand-labeling with active learning, bulk-labeling, zero-shot models, and weak supervision in **novel** data annotation workflows**.

## 🫱🏾‍🫲🏼 Contribute

We love contributors and have launched a [collaboration with JustDiggit](https://argilla.io/blog/introducing-argilla-community-growers) to hand out our very own bunds and help the re-greening of sub-Saharan Africa. To help our community with the creation of contributions, we have created our [developer](https://docs.argilla.io/en/latest/community/developer_docs.html) and [contributor](https://docs.argilla.io/en/latest/community/contributing.html) docs. Additionally, you can always [schedule a meeting](https://calendly.com/argilla-office-hours/meeting-with-david-from-argilla-30m) with our Developer Advocacy team so they can get you up to speed.

## 🥇 Contributors
<a  href="https://github.com/argilla-io/argilla/graphs/contributors">

<img  src="https://contrib.rocks/image?repo=argilla-io/argilla" />

</a>


```{include} /_common/next_steps.md
```
