# Fine-tune other models

After [collecting the responses](./collect_responses.html) from our `FeedbackDataset` we can start fine-tuning our basic models. Due to the customizability of the `FeedbackDataset`, this might require setting up a custom post-processing workflow but we will provide some good toy examples for the text classification task. We will add additional support for other tasks in the future.

Generally, this is as easy as one-two-three but does slightly differ per task.

1. First, we define a unification strategy for responses to `questions` we want to use.
2. Next, we then define a task-mapping. This mapping defines which `fields` and `questions` we want to use from our dataset for the downstream training task. These mappings are then used for retrieving data from a dataset and initializing the training.
3. Lastly, we initialize the `ArgillaTrainer` and forward the task mapping, unification strategies and training framework.

## Text classification

### Background

Text classification is a widely used NLP task where labels are assigned to text. Major companies rely on it for various applications. Sentiment analysis, a popular form of text classification, assigns labels like 🙂 positive, 🙁 negative, or 😐 neutral to text. Additionally, we distinguish between single- and multi-label text classification.

#### Single-label

Single-label text classification refers to the task of assigning a single category or label to a given text sample. Each text is associated with only one predefined class or category. For example, in sentiment analysis, a single-label text classification task would involve assigning labels such as "positive," "negative," or "neutral" to individual texts based on their sentiment.

#### Multi-label

Multi-label text classification is generally more complex than single-label classification due to the challenge of determining and predicting multiple relevant labels for each text. It finds applications in various domains, including document tagging, topic labeling, and content recommendation systems.

### Training

Data for the training text classification using our `FeedbackDataset` is defined by following three easy steps.

1. We need to define a unification strategy `RatingStrategy`, a `LabelStrategy` or a `MultiLabelStrategy`.

2.  For this task, we assume we need a `text-label`-pair for defining a text classification task. We allow mapping for creating a `TrainingTask.for_text_classification` by mapping `*Field` to a `text`-value and allow for mapping a `RatingStrategy`, `LabelStrategy` or a `MultiLabelStrategy` to a `label`-value.

3.  We then define an `ArgillaTrainer` instance with support for "openai", "setfit", "peft", "spacy" and "transformers".


#### Unify responses

Argilla `*Question`s need to be [unified using a strategy](/guides/llms/practical_guides/collect_responses) and so do `RatingQuestions`s, `LabelQuestion`s and `MultiLabelQuestion`s. Therefore, records need to be unified by using a strategy, which takes one of the questions and one of their associated strategies. Luckily this is integrated within the `TrainingTask`-step underneath, but you can also do this individually as shown [here](/guides/llms/practical_guides/collect_responses).

````{note}
A brief shortcut that `RatingQuestion`s can be unified using a "majority"-, "min"-, "max"- or "disagreement"-strategy. Both `LabelQuestion`s and `MultiLabelQuestion`s can be resolved using a "majority"-, or "disagreement"-strategy.
````

#### Define a task

##### `text-label`-pair

We offer the option to use default unification strategies and formatting based on a `text-label`-pair. Here we infer formatting information based on `*Field` and `*Question` names from the dataset. This is the easiest way to define a `TrainingTask` for text classification.

::::{tab-set}

:::{tab-item} RatingQuestion
```python
from argilla.feedback import FeedbackDataset, TrainingTask

dataset = FeedbackDataset.from_huggingface(
    repo_id="argilla/stackoverflow_feedback_demo"
)
task = TrainingTask.for_text_classification(
    text=dataset.field_by_name("title"),
    label=dataset.question_by_name("answer_quality"), # RatingQuestion
    label_strategy=None # default to "majority", or use "min", "max", "disagreement"
)
```
:::

:::{tab-item} LabelQuestion
```python
from argilla.feedback import FeedbackDataset, TrainingTask

dataset = FeedbackDataset.from_huggingface(
    repo_id="argilla/stackoverflow_feedback_demo"
)
task = TrainingTask.for_text_classification(
    text=dataset.field_by_name("title"),
    label=dataset.question_by_name("title_question_fit"), # LabelQuestion
    label_strategy=None # default to "majority", or use "disagreement"
)
```
:::

:::{tab-item} MultiLabelQuestion
```python
from argilla.feedback import FeedbackDataset, TrainingTask

dataset = FeedbackDataset.from_huggingface(
    repo_id="argilla/stackoverflow_feedback_demo"
)
task = TrainingTask.for_text_classification(
    text=dataset.field_by_name("title"),
    label=dataset.question_by_name("tags"), # MultiLabelQuestion
    label_strategy=None # default to "majority", or use "disagreement"
)
```
:::

:::{tab-item} RatingQuestion
```python
from argilla.feedback import FeedbackDataset, TrainingTask

dataset = FeedbackDataset.from_huggingface(
    repo_id="argilla/stackoverflow_feedback_demo"
)
task = TrainingTask.for_text_classification(
    text=dataset.field_by_name("title"),
    label=dataset.question_by_name("answer_quality"), # RatingQuestion
    label_strategy=None # default to "majority", or use "min", "max", "disagreement"
)
```
:::

::::

##### `formatting_func`

We offer the option to provide a `formatting_func` to the `TrainingTask` or `TrainingTask`. This function is applied to each sample in the dataset and can be used for more advanced preprocessing and data formatting. The function should return a tuple of `(text, label)`.

```python
from argilla.feedback import FeedbackDataset, TrainingTask

dataset = FeedbackDataset.from_huggingface(
    repo_id="argilla/stackoverflow_feedback_demo"
)

def formatting_func(sample):
    text = sample["title"] + " " + sample["question"]
    values = [resp["value"] for resp in sample["title_question_fit"]]
    counter = Counter(values)
    if counter:
        most_common = counter.most_common()
        max_frequency = most_common[0][1]
        most_common_elements = [
            element for element, frequency in most_common if frequency == max_frequency
        ]
        label = random.choice(most_common_elements)
        return (text, label)
    else:
        return None

task = TrainingTask.for_text_classification(
    formatting_func=formatting_func,
)
```

#### Use ArgillaTrainer

Next, we can use our `FeedbackDataset` and `TrainingTaskForTextClassification` to initialize our `argilla.ArgillaTrainer`. We support the frameworks "openai", "setfit", "peft", "spacy" and "transformers".

````{note}
This is a newer version and can be imported via `from argilla.feedback import ArgillaTrainer`. The old trainer can be imported via `from argilla.training import ArgillaTrainer`. Our docs, contain some [additional information on usage of the ArgillaTrainer](/guides/train_a_model).
````


::::{tab-set}

:::{tab-item} text-label-pair
```python
from argilla.feedback import ArgillaTrainer, FeedbackDataset, TrainingTask

dataset = FeedbackDataset.from_huggingface(
    repo_id="argilla/stackoverflow_feedback_demo"
)
task = TrainingTask.for_text_classification(
    text=dataset.field_by_name("title"),
    label=dataset.question_by_name("tags")
)
trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="setfit",
    fetch_records=False
)
trainer.update_config(num_train_epochs=2)
trainer.train(output_dir="my_awesone_model")
```
:::

:::{tab-item} formatting_func
```python
from argilla.feedback import ArgillaTrainer, FeedbackDataset, TrainingTask

dataset = FeedbackDataset.from_huggingface(
    repo_id="argilla/stackoverflow_feedback_demo"
)

def formatting_func(sample):
    text = sample["title"] + " " + sample["question"]
    values = [resp["value"] for resp in sample["title_question_fit"]]
    counter = Counter(values)
    if counter:
        most_common = counter.most_common()
        max_frequency = most_common[0][1]
        most_common_elements = [
            element for element, frequency in most_common if frequency == max_frequency
        ]
        label = random.choice(most_common_elements)
        return (text, label)
    else:
        return None

task = TrainingTask.for_text_classification(
    formatting_func=formatting_func,
)
trainer.update_config(num_train_epochs=2)
trainer.train(output_dir="my_awesone_model")
:::
::::

````{note}
The `FeedbackDataset` also allows for custom workflows via the `prepare_for_training()` method.
```python
task = ...
dataset = rg.FeedbackDataset.from_huggingface(
    repo_id="argilla/stackoverflow_feedback_demo"
)
dataset.prepare_for_training(
    framework="setfit",
    task=task
)
```
````

### An end-to-end example

Below you can also find an end-to-end example of how to use the `ArgillaTrainer`.

```python
from argilla.feedback import (
    ArgillaTrainer,
    FeedbackDataset,
    FeedbackRecord,
    LabelQuestion,
    TextField,
    TrainingTask,
)

dataset = FeedbackDataset(
    guidelines="Add some guidelines for the annotation team here.",
    fields=[
        TextField(name="text", title="Human prompt"),
    ],
    questions =[
        LabelQuestion(
            name="relevant",
            title="Is the response relevant for the given prompt?",
            labels=["yes","no"],
            required=True,
        )
    ]
)
dataset.add_records(
    records=[
        FeedbackRecord(
            fields={"text": "What is your favorite color?"},
            responses=[{"values": {"relevant": {"value": "no"}}}]
        ),
        FeedbackRecord(
            fields={"text": "What do you think about the new iPhone?"},
            responses=[{"values": {"relevant": {"value": "yes"}}}]
        ),
        FeedbackRecord(
            fields={"text": "What is your feeling about the technology?"},
            responses=[{"values": {"relevant": {"value": "yes"}}},
                       {"values": {"relevant": {"value": "no"}}},
                       {"values": {"relevant": {"value": "yes"}}}]
        ),
        FeedbackRecord(
            fields={"text": "When do you expect to buy a new phone?"},
            responses=[{"values": {"relevant": {"value": "no"}}},
                       {"values": {"relevant": {"value": "yes"}}}]
        )

    ]
)

task = TrainingTask.for_text_classification(
    text=dataset.field_by_name("text"),
    label=dataset.question_by_name("relevant")
)

trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="setfit",
    fetch_records=False
)
trainer.update_config(num_train_epochs=2)
trainer.train(output_dir="my_awesone_model")
```
