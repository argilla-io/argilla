# 🦾 Fine-tune LLMs and other language models

## Feedback Dataset

```{include} /_common/feedback_dataset.md
```

After [collecting the responses](/practical_guides/collect_responses) from our `FeedbackDataset`, we can start fine-tuning our LLMs and other models. Due to the customizability of the task, this might require setting up a custom post-processing workflow, but we will provide some good toy examples for the [LLM approaches](/conceptual_guides/llm/rlhf): supervised fine-tuning, and reinforcement learning through human feedback (RLHF). However, we still provide for other NLP tasks like text classification.

### The `ArgillaTrainer`

The `ArgillaTrainer` is a wrapper around many of our favorite NLP libraries. It provides a very intuitive abstract representation to facilitate simple training workflows using decent default pre-set configurations without having to worry about any data transformations from Argilla.

Using the `ArgillaTrainer` is straightforward, but it slightly differs per task.

1. First, we define a `TrainingTask`. This is done using a custom `formatting_func`. However, tasks like Text Classification can also be defined using default definitions using the `FeedbackDataset` fields and questions. These tasks are then used for retrieving data from a dataset and initializing the training. We also offer some ideas for [unifying data](/practical_guides/collect_responses) out of the box.
2. Next, we initialize the `ArgillaTrainer` and forward the task and training framework. Internally, this uses the `FeedbackData.prepare_for_training`-method to format the data according to the expectations from the framework. Some other interesting methods are:
   1. `ArgillaTrainer.update_config` to change framework-specific training parameters.
   2. `ArgillaTrainer.train` to start training.
   3. `ArgillTrainer.predict` to run inference.

Underneath, you can see the happy flow for using the `ArgillaTrainer`.

```python
from argilla.feedback import ArgillaTrainer, FeedbackDataset, TrainingTask

dataset = FeedbackDataset.from_huggingface(
    repo_id="argilla/emotion"
)
task = TrainingTask.for_text_classification(
    text=dataset.field_by_name("text"),
    label=dataset.question_by_name("label"),
)
trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="setfit"
)
trainer.update_config(num_iterations=1)
trainer.train(output_dir="my_setfit_model")
trainer.predict("This is awesome!")
```

#### Supported Frameworks

We plan on adding more support for other tasks and frameworks so feel free to reach out on our Discord channel or GitHub to help us prioritize each task.

| Task/Framework                  | TRL  | OpenAI | SetFit | spaCy | Transformers | PEFT | SentenceTransformers |
|:--------------------------------|:-----|:-------|:-------|:------|:-------------|:-----|:---------------------|
| Text Classification             |      |        |  ✔️     | ✔️     | ✔️            | ✔️    |                      |
| Question Answering              |      |        |        |       | ✔️            |      |                      |
| Sentence Similarity             |      |        |        |       |              |      | ✔️                    |
| Supervised Fine-tuning          | ✔️    |        |        |       |              |      |                      |
| Reward Modeling                 | ✔️    |        |        |       |              |      |                      |
| Proximal Policy Optimization    | ✔️    |        |        |       |              |      |                      |
| Direct Preference Optimization  | ✔️    |        |        |       |              |      |                      |
| Chat Completion                 |      | ✔️      |        |       |              |      |                      |

##### Training Configs

The trainer also has an `ArgillaTrainer.update_config()` method, which maps a dict with `**kwargs` to the respective framework. So, these can be derived from the underlying framework that was used to initialize the trainer. Underneath, you can find an overview of these variables for the supported frameworks.

```{note}
Note that you don't need to pass all of them directly and that the values below are their default configurations.
```

```{include} /_common/tabs/train_update_config.md
```

#### The `TrainingTask`

A `TrainingTask` is used to define how the data should be processed and formatted according to the associated task and framework. Each task has its own `TrainingTask.for_*`-classmethod and the data formatting can always be defined using a custom `formatting_func`. However, simpler tasks like Text Classification can also be defined using default definitions. These directly use the fields and questions from the FeedbackDataset configuration to infer how to prepare the data. Underneath you can find an overview of the `TrainingTask` requirements.

| Method                             | Content                      | `formatting_func` return type                                                    | Default|
|:-----------------------------------|:-----------------------------|:---------------------------------------------------------------------------------|:-------|
| for_text_classification            | `text-label`                 | `Union[Tuple[str, str], Tuple[str, List[str]]]`                                  | ✔️      |
| for_question_answering             | `questio-context-answer`     | `Union[Tuple[str, str], Tuple[str, List[str]]]`                                  | ✔️      |
| for_sentence_similarity            | `sentence-1-sentence-2-(sentence-3)-(label)` | `Union[Dict[str, Union[float, int]], Dict[str, str], List[Dict[str, Union[float, int]]], List[Dict[str, str]]]`| ✔️      |
| for_supervised_fine_tuning         | `text`                       | `Union[str, Iterator[str]]`                                            | ✗      |
| for_reward_modeling                | `chosen-rejected`            | `Union[Tuple[str, str], Iterator[Tuple[str, str]]]`                    | ✗      |
| for_proximal_policy_optimization   | `text`                       | `Union[str, Iterator[str]]]`                                            | ✗      |
| for_direct_preference_optimization | `prompt-chosen-rejected`     | `Union[Tuple[str, str, str], Iterator[Tuple[str, str, str]]]`          | ✗      |
| for_chat_completion                | `chat-turn-role-content`     | `Union[Tuple[str, str, str, str], Iterator[Tuple[str, str, str, str]]]`| ✗      |

#### Filter and Sort datasets for training

Say you want to filter a part of your dataset, keep only the submitted records, or maybe sort by date to train on the latest additions to your dataset only. You can do it easily from the `ArgillaTrainer` by using the `filter_by`, `sort_by`, and `max_records` arguments:

```python
from argilla import SortBy

trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="setfit",
    filter_by={"response_status": ["submitted"]},
    sort_by=[SortBy(field="metadata.my-metadata", order="asc")],
    max_records=1000
)
```

:::{note}
You can take a look at the [filter and query datasets](/practical_guides/fine_tune.md) page in the docs to learn more about how to filter and sort datasets.
:::

#### Huggingface hub Integration

This section presents some integrations with the Hugging Face 🤗[model hub](https://huggingface.co/docs/hub/models-the-hub), the easiest way to share your Argilla models, as well as the possibility of generating an automated model card.

:::{note}
Take a look at the following [sample model](https://huggingface.co/plaguss/test_model) in the 🤗huggingface hub with the autogenerated model card, and check [https://huggingface.co/models?other=argilla](https://huggingface.co/models?other=argilla) for shared Argilla models to come.
:::

##### Model card generation

The `ArgillaTrainer` automatically generates a [model card](https://huggingface.co/docs/hub/model-cards) when saving the model. After calling `trainer.train(output_dir="my_model")`, you should see the model card under the same output directory you passed through the train method: `./my_model/README.md`. Most of the fields in the card are automatically generated when possible, but the following fields can be (optionally) updated via the `framework_kwargs` variable of the `ArgillaTrainer` like so:

```python
model_card_kwargs = {
    "language": ["en", "es"],
    "license": "Apache-2.0",
    "dataset_name": "argilla/emotion",
    "tags": ["nlp", "few-shot-learning", "argilla", "setfit"],
    "model_summary": "Small summary of what the model does",
    "model_description": "An extended explanation of the model",
    "model_type": "A 1.3B parameter embedding model fine-tuned on an awesome dataset",
    "finetuned_from": "all-MiniLM-L6-v2",
    "repo": "https://github.com/..."
    "developers": "",
    "shared_by": "",
}

trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="setfit",
    framework_kwargs={"model_card_kwargs": model_card_kwargs}
)
trainer.train(output_dir="my_model")
```

Even though its generated internally, you can get the card by calling the `generate_model_card` method:

```python
argilla_model_card = trainer.generate_model_card("my_model")
```

##### Upload your models to Huggingface Hub


If you don't have huggingface hub installed yet, you can do it with the following command:

```console
pip install huggingface_hub
```

:::{note}

If your framework chosen is `spacy` or `spacy-transformers` you should also install the following dependency:

```console
pip install spacy-huggingface-hub
```
:::

And then select the environment, depending on whether you are working with a script or from a jupyter notebook:

::::{tab-set}

:::{tab-item} Console

Run the following command from a console window and insert your 🤗huggingface hub token:

```console
huggingface-cli login
```

:::

:::{tab-item} Notebook

Run the following command from a notebook cell and insert your 🤗huggingface hub token:


```python
from huggingface_hub import notebook_login

notebook_login()
```

:::

::::

Internally, the token will be used when calling the `push_to_huggingface` model.

Be sure to take a look at the huggingface hub
[requirements](https://huggingface.co/docs/hub/repositories-getting-started#requirements) in case you need more help publishing your models.

After your model is trained, you just need to call `push_to_huggingface` and wait for your model to be pushed to the hub (by default, a model card will be generated, put the argument to `False` if you don't want it):

```python
# spaCy based models:
repo_id = output_dir

# Every other framework:
repo_id = "organization/model-name"  # for example: argilla/newest-model

trainer.push_to_huggingface(repo_id, generate_card=True)
```

Due to the spaCy behavior when pushing models, the repo_id is automatically generated internally, you need to pass the path to where the model was saved (the same `output_dir` variable you may pass to the `train` method), and it will work out just the same.

### Tasks

#### Text Classification

##### Background

Text classification is a widely used NLP task where labels are assigned to text. Major companies rely on it for various applications. Sentiment analysis, a popular form of text classification, assigns labels like 🙂 positive, 🙁 negative, or 😐 neutral to text. Additionally, we distinguish between single- and multi-label text classification.

::::{tab-set}

:::{tab-item} Single-label

Single-label text classification refers to the task of assigning a single category or label to a given text sample. Each text is associated with only one predefined class or category. For example, in sentiment analysis, a single-label text classification task would involve assigning labels such as "positive," "negative," or "neutral" to texts based on their sentiment.

```batch
"The help for my application of a new card and mortgage was great", "positive"
```

:::

:::{tab-item} Multi-label

Multi-label text classification is generally more complex than single-label classification due to the challenge of determining and predicting multiple relevant labels for each text. It finds applications in various domains, including document tagging, topic labeling, and content recommendation systems. For example, in customer care, a multi-label text classification task would involve assigning topics such as "new_card," "mortgage," or "opening_hours" to texts based on their content.

```{tip}
For a multi-label scenario, it is recommended to add some examples without any labels to improve model performance.
```

```batch
"The help for my application of a new card and mortgage was great", ["new_card", "mortgage"]
```

:::

::::

We then use either `text-label`-pair to further fine-tune the model.

##### Training

Text classification is one of the most widely supported training tasks within NLP. As an illustration, we will use our [emotion demo dataset](https://huggingface.co/datasets/argilla/emotion).

**Data Preparation**

```python
from argilla.feedback import FeedbackDataset

dataset = FeedbackDataset.from_huggingface(
    repo_id="argilla/emotion"
)
```

For this task, we assume we need a `text-label`-pair or a `formatting_func` for defining the `TrainingTask.for_text_classification`.

::::{tab-set}

:::{tab-item} text-label-pair
We offer the option to use default unification strategies and formatting based on a `text-label`-pair. Here we infer formatting information based on a `TextField` and a `LabelQuestion`, `MultiLabelQuestion`, `RatingQuestion` or `RankingQuestion` from the dataset. This is the easiest way to define a `TrainingTask` for text classification but if you need a custom workflow, you can use `formatting_func`.

```{note}
An overview of the unifcation measures can be found [here](/practical_guides/collect_responses). The `RatingQuestion` and `RankingQuestion` can be unified using a "majority"-, "min"-, "max"- or "disagreement"-strategy. Both the `LabelQuestion` and `MultiLabelQuestion` can be resolved using a "majority"-, or "disagreement"-strategy.
```

```python
from argilla.feedback import FeedbackDataset, TrainingTask

dataset = FeedbackDataset.from_huggingface(
    repo_id="argilla/emotion"
)
task = TrainingTask.for_text_classification(
    text=dataset.field_by_name("text"),
    label=dataset.question_by_name("label"),
    label_strategy=None # defaults presets
)
```

:::

:::{tab-item} formatting_func
We offer the option to provide a `formatting_func` to the `TrainingTask.for_text_classification`. This function is applied to each sample in the dataset and can be used for more advanced preprocessing and data formatting. The function should return a tuple of `(text, label)`  as `Tuple[str, str]` or `Tuple[str, List[str]]`.

```python
from argilla.feedback import FeedbackDataset, TrainingTask

dataset = FeedbackDataset.from_huggingface(
    repo_id="argilla/emotion"
)

def formatting_func(sample):
    text = sample["text"]
    # Choose the most common label
    values = [resp["value"] for resp in sample["label"]]
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

task = TrainingTask.for_text_classification(formatting_func=formatting_func)
```

:::

::::

We can then define our `ArgillaTrainer` for any of the supported frameworks and customize the training config using `ArgillaTrainer.update_config`.

```python
from argilla.feedback import ArgillaTrainer

trainer = ArgillaTrainer(
    dataset=feedback_dataset,
    task=task,
    framework="spacy",
    train_size=0.8,
    model="en_core_web_sm",
)

trainer.train(output_dir="textcat_model")
```

#### Question Answering

##### Background

The extractive Question Answering (QnA) task involves answering questions posed by users based on a given context. It is a challenging task that requires the model to understand the context of the question and provide an accurate answer. The model must be able to comprehend the question and the context in which it is asked, as well as the relationship between the two. Additionally, it must be able to extract the relevant information from the context and provide an answer that is both accurate and relevant to the question.

You can find a sample of an extractive QnA dataset underneath:

```batch
{
    'question': 'To whom did the Virgin Mary allegedly appear in 1858 in Lourdes France?',
    'context': 'Architecturally, the school has a Catholic character. Atop the Main Building\'s gold dome is a golden statue of the Virgin Mary. Immediately in front of the Main Building and facing it, is a copper statue of Christ with arms upraised with the legend "Venite Ad Me Omnes". Next to the Main Building is the Basilica of the Sacred Heart. Immediately behind the basilica is the Grotto, a Marian place of prayer and reflection. It is a replica of the grotto at Lourdes, France where the Virgin Mary reputedly appeared to Saint Bernadette Soubirous in 1858. At the end of the main drive (and in a direct line that connects through 3 statues and the Gold Dome), is a simple, modern stone statue of Mary.',
    'answers': 'Saint Bernadette Soubirous',
}
```

```{note}
Officially, answers need to be passed as a list of `{'answer_start': int, 'text': str}`-dicts. However, we only support a string, where the `answer_start` is inferred from the `context` and `text`-field.
```

We then use either a `question-context-answer`-set or a `formatting_func` to further fine-tune the model.

##### Training

**Data Preparation**

```python
import argilla as rg
from datasets import Dataset

feedback_dataset = rg.FeedbackDataset.from_huggingface("argilla/squad")
```

We can use a default configuration where we initialize the `TrainingTask.for_question_answering` using the `question-context-answer`-set from the dataset. We also offer the option to provide a `formatting_func` to the `TrainingTask.for_question_asnwering`. This function is applied to each sample in the dataset and can be used for advanced preprocessing and data formatting. The function should return a `question-context-answer`-set as `str-str-str`.

::::{tab-set}

:::{tab-item} question-context-answer-set

```python
from argilla.feedback import TrainingTask

task = TrainingTask.for_question_answering(
    question=feedback_dataset.field_by_name("question"),
    context=feedback_dataset.field_by_name("context"),
    answer=feedback_dataset.question_by_name("answer"),
)
```

:::

:::{tab-item} formatting_func

```python
from argilla.feedback import TrainingTask

def formatting_func(sample):
    question = sample["question"]
    context = sample["context"]
    for answer in sample["answer"]:
        if not all([question, context, answer["value"]]):
            continue
        yield question, context, answer["value"]

task = TrainingTask.for_question_answering(formatting_func=formatting_func)
```

:::

::::

**ArgillaTrainer**

Next, we can define our `ArgillaTrainer` for any of the supported frameworks and customize the training config using `ArgillaTrainer.update_config`.

```python
from argilla.feedback import ArgillaTrainer

trainer = ArgillaTrainer(
    dataset=feedback_dataset,
    task=task,
    framework="transformers",
    train_size=0.8,
)

trainer.train(output_dir="qna_model")

```

**Inference**

Lastly, this model can be used for inference using the `pipeline`-method from the [Transformers library](https://huggingface.co/tasks/question-answering). We can use the `question-answering`-pipeline for this task.

```python
from transformers import pipeline

qa_model = pipeline("question-answering", model="qna_model")
question = "Where do I live?"
context = "My name is Merve and I live in İstanbul."
qa_model(question = question, context = context)
## {'answer': 'İstanbul', 'end': 39, 'score': 0.953, 'start': 31}
```

#### Sentence Similarity

##### Background

Sentence Similarity is the task of determining how similar two texts are. By transforming the text into embeddings (vectors representing the semantic information) we can compute the similarity between these texts, computing the distance between their vectors. The [Sentence-Transformers](https://www.sbert.net/) library makes it easy to compute these sentence embeddings and use them for information retrieval and clustering. Besides these tasks, it is also commonly used to optimize Retrieval Augmented Generation (RAG) and re-ranking tasks. Generally, two types of models can be fine-tuned.

::::{tab-set}

:::{tab-item} Bi-Encoder

A bi-encoder consists of two separate neural network models, each responsible for encoding a single sentence or text. These encoders work independently and do not share weights. The primary objective of a bi-encoder is to encode individual sentences or texts into fixed-length vectors in a way that preserves the semantic meaning of the input. These fixed-length vectors can later be used for various tasks, such as retrieval or classification. Bi-encoders are often used in tasks where you need to encode a large set of texts into vectors (e.g., creating embeddings for documents in a corpus). These embeddings can then be used for tasks like information retrieval, clustering, and classification.

:::

:::{tab-item} Cross-Encoder

A cross-encoder consists of a single neural network model that takes multiple input sentences or texts simultaneously. It processes pairs of sentences or texts in one forward pass. The main objective of a cross-encoder is to provide a single scalar score or similarity measure for a pair of input sentences or texts. This score represents the similarity or relevance between the two input texts. Cross encoders are commonly used in applications like text matching, question-answering, document retrieval, and recommendation systems where you need to compare two pieces of text and assess their similarity or relevance.

:::

::::

In this [blog article](https://huggingface.co/blog/how-to-train-sentence-transformers) from hugging face you can see the different types of datasets that can be used for training `sentence-transformers` models.

##### Training

:::{note}
We can easily switch between `Bi-Encoder` and `Cross Encoder` based models using the `framework_kwargs={"cross_encoder": True}`. Additionally, data can be provided in three different ways, hence. Keep in mind the `Cross Encoder` based models don't allow training with sentence triplets.
:::

::::{tab-set}

:::{tab-item} sentence-1-sentence-2

The example is a pair of positive (similar) sentences without a label. For example, pairs of paraphrases, pairs of full texts and their summaries, pairs of duplicate questions, pairs of (query, response), or pairs of (source_language, target_language). Natural Language Inference datasets can also be formatted this way by pairing entailing sentences.

:::

:::{tab-item} sentence-1-sentence-2-label

The example is a pair of sentences and a label indicating how similar they are. The label can be either an integer or a float. This case applies to datasets originally prepared for Natural Language Inference (NLI) since they contain pairs of sentences with a label indicating whether they infer each other or not.

:::

:::{tab-item} sentence-1-sentence-2-sentence-3

**only works with Bi Encoders**

The example is a triplet (anchor, positive, negative) without classes or labels for the sentences.

:::

:::{tab-item} sentence-1-label

**only works with Bi Encoders**

The example is a sentence with an integer label. This data format is easily converted by loss functions into three sentences (triplets) where the first is an "anchor", the second a "positive" of the same class as the anchor, and the third a "negative" of a different class. Each sentence has an integer label indicating the class to which it belongs.

:::

::::

**Data Preparation**

Let's use a small version of [snli](https://huggingface.co/datasets/snli) dataset for this example, ready to work with Argilla [snli-small](https://huggingface.co/datasets/plaguss/snli-small).


```python
import argilla as rg

dataset = rg.FeedbackDataset.from_huggingface("plaguss/snli-small")
```

::::{tab-set}

:::{tab-item} sentence-1-sentence-2-label

We offer the option to use default unification strategies and formatting based on a `sentence`-pairs and `sentence-` triplets, with or without a `label`. Here we infer formatting information based on two `TextField` and a `LabelQuestion` or `RankingQuestion`. This is the easiest way to define a `TrainingTask` for sentence similarity but if you need a custom workflow, you can use `formatting_func`.

```{note}
An overview of the unifcation measures can be found [here](/practical_guides/collect_responses). For this type of task, only `LabelQuestion` or `RankingQuestion` applies.
```

```python
from argilla.feedback import TrainingTask

task = TrainingTask.for_sentence_similarity(
    texts=[dataset.field_by_name("premise"), dataset.field_by_name("hypothesis")],
    label=dataset.question_by_name("label")
)
```

For datasets that where annotated with numerical values we could also pass the label strategy we want to use (let's assume we have another question in the dataset named "other-question" that contains values that come from rated answers):

```python
task = TrainingTask.for_sentence_similarity(
    texts=[dataset.field_by_name("premise"), dataset.field_by_name("hypothesis")],
    label=dataset.question_by_name("other-question"),
    label_strategy="majority" # or "mean" for RankingQuestion
)
```

:::

:::{tab-item} formatting_func
We offer the option to provide a `formatting_func` to the `TrainingTask.for_sentence_similarity`. This function is applied to each sample in the dataset and can be used for more advanced preprocessing and data formatting. The function can return a dict with `sentence-1`, `sentence-2` and optionally `sentence-3` and the corresponding sentences, and it can also include a `label`, which can be either an `int` (to represent the class) or a `float`, as well as lists of these elements.

```python
def formatting_func(sample):
    record = {"sentence-1": sample["premise"], "sentence-2": sample["hypothesis"]}

    # Choose the most common label
    values = [resp["value"] for resp in sample["label"]]
    counter = Counter(values)
    if counter:
        most_common = counter.most_common()
        max_frequency = most_common[0][1]
        most_common_elements = [
            element for element, frequency in most_common if frequency == max_frequency
        ]
        label = random.choice(most_common_elements)
        record["label"] = label
        return record
    else:
        return None

task = TrainingTask.for_sentence_similarity(formatting_func=formatting_func)
```

:::

::::

**ArgillaTrainer**

We’ll use the task directly with our `FeedbackDataset` in the `ArgillaTrainer`. For this case we are using the default `SentenceTransformer` model, to fine-tune a `Cross Encoder` based, pass `framework_kwargs={"cross_encoder": True}`.

```python
from argilla.feedback import ArgillaTrainer

trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="sentence-transformers",
    framework_kwargs={"cross_encoder": False}
)
trainer.train(output_dir="my_sentence_transformer_model")
```

**Inference**

These models can be loaded using `sentence-transformers` (or `transformers`), the reader can take a look at each type of model at the following links:

- [Bi-Encoder](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [Cross-Encoder](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2)

However the `ArgillaTrainer` offers the possibility to predict the sentence similarity from its API. Let's check how they work using the same sample sentences from [sentence similarity task](https://huggingface.co/tasks/sentence-similarity) in Hugging Face:

```python
from argilla.feedback import ArgillaTrainer, FeedbackDataset, TrainingTask

trainer.predict(
    [
        "Machine learning is so easy.",
        ["Deep learning is so straightforward.", "This is so difficult, like rocket science.", "I can't believe how much I struggled with this."]
    ]
)
# [0.77857256, 0.4587626, 0.29062212]
```

Just to see the other format that can be passed to get the sentence similarity (a list with pairs of sentences), let's see the following example (the pairs don't need to share the first sentence, it's an example to check the same values are returned with both options).

```python

trainer.predict(
    [
        ["Machine learning is so easy.", "Deep learning is so straightforward."],
        ["Machine learning is so easy.", "This is so difficult, like rocket science."],
        ["Machine learning is so easy.", "I can't believe how much I struggled with this."]
    ]
)
# [0.77857256, 0.4587626, 0.29062212]
```

The previous results were obtained assuming the model trained was a `SentenceTransformer`. If instead of using a `SentenceTransformer` model (a `Bi-Encoder` based model) we would have chosen a `Cross-Encoder` we would obtain a different result, but with the same interpretation.

```python
trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="sentence-transformers",
    framework_kwargs={"cross_encoder": True}
)
trainer.predict(
    [
        "Machine learning is so easy.",
        ["Deep learning is so straightforward.", "This is so difficult, like rocket science.", "I can't believe how much I struggled with this."]
    ]
)
# [2.2006402, -6.2634926, -10.251489]
```

#### Supervised finetuning

##### Background

The goal of Supervised Fine Tuning (SFT) is to optimize a pre-trained model to generate the responses that users are looking for. A causal language model can generate feasible human text, but it will not be able to have proper `answers` to `question` phrases posed by the user in a conversational or instruction set. Therefore, we need to collect and curate data tailored to this use case to teach the model to mimic this data. We have a section in our docs about [collecting data for this task](/conceptual_guides/llm/sft) and there are many good [pre-trained causal language models](https://huggingface.co/models?pipeline_tag=text-generation&sort=downloads) available on Hugging Face.

Data for the training phase is generally divided into two different types generic for domain-like finetuning or chat for fine-tuning an instruction set.

*Generic*

In a generic fine-tuning setting, the aim is to make the model more proficient in generating coherent and contextually appropriate text within a particular domain. For example, if we want the model to generate text related to medical research, we would fine-tune it using a dataset consisting of medical literature, research papers, or related documents. By exposing the model to domain-specific data during training, it becomes more knowledgeable about the terminology, concepts, and writing style prevalent in that domain. This enables the model to generate more accurate and contextually appropriate responses when prompted with queries or tasks related to the specific domain. An example of this format is the [PubMed data](https://huggingface.co/datasets/pubmed), but it might be smart to add some nuance by generic instruction phrases that indicate the scope of the data, like `Generate a medical paper abstract: ...`.

```bash
# Five distinct ester hydrolases (EC 3-1) have been characterized in guinea-pig epidermis. These are carboxylic esterase, acid phosphatase, pyrophosphatase, and arylsulphatase A and B. Their properties are consistent with those of lysosomal enzymes.
```

*Chat*

On the other hand, instruction-based fine-tuning involves training the model to understand and respond to specific instructions or prompts given by the user. This approach allows for greater control and specificity in the generated output. For example, if we want the model to summarize a given text, we can fine-tune it using a dataset that consists of pairs of text passages and their corresponding summaries. The model can then be instructed to generate a summary based on a given input text. By fine-tuning the model in this manner, it becomes more adept at following instructions and producing output that aligns with the desired task or objective. An example of this format used is our [curated Dolly dataset](https://huggingface.co/datasets/argilla/databricks-dolly-15k-curated-en) with `instruction`, `context` and `response` fields. However, we can also have simpler datasets with only the `question` and `answer` fields.

::::{tab-set}

:::{tab-item} Template

```bash
### Instruction
{instruction}

### Context
{context}

### Response:
{response}
```

:::

:::{tab-item} Example

```
### Instruction
When did Virgin Australia start operating?

### Context
Virgin Australia, the trading name of Virgin Australia Airlines Pty Ltd, is an Australian-based airline. It is the largest airline by fleet size to use the Virgin brand. It commenced services on 31 August 2000 as Virgin Blue, with two aircraft on a single route. It suddenly found itself as a major airline in Australia's domestic market after the collapse of Ansett Australia in September 2001. The airline has since grown to directly serve 32 cities in Australia, from hubs in Brisbane, Melbourne and Sydney.

### Response:
Virgin Australia commenced services on 31 August 2000 as Virgin Blue, with two aircraft on a single route.
```

:::

::::

Ultimately, the choice between these two approaches to be used as `text`-field depends on the specific requirements of the application and the desired level of control over the model's output. By employing the appropriate fine-tuning strategy, we can enhance the model's performance and make it more suitable for a wide range of applications and use cases.

##### Training

There are many good libraries to help with this step, however, we are a fan of the [Transformer Reinforcement Learning (TRL)](https://huggingface.co/docs/trl) package, [Transformer Reinforcement Learning X (TRLX)](https://github.com/CarperAI/trlx),and the no-code [Hugging Face AutoTrain](https://huggingface.co/spaces/autotrain-projects/autotrain-advanced) for fine-tuning. In both cases, we need a backbone model and for example purposes, we will use our [curated Dolly dataset](https://huggingface.co/datasets/argilla/databricks-dolly-15k-curated-en).

```{note}
This dataset only contains a single annotator response per record. We gave some suggestions on dealing with [responses from multiple annotators](/practical_guides/collect_responses).
```

The [Transformer Reinforcement Learning (TRL)](https://huggingface.co/docs/trl) package provides a flexible and customizable framework for fine-tuning models. It allows users to have fine-grained control over the training process, enabling them to define their functions and to further specify the desired behavior of the model. This approach requires a deeper understanding of reinforcement learning concepts and techniques, as well as more careful experimentation. It is best suited for users who have experience in reinforcement learning and want fine-grained control over the training process. Additionally, it directly integrates with [Parameter-Efficient Fine-Tuning](https://huggingface.co/docs/peft/index) (PEFT) decreasing the computational complexity of this step of training an LLM.

**Data Preparation**

```python
import argilla as rg
from datasets import Dataset

feedback_dataset = rg.FeedbackDataset.from_huggingface("argilla/databricks-dolly-15k-curated-en")
```

We offer the option to provide a `formatting_func` to the `TrainingTask.for_supervised_fine_tuning`. This function is applied to each sample in the dataset and can be used for advanced preprocessing and data formatting. The function should return a `text` as `str`.

```python
from argilla.feedback import TrainingTask
from typing import Dict, Any

template = """\
### Instruction: {instruction}\n
### Context: {context}\n
### Response: {response}"""

def formatting_func(sample: Dict[str, Any]) -> str:
    # What `sample` looks like depends a lot on your FeedbackDataset fields and questions
    return template.format(
        instruction=sample["new-instruction"][0]["value"],
        context=sample["new-context"][0]["value"],
        response=sample["new-response"][0]["value"],
    )

task = TrainingTask.for_supervised_fine_tuning(formatting_func=formatting_func)
```

You can observe the resulting dataset by calling `FeedbackDataset.prepare_for_training`. We can use `"trl"` as the framework for example:

```python
dataset = feedback_dataset.prepare_for_training(
    framework="trl",
    task=task
)
"""
>>> dataset
Dataset({
    features: ['id', 'text'],
    num_rows: 15015
})
>>> dataset[0]["text"]
### Instruction: When did Virgin Australia start operating?

### Context: Virgin Australia, the trading name of Virgin Australia Airlines Pty Ltd, is an Australian-based airline. It is the largest airline by fleet size to use the Virgin brand. It commenced services on 31 August 2000 as Virgin Blue, with two aircraft on a single route. It suddenly found itself as a major airline in Australia's domestic market after the collapse of Ansett Australia in September 2001. The airline has since grown to directly serve 32 cities in Australia, from hubs in Brisbane, Melbourne and Sydney.

### Response: Virgin Australia commenced services on 31 August 2000 as Virgin Blue, with two aircraft on a single route.
"""
```

**ArgillaTrainer**

```python
from argilla.feedback import ArgillaTrainer

trainer = ArgillaTrainer(
    dataset=feedback_dataset,
    task=task,
    framework="trl",
    train_size=0.8,
    model="gpt2",
)
# e.g. using LoRA:
# from peft import LoraConfig
# trainer.update_config(peft_config=LoraConfig())
trainer.train(output_dir="sft_model")
```

```{note}
You can also initialize the `ArgillaTrainer` with an already initialized `model` and `tokenizer` for additional fine-grained control. This might be useful if you wish to ensure that the tokenizer adds the EOS token. A lack of this token might result in the model generating endlessly.

If the trained model still generates endlessly, then it is recommended to 1) pass a `tokenizer` that certainly adds an EOS token and 2) pass a custom Data Collator that does not set the label for the EOS token to -100.
```

**Inference**

Let's observe if it worked to train the model to respond within our template. We'll create a quick helper method for this.

```python
from transformers import GenerationConfig, AutoTokenizer, GPT2LMHeadModel

def generate(model_id: str, instruction: str, context: str = "") -> str:
    model = GPT2LMHeadModel.from_pretrained(model_id)
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    inputs = template.format(
        instruction=instruction,
        context=context,
        response="",
    ).strip()

    encoding = tokenizer([inputs], return_tensors="pt")
    outputs = model.generate(
        **encoding,
        generation_config=GenerationConfig(
            max_new_tokens=32,
            min_new_tokens=12,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        ),
    )
    return tokenizer.decode(outputs[0])
```

```python
>>> generate("sft_model", "Is a toad a frog?")
### Instruction: Is a toad a frog?

### Context:

### Response: A frog is a small, round, black-eyed, frog with a long, black-winged head. It is a member of the family Pter
```

Much better! This model follows the template as we want.

#### Reward Modeling

##### Background

A Reward Model (RM) is used to rate responses in alignment with human preferences and afterwards, using this RM, to fine-tune the LLM with the associated scores. Fine-tuning using a Reward Model can be done in different ways. We can either get the annotator to rate output completely manually, we can use a simple heuristic or we can use a stochastic preference model. Both [TRL](https://huggingface.co/docs/trl) and [TRLX](https://github.com/CarperAI/trlx) provide decent options for incorporating rewards. The [DeepSpeed library of Microsoft](https://github.com/microsoft/DeepSpeed/tree/master/blogs/deepspeed-chat) is a worthy mention too but will not be covered in our docs.

```{include} /_common/dolly_dataset_info.md
```

In the case of training an RM, we then use the `chosen-rejected`-pairs and train a classifier to distinguish between them.

##### Training

```{include} /_common/dolly_dataset_info.md
```

[TRL](https://huggingface.co/docs/trl) implements reward modeling, which can be used via the `ArgillaTrainer` class. We offer the option to provide a `formatting_func` to the `TrainingTask.for_reward_modeling`. This function is applied to each sample in the dataset and can be used for preprocessing and data formatting. The function should return a tuple of `chosen-rejected`-pairs  as `Tuple[str, str]`. To determine which response from the FeedbackDataset is superior, we can use the user annotations.

```{note}
The formatting function can also return `None` or a list of tuples. The `None` may be used if the annotations indicate that the text is low quality or harmful, and the latter could be used if multiple annotators provide additional written responses, resulting in multiple good `chosen-rejected` pairs.
```

**Data Preparation**

What the parameter to `formatting_func` looks like depends a lot on your FeedbackDataset fields and questions.
However, fields (i.e. the left side of the Argilla annotation view) are provided as their values, e.g.
```python
>>> sample
{
    ...
    'original-response': 'Virgin Australia commenced services on 31 August 2000 '
                         'as Virgin Blue, with two aircraft on a single route.',
    ...
}
```
And, all questions (i.e. the right side of the Argilla annotation view) are provided like so:
```python
>>> sample
{
    ...
    'new-response': [{'status': 'submitted',
                      'value': 'Virgin Australia commenced services on 31 August '
                               '2000 as Virgin Blue, with two aircraft on a '
                               'single route.',
                      'user-id': ...}],
    'new-response-suggestion': None,
    'new-response-suggestion-metadata': {'agent': None,
                                         'score': None,
                                         'type': None},
    ...
}
```

We can now define our formatting function, which should return `chosen-rejected`-pairs as tuple.

```python
from typing import Any, Dict, Iterator, Tuple
from argilla.feedback import TrainingTask

template = """\
### Instruction: {instruction}\n
### Context: {context}\n
### Response: {response}"""

def formatting_func(sample: Dict[str, Any]) -> Iterator[Tuple[str, str]]:
    # Our annotators were asked to provide new responses, which we assume are better than the originals
    og_instruction = sample["original-instruction"]
    og_context = sample["original-context"]
    og_response = sample["original-response"]
    rejected = template.format(instruction=og_instruction, context=og_context, response=og_response)

    for instruction, context, response in zip(sample["new-instruction"], sample["new-context"], sample["new-response"]):
        if response["status"] == "submitted":
            chosen = template.format(
                instruction=instruction["value"],
                context=context["value"],
                response=response["value"],
            )
            if chosen != rejected:
                yield chosen, rejected

task = TrainingTask.for_reward_modeling(formatting_func=formatting_func)
```

You can observe the dataset created using this task by using `FeedbackDataset.prepare_for_training`, for example using the "trl" framework:

```python
dataset = feedback_dataset.prepare_for_training(framework="trl", task=task)
"""
>>> dataset
Dataset({
    features: ['chosen', 'rejected'],
    num_rows: 2872
})
>>> dataset[2772]
{
    'chosen': '### Instruction: Answer based on the text: Is Leucascidae a sponge\n\n'
    '### Context: Leucascidae is a family of calcareous sponges in the order Clathrinida.\n\n'
    '### Response: Yes',
    'rejected': '### Instruction: Is Leucascidae a sponge\n\n'
    '### Context: Leucascidae is a family of calcareous sponges in the order Clathrinida.[1]\n\n'
    '### Response: Leucascidae is a family of calcareous sponges in the order Clathrinida.'}
"""
```
Looks great!

**ArgillaTrainer**

Now let's use the `ArgillaTrainer` to train a reward model with this task.

```python
from argilla.feedback import ArgillaTrainer

trainer = ArgillaTrainer(
    dataset=feedback_dataset,
    task=task,
    framework="trl",
    model="distilroberta-base",
)
trainer.train(output_dir="reward_model")
```

**Inference**

Let's try out the trained model in practice.

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model = AutoModelForSequenceClassification.from_pretrained("reward_model")
tokenizer = AutoTokenizer.from_pretrained("reward_model")

def get_score(model, tokenizer, text):
    # Tokenize the input sequences
    inputs = tokenizer(text, truncation=True, padding="max_length", max_length=512, return_tensors="pt")

    # Perform forward pass
    with torch.no_grad():
        outputs = model(**inputs)

    # Extract the logits
    return outputs.logits[0, 0].item()

# Example usage
prompt = "Is a toad a frog?"
context = "Both frogs and toads are amphibians in the order Anura, which means \"without a tail.\" Toads are a sub-classification of frogs, meaning that all toads are frogs, but not all frogs are toads."
good_response = "Yes"
bad_response = "Both frogs and toads are amphibians in the order Anura, which means \"without a tail.\""
example_good = template.format(instruction=prompt, context=context, response=good_response)
example_bad = template.format(instruction=prompt, context=context, response=bad_response)

score = get_score(model, tokenizer, example_good)
print(score)
# >> 5.478324890136719

score = get_score(model, tokenizer, example_bad)
print(score)
# >> 2.2948970794677734
```
As expected, the good response has a higher score than the worse response.

#### Proximal Policy Optimization

##### Background

The [TRL](https://huggingface.co/docs/trl) library implements the last step of RLHF: Proximal Policy Optimization (PPO). It requires prompts, which are then fed through the model being finetuned. Its results are passed through a reward model. Lastly, the prompts, responses and rewards are used to update the model through reinforcement learning.

```{note}
PPO requires a trained supervised fine-tuned model and reward model to work. Take a look at the task outlines above to train your own models.
```

```{include} /_common/dolly_dataset_info.md
```

In the case of training an PPO, we then use the prompt and context data and correct the generated response from the SFT model by using the reward model. Hence, we will need to format the following `text`.

```
### Instruction
When did Virgin Australia start operating?

### Context
Virgin Australia, the trading name of Virgin Australia Airlines Pty Ltd, is an Australian-based airline.
It is the largest airline by fleet size to use the Virgin brand.
It commenced services on 31 August 2000 as Virgin Blue, with two aircraft on a single route.
It suddenly found itself as a major airline in Australia's domestic market after the collapse of Ansett Australia in September 2001.
The airline has since grown to directly serve 32 cities in Australia, from hubs in Brisbane, Melbourne and Sydney.

### Response:
{to be generated by SFT model}
```

##### Training

```{include} /_common/dolly_dataset_load.md
```

**Data Preparation**

As usual, we start with a task with a formatting function. For PPO, the formatting function only returns prompts as `text`, which are formatted according to a template.

```python
from argilla.feedback import TrainingTask
from typing import Dict, Any, Iterator

template = """\
### Instruction: {instruction}\n
### Context: {context}\n
### Response: {response}"""

def formatting_func(sample: Dict[str, Any]) -> Iterator[str]:
    for instruction, context in zip(sample["new-instruction"], sample["new-context"]):
        if instruction["status"] == "submitted":
            yield template.format(
                instruction=instruction["value"],
                context=context["value"][:500],
                response=""
            ).strip()

task = TrainingTask.for_proximal_policy_optimization(formatting_func=formatting_func)
```

Like before, we can observe the resulting dataset:

```python
dataset = feedback_dataset.prepare_for_training(framework="trl", task=task)
"""
>>> dataset
Dataset({
    features: ['id', 'query'],
    num_rows: 15015
})
>>> dataset[922]
{'id': 922, 'query': '### Instruction: Is beauty objective or subjective?\n\n### Context: \n\n### Response:'}
"""
```

**ArgillaTrainer**

Instead of using this dataset, we'll use the task directly with our `FeedbackDataset` in the `ArgillaTrainer`. PPO requires us to specify the `reward_model`, and allows us to specify some other useful values as well:
* `reward_model`: A sentiment analysis pipeline with the reward model. This produces a reward for a prompt + response.
* `length_sampler_kwargs`: A dictionary with `min_value` and `max_value` keys, indicating the lower and upper bound on the number of tokens the finetuning model should generate while finetuning.
* `generation_kwargs`: The keyword arguments passed to the `generate` method of the finetuning model.
* `config`: A `trl.PPOConfig` instance with many useful parameters such as `learning_rate` and `batch_size`.

```python
from argilla.feedback import ArgillaTrainer
from transformers import pipeline
from trl import PPOConfig

trainer = ArgillaTrainer(
    dataset=feedback_dataset,
    task=task,
    framework="trl",
    model="gpt2",
)
reward_model = pipeline("sentiment-analysis", model="reward_model")
trainer.update_config(
    reward_model=reward_model,
    length_sampler_kwargs={"min_value": 32, "max_value": 256},
    generation_kwargs={
        "min_length": -1,
        "top_k": 0.0,
        "top_p": 1.0,
        "do_sample": True,
    },
    config=PPOConfig(batch_size=16)
)
trainer.train(output_dir="ppo_model")
```

**Inference**

After training, we can load this model and generate with it!

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("ppo_model")
tokenizer = AutoTokenizer.from_pretrained("ppo_model")
tokenizer.pad_token = tokenizer.eos_token

inputs = template.format(
    instruction="Is a toad a frog?",
    context="Both frogs and toads are amphibians in the order Anura, which means \"without a tail.\" Toads are a sub-classification of frogs, meaning that all toads are frogs, but not all frogs are toads.",
    response=""
).strip()
encoding = tokenizer([inputs], return_tensors="pt")
outputs = model.generate(**encoding, max_new_tokens=30)
output_text = tokenizer.decode(outputs[0])
print(output_text)
# Yes it is, toads are a sub-classification of frogs.
```

#### Direct Preference Optimization

##### Background

The [TRL](https://huggingface.co/docs/trl) library implements an alternative way to incorporate human feedback into an LLM which is called Direct Preference Optimization (DPO). This approach skips the step of training a separate reward model and directly uses the preference data during training as a measure for optimization of human feedback.

```{note}
DPO requires a trained supervised fine-tuned model to function. Take a look at the task outline above to train your own model.
```

```{include} /_common/dolly_dataset_info.md
```

In the case of training using PPO, we then use the prompt and context data and correct the generated response from the SFT model by using the reward model. Hence, we will need to format the following `text`.

```
### Instruction
When did Virgin Australia start operating?

### Context
Virgin Australia, the trading name of Virgin Australia Airlines Pty Ltd, is an Australian-based airline.
It is the largest airline by fleet size to use the Virgin brand.
It commenced services on 31 August 2000 as Virgin Blue, with two aircraft on a single route.
It suddenly found itself as a major airline in Australia's domestic market after the collapse of Ansett Australia in September 2001.
The airline has since grown to directly serve 32 cities in Australia, from hubs in Brisbane, Melbourne and Sydney.

### Response:
{to be generated by SFT model}
```

Within the DPO approach, we infer the reward from the formatted prompt and the provided preference data as `prompt-chosen-rejected`-pairs.

##### Training

```{include} /_common/dolly_dataset_load.md
```

**Data Preparation**

We will start with our basic example of a formatting function. For DPO it should return `prompt-chosen-rejected`-pairs, where the prompt is formatted according to a template.

```python
from argilla.feedback import TrainingTask
from typing import Dict, Any, Iterator

template = """\
### Instruction: {instruction}\n
### Context: {context}\n
### Response: {response}"""

def formatting_func(sample: Dict[str, Any]) -> Iterator[Tuple[str, str]]:
    # Our annotators were asked to provide new responses, which we assume are better than the originals
    og_instruction = sample["original-instruction"]
    og_context = sample["original-context"]
    rejected = sample["original-response"]
    prompt = template.format(instruction=og_instruction, context=og_context, response="")

    for instruction, context, response in zip(sample["new-instruction"], sample["new-context"], sample["new-response"]):
        if response["status"] == "submitted":
            chosen = response["value"]
            if chosen != rejected:
                yield prompt, chosen, rejected


task = TrainingTask.for_direct_preference_optimization(formatting_func=formatting_func)
```

**ArgillaTrainer**

We'll use the task directly with our `FeedbackDataset` in the `ArgillaTrainer`. In contrary to PPO, we do not need to specify any reward model, because this preference modeling is inferred internally by the DPO algorithm.

```python
from argilla.feedback import ArgillaTrainer

trainer = ArgillaTrainer(
    dataset=feedback_dataset,
    task=task,
    framework="trl",
    model="gpt2",
)
trainer.train(output_dir="dpo_model")
```

**Inference**

After training, we can load this model and generate with it!

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("dpo_model")
tokenizer = AutoTokenizer.from_pretrained("dpo_model")
tokenizer.pad_token = tokenizer.eos_token

inputs = template.format(
    instruction="Is a toad a frog?",
    context="Both frogs and toads are amphibians in the order Anura, which means \"without a tail.\" Toads are a sub-classification of frogs, meaning that all toads are frogs, but not all frogs are toads.",
    response=""
).strip()
encoding = tokenizer([inputs], return_tensors="pt")
outputs = model.generate(**encoding, max_new_tokens=30)
output_text = tokenizer.decode(outputs[0])
print(output_text)
# Yes it is, toads are a sub-classification of frogs.
```

#### Chat Completion

##### Background

With the rise of chat-oriented models under OpenAI's ChatGPT, we have seen a lot of interest in the use of LLMs for chat-oriented tasks. The main difference between chat-oriented models and the other LLMs is that they are trained on a differently formatted dataset. Instead of using a dataset of prompts and responses, they are trained on a dataset of conversations. This allows them to generate responses that are more conversational. And, OpenAI does support fine-tuning LLMs for chat-completion use cases. More information at https://openai.com/blog/gpt-3-5-turbo-fine-tuning-and-api-updates.

::::{tab-set}

:::{tab-item} conversation

```bash
User: Hello, how are you?
Agent: I am doing great!
User: When did Virgin Australia start operating?
Agent: Virgin Australia commenced services on 31 August 2000 as Virgin Blue.
User: That is incorrect. I believe it was 2001.
Agent: You are right, it was 2001.
```

:::

:::{tab-item} prompt-completion

```
### Instruction
When did Virgin Australia start operating?

### Context
Virgin Australia, the trading name of Virgin Australia Airlines Pty Ltd, is an Australian-based airline.
It is the largest airline by fleet size to use the Virgin brand.
It commenced services on 31 August 2000 as Virgin Blue, with two aircraft on a single route.
It suddenly found itself as a major airline in Australia's domestic market after the collapse of Ansett Australia in September 2001.
The airline has since grown to directly serve 32 cities in Australia, from hubs in Brisbane, Melbourne and Sydney.

### Response:
{to be generated by SFT model}
```

:::

::::

##### Training

```{include} /_common/dolly_dataset_load.md
```

**Data Preparation**

We will use [the dataset](https://huggingface.co/datasets/argilla/customer_assistant) from [this tutorial](/tutorials_and_integrations/tutorials/feedback/fine-tuning-openai-rag-feedback).

```python
dataset = rg.FeedbackDataset.from_huggingface("argilla/customer_assistant")
```

We will start with our basic example of a formatting function. For Chat Completion it should return `chat-turn-role-text`, where the prompt is formatted according to a template. We require this split because each conversational chain needs to be able to be retraced in the correct order and based on the user roles that might have been speaking.

```{note}
We infer a so-called message because OpenAI expects this output format but this might differ for other scenarios.
```

```python
from argilla.feedback import TrainingTask
from typing import Dict, Any, Iterator


# adapation from LlamaIndex's TEXT_QA_PROMPT_TMPL_MSGS[1].content
user_message_prompt ="""Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge but keeping your Argilla Cloud assistant style, answer the query.
Query: {query_str}
Answer:
"""
# Adapation from LlamaIndex's TEXT_QA_SYSTEM_PROMPT
system_prompt = """You are an expert customer service assistant for the Argilla Cloud product that is trusted around the world.
Always answer the query using the provided context information, and not prior knowledge.
Some rules to follow:
1. Never directly reference the given context in your answer.
2. Avoid statements like 'Based on the context, ...' or 'The context information ...' or anything along those lines.
"""

def formatting_func(sample: dict) -> Union[Tuple[str, str, str, str], List[Tuple[str, str, str, str]]]:
    from uuid import uuid4
    if sample["response"]:
        chat = str(uuid4())
        user_message = user_message_prompt.format(context_str=sample["context"], query_str=sample["user-message"])
        yield [
            (chat, "0", "system", system_prompt),
            (chat, "1", "user", user_message),
            (chat, "2", "assistant", sample["response"][0]["value"])
        ]

task = TrainingTask.for_chat_completion(formatting_func=formatting_func)
```

**ArgillaTrainer**

We'll use the task directly with our `FeedbackDataset` in the `ArgillaTrainer`. The only configurable parameter is `n_epochs` but this is also optimized internally.

```python
from argilla.feedback import ArgillaTrainer

trainer = ArgillaTrainer(
    dataset=feedback_dataset,
    task=task,
    framework="openai",
)
trainer.train(output_dir="chat-completion")
```

**Inference**

After training, we can directly use the model but we need to do so so, we need to use the `openai` framework. Therefore, we suggest taking a look at [their docs](https://platform.openai.com/docs/guides/fine-tuning/use-a-fine-tuned-model).

```python
import openai

completion = openai.ChatCompletion.create(
  model="ft:gpt-3.5-turbo:my-org:custom_suffix:id",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ]
)
```

## Other datasets

```{include} /_common/other_datasets.md
```

### The `ArgillaTrainer`

The `ArgillaTrainer` is a wrapper around many of our favorite NLP libraries. It provides a very intuitive abstract representation to facilitate simple training workflows using decent default pre-set configurations without having to worry about any data transformations from Argilla.

#### Supported frameworks

| Framework/Task    | TextClassification | TokenClassification | Text2Text |
|-------------------|--------------------|---------------------|-----------|
| OpenAI            | ✔️                  |                     | ✔️         |
| SetFit            | ✔️                  |                     |           |
| spaCy             | ✔️                  | ✔️                   |           |
| Transformers      | ✔️                  | ✔️                   |           |
| PEFT              | ✔️                  | ✔️                   |           |
| SpanMarker        |                    | ✔️                   |           |


##### Training configs

The trainer also has an `ArgillaTrainer.update_config()` method, which maps a dict with `**kwargs` to the respective framework. So, these can be derived from the underlying framework that was used to initialize the trainer. Underneath, you can find an overview of these variables for the supported frameworks.

```{note}
Note that you don't need to pass all of them directly and that the values below are their default configurations.
```

```{include} /_common/tabs/train_update_config_other_datasets.md
```

### Tasks

In this part, we'll explore Text Classification, Token Classification, and Text2Text tasks. We'll provide concise descriptions of what each task entails and the steps involved in training and making predictions.

#### Text Classification

##### Background

Text classification is a widely used NLP task where labels are assigned to text. Major companies rely on it for various applications. Sentiment analysis, a popular form of text classification, assigns labels like 🙂 positive, 🙁 negative, or 😐 neutral to text. Additionally, we distinguish between single- and multi-label text classification.

::::{tab-set}

:::{tab-item} Single-label
Single-label text classification refers to the task of assigning a single category or label to a given text sample. Each text is associated with only one predefined class or category. For example, in sentiment analysis, a single-label text classification task would involve assigning labels such as "positive," "negative," or "neutral" to texts based on their sentiment.

```batch
"The help for my application of a new card and mortgage was great", "positive"
```

:::

:::{tab-item} Multi-label
Multi-label text classification is generally more complex than single-label classification due to the challenge of determining and predicting multiple relevant labels for each text. It finds applications in various domains, including document tagging, topic labeling, and content recommendation systems. For example, in customer care, a multi-label text classification task would involve assigning topics such as "new_card," "mortgage," or "opening_hours" to texts based on their content.

```{tip}
For a multi-label scenario, it is recommended to add some examples without any labels to improve model performance.
```

```batch
"The help for my application of a new card and mortgage was great", ["new_card", "mortgage"]
```

:::

::::

##### Training

```python
from argilla.feedback import ArgillaTrainer, FeedbackDataset, TrainingTask

dataset = FeedbackDataset.from_huggingface(
    repo_id="argilla/emotion"
)
task = TrainingTask.for_text_classification(
    text=dataset.field_by_name("text"),
    label=dataset.question_by_name("label"),
)
trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="setfit"
)
trainer.update_config(num_iterations=1)
trainer.train(output_dir="my_setfit_model")
trainer.predict("This is awesome!")
```


#### Token Classification

##### Background

Token classification is a crucial concept in the domain of NLP. It entails the act of assigning specific labels to individual words or tokens in a given text. These labels can encompass diverse linguistic or semantic attributes, such as part-of-speech annotations, named entities (including people's names, organizations, or locations), or sentiment indicators (expressing positivity, negativity, or neutrality). This process serves as an indispensable foundation for numerous NLP applications, facilitating the extraction of valuable insights from textual data.

##### Training

```python
import argilla as rg
from datasets import load_dataset
from argilla.training import ArgillaTrainer

dataset_rg = rg.DatasetForTokenClassification.from_datasets(
    dataset=load_dataset("conll2003", split="train[:100]"),
    tags="ner_tags",
)
rg.log(dataset_rg, name="conll2003", workspace="admin")

trainer = ArgillaTrainer(
    name="conll2003",
    workspace="admin",
    framework="spacy",
    train_size=0.8
)
trainer.update_config(num_train_epochs=2)
trainer.train(output_dir="my_spacy_model")
records = trainer.predict("The ArgillaTrainer is great!", as_argilla_records=True)
rg.log(records=records, name="conll2003", workspace="admin")
```


#### Text2Text

##### Background

The Text2Text task in the realm of NLP represents a framework that takes a piece of text as input to transform it into another. Instead of approaching different NLP challenges as isolated issues, T2T seeks to create a generalized solution by framing them as sequence-to-sequence transformations. In this approach, both the input and output are considered as sequences of text, and their lengths can vary.

##### Training

```python
import argilla as rg
from datasets import load_dataset
from argilla.training import ArgillaTrainer

dataset_rg = rg.DatasetForText2Text.from_datasets(
    dataset=load_dataset("opus_books", "en-fr", split="train[:100]"),
    tags="ner_tags",
)
rg.log(dataset_rg, name="opus_books", workspace="admin")

trainer = ArgillaTrainer(
    name="opus_books",
    workspace="admin",
    framework="openAI",
    train_size=0.8
)
trainer.update_config(max_epochs=2)
trainer.train(output_dir="my_openAI_model")
records = trainer.predict("The ArgillaTrainer is great!", as_argilla_records=True)
rg.log(records=records, name="opus_books", workspace="admin")
```

### Other options

#### Prepare for training

If you want to train a model we provide a handy method to prepare your dataset: `DatasetFor*.prepare_for_training()`.
It will return a Hugging Face dataset, a spaCy DocBin or a SparkNLP-formatted DataFrame, optimized for the training process with the Hugging Face Trainer, the spaCy CLI or the SparkNLP API.

It is possible to directly include train-test splits to the `prepare_for_training` by passing the `train_size` and `test_size` parameters.

```{include} /_common/tabs/train_prepare_for_training.md
```

#### CLI support

We also have CLI support for the ArgillaTrainer. This can be used when, for example, executing training on an external machine. Not that the --update-config-kwargs always uses the update_config() method for the corresponding class. Hence, you should take this into account to configure training via the CLI command by passing a JSON-serializable string.

```bash

Usage: python -m argilla train [OPTIONS] COMMAND [ARGS]...

Starts the ArgillaTrainer.

Options:
--name                        TEXT                                                      The name of the dataset to be used for training. [default: None]
--framework                   [transformers|peft|setfit|spacy|                          The framework to be used for training. [default: None]
                            spacy-transformers|span_marker|spark-nlp|
                            openai|trl|trlx|sentence-transformers]
--workspace                   TEXT                                                      The workspace to be used for training. [default: None]
--limit                       INTEGER                                                   The number of record to be used. [default: None]
--query                       TEXT                                                      The query to be used. [default: None]
--model                       TEXT                                                      The modelname or path to be used for training. [default: None]
--train-size                  FLOAT                                                     The train split to be used. [default: 1.0]
--seed                        INTEGER                                                   The random seed number. [default: 42]
--device                      INTEGER                                                   The GPU id to be used for training. [default: -1]
--output-dir                  TEXT                                                      Output directory for the saved model. [default: model]
--update-config-kwargs        TEXT                                                      update_config() kwargs to be passed as a dictionary. [default: {}]
--help                                                                                  Show this message and exit.

```