# 🧑‍💻 Create and update a dataset

## Feedback Dataset

```{include} /_common/feedback_dataset.md
```

The Feedback Task datasets allow you to combine multiple questions of different kinds, so the first step will be to define the aim of your project and the kind of data and feedback you will need to get there. With this information, you can start configuring a dataset and formatting records using the Python SDK. The image underneath provides a general step-by-step overview. For some end-to-end examples, you can have a look at our [tutorials page](/tutorials_and_integrations/tutorials/tutorials.md).

![workflow](/_static/tutorials/end2end/base/workflow_create_dataset.svg)

This guide will walk you through all the elements you will need to configure a `FeedbackDataset`. For more information on how to add [records](/practical_guides/create_update_dataset/records), [metadata](/practical_guides/create_update_dataset/metadata), [vectors](/practical_guides/create_update_dataset/vectors) or [suggestions and responses](/practical_guides/create_update_dataset/suggestions_and_responses), please refer to the corresponding guides.

```{note}
To follow the steps in this guide, you will first need to connect to Argilla. Check how to do so in our [cheatsheet](/getting_started/cheatsheet.md#connect-to-argilla).
```

### Configure the dataset

A record in Argilla refers to a data item that requires annotation and can consist of one or multiple `fields` i.e., the pieces of information that will be shown to the user in the UI in order to complete the annotation task. This can be, for example, a prompt and output pair in the case of instruction datasets. Additionally, the record will contain `questions` that the annotators will need to answer and guidelines to help them complete the task.

