# 🤔 Work with suggestions and responses

## Feedback Dataset

```{include} /_common/feedback_dataset.md
```

![workflow](/_static/tutorials/end2end/base/workflow_suggestions_and_responses.svg)

Unlike metadata and vectors, `suggestions` and `responses` are not defined as part of the `FeedbackDataset` schema. Instead, they are added to the records as you create them.

### Format `suggestions`

Suggestions refer to suggested responses (e.g. model predictions) that you can add to your records to make the annotation process faster. These can be added during the creation of the record or at a later stage. Only one suggestion can be provided for each question, and suggestion values must be compliant with the pre-defined questions e.g. if we have a `RatingQuestion` between 1 and 5, the suggestion should have a valid value within that range.

::::{tab-set}

:::{tab-item} Label

```python
record = rg.FeedbackRecord(
    fields=...,
    suggestions = [
        {
            "question_name": "relevant",
            "value": "YES",
            "score": 0.7,
            "agent": model_name,
        }
    ]
)
```

:::

:::{tab-item} Multi-label

```python
record = rg.FeedbackRecord(
    fields=...,
    suggestions = [
        {
            "question_name": "content_class",
            "value": ["hate", "violent"],
            "score": [0.3, 0.2],
            "agent": model_name,
        }
    ]
)
```

:::

:::{tab-item} Ranking

```python
record = rg.FeedbackRecord(
    fields=...,
    suggestions = [
        {
            "question_name": "preference",
            "value":[
                {"rank": 1, "value": "reply-2"},
                {"rank": 2, "value": "reply-1"},
                {"rank": 3, "value": "reply-3"},
            ],
            "score": [0.20, 0.10, 0.01],
            "agent": model_name,
        }
    ]
)
```

:::

:::{tab-item} Rating

```python
record = rg.FeedbackRecord(
    fields=...,
    suggestions = [
        {
            "question_name": "quality",
            "value": 5,
            "score": 0.7,
            "agent": model_name,
        }
    ]
)
```

:::

:::{tab-item} Span

```python
from argilla.client.feedback.schemas import SpanValueSchema

record = rg.FeedbackRecord(
    fields=...,
    suggestions = [
        {
            "question_name": "entities",
            "value": [
                SpanValueSchema(
                    start=0, # position of the first character of the span
                    end=10, # position of the character right after the end of the span
                    label="ORG",
                    score=1.0
                )
            ],
            "agent": model_name,
        }
    ]
)
```

:::

:::{tab-item} Text

```python
record = rg.FeedbackRecord(
    fields=...,
    suggestions = [
        {
            "question_name": "corrected-text",
            "value": "This is a *suggestion*.",
            "score": 0.7,
            "agent": model_name,
        }
    ]
)
```

:::

::::

#### Add `suggestions`

To add suggestions to the records, it slightly depends on whether you are using a `FeedbackDataset` or a `RemoteFeedbackDataset`. For an end-to-end example, check our [tutorial on adding suggestions and responses](/tutorials_and_integrations/tutorials/feedback/end2end_examples/add-suggestions-and-responses-005.ipynb).

```{note}
The dataset not yet pushed to Argilla or pulled from HuggingFace Hub is an instance of `FeedbackDataset` whereas the dataset pulled from Argilla is an instance of `RemoteFeedbackDataset`. The difference between the two is that the former is a local one and the changes made on it stay locally. On the other hand, the latter is a remote one and the changes made on it are directly reflected on the dataset on the Argilla server, which can make your process faster.
```

::::{tab-set}

:::{tab-item} Local dataset

```python
for record in dataset.records:
    record.suggestions = [
        {
            "question_name": "relevant",
            "value": "YES",
            "agent": model_name,
        }
    ]
```

:::

:::{tab-item} Remote dataset

```python
modified_records = []
for record in dataset.records:
    record.suggestions = [
        {
            "question_name": "relevant",
            "value": "YES",
            "agent": model_name,
        }
    ]
    modified_records.append(record)
dataset.update_records(modified_records)
```

:::

::::

```{note}
You can also follow the same strategy to modify existing suggestions.
```

### Format `responses`

If your dataset includes some annotations, you can add those to the records as you create them. Make sure that the responses adhere to the same format as Argilla's output and meet the schema requirements for the specific type of question being answered. Also make sure to include the `user_id` in case you're planning to add more than one response for the same question. You can only specify one response with an empty `user_id`: the first occurrence of `user_id=None` will be set to the active `user_id`, while the rest of the responses with `user_id=None` will be discarded.

::::{tab-set}

:::{tab-item} Label

```python
record = rg.FeedbackRecord(
    fields=...,
    responses = [
        {
            "values":{
                "relevant":{
                    "value": "YES"
                }
            }
        }
    ]
)
```

:::

:::{tab-item} Multi-label

```python
record = rg.FeedbackRecord(
    fields=...,
    responses = [
        {
            "values":{
                "content_class":{
                    "value": ["hate", "violent"]
                }
            }
        }
    ]
)
```

:::

:::{tab-item} Ranking

```python
record = rg.FeedbackRecord(
    fields=...,
    responses = [
        {
            "values":{
                "preference":{
                    "value":[
                        {"rank": 1, "value": "reply-2"},
                        {"rank": 2, "value": "reply-1"},
                        {"rank": 3, "value": "reply-3"},
                    ],
                }
            }
        }
    ]
)
```

:::

:::{tab-item} Rating

```python
record = rg.FeedbackRecord(
    fields=...,
    responses = [
        {
            "values":{
                "quality":{
                    "value": 5
                }
            }
        }
    ]
)
```

:::

:::{tab-item} Span

