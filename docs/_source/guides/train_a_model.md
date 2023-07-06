# 🦾 Train a Model

This guide showcases how to train a model on the `Dataset` classes in the Argilla client.
The Dataset classes are lightweight containers for Argilla records. These classes facilitate importing from and exporting to different formats (e.g., `pandas.DataFrame`, `datasets.Dataset`) as well as sharing and versioning Argilla datasets using the Hugging Face Hub.

For each record type, there's a corresponding Dataset class called `DatasetFor<RecordType>`.
You can look up their API in the [reference section](../reference/python/python_client.rst).

There are two ways to train custom models on top of your annotated data:

1. Train models using the Argilla training module, which is quick and easy but does not offer specific customization.
2. Train with a custom workflow using the prepare for training methods, which requires some configuration but also offers more flexibility to integrate with your existing training workflows.


````{note}
For training models with the `FeedbackDataset` take a look [here](/guides/llms/practical_guides/practical_guides).
````

## Train directly

This is, quick and easy but does not offer specific customizations.

The `ArgillaTrainer` is a wrapper around many of our favorite NLP libraries. It provides a very intuitive abstract workflow to facilitate simple training workflows using decent default pre-set configurations without having to worry about any data transformations from Argilla. We plan on adding more support for other tasks and frameworks so feel free to reach out on our Slack or GitHub.

| Framework/Task    | TextClassification | TokenClassification | Text2Text | Feedback  |
|-------------------|--------------------|---------------------|-----------|-----------|
| OpenAI            | ✔️                  |                     | ✔️         |           |
| AutoTrain         | ✔️                  | ✔️                   | ✔️         |           |
| SetFit            | ✔️                  |                     |           |           |
| spaCy             | ✔️                  | ✔️                   |           |           |
| Transformers      | ✔️                  | ✔️                   |           |           |
| PEFT              | ✔️                  | ✔️                   |           |           |
| SpanMarker        |                    | ✔️                   |           |           |

### The `ArgillaTrainer`

We can use the `ArgillaTrainer` to train directly using `spacy`, `setfit` and `transformers` as framework variables.

```python
import argilla as rg
from argilla.training import ArgillaTrainer

trainer = ArgillaTrainer(
    name="<my_dataset_name>",
    workspace="<my_workspace_name>",
    framework="<my_framework>",
    train_size=0.8
)

trainer.train(path="<my_model_path>")
records = trainer.predict("The ArgillaTrainer is great!", as_argilla_records=True)
rg.log(records=records, name="<my_dataset_name>", workspace="<my_workspace_name>")
```

### Update training config

The trainer also has an `ArgillaTrainer.update_config()` method, which maps `**kwargs` to the respective framework. So, these can be derived from the underlying framework that was used to initialize the trainer. Underneath, you can find an overview of these variables for the supported frameworks. Note that you don't need to pass all of them directly and that the values below are their default configurations.


```{include} /_common/tabs/train_update_config.md
```

### CLI support

We also add CLI support for the `ArgillaTrainer`. This can be used when for example executing training on an external machine. Not that the `--update-config-kwargs` always uses the `update_config()` method for the corresponding class. Hence, you should take this into account to configure training via the CLI command by passing a JSON-serializable string.

```bash
Usage: python -m argilla train [OPTIONS] COMMAND [ARGS]...

Starts the ArgillaTrainer.

Options:
--name                        TEXT                                                      The name of the dataset to be used for training. [default: None]
--framework                   [transformers|setfit|spacy|span_marker|spark-nlp|openai]  The framework to be used for training. [default: None]
--workspace                   TEXT                                                      The workspace to be used for training. [default: None]
--limit                       INTEGER                                                   The number of record to be used. [default: None]
--query                       TEXT                                                      The query to be used. [default: None]
--model                       TEXT                                                      The modelname or path to be used for training. [default: None]
--train-size                  FLOAT                                                     The train split to be used. [default: 1.0]
--seed                        INTEGER                                                   The random seed number. [default: 42]
--device                      INTEGER                                                   The GPU id to be used for training. [default: -1]
--output-dir                  TEXT                                                      Output directory for the saved model. [default: model]
--update-config-kwargs        TEXT                                                      update_config() kwargs to be passed as a dictionary. [default: {}]
--api-url                     TEXT                                                      The API url to be used for training. [env var: ARGILLA_API_URL] [default: None]
--api-key                     TEXT                                                      The API key to be used for training. [env var: ARGILLA_API_KEY] [default: None]
```

### An example workflow

```python
import argilla as rg
from datasets import load_dataset

dataset_rg = rg.DatasetForTokenClassification.from_datasets(
    dataset=load_dataset("conll2003", split="train[:100]"),
    tags="ner_tags",
)
rg.log(dataset_rg, name="conll2003", workspace="argilla")

trainer = ArgillaTrainer(
    name="conll2003",
    workspace="argilla",
    framework="spacy",
    train_size=0.8
)
trainer.update_config(max_epochs=2)
trainer.train(output_dir="my_easy_model")
records = trainer.predict("The ArgillaTrainer is great!", as_argilla_records=True)
rg.log(records=records, name="conll2003", workspace="argilla")
```

## Train custom workflow

Custom workflows give you more flexibility to integrate with your existing training workflows.

### Prepare for training
If you want to train a model we provide a handy method to prepare your dataset: `DatasetFor*.prepare_for_training()`.
It will return a Hugging Face dataset, a spaCy DocBin or a SparkNLP-formatted DataFrame, optimized for the training process with the Hugging Face Trainer, the spaCy CLI or the SparkNLP API. Our [training tutorials](../tutorials/steps/2_training.md) show entire training workflows for your favorite packages.

### Train-test split

It is possible to directly include train-test splits to the `prepare_for_training` by passing the `train_size` and `test_size` parameters.

### Frameworks and Tasks

*TextClassification*

For text classification tasks, it flattens the inputs into separate columns of the returned dataset and converts the annotations of your records into integers and writes them in a label column:
By passing the `framework` variable as `setfit`, `transformers`, `spark-nlp` or `spacy`. This task requires a `DatastForTextClassification`.


*TokenClassification*

For token classification tasks, it converts the annotations of a record into integers representing BIO tags and writes them in a `ner_tags` column:
By passing the `framework` variable as `transformers`, `spark-nlp` or `spacy`.  This task requires a `DatastForTokenClassification`.

*Text2Text*

For text generation tasks like `summarization` and translation tasks, it converts the annotations of a record `text` and `target` columns.
By passing the `framework` variable as `transformers` and `spark-nlp`.  This task requires a `DatastForText2Text`.

*Feedback*
For feedback-oriented datasets, we currently rely on a fully customizable workflow, which means automation is limited and yet to be thought out.
This task requires a `FeedbackDataset`.


| Framework/Dataset | TextClassification | TokenClassification | Text2Text | Feedback  |
|-------------------|--------------------|---------------------|-----------|-----------|
| OpenAI            | ✔️                  | ✔️                   | ✔️         |           |
| AutoTrain         | ✔️                  | ✔️                   |           |           |
| SetFit            | ✔️                  |                     |           |           |
| spaCy             | ✔️                  | ✔️                   |           |           |
| Transformers      | ✔️                  | ✔️                   | ✔️         |           |
| PEFT              | ✔️                  | ✔️                   | ✔️         |           |
| SpanMarker        |                    | ✔️                   |           |           |
| Spark NLP         | ✔️                  | ✔️                   | ✔️         |           |


```{include} /_common/tabs/train_prepare_for_training.md
```