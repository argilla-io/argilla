# 📊 Collect responses and metrics

## Feedback Dataset

```{include} /_common/feedback_dataset.md
```

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

![Plot 1: Submitted responses per record](/_static/images/llms/collect_responses_plot_1.png)

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

![Plot 2: Distance in annotator responses for the rating question](/_static/images/llms/collect_responses_plot_2.png)


```{hint}
If you feel that the disagreement between annotators is too high, especially for questions that aren't as subjective, this is a good sign that you should review your annotation guidelines and/or the questions and options.
```

### Unifying Disagreements

In this section, we explore some techniques you can use to solve disagreements in the responses. These are not the only possible techniques and you should choose them carefully according to the needs of your project and annotation team. Even though there are many ways in which you can unify responses, we offer support for some of them out-of-the-box.

#### Code

You can unify responses by using a `FeedbackDataset` in combination with a `QuestionStrategy`.

```{include} /_common/tabs/unfication_strategies.md
```

Once you have unified your responses, you will have a dataset that's ready for [fine-tuning](fine_tune.md). Remember to save your unified dataset following one of the methods explained in [Export a Feedback Dataset](export_dataset.md).

#### Strategies

##### For labels: `LabelQuestion` and `MultiLabelQuestion`

* *Majority vote (single-label questions)*: Labels can be aggregated using the most popular option, for which you will need to have at least 3 submitted responses. In the case of a tie, you can break it by choosing a random option.
* *Majority vote (multi-label questions)*: If you are aggregating labels from a multi-label question, it would be more correct to calculate the majority vote per label. That means that for each label you need to check whether the majority of the annotators selected that specific label or not.
* *Weighted majority vote*: You may decide to give some of your annotators more weight than others when aggregating labels so that their decisions count more than others. Some reasons to consider a weighted majority might be: because some annotators tend to have better agreement with ground truth annotations, they are experts or they represent the demographic target for specific questions. If you want to choose this option, first calculate a score from 0 to 1 for each annotator, then apply these weights to their responses. Finally, sum all the values and choose the option with the highest score.
* *Train with disagreements*: If your labels are meant to solve highly subjective tasks, like sentiment analysis or abusive language detection, you may want to consider other options that preserve the natural disagreement between annotators during training. This is especially helpful to avoid diluting the feedback of minorities within your annotation team. If you want to learn more about this approach, we recommend checking the different methods discussed in [Davani et al. (2021)](https://arxiv.org/pdf/2110.05719.pdf).

##### For numerical values: `RankingQuestion` and `RatingQuestion`

* *Majority vote*: If a record has more than 2 submitted responses, you can take the most popular value (for `RankingQuestion`s the most popular rank, for `RatingQuestion`s the most popular rating) as the final score. In the case of a tie, you can break it by choosing a random option or the lowest / highest score.
* *Weighted majority vote*: As explained [above](#for-labels-labelquestion-and-multilabelquestion), you may want to weigh the responses of different annotators. In that case, calculate a score from 0 to 1 for each annotator, then apply these weights to their responses. Finally, sum all the values and choose the option with the highest score.
* *Mean score*: For this technique, you can take all responses and calculate the mean score.
* *Lowest / highest score*: Depending on how the question is formulated, you can take the `max` or `min` value.

##### For texts: `TextQuestion`

* *Rate / rank the responses*: Make a new dataset that includes the texts you have collected in the record fields and ask your annotation team to rate or rank the responses. Then choose the response with the highest score. If there is a tie, choose one of the options randomly or consider duplicating the record as explained below.
* *Choose based on the annotator*: Take a subset of the records (enough to get a good representation of responses from each annotator), and rate / rank them as explained in the section above. Then, give each annotator a score based on the preferences of the team. You can use this score to choose text responses over the whole dataset.
* *Choose based on answers to other questions*: You can use the answers to other questions as quality markers. For example, you can assume that whoever gave the lowest score will make a more extensive correction and you may want to choose that as the final text. However, this method does not guarantee that the text will be of good quality.
* *Duplicate the record*: You may consider that the different answers given by your annotation team are all valid options. In this case, you can duplicate the record to keep each answer. Again, this method does not guarantee the quality of the text, so it is recommended to check the quality of the text, for example using a rating question.


### Annotation metrics

There are multiple ways to analyse the annotations on a dataset. In this section we present two different approaches, from the point of view of the annotators, to see how reliable their responses are, or from the point of view of a single annotator, to see whether the suggestions simplify their annotation task.

```{note}
The following metrics only apply to the `FeedbackDataset`.
```

#### Annotator Agreement metrics

After we gather responses for a dataset from a team of annotators, we may want to analyse their agreement level to see how reliable are the final responses after the unification (this module covers what it's also named inter-coder reliability measures).

```python
import argilla as rg
from argilla.client.feedback.metrics import AgreementMetric

feedback_dataset = rg.FeedbackDataset.from_argilla("...", workspace="...")
metric = AgreementMetric(dataset=feedback_dataset, question_name="question_name")
agreement_metrics = metric.compute("alpha")
# >>> agreement_metrics
# [AgreementMetricResult(metric_name='alpha', count=3, result=0.0)]
```

We will obtain a container that stores the `metric_name`, the `result`, and the number of records used to compute the given metric (`count`).

The metrics can also be computed from the `FeedbackDataset`:

```python
import argilla as rg

dataset = rg.FeedbackDataset.from_huggingface("argilla/go_emotions_raw")

agreement_metrics = dataset.compute_agreement_metrics(question_name="label", metric_names="alpha")
agreement_metrics
# AgreementMetricResult(metric_name='alpha', count=191792, result=0.0)
```

Currently only [Krippendorf's alpha](https://en.wikipedia.org/wiki/Krippendorff%27s_alpha) is defined, for all question types except the `TextQuestion`. This metric can be computed for any number of annotators, even if some of the responses are not submitted.
The value from this measure is in the range [0,1] and is usually interpreted in the following way: alpha >= 0.8 indicates a reliable annotation, alpha >= 0.667 allows making tentative conclusions, while the lower values suggest unreliable annotation.

```{note}
In case you want to dig deeper into the measurement of the agreement between different annotators, take a look at [*Implementations of inter-annotator agreement coefficients surveyed by Artstein
and Poesio (2007), Inter-Coder Agreement for Computational Linguistics*](https://www.researchgate.net/publication/200044186_Inter-Coder_Agreement_for_Computational_Linguistics).
```

##### Supported metrics

We plan on adding more support for other metrics so feel free to reach out on our Slack or GitHub to help us prioritize each task.

| Question type/Metric  | alpha  |
|:----------------------|:-------|
| LabelQuestion         | ✔️      |
| MultiLabelQuestion    | ✔️      |
| RatingQuestion        | ✔️      |
| RankingQuestion       | ✔️      |
| TextQuestion          |        |


#### Annotator metrics

In contrast to the agreement metrics, annotator metrics are the metrics computed by comparing the responses given by an annotator, against model predictions. As `FeedbackDataset` already offers the possibility to add `suggestions` to the responses, we can use the annotator metrics to compare the responses against the suggestions. This will give us two important insights: how reliable are the responses of a given annotator, and how good are the suggestions we are giving to the annotators. This way, we can take actions to improve the quality of the responses by making changes to the guidelines or the structure, and the suggestions given to the annotators by changing or updating the model we use. Note that each question type has a different set of metrics available.

The following snippet shows an example of use:

```python
import argilla as rg
from argilla.client.feedback.metrics import ResponsesMetric

feedback_dataset = rg.FeedbackDataset.from_argilla("...", workspace="...")
metric = ResponsesMetric(dataset=feedback_dataset, question_name="question_name")
annotator_metrics = metric.compute("accuracy")
# >>> annotator_metrics
# {'00000000-0000-0000-0000-000000000001': [AnnotatorMetricResult(metric_name='accuracy', count=3, result=0.5)], '00000000-0000-0000-0000-000000000002': [AnnotatorMetricResult(metric_name='accuracy', count=3, result=0.25)], '00000000-0000-0000-0000-000000000003': [AnnotatorMetricResult(metric_name='accuracy', count=3, result=0.5)]}
```

We would obtain a `dict` where the keys contain the `user_id` of a given annotator and a list with the metrics requested. For the interpretation of these metrics, we assume here that the *true* labels or responses correspond to the points given by an annotator, and the *predictions* correspond to the suggestions given to a user. This way we can analyse whether we are offering good suggestions to a given annotator, and therefore simplifying their work (shortening the annotation task), or otherwise we should change the suggestions given (or fine-tune our model if we can do it).

If instead of taking the `responses` as the reference for the true labels, we want to assume the suggestions are our reference labels, we can use the equivalent corresponding class, that works just the same way:

```python
import argilla as rg
from argilla.client.feedback.metrics import SuggestionsMetric

feedback_dataset = rg.FeedbackDataset.from_argilla("...", workspace="...")
metric = SuggestionsMetric(dataset=feedback_dataset, question_name="question_name")
annotator_metrics = metric.compute("accuracy")
# >>> annotator_metrics
# {'00000000-0000-0000-0000-000000000001': [AnnotatorMetricResult(metric_name='accuracy', count=3, result=0.5)], '00000000-0000-0000-0000-000000000002': [AnnotatorMetricResult(metric_name='accuracy', count=3, result=0.25)], '00000000-0000-0000-0000-000000000003': [AnnotatorMetricResult(metric_name='accuracy', count=3, result=0.5)]}
```

We can compute the metrics directly from our feedback dataset. Let's use the following dataset for this, and compute the metrics for the responses:

```python
# Compute the metrics per annotator, assuming the true labels correspond to the responses, and the predicted labels are the suggestions
responses_metrics = dataset.compute_responses_metrics(question_name="label", metric_names=["accuracy", "precision", "recall", "f1-score"])
responses_metrics['00000000-0000-0000-0000-000000000001']
# [AnnotatorMetricResult(metric_name='accuracy', count=1269, result=0.43341213553979513),
#  AnnotatorMetricResult(metric_name='precision', count=1269, result=0.6166023130799764),
#  AnnotatorMetricResult(metric_name='recall', count=1269, result=0.5593881715337764),
#  AnnotatorMetricResult(metric_name='f1-score', count=1269, result=0.5448304082545485)]
```

and using the suggestions as the reference true labels vs the responses:

```python
suggestions_metrics = dataset.compute_suggestions_metrics(question_name="label", metric_names=["accuracy", "precision", "recall", "f1-score"])
suggestions_metrics['00000000-0000-0000-0000-000000000001']
# [AnnotatorMetricResult(metric_name='accuracy', count=1269, result=0.43341213553979513),
#  AnnotatorMetricResult(metric_name='precision', count=1269, result=0.5593881715337764),
#  AnnotatorMetricResult(metric_name='recall', count=1269, result=0.6166023130799764),
#  AnnotatorMetricResult(metric_name='f1-score', count=1269, result=0.5448304082545485)]
```

Keep in mind this dataset is quite big, and it may take some time both to download and compute the metrics. You can check it here: [argilla/go_emotions_raw](https://huggingface.co/datasets/argilla/go_emotions_raw).


##### Supported metrics

We plan on adding more support for other metrics so feel free to reach out on our Slack or GitHub to help us prioritize each task.

| Metric/Question type  | LabelQuestion  | MultiLabelQuestion | RatingQuestion | RankingQuestion | TextQuestion |
|:----------------------|:---------------|:-------------------|:---------------|:----------------|:-------------|
| accuracy              | ✔️              | ✔️                  | ✔️              |                 |              |
| precision             | ✔️              | ✔️                  | ✔️              |                 |              |
| recall                | ✔️              | ✔️                  | ✔️              |                 |              |
| f1-score              | ✔️              | ✔️                  | ✔️              |                 |              |
| confusion-matrix      | ✔️              | ✔️                  | ✔️              |                 |              |
| pearson-r             | ✔️              |                    |                |                 |              |
| spearman-r            |                |                    | ✔️              |                 |              |
| gleu                  |                |                    |                |                 | ✔️            |
| rouge                 |                |                    |                |                 | ✔️            |
| ndcg-score            |                |                    |                | ✔️               |              |


#### Unified annotation metrics

This section covers the metrics for unified annotations. After we have unified our responses we can analyse the annotations (unified responses) against the suggestions (or the other way around), to gather a different perspective from the final dataset prepared for training.

The following snippet shows an example of use where we use as true labels the responses:

```python
import argilla as rg
from argilla.client.feedback.metrics import UnifiedResponsesMetric

feedback_dataset = rg.FeedbackDataset.from_argilla("...", workspace="...")
strategy_name = "majority"
unified_dataset = feedback_dataset.compute_unified_responses(question, strategy_name)
metric = UnifiedResponsesMetric(dataset=unified_dataset, question_name="question_name")
unified_metrics = metric.compute("accuracy")
# >>> unified_metrics
# AnnotatorMetricResult(metric_name='accuracy', count=3, result=0.25)
```

And the same but assuming our true labels are the suggestions:

```python
import argilla as rg
from argilla.client.feedback.metrics import UnifiedSuggestionsMetric

feedback_dataset = rg.FeedbackDataset.from_argilla("...", workspace="...")
strategy_name = "majority"
unified_dataset = feedback_dataset.compute_unified_responses(question, strategy_name)
metric = UnifiedSuggestionsMetric(dataset=unified_dataset, question_name="question_name")
unified_metrics = metric.compute("accuracy")
# >>> unified_metrics
# AnnotatorMetricResult(metric_name='accuracy', count=3, result=0.25)
```

We obtain the same container for the metrics result, but in this case, it's not associated with any annotator. The same interpretation that we saw for the Annotator metrics holds here regarding the labels and suggestions.

Once again we can make use of the same methods we saw for the annotator metrics directly from the `FeedbackDataset`, but note the use of the strategy argument used here:

```python
responses_metrics_unified = dataset.compute_responses_metrics(question_name="label", metric_names=["accuracy", "precision", "recall", "f1-score"], strategy="majority")
responses_metrics_unified
# [AnnotatorMetricResult(metric_name='accuracy', count=53990, result=0.8057232820892758),
#  AnnotatorMetricResult(metric_name='precision', count=53990, result=0.7700497205894691),
#  AnnotatorMetricResult(metric_name='recall', count=53990, result=0.8051097334033145),
#  AnnotatorMetricResult(metric_name='f1-score', count=53990, result=0.7855678821135942)]

suggestions_metrics_unified = dataset.compute_suggestions_metrics(question_name="label", metric_names=["accuracy", "precision", "recall", "f1-score"], strategy="majority")
suggestions_metrics_unified
# [AnnotatorMetricResult(metric_name='accuracy', count=53990, result=0.8048342285608446),
#  AnnotatorMetricResult(metric_name='precision', count=53990, result=0.8085185809086417),
#  AnnotatorMetricResult(metric_name='recall', count=53990, result=0.7679974812646655),
#  AnnotatorMetricResult(metric_name='f1-score', count=53990, result=0.786466989240015)]
```

By default, the responses will not be unified and we will have the responses at the annotator level, but if we ask for a specific strategy (see the strategies available for each question), they will be unified automatically and computed.

##### Supported metrics

We plan on adding more support for other metrics so feel free to reach out on our Slack or GitHub to help us prioritize each task.

| Metric/Question type  | LabelQuestion  | MultiLabelQuestion | RatingQuestion | RankingQuestion | TextQuestion |
|:----------------------|:---------------|:-------------------|:---------------|:----------------|:-------------|
| accuracy              | ✔️              | ✔️                  | ✔️              |                 |              |
| precision             | ✔️              | ✔️                  | ✔️              |                 |              |
| recall                | ✔️              | ✔️                  | ✔️              |                 |              |
| f1-score              | ✔️              | ✔️                  | ✔️              |                 |              |
| confusion-matrix      | ✔️              | ✔️                  | ✔️              |                 |              |
| pearson-r             | ✔️              |                    |                |                 |              |
| spearman-r            |                |                    | ✔️              |                 |              |
| gleu                  |                |                    |                |                 | ✔️            |
| rouge                 |                |                    |                |                 | ✔️            |
| ndcg-score            |                |                    |                | ✔️               |              |


## Other datasets

```{include} /_common/other_datasets.md
```

This guide gives you a brief introduction to Argilla Metrics. Argilla Metrics enables you to perform fine-grained analyses of your models and training datasets. Argilla Metrics are inspired by a number of seminal works such as [Explainaboard](https://explainaboard.inspiredco.ai/).

The main goal is to make it easier to build more robust models and training data, going beyond single-number metrics (e.g., F1).

This guide gives a brief overview of currently supported metrics. For the full API documentation see the [Python API reference](/reference/python/python_metrics.rst).

All Python metrics are covered in:

```python
from argilla import metrics
```

```{note}
This feature is experimental, you can expect some changes in the Python API. Please report any issue you encounter on Github.
````

```{note}
Verify you have already installed Jupyter Widgets in order to properly visualize the plots. See https://ipywidgets.readthedocs.io/en/latest/user_install.html
````

To run this guide, you need to install the following dependencies:

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
![Token length plot](/_static/images/guides/metrics/token_length_plot.png)

```python
from argilla.metrics.token_classification import token_capitalness

token_capitalness(name="spacy_sm_wnut17").visualize()
```

![Capitalness plot](/_static/images/guides/metrics/capitalness_plot.png)

```python
from argilla.metrics.token_classification import token_frequency

token_frequency(name="spacy_sm_wnut17", tokens=50).visualize()
```

![Token frequency plot](/_static/images/guides/metrics/token_frequency.png)

```python
from argilla.metrics.token_classification.metrics import top_k_mentions

top_k_mentions(name="spacy_sm_wnut17", k=5000, threshold=2).visualize()
```

![Top-k mentions plot](/_static/images/guides/metrics/top_k_plot.png)

```python
from argilla.metrics.token_classification import entity_labels

entity_labels(name="spacy_sm_wnut17").visualize()
```

![Predicted entities distribution](/_static/images/guides/metrics/entity_labels.png)

```python
from argilla.metrics.token_classification import entity_density

entity_density(name="spacy_sm_wnut17").visualize()
```
![Entity density](/_static/images/guides/metrics/entity_density.png)

```python
from argilla.metrics.token_classification import entity_capitalness

entity_capitalness(name="spacy_sm_wnut17").visualize()
```

![Entity capitalness](/_static/images/guides/metrics/entity_capitalness.png)

```python
from argilla.metrics.token_classification import mention_length

mention_length(name="spacy_sm_wnut17").visualize()
```
![Mention length](/_static/images/guides/metrics/mention_length.png)

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

![Top-k annotated entities](/_static/images/guides/metrics/top_k_annotated_entities.png)

From the above, we see we can quickly detect an annotation issue: double quotes `"` are most of the time tagged as `O` (no entity) but in some cases (~60 examples) are tagged as the beginning of entities like ORG or MISC, which is likely a hand-labeling error, including the quotes inside the entity span.

```python
from argilla.metrics.token_classification import *

entity_density(name="conll2002_es", compute_for=Annotations).visualize()
```

![Entity density in Conll2002 dataset](/_static/images/guides/metrics/entity_density_conll2002.png)

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

![F1 metrics](/_static/images/guides/metrics/f1.png)

```python
# now compute metrics for negation ( -> negative precision and positive recall go down)
f1(name="sst2", query="n't OR not").visualize()
```
![F1 metrics from query](/_static/images/guides/metrics/negation_f1.png)