```python
from argilla.client.feedback.schemas import SpanValueSchema

record = rg.FeedbackRecord(
    fields=...,
    responses = [
        {
            "values":{
                "entities":{
                    "value": [
                        SpanValueSchema(
                            start=0,
                            end=10,
                            label="ORG"
                        )
                    ]
                }
            }
        }
    ]
)
```

:::

:::{tab-item} Text

```python
record = rg.FeedbackRecord(
    fields=...,
    responses = [
        {
            "values":{
                "corrected-text":{
                    "value": "This is a *response*."
                }
            }
        }
    ]
)
```

:::

::::

#### Add `responses`

To add responses to the records, it slightly depends on whether you are using a `FeedbackDataset` or a `RemoteFeedbackDataset`. For an end-to-end example, check our [tutorial on adding suggestions and responses](/tutorials_and_integrations/tutorials/feedback/end2end_examples/add-suggestions-and-responses-005.ipynb).

```{note}
The dataset not yet pushed to Argilla or pulled from HuggingFace Hub is an instance of `FeedbackDataset` whereas the dataset pulled from Argilla is an instance of `RemoteFeedbackDataset`. The difference between the two is that the former is a local one and the changes made on it stay locally. On the other hand, the latter is a remote one and the changes made on it are directly reflected on the dataset on the Argilla server, which can make your process faster.
```

::::{tab-set}

:::{tab-item} Local dataset

```python
for record in dataset.records:
    record.responses = [
        {
            "values":{
                "label":{
                    "value": "YES",
                }
            }
        }
    ]
```

:::

:::{tab-item} Remote dataset

```python
from datetime import datetime

modified_records = []
for record in dataset.records:
    record.responses = [
        {
            "values":{
                "label":{
                    "value": "YES",
                }
            },
            "inserted_at": datetime.now(),
            "updated_at": datetime.now(),
        }
    ]
    modified_records.append(record)
dataset.update_records(modified_records)
```

:::

::::

```{note}
You can also follow the same strategy to modify existing responses.
```


## Other datasets

```{include} /_common/other_datasets.md
```

### Add `suggestions`

Suggestions refer to suggested responses (e.g. model predictions) that you can add to your records to make the annotation process faster. These can be added during the creation of the record or at a later stage. We allow for multiple suggestions per record.

::::{tab-set}

:::{tab-item} Text Classification

In this case, we expect a `List[Tuple[str, float]]` as the prediction, where the first element of the tuple is the label and the second the confidence score.

```python
import argilla as rg

rec = rg.TextClassificationRecord(
    text=...,
    prediction=[("label_1", 0.75), ("label_2", 0.25)],
)
```

![single_textclass_record](/_static/reference/webapp/features-single_textclass_record.png)
:::

:::{tab-item} Text Classification (multi-label)

In this case, we expect a `List[Tuple[str, float]]` as the prediction, where the second element of the tuple is the confidence score of the prediction. In the case of multi-label, the `multi_label` attribute of the record should be set to `True`.

```python
import argilla as rg

rec = rg.TextClassificationRecord(
    text=...,
    prediction=[("label_1", 0.75), ("label_2", 0.75)],
    multi_label=True
)
```

![multi_textclass_record](/_static/reference/webapp/features-multi_textclass_record.png)
:::

:::{tab-item} Token Classification

In this case, we expect a `List[Tuple[str, int, int, float]]` as the prediction, where the second and third elements of the tuple are the start and end indices of the token in the text.

```python
import argilla as rg

rec = rg.TokenClassificationRecord(
    text=...,
    tokens=...,
    prediction=[("label_1", 0, 7, 0.75), ("label_2", 26, 33, 0.8)],
)
```

![tokclass_record](/_static/reference/webapp/features-tokclass_record.png)
:::

:::{tab-item} Text2Text

In this case, we expect a `List[str]` as the prediction.

```python
import argilla as rg

rec = rg.Text2TextRecord(
    text=...,
    prediction=["He has 3*4 trees. So he has 12*5=60 apples."],
)
```

![text2text_record](/_static/reference/webapp/features-text2text_record.png)
:::

::::

### Add `responses`

If your dataset includes some annotations, you can add those to the records as you create them. Make sure that the responses adhere to the same format as Argilla’s output and meet the schema requirements.

::::{tab-set}

:::{tab-item} Text Classification

In this case, we expect a `str` as the annotation.

```python
import argilla as rg

rec = rg.TextClassificationRecord(
    text=...,
    annotation="label_1",
)
```

![single_textclass_record](/_static/reference/webapp/features-single_textclass_record.png)

:::

:::{tab-item} Text Classification (multi-label)

In this case, we expect a `List[str]` as the annotation. In case of multi-label, the `multi_label` attribute of the record should be set to `True`.

```python
import argilla as rg

rec = rg.TextClassificationRecord(
    text=...,
    annotation=["label_1", "label_2"],
    multi_label=True
)
```

![multi_textclass_record](/_static/reference/webapp/features-multi_textclass_record.png)

:::

:::{tab-item} Token Classification

In this case, we expect a `List[Tuple[str, int, int]]` as the annotation, where the second and third elements of the tuple are the start and end indices of the token in the text.

```python
import argilla as rg

rec = rg.TokenClassificationRecord(
    text=...,
    tokens=...,
    annotation=[("label_1", 0, 7), ("label_2", 26, 33)],
)
```

![tokclass_record](/_static/reference/webapp/features-tokclass_record.png)

:::

:::{tab-item} Text2Text

In this case, we expect a `str` as the annotation.

```python
import argilla as rg

rec = rg.Text2TextRecord(
    text=...,
    annotation="He has 3*4 trees. So he has 12*5=60 apples.",
)
```

![text2text_record](/_static/reference/webapp/features-text2text_record.png)

:::

::::