# 📊 Collect responses and metrics

## Feedback Dataset

To collect the responses given by annotators via Python, you can simply load the dataset from Argilla as follows:

```python
import argilla as rg

rg.init(
    api_url="...",
    api_key="...",
)

feedback = rg.FeedbackDataset.from_argilla("demo_feedback", workspace="recognai")
```

Each record in `feedback.records` will have an attribute `responses` where you will find a list with all the responses to that record, if any. Each response will have the following attributes:

- `user_id`: contains the Argilla user ID of the annotator
- `values`: contains the responses given by the annotator in the shape of a dictionary, where the key is the name of the question and the value is another dictionary where you can find the answer to the question under the key `value`.
- `status`: contains the status of the response i.e., whether it is `submitted`, or `discarded`.


If your dataset doesn't have any annotation overlap i.e., all records have at most one response, the post-processing stage will be quite simple since you won't need to decide which annotations to keep and which to discard.

```{note}
Remember to only take into account responses with the `submitted` status.
```

### Measure disagreements

If your dataset does have records with more than one `submitted` response, you will need to unify the responses before using the data for training.

Ratings often represent a subjective value, meaning that there is no wrong or right answer to these questions. However, since a `RatingQuestion` has a closed set of options, their results can help with visualizing the disagreement between annotators. On the other hand, texts are unique and subjective, making it almost impossible that two annotators will give the same answer for a `TextQuestion`. For this reason, we don't recommend using these responses to measure disagreements.

If you want to do an initial exploration of the responses, you can use your preferred library for plotting data. Here are some simple examples of some visualizations that you could do to evaluate the potential disagreement between annotators:

```python
# plot 1: submitted responses per record
from collections import Counter, OrderedDict
import plotly.express as px

count_submitted = Counter()
for record in feedback.records:
    if record.responses:
        submitted = [r for r in record.responses if r.status == "submitted"]
        count_submitted[len(submitted)] += 1
count_submitted = OrderedDict(sorted(count_submitted.items()))
count_submitted = [{"submitted_responses": k, "no_records": v} for k, v in count_submitted.items()]

fig = px.bar(count_submitted, x="submitted_responses", y="no_records")
fig.update_xaxes(title_text="No. of submitted responses", dtick=1)
fig.update_yaxes(title_text="No. of records")
fig.show()
```

![Plot 1: Submitted responses per record](../../../_static/images/llms/collect_responses_plot_1.png)

```python
# plot 2: distance between responses in rating question
list_values = []
for record_ix,record in enumerate(feedback):
    if record.responses:
        submitted = [r for r in record.responses if r.status == "submitted"]
        if len(submitted) > 1:
            for response_ix, response in enumerate(submitted):
                list_values.append({"record": str(record_ix+1), "annotator": str(response_ix+1), "value": response.values["rating"].value})


fig = px.box(list_values, x="annotator", y="value", color="annotator", points="all", hover_data="record")
fig.update_yaxes(dtick=1)
fig.show()
```

![Plot 2: Distance in annotator responses for the rating question](../../../_static/images/llms/collect_responses_plot_2.png)


```{hint}
If you feel that the disagreement between annotators is too high, especially for questions that aren"t as subjective, this is a good sign that you should review your annotation guidelines and/or the questions and options.
```

### Unifying Disagreements

In this section, we explore some techniques you can use to solve disagreements in the responses. These are not the only possible techniques and you should choose them carefully according to the needs of your project and annotation team. Even though there are many ways in which you can unify responses, we offer support for some of them out-of-the box.

#### Code

You can unify responses by using a `FeedbackDataset` in combination with a `QuestionStrategy`.

```{include} /_common/tabs/unfication_strategies.md
```

Once you have unified your responses, you will have a dataset that's ready for [fine-tuning](fine_tune.ipynb). Remember to save your unified dataset following one of the methods explained in [Export a Feedback Dataset](export_dataset.ipynb).

#### Strategies

##### For labels: `LabelQuestion` and `MultiLabelQuestion`