All of this is fully configurable with [custom configuration](#custom-configuration) using the Python SDK. However, we can also use pre-made [Hugging Face datasets](#hugging-face-hub-datasets) or out-of-the-box [task templates](#task-templates).

#### Hugging Face hub datasets

Argilla loves Hugging Face and is tightly integrated with its eco-system. To get started with a `FeedbackDataset`, we can directly retrieve a [Argilla-compatible dataset from the Hugging Face datasets hub](https://huggingface.co/datasets?other=argilla). These datasets already contain a complete configuration and data.

```python
import argilla as rg

ds = rg.FeedbackDataset.from_huggingface("<huggingface_dataset_id>")
```

#### Task Templates

The `FeedbackDataset` has a set of predefined task templates that you can use to quickly set up your dataset. These templates include the `fields` and `questions` needed for the task, as well as the `guidelines` to provide to the annotators. Additionally, you can customize the `fields`, `questions`, `guidelines`, `metadata` and `vectors` to fit your specific needs using a [custom configuration](#custom-configuration).

```{include} /_common/tabs/task_templates.md
```

After having initialized the `FeedbackDataset` templates, we can still alter the `fields`, `questions`, `guidelines`, `metadata` and `vectors` to fit our specific needs you can refer to the [update configuration](#update-configuration) section.

#### Custom Configuration

##### Define `fields`

A record in Argilla refers to a data item that requires annotation and can consist of one or multiple fields i.e., the pieces of information that will be shown to the user in the UI in order to complete the annotation task. This can be, for example, a prompt and output pair in the case of instruction datasets.

As part of the `FeedbackDataset` configuration, you will need to specify the list of fields to show in the record card. As of Argilla 1.8.0, we only support one type of field, `TextField`, which is a plain text field. We have plans to expand the range of supported field types in future releases of Argilla.

You can define the fields using the Python SDK providing the following arguments:

- `name`: The name of the field, as it will be seen internally.
- `title` (optional): The name of the field, as it will be displayed in the UI. Defaults to the `name` value, but capitalized.
- `required` (optional): Whether the field is required or not. Defaults to `True`. Note that at least one field must be required.
- `use_markdown` (optional): Specify whether you want markdown rendered in the UI. Defaults to `False`. If you set it to `True`, you will be able to use all the Markdown features for text formatting, as well as embed multimedia content and PDFs. To delve further into the details, please refer to this [tutorial](/tutorials_and_integrations/tutorials/feedback/making-most-of-markdown.ipynb).

```{note}
Multimedia in Markdown is here, but it's still in the experimental phase. As we navigate the early stages, there are limits on file sizes due to ElasticSearch constraints, and the visualization and loading times may vary depending on your browser. We're on the case to improve this and welcome your feedback and suggestions!
```

```python
fields = [
    rg.TextField(name="question", required=True),
    rg.TextField(name="answer", required=True, use_markdown=True),
]
```

```{note}
The order of the fields in the UI follows the order in which these are added to the `fields` attribute in the Python SDK.
```

##### Define `questions`

To collect feedback for your dataset, you need to formulate questions. The Feedback Task currently supports the following types of questions:

- `LabelQuestion`: These questions ask annotators to choose one label from a list of options. This type is useful for text classification tasks. In the UI, the labels of the `LabelQuestion` will have a rounded shape.
- `MultiLabelQuestion`: These questions ask annotators to choose all applicable labels from a list of options. This type is useful for multi-label text classification tasks. In the UI, the labels of the `MultiLabelQuestion` will have a squared shape.
- `RankingQuestion`: This question asks annotators to order a list of options. It is useful to gather information on the preference or relevance of a set of options. Ties are allowed and all options will need to be ranked.
- `RatingQuestion`: These questions require annotators to select one option from a list of integer values. This type is useful for collecting numerical scores.
- `SpanQuestion`: Here, annotators are asked to select a portion of the text of a specific field and apply a label to it. This type of question is useful for named entity recognition or information extraction tasks.
- `TextQuestion`: These questions offer annotators a free-text area where they can enter any text. This type is useful for collecting natural language data, such as corrections or explanations.

You can define your questions using the Python SDK and set up the following configurations:

- `name`: The name of the question, as it will be seen internally.
- `title` (optional): The name of the question, as it will be displayed in the UI. Defaults to the `name` value, but capitalized.
- `required` (optional): Whether the question is required or not. Defaults to `True`. Note that at least one question must be required.
- `description` (optional): The text to be displayed in the question tooltip in the UI. You can use it to give more context or information to annotators.

The following arguments apply to specific question types:

- `values`: In the `RatingQuestion` this will be any list of unique integers that represent the options that annotators can choose from. These values must be defined in the range [0, 10]. In the `RankingQuestion`, values will be a list of strings with the options they will need to rank. If you'd like the text of the options to be different in the UI and internally, you can pass a dictionary instead where the key is the internal name and the value is the text to display in the UI.
- `labels`: In `LabelQuestion`, `MultiLabelQuestion` and `SpanQuestion` this is a list of strings with the options for these questions. If you'd like the text of the labels to be different in the UI and internally, you can pass a dictionary instead where the key is the internal name and the value will be the text to display in the UI.
- `field`: A `SpanQuestion` is always attached to a specific field. Here you should pass a string with the name of the field where the labels of the `SpanQuestion` should be used.
- `allow_overlapping`: In a `SpanQuestion`, this value specifies whether overlapped spans are allowed or not. It is set to `False` by default. Set to `True` to allow overlapping spans.
- `visible_labels` (optional): In `LabelQuestion`, `MultiLabelQuestion` and `SpanQuestion` this is the number of labels that will be visible at first sight in the UI. By default, the UI will show 20 labels and collapse the rest. Set your preferred number to change this limit or set `visible_labels=None` to show all options.
- `labels_order` (optional): In `MultiLabelQuestion`, this determines the order in which labels are displayed in the UI. Set it to `natural` to show labels in the order they were defined, or `suggestion` to prioritize labels associated with suggestions. If scores are available, labels will be ordered by descending score. Defaults to `natural`.
- `use_markdown` (optional): In `TextQuestion` define whether the field should render markdown text. Defaults to `False`. If you set it to `True`, you will be able to use all the Markdown features for text formatting, as well as embed multimedia content and PDFs. To delve further into the details, please refer to this [tutorial](/tutorials_and_integrations/tutorials/feedback/making-most-of-markdown.ipynb).

```{note}
Multimedia in Markdown is here, but it's still in the experimental phase. As we navigate the early stages, there are limits on file sizes due to ElasticSearch constraints, and the visualization and loading times may vary depending on your browser. We're on the case to improve this and welcome your feedback and suggestions!
```

Check out the following tabs to learn how to set up questions according to their type:

```{include} /_common/tabs/question_settings.md
```

##### Define `metadata`

Metadata properties allow you to configure the use of metadata information for the filtering and sorting features available in the UI and Python SDK.

You can define metadata properties using the Python SDK by providing the following arguments:

- `name`: The name of the metadata property, as it will be used internally.
- `title` (optional): The name of the metadata property, as it will be displayed in the UI. Defaults to the `name` value, but capitalized.
- `visible_for_annotators` (optional): A boolean to specify whether the metadata property will be accessible for users with an `annotator` role in the UI (`True`), or if it will only be visible for users with `owner` or `admin` roles (`False`). It is set to `True` by default.

The following arguments apply to specific metadata types:

- `values` (optional): In a `TermsMetadataProperty`, you can pass a list of valid values for this metadata property, in case you want to run a validation. If none are provided, the list of values will be computed from the values provided in the records.
- `min` (optional): In an `IntegerMetadataProperty` or a `FloatMetadataProperty`, you can pass a minimum valid value. If none is provided, the minimum value will be computed from the values provided in the records.
- `max` (optional): In an `IntegerMetadataProperty` or a `FloatMetadataProperty`, you can pass a maximum valid value. If none is provided, the maximum value will be computed from the values provided in the records.

```{include} /_common/tabs/metadata_types.md
```

```{note}
You can also define metadata properties after the dataset has been configured or add them to an existing dataset in Argilla using the `add_metadata_property` method. In addition, you can now add text descriptives of your fields as metadata automatically with the `TextDescriptivesExtractor`. For more info, take a look [here](/practical_guides/create_update_dataset/metadata.md).
```

##### Define `vectors`

To use the similarity search in the UI and the Python SDK, you will need to configure vector settings. These are defined using the SDK as a list of up to 5 vectors. They have the following arguments:

- `name`: The name of the vector, as it will appear in the records.
- `dimensions`: The dimensions of the vectors used in this setting.
- `title` (optional): A name for the vector to display in the UI for better readability.

```python
vectors_settings = [
    rg.VectorSettings(
        name="my_vector",
        dimensions=768
    ),
    rg.VectorSettings(
        name="my_other_vector",
        title="Another Vector", # optional
        dimensions=768
    )
]
```

```{note}
You can also define vector settings after the dataset has been configured or add them to an existing dataset in Argilla. To do that use the `add_vector_settings` method. In addition, you can now add text descriptives of your fields as metadata automatically with the `SentenceTransformersExtractor`. For more info, take a look [here](/practical_guides/create_update_dataset/vectors.md).
```

##### Define `guidelines`

Once you have decided on the data to show and the questions to ask, it's important to provide clear guidelines to the annotators. These guidelines help them understand the task and answer the questions consistently. You can provide guidelines in two ways:

- In the dataset guidelines: this is added as an argument when you create your dataset in the Python SDK (see [below](#configure-the-dataset)). It will appear in the dataset settings in the UI.
- As question descriptions: these are added as an argument when you create questions in the Python SDK (see [above](#define-questions)). This text will appear in a tooltip next to the question in the UI.

It is good practice to use at least the dataset guidelines if not both methods. Question descriptions should be short and provide context to a specific question. They can be a summary of the guidelines to that question, but often that is not sufficient to align the whole annotation team. In the guidelines, you can include a description of the project, details on how to answer each question with examples, instructions on when to discard a record, etc.

##### Create the dataset

Once the scope of the project is defined, which implies knowing the `fields`, `questions` and `guidelines` (if applicable), you can proceed to create the `FeedbackDataset`. To do so, you will need to define the following arguments:

- `fields`: The list of fields to show in the record card. The order in which the fields will appear in the UI matches the order of this list.
- `questions`: The list of questions to show in the form. The order in which the questions will appear in the UI matches the order of this list.
- `metadata`(optional): The list of metadata properties included in this dataset.
- `allow_extra_metadata` (optional): A boolean to specify whether this dataset will allow metadata fields in the records other than those specified under `metadata`. Note that these will not be accessible from the UI for any user, only retrievable using the Python SDK.
- `vectors_settings` (optional): A list of vector settings (up to 5) to use for similarity search.
- `guidelines` (optional): A set of guidelines for the annotators. These will appear in the dataset settings in the UI.

If you haven't done so already, check the sections above to learn about each of them.

Below you can find a quick example where we create locally a `FeedbackDataset` to assess the quality of a response in a question-answering task. The `FeedbackDataset` contains two fields, question and answer, and two questions to measure the quality of the answer and to correct it if needed.

```python
dataset = rg.FeedbackDataset(
    fields=[
        rg.TextField(name="question"),
        rg.TextField(name="answer"),
    ],
    questions=[
        rg.RatingQuestion(
            name="answer_quality",
            description="How would you rate the quality of the answer?",
            values=[1, 2, 3, 4, 5],
        ),
        rg.TextQuestion(
            name="answer_correction",
            description="If you think the answer is not accurate, please, correct it.",
            required=False,
        ),
    ],
    metadata_properties = [
        rg.TermsMetadataProperty(
            name="groups",
            title="Annotation groups",
            values=["group-a", "group-b", "group-c"] #optional
        ),
        rg.FloatMetadataProperty(
            name="temperature",
            min=-0, #optional
            max=1, #optional
            visible_for_annotators=False
        )
    ],
    allow_extra_metadata = False,
    vectors_settings=[
        rg.VectorSettings(
            name="sentence_embeddings",
            dimensions=768,
            title="Sentence Embeddings" #optional
        )
    ],
    guidelines="Please, read the question carefully and try to answer it as accurately as possible."
)
```

After having defined the dataset, it is possible to get their dedicated properties via the `field_by_name`, `question_by_name`, `metadata_property_by_name` and `vector_settings_by_name` methods:

```python
dataset.field_by_name("question")
# rg.TextField(name="question")
dataset.question_by_name("answer_quality")
# rg.RatingQuestion(
#     name="answer_quality",
#     description="How would you rate the quality of the answer?",
#     values=[1, 2, 3, 4, 5],
# )
dataset.metadata_property_by_name("groups")
# rg.TermsMetadataProperty(
#     name="groups",
#     title="Annotation groups",
#     values=["group-a", "group-b", "group-c"]
# )
dataset.vector_settings_property_by_name("sentence_embeddings")
# rg.VectorSettings(
#     name="sentence_embeddings",
#     title="Sentence Embeddings",
#     dimensions=768
# )
```

```{note}
After configuring your dataset, you can still edit the main information such as field titles, questions, descriptions, and markdown format from the UI. More info in [dataset settings](/reference/webapp/pages).
```

```{note}
Fields and questions in the UI follow the order in which these are added to the `fields` and `questions` attributes in the Python SDK.
```

```{hint}
If you are working as part of an annotation team and you would like to control how much overlap you'd like to have between your annotators, you should consider the different workflows in the [Set up your annotation team guide](/practical_guides/assign_records) before configuring and pushing your dataset.
```

#### Push to Argilla

To import the dataset to your Argilla instance you can use the `push_to_argilla` method from your `FeedbackDataset` instance. Once pushed, you will be able to see your dataset in the UI.

:::{note}
From Argilla 1.14.0, calling `push_to_argilla` will not just push the `FeedbackDataset` into Argilla, but will also return the remote `FeedbackDataset` instance, which implies that the additions, updates, and deletions of records will be pushed to Argilla as soon as they are made. This is a change from previous versions of Argilla, where you had to call `push_to_argilla` again to push the changes to Argilla.
:::

::::{tab-set}

:::{tab-item} Argilla 1.14.0 or higher

```python
remote_dataset = dataset.push_to_argilla(name="my-dataset", workspace="my-workspace")
```

:::

:::{tab-item} Lower than Argilla 1.14.0

```python
dataset.push_to_argilla(name="my-dataset", workspace="my-workspace")
```

:::

::::

### Update Configuration

Configuration updates behavior differs slightly depending on whether you are working with a local or remote `FeedbackDataset` instance. We do not allow for changing the `fields` and `questions` of a remote `FeedbackDataset` from the Python SDK but do allow for changing their `description` and `title` from the Argilla UI. Additionally, changing the `guidelines`, `metadata_properties` and `vector_settings` can be changed from the Argilla UI and Python SDK. For local `FeedbackDataset` instances, we allow for changing all of these attributes. Updating configuration is limited because we want to avoid inconsistencies between the dataset and defined records and annotations.

::::{tab-set}

:::{tab-item} Fields
This works only for local `FeedbackDataset` instances.

```python
# Add new fields
dataset = rg.FeedbackDataset(...)

new_fields=[
    rg.Type_of_field(.,.,.),
    rg.Type_of_field(.,.,.),
]

dataset.fields.extend(new_fields)

# Remove a non-required field
dataset.fields.pop(0)
```

:::

:::{tab-item} Questions
This works only for local `FeedbackDataset` instances.

```python
# Add new questions
dataset = rg.FeedbackDataset(...)

new_questions=[
    rg.Type_of_question(.,.,.),
    rg.Type_of_question(.,.,.),
]

dataset.questions.extend(new_questions)

# Remove a non-required question
dataset.questions.pop(0)
```

:::

:::{tab-item} Metadata
This works for both local and remote `FeedbackDataset` instances. `update_metadata_properties` is only supported for `RemoteFeedbackDataset` instances.

```python
dataset = rg.FeedbackDataset(...)

# Add metadata properties
metadata = rg.TermsMetadataProperty(name="my_metadata", values=["like", "dislike"])
dataset.add_metadata_property(metadata)

# Change metadata properties title
metadata_cfg = dataset.metadata_property_by_name("my_metadata")
metadata_cfg.title = "Likes"
dataset.update_metadata_properties(metadata_cfg)

# Delete a metadata property
dataset.delete_metadata_properties(metadata_properties="my_metadata")
```

:::

:::{tab-item} Vectors
This works for both local and remote `FeedbackDataset` instances. `update_vectors_settings` is only supported for `RemoteFeedbackDataset` instances.

```python
dataset = rg.FeedbackDataset(...)

# Add vector settings to the dataset
dataset.add_vector_settings(rg.VectorSettings(name="my_vectors", dimensions=786))

# Change vector settings title
vector_cfg = ds.vector_settings_by_name("my_vectors")
vector_cfg.title = "Old vectors"
dataset.update_vectors_settings(vector_cfg)

# Delete vector settings
dataset.delete_vectors_settings("my_vectors")
```

:::

:::{tab-item} Guidelines
This works for both local and remote `FeedbackDataset` instances.

```python
# Define new guidelines from the template
dataset = rg.FeedbackDataset(...)

# Define new guidelines for a question
dataset.questions[0].description = 'New description for the question.'
```

:::

::::


## Other Datasets

```{include} /_common/other_datasets.md
```

Under the hood, the Dataset classes store the records in a simple Python list. Therefore, working with a Dataset class is not very different from working with a simple list of records, but before creating a dataset we should first define dataset settings and a labeling schema.

Argilla datasets have certain *settings* that you can configure via the `rg.*Settings` classes, for example, `rg.TextClassificationSettings`. The Dataset classes do some extra checks for you, to make sure you do not mix record types when appending or indexing into a dataset.

### Configure the dataset

You can define your Argilla dataset, which sets the allowed labels for your predictions and annotations. Once you set a labeling schema, each time you log into the corresponding dataset, Argilla will perform validations of the added predictions and annotations to make sure they comply with the schema. You can set your labels using the code below or from the [Dataset settings page](/reference/webapp/pages.md#dataset-settings) in the UI. For more information on how to add [records](/practical_guides/create_update_dataset/records), [metadata](/practical_guides/create_update_dataset/metadata), [vectors](/practical_guides/create_update_dataset/vectors) or [suggestions and responses](/practical_guides/create_update_dataset/suggestions_and_responses), please refer to the corresponding guides.

If you forget to define a labeling schema, Argilla will aggregate the labels it finds in the dataset automatically, but you will need to validate it. To do this, go to your [Dataset settings page](/reference/webapp/pages.md#dataset-settings) and click _Save schema_.

![Schema not saved](/_static/images/guides/guides-define_schema.png)

::::{tab-set}

:::{tab-item} Text Classification

```python
import argilla as rg

settings = rg.TextClassificationSettings(label_schema=["A", "B", "C"])

rg.configure_dataset_settings(name="my_dataset", settings=settings)
```

:::

:::{tab-item} Token Classification

```python
import argilla as rg

settings = rg.TokenClassificationSettings(label_schema=["A", "B", "C"])

rg.configure_dataset_settings(name="my_dataset", settings=settings)
```

:::

:::{tab-item} Text2Text
Because we do not require a labeling schema for `Text2Text`, we can create a dataset by directly logging records via `rg.log()`.
:::

::::

#### Push to Argilla

We can push records to Argilla using the `rg.log()` function. This function takes a list of records and the name of the dataset to which we want to push the records.

```python
import argilla as rg

rec = rg.TextClassificationRecord(
    text="beautiful accommodations stayed hotel santa... hotels higher ranked website.",
    prediction=[("price", 0.75), ("hygiene", 0.25)],
    annotation="price"
)

rg.log(records=rec, name="my_dataset")
```

```{toctree}
:hidden:

records
metadata
vectors
suggestions_and_responses
```
