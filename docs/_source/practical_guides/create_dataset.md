# 🧑‍💻 Create and update a dataset

## Feedback Dataset

```{include} /_common/feedback_dataset.md
```

The Feedback Task datasets allow you to combine multiple questions of different kinds, so the first step will be to define the aim of your project and the kind of data and feedback you will need to get there. With this information, you can start configuring a dataset and formatting records using the Python SDK.

This guide will walk you through all the elements you will need to configure to create a `FeedbackDataset` and add records to it.

```{note}
To follow the steps in this guide, you will first need to connect to Argilla. Check how to do so in our [cheatsheet](/getting_started/cheatsheet.md#connect-to-argilla).
```

### Configure the dataset

A record in Argilla refers to a data item that requires annotation and can consist of one or multiple `fields` i.e., the pieces of information that will be shown to the user in the UI in order to complete the annotation task. This can be, for example, a prompt and output pair in the case of instruction datasets. Additionally, the record will contain `questions` that the annotators will need to answer and guidelines to help them complete the task.

All of this is fully configurable with [custom configuration](#custom-configuration) using the Python SDK. However, we can also use pre-made [Hugging Face datasets](#hugging-face-hub-datasets) or out-of-the-box [task templates](#task-templates).

#### Hugging Face hub datasets

Argilla loves Hugging Face and is tightly integrated with their eco-system. To get started with a `FeedbackDataset`, we can directly retrieve a [Argilla-compatible dataset from the Hugging Face datasets hub](https://huggingface.co/datasets?other=argilla). These datasets already contain a complete configuration and data.

```python
import argilla as rg

ds = rg.FeedbackDataset.from_huggingface("<huggingface_dataset_id>")
```

#### Task Templates

The `FeedbackDataset` has a set of predefined task templates that you can use to quickly set up your dataset. These templates include the `fields` and `questions` needed for the task, as well as the `guidelines` to provide to the annotators. Additionally, you can customize the `fields`, `questions`, and `guidelines` to fit your specific needs using a [custom configuration](#custom-configuration).

```{include} /_common/tabs/task_templates.md
```

After having initialized the `FeedbackDataset` templates, we can still alter the `fields`, `questions`, and `guidelines` to fit our specific needs using approached to [update configuration](#update-configuration).

#### Custom Configuration

##### Define `fields`

A record in Argilla refers to a data item that requires annotation and can consist of one or multiple fields i.e., the pieces of information that will be shown to the user in the UI in order to complete the annotation task. This can be, for example, a prompt and output pair in the case of instruction datasets.

As part of the `FeedbackDataset` configuration, you will need to specify the list of fields to show in the record card. As of Argilla 1.8.0, we only support one type of field, `TextField`, which is a plain text field. We have plans to expand the range of supported field types in future releases of Argilla.

You can define the fields using the Python SDK providing the following arguments:

- `name`: The name of the field, as it will be seen internally.
- `title` (optional): The name of the field, as it will be displayed in the UI. Defaults to the `name` value, but capitalized.
- `required` (optional): Whether the field is required or not. Defaults to `True`. Note that at least one field must be required.
- `use_markdown`(optional): Specify whether you want markdown rendered in the UI. Defaults to `False`.

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

- `RatingQuestion`: These questions require annotators to select one option from a list of integer values. This type is useful for collecting numerical scores.
- `TextQuestion`: These questions offer annotators a free-text area where they can enter any text. This type is useful for collecting natural language data, such as corrections or explanations.
- `LabelQuestion`: These questions ask annotators to choose one label from a list of options. This type is useful for text classification tasks. In the UI, the labels of the `LabelQuestion` will have a rounded shape.
- `MultiLabelQuestion`: These questions ask annotators to choose all applicable labels from a list of options. This type is useful for multi-label text classification tasks. In the UI, the labels of the `MultiLabelQuestion` will have a squared shape.
- `RankingQuestion`: This question asks annotators to order a list of options. It is useful to gather information on the preference or relevance of a set of options. Ties are allowed and all options will need to be ranked.

You can define your questions using the Python SDK and set up the following configurations:

- `name`: The name of the question, as it will be seen internally.
- `title` (optional): The name of the question, as it will be displayed in the UI. Defaults to the `name` value, but capitalized.
- `required` (optional): Whether the question is required or not. Defaults to `True`. Note that at least one question must be required.
- `description` (optional): The text to be displayed in the question tooltip in the UI. You can use it to give more context or information to annotators.

The following arguments apply to specific question types:

- `values`: In the `RatingQuestion` this will be any list of unique integers that represent the options that annotators can choose from. These values must be defined in the range [1, 10]. In the `RankingQuestion`, values will be a list of strings with the options they will need to rank. If you'd like the text of the options to be different in the UI and internally, you can pass a dictionary instead where the key is the internal name and the value is the text to display in the UI.
- `labels`: In `LabelQuestion` and `MultiLabelQuestion` this is a list of strings with the options for these questions. If you'd like the text of the labels to be different in the UI and internally, you can pass a dictionary instead where the key is the internal name and the value the text to display in the UI.
- `visible_labels` (optional): In `LabelQuestion` and `MultiLabelQuestion` this is the number of labels that will be visible in the UI. By default, the UI will show 20 labels and collapse the rest. Set your preferred number to change this limit or set `visible_labels=None` to show all options.
- `use_markdown` (optional): In `TextQuestion` define whether the field should render markdown text. Defaults to `False`.

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
You can also define metadata properties after the dataset has been configured or add them to an existing dataset in Argilla. To do that use the `add_metadata_property` method as explained [here](/practical_guides/create_dataset.md).
```

##### Define `vectors`

To use the similarity search in the UI and the Python SDK, you will need to configure vector settings. These are defined using the SDK as a list of up to 5 vectors. They have the following arguments:

- `name`: The name of the vector, as it will appear in the records.
- `dimensions`: The dimensions of the vectors used in this setting.
- `title` (optional): A name for the vector to display in the UI for better readability.

```python
vector_settings = [
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
- `extra_metadata_properties` (optional): A boolean to specify whether this dataset will allow metadata fields in the records other than those specified under `metadata`. Note that these will not be accessible from the UI for any user, only retrievable using the Python SDK.
- `vector_settings` (optional): A list of vector settings (up to 5) to use for similarity search.
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
    vectors=[
        rg.VectorSettings(
            name="my_vectors",
            dimensions=678,
            tite="My Vectors" #optional
        )
    ],
    guidelines="Please, read the question carefully and try to answer it as accurately as possible."
)
```

After having defined the dataset, it is possible to get their dedicated properties via the `field_by_name`, `question_by_name` and `metadata_property_by_name` methods:

```python
ds.field_by_name("question")
# rg.TextField(name="question")
ds.question_by_name("answer_quality")
# rg.RatingQuestion(
#     name="answer_quality",
#     description="How would you rate the quality of the answer?",
#     values=[1, 2, 3, 4, 5],
# )
ds.metadata_property_by_name("groups")
# rg.TermsMetadataProperty(
#     name="groups",
#     title="Annotation groups",
#     values=["group-a", "group-b", "group-c"]
# )
```

```{note}
After configuring your dataset, you can still edit the main information such as field titles, questions, descriptions, and markdown format from the UI. More info in [dataset settings](/reference/webapp/pages).
```

```{note}
Fields and questions in the UI follow the order in which these are added to the `fields` and `questions` attributes in the Python SDK.
```

```{hint}
If you are working as part of an annotation team and you would like to control how much overlap you'd like to have between your annotators, you should consider the different workflows in the [Set up your annotation team guide](/installation/configurations/workspace_management) before configuring and pushing your dataset.
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

#### Update Configuration

Configuration updates behavior differs slightly depending on whether you are working with a local or remote `FeedbackDataset` instance. We do not allow for changing the `fields` and `questions` of a remote `FeedbackDataset` from the Python SDK but do allow for changing their `description` and `title` from the Argilla UI. Additionally, changing the `guidelines` and `metadata_properties` can be changed from the Argilla UI and Python SDK. For local `FeedbackDataset` instances, we allow for changing all of these attributes. Updating configuraiton is limited because we want to avoid inconsistencies between the dataset and defined records and annotations.

::::{tab-set}

:::{tab-item} Fields
This works only for local `FeedbackDataset` instances.
```python
# Add new fields
ds = rg.FeedbackDataset(...)

new_fields=[
    rg.Type_of_field(.,.,.),
    rg.Type_of_field(.,.,.),
]

ds.fields.extend(new_fields)

# Remove a non-required field
ds.fields.pop(0)
```
:::

:::{tab-item} Questions
This works only for local `FeedbackDataset` instances.
```python
# Add new questions
ds = rg.FeedbackDataset(...)

new_questions=[
    rg.Type_of_question(.,.,.),
    rg.Type_of_question(.,.,.),
]

ds.questions.extend(new_questions)

# Remove a non-required question
ds.questions.pop(0)
```
:::

:::{tab-item} Metadata
This works for both local and remote `FeedbackDataset` instances.
```python
# Add metadata to the dataset
ds = rg.FeedbackDataset(...)

metadata = rg.TermsMetadataProperty(name="metadata", values=["like", "dislike"])

ds.add_metadata_property(metadata)

# Delete a metadata property
ds.delete_metadata_properties(metadata_properties="metadata")
```
:::

:::{tab-item} Vectors
This works for both local and remote `FeedbackDataset` instances.
```python
ds = rg.FeedbackDataset(...)

# Add vector settings to the dataset
ds.add_vector_settings(rg.VectorSettings(name="my_new_vectors", dimensions=786))

# Change vector settings title
vector_cfg = ds.vector_settings_by_name("my_vector")
vector_cfg.title = "Old vectors"
ds.update_vector_settings(vector_cfg)

# Delete vector settings
ds.delete_vector_settings("my_vectors")
```
:::

:::{tab-item} Guidelines
This works for both local and remote `FeedbackDataset` instances.
```python
# Define new guidelines from the template
ds = rg.FeedbackDataset(...)

# Define new guidelines for a question
ds.questions[0].description = 'New description for the question.'
```
:::

::::

### Configure the records

We can add records to our `FeedbackDataset`. Take some time to explore and find data that fits the purpose of your project. If you are planning to use public data, the [Datasets page](https://huggingface.co/datasets) of the Hugging Face Hub is a good place to start.

```{tip}
If you are using a public dataset, remember to always check the license to make sure you can legally employ it for your specific use case.
```

```python
from datasets import load_dataset

# Load and inspect a dataset from the Hugging Face Hub
hf_dataset = load_dataset('databricks/databricks-dolly-15k', split='train')
df = hf_dataset.to_pandas()
df
```

```{hint}
Take some time to inspect the data before adding it to the dataset in case this triggers changes in the `questions` or `fields`.
```

The next step is to create records following Argilla's `FeedbackRecord` format. These are the attributes of a `FeedbackRecord`:

- `fields`: A dictionary with the name (key) and content (value) of each of the fields in the record. These will need to match the fields set up in the dataset configuration (see [Define record fields](#define-record-fields)).
- `external_id` (optional): An ID of the record defined by the user. If there is no external ID, this will be `None`.
- `metadata` (optional): A dictionary with the metadata of the record. Read more about [including metadata](#format-metadata).
- `vectors` (optional): A dictionary with the vector associated to the record. Read more about [including vectors](#format-vectors).
- `suggestions`(optional): A list of all suggested responses for a record e.g., model predictions or other helpful hints for the annotators. Read more about [including suggestions](#format-suggestions).
- `responses` (optional): A list of all responses to a record. You will only need to add them if your dataset already has some annotated records. Read more about [including responses](#format-responses).

```python
# Create a single Feedback Record
record = rg.FeedbackRecord(
    fields={
        "question": "Why can camels survive long without water?",
        "answer": "Camels use the fat in their humps to keep them filled with energy and hydration for long periods of time."
    },
    metadata={"source": "encyclopedia"},
    vectors={"my_vector": [...], "my_other_vector": [...]},
    external_id=None
)
```

#### Format `metadata`
Record metadata can include any information about the record that is not part of the fields in the form of a dictionary. If you want the metadata to correspond with the metadata properties configured for your dataset so that these can be used for filtering and sorting records, make sure that the key of the dictionary corresponds with the metadata property `name`. When the key doesn't correspond, this will be considered extra metadata that will get stored with the record (as long as `allow_extra_metadata` is set to `True` for the dataset), but will not be usable for filtering and sorting.

```python
record = rg.FeedbackRecord(
    fields={...},
    metadata={"source": "encyclopedia", "text_length":150}
)
```

#### Format `vectors`
You can associate vectors, like text embeddings, to your records. This will enable the [semantic search](filter_dataset.md#semantic-search) in the UI and the Python SDK. These are saved as a dictionary, where the keys corresponds to the `name`s of the vector settings that were configured for your dataset and the value is a list of floats. Make sure that the length of the list corresponds to the dimensions set in the vector settings.

```{hint}
Vectors should have the following format `List[float]`. If you are using numpy arrays, simply convert them using the method `.tolist()`.
```

```python
record = rg.FeedbackRecord(
    fields={...},
    vectors={"my_vector": [...], "my_other_vector": [...]}
)
```

#### Format `suggestions`

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
            "value": ["hate", "violent"]
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
        }
    ]
)
```

:::

::::



#### Format `responses`

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

#### Add records to a dataset

Once you have a list of configured `FeedbackRecord`s, you can add those to a local or remote `FeedbackDataset` using the `add_records` method.

```python
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")

records = [
    rg.FeedbackRecord(
        fields={"question": record["instruction"], "answer": record["response"]}
    )
    for record in hf_dataset if record["category"]=="open_qa"
]

dataset.add_records(records)
```

```{note}
As soon as you add records to a remote dataset, these should be available in the Argila UI. If you cannot see them, try hitting the `Refresh` button on the sidebar.
```

#### Update records

It is possible to add, update and delete attributes of existing records such as suggestions and metadata by simply modifying the records and saving the changes with the `update_records` method. To learn more about the format that these should have check the section ["Configure the records"](#configure-the-records) above.

This is an example of how you would do this:

```python
# Load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")
modified_records = []
# Loop through the records and make modifications
for record in dataset.records:
    # e.g. adding/modifying a metadata field
    record.metadata["my_metadata"] = "new_metadata"
    # e.g. removing all suggestions
    record.suggestions = []
    modified_records.append(record)

dataset.update_records(modified_records)
```

```{note}
As soon as you update the records in a remote dataset, the changes should be available in the Argila UI. If you cannot see them, try hitting the `Refresh` button on the sidebar.
```

```{note}
Only fields cannot be added, modified or removed from the records, as this would compromise the consistency of the dataset.
```

#### Delete records

From `v1.14.0`, it is possible to delete records from a `FeedbackDataset` in Argilla. Remember that from 1.14.0, when pulling a `FeedbackDataset` from Argilla via the `from_argilla` method, the returned instance is a remote `FeedbackDataset`, which implies that all the additions, updates, and deletions are directly pushed to Argilla, without having to call `push_to_argilla` for those to be pushed to Argilla.

::::{tab-set}

:::{tab-item} Single record
The first alternative is to call the `delete` method over a single `FeedbackRecord` in the dataset, which will delete that record from Argilla.

```python
# Load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")
# Delete a specific record
dataset.records[0].delete()
```
:::

:::{tab-item} Multiple records
Otherwise, you can also select one or more records from the existing `FeedbackDataset` (which are `FeedbackRecord`s in Argilla) and call the `delete_records` method to delete them from Argilla.

```python
# Load the dataset
dataset = rg.FeedbackDataset.from_argilla(name="my_dataset", workspace="my_workspace")
# List the records to be deleted
records_to_delete = list(dataset.records[:5])
# Delete the list of records from the dataset
dataset.delete_records(records_to_delete)
```
:::

::::

## Other Datasets

```{include} /_common/other_datasets.md
```

Under the hood, the Dataset classes store the records in a simple Python list. Therefore, working with a Dataset class is not very different from working with a simple list of records, but before creating a dataset we should first define dataset settings and a labeling schema.

Argilla datasets have certain *settings* that you can configure via the `rg.*Settings` classes, for example, `rg.TextClassificationSettings`. The Dataset classes do some extra checks for you, to make sure you do not mix record types when appending or indexing into a dataset.

### Configure the dataset

You can define your Argilla dataset, which sets the allowed labels for your predictions and annotations. Once you set a labeling schema, each time you log into the corresponding dataset, Argilla will perform validations of the added predictions and annotations to make sure they comply with the schema.
You can set your labels using the code below or from the [Dataset settings page](/reference/webapp/pages.md#dataset-settings) in the UI.

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

### Update the dataset

#### Add records

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

 - `vectors`: Input vectors to enable [semantic search](/practical_guides/annotate_dataset.md#semantic-search).
 - `explanation`: Token attributions for [highlighting text](/tutorials/notebooks/monitoring-textclassification-shaptransformersinterpret-explainability).

In Argilla, records are created programmatically using the [client library](/reference/python/python_client.rst) within a Python script, a [Jupyter notebook](https://jupyter.org/), or another IDE.

Let's see how to create and upload a basic record to the Argilla web app  (make sure Argilla is already installed on your machine as described in the [setup guide](/getting_started/quickstart_installation)).

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
    text="damn this kid and her fancy clothes make me feel like a bad parent.",
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

rec = rg.TokenClassificationRecord(
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

rec = rg.Text2TextRecord(
    text="A giant giant spider is discovered... how much does he make in a year?",
    prediction=["He has 3*4 trees. So he has 12*5=60 apples."],
)
rg.log(records=rec, name="my_dataset")
```

![text2text_record](/_static/reference/webapp/features-text2text_record.png)
:::

::::

##### Add suggestions

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

##### Add annotations

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

#### Update records

It is possible to update records from your Argilla datasets using our Python API. This approach works the same way as an upsert in a normal database, based on the record `id`. You can update any arbitrary parameters and they will be over-written if you use the `id` of the original record.

```python
import argilla as rg

# Read all records in the dataset or define a specific search via the `query` parameter
record = rg.load("my_first_dataset")

# Modify first record metadata (if no previous metadata dict, you might need to create it)
record[0].metadata["my_metadata"] = "I'm a new value"

# Log record to update it, this will keep everything but add my_metadata field and value
rg.log(name="my_first_dataset", records=record[0])
```

#### Delete records

You can delete records by passing their `id` into the `rg.delete_records()` function or using a query that matches the records. Learn more [here](/reference/python/python_client.rst#argilla.delete_records).

::::{tab-set}

:::{tab-item} Delete by id
```python
## Delete by id
import argilla as rg
rg.delete_records(name="example-dataset", ids=[1,3,5])
```
:::
:::{tab-item} Delete by query
```python
## Discard records by query
import argilla as rg
rg.delete_records(name="example-dataset", query="metadata.code=33", discard_only=True)
```
:::
::::

#### Push to Argilla

We can push records to Argilla using the `rg.log()` function. This function takes a list of records and the name of the dataset to which we want to push the records.

```python
import argilla as rg

rec = rg.TextClassificationRecord(
    text="beautiful accomodations stayed hotel santa... hotels higer ranked website.",
    prediction=[("price", 0.75), ("hygiene", 0.25)],
    annotation="price"
)

rg.log(records=rec, name="my_dataset")
```