* *Majority vote (single-label questions)*: Labels can be aggregated using the most popular option, for which you will need to have at least 3 submitted responses. In the case of a tie, you can break it by choosing a random option.
* *Majority vote (multi-label questions)*: If you are aggregating labels from a multi-label question, it would be more correct to calculate the majority vote per label. That means that for each label you need to check whether the majority of the annotators selected that specific label or not.
* *Weighted majority vote*: You may decide to give some of your annotators more weight than others when aggregating labels so that their decisions count more than others. Some reasons to consider a weighted majority might be: because some annotators tend to have better agreement with ground truth annotations, they are experts or they represent the demographic target for specific questions. If you want to choose this option, first calculate a score from 0 to 1 for each annotator, then apply these weights to their responses. Finally, sum all the values and choose the option with the highest score.
* *Train with disagreements*: If your labels are meant to solve highly subjective tasks, like sentiment analysis or abusive language detection, you may want to consider other options that preserve the natural disagreement between annotators during training. This is specially helpful to avoid diluting the feedback of minorities within your annotation team. If you want to learn more about this approach, we recommend checking the different methods discussed in [Davani et al. (2021)](https://arxiv.org/pdf/2110.05719.pdf).

##### For numerical values: `RankingQuestion` and `RatingQuestion`

* *Majority vote*: If a record has more than 2 submitted responses, you can take the most popular value (for `RankingQuestion`s the most popular rank, for `RatingQuestion`s the most popular rating) as the final score. In the case of a tie, you can break it by choosing a random option or the lowest / highest score.
* *Weighted majority vote*: As explained [above](#for-labels-labelquestion-and-multilabelquestion), you may want to weight the responses of different annotators. In that case, calculate a score from 0 to 1 for each annotator, then apply these weights to their responses. Finally, sum all the values and choose the option with the highest score.
* *Mean score*: For this technique, you can take all responses and calculate the mean score.
* *Lowest / highest score*: Depending on how the question is formulated, you can take the `max` or `min` value.

##### For texts: `TextQuestion`

* *Rate / rank the responses*: Make a new dataset that includes the texts you have collected in the record fields and ask your annotation team to rate or rank the responses. Then choose the response with the highest score. If there is a tie, choose one of the options randomly or consider duplicating the record as explained below.
* *Choose based on the annotator*: Take a subset of the records (enough to get a good representation of responses from each annotator), and rate / rank them as explained in the section above. Then, give each annotator a score based on the preferences of the team. You can use this score to choose text responses over the whole dataset.
* *Choose based on answers to other questions*: You can use the answers to other questions as quality markers. For example, you can assume that whoever gave the lowest score will make a more extensive correction and you may want to choose that as the final text. However, this method does not guarantee that the text will be of good quality.
* *Duplicate the record*: You may consider that the different answers given by your annotation team are all valid options. In this case, you can duplicate the record to keep each answer. Again, this method does not guarantee the quality of the text, so it is recommended to check the quality of the text, for example using a rating question.


## Other datasets

```{include} /_common/other_datasets.md
```

This guide gives you a brief introduction to Argilla Metrics. Argilla Metrics enable you to perform fine-grained analyses of your models and training datasets. Argilla Metrics are inspired by a a number of seminal works such as [Explainaboard](http://explainaboard.nlpedia.ai/).

The main goal is to make it easier to build more robust models and training data, going beyond single-number metrics (e.g., F1).

This guide gives a brief overview of currently supported metrics. For the full API documentation see the [Python API reference](../reference/python/python_metrics.rst).

All Python metrics are covered in:

```python
from argilla import metrics
```

.. note::
This feature is experimental, you can expect some changes in the Python API. Please report on Github any issue you encounter.

.. note:: Verify you have already installed Jupyter Widgets in order to properly visualize the plots. See https://ipywidgets.readthedocs.io/en/latest/user_install.html

For running this guide you need to install the following dependencies:

```python
%pip install datasets spacy plotly -qqq
```

and the spacy model:

```python
!python -m spacy download en_core_web_sm -qqq
```

### 1. NER prediction metrics

#### Load dataset and model

We'll be using spaCy for this guide, but all the metrics we'll see are computed for any other framework (Flair, Stanza, Hugging Face, etc.). As an example will use the WNUT17 NER dataset.

```python
import argilla as rg
import spacy
from datasets import load_dataset

nlp = spacy.load("en_core_web_sm")
dataset = load_dataset("wnut_17", split="train")
```

#### Log records in `dataset`

Let's log spaCy predictions using the built-in `rg.monitor` method:

```python
nlp = rg.monitor(nlp, dataset="spacy_sm_wnut17")

def predict(records):
    for _ in nlp.pipe([
        " ".join(record_tokens)
        for record_tokens in records["tokens"]
    ]):
        pass
    return {"predicted": [True]*len(records["tokens"])}

dataset.map(predict, batched=True, batch_size=512)
```

#### Explore pipeline metrics
```python
from argilla.metrics.token_classification import token_length

token_length(name="spacy_sm_wnut17").visualize()
```
![Token length plot](../_static/images/guides/metrics/token_length_plot.png)

```python
from argilla.metrics.token_classification import token_capitalness

token_capitalness(name="spacy_sm_wnut17").visualize()
```

![Capitalness plot](../_static/images/guides/metrics/capitalness_plot.png)

```python
from argilla.metrics.token_classification import token_frequency

token_frequency(name="spacy_sm_wnut17", tokens=50).visualize()
```

![Token frequency plot](../_static/images/guides/metrics/token_frequency.png)

```python
from argilla.metrics.token_classification.metrics import top_k_mentions

top_k_mentions(name="spacy_sm_wnut17", k=5000, threshold=2).visualize()
```

![Top-k mentions plot](../_static/images/guides/metrics/top_k_plot.png)

```python
from argilla.metrics.token_classification import entity_labels

entity_labels(name="spacy_sm_wnut17").visualize()
```

![Predicted entities distribution](../_static/images/guides/metrics/entity_labels.png)

```python
from argilla.metrics.token_classification import entity_density

entity_density(name="spacy_sm_wnut17").visualize()
```
![Entity density](../_static/images/guides/metrics/entity_density.png)

```python
from argilla.metrics.token_classification import entity_capitalness

entity_capitalness(name="spacy_sm_wnut17").visualize()
```

![Entity capitalness](../_static/images/guides/metrics/entity_capitalness.png)

```python
from argilla.metrics.token_classification import mention_length

mention_length(name="spacy_sm_wnut17").visualize()
```
![Mention length](../_static/images/guides/metrics/mention_length.png)

### 2. NER training metrics
#### Analyze tags

Let's analyze the conll2002 dataset at the tag level.

```python
dataset = load_dataset("conll2002", "es", split="train[0:5000]")
```
```python
def parse_entities(record):
    entities = []
    counter = 0
    for i in range(len(record["ner_tags"])):
        entity = (
            dataset.features["ner_tags"].feature.names[record["ner_tags"][i]],
            counter,
            counter + len(record["tokens"][i]),
        )
        entities.append(entity)
        counter += len(record["tokens"][i]) + 1
    return entities
```
```python
records = [
    rg.TokenClassificationRecord(
        text=" ".join(example["tokens"]),
        tokens=example["tokens"],
        annotation=parse_entities(example),
    )
    for example in dataset
]
```
```python
rg.log(records, "conll2002_es")
```
```python
from argilla.metrics.token_classification import top_k_mentions
from argilla.metrics.token_classification.metrics import Annotations

top_k_mentions(
    name="conll2002_es",
    k=30,
    threshold=4,
    compute_for=Annotations
).visualize()
```

![Top-k annotated entities](../_static/images/guides/metrics/top_k_annotated_entities.png)

From the above we see we can quickly detect an annotation issue: double quotes `"` are most of the time tagged as `O` (no entity) but in some cases (~60 examples) are tagged as beginning of entities like ORG or MISC, which is likely a hand-labeling error, including the quotes inside the entity span.

```python
from argilla.metrics.token_classification import *

entity_density(name="conll2002_es", compute_for=Annotations).visualize()
```

![Entity density in Conll2002 dataset](../_static/images/guides/metrics/entity_density_conll2002.png)

### 3. TextClassification metrics

```python
from datasets import load_dataset
from transformers import pipeline

import argilla as rg

sst2 = load_dataset("glue", "sst2", split="validation")
labels = sst2.features["label"].names
nlp = pipeline("sentiment-analysis")
```

```python
records = [
    rg.TextClassificationRecord(
        text=record["sentence"],
        annotation=labels[record["label"]],
        prediction=[
            (pred["label"].lower(), pred["score"]) for pred in nlp(record["sentence"])
        ],
    )
    for record in sst2
]
```

```python
rg.log(records, name="sst2")
```
```python
from argilla.metrics.text_classification import f1

f1(name="sst2").visualize()
```

![F1 metrics](../_static/images/guides/metrics/f1.png)

```python
# now compute metrics for negation ( -> negative precision and positive recall go down)
f1(name="sst2", query="n't OR not").visualize()
```
![F1 metrics from query](../_static/images/guides/metrics/negation_f1.png)