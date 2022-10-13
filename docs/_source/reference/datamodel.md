(concepts)=
# Data Model

Argilla is built around a few simple concepts. This section clarifies what those concepts are. Let's take a look at Argilla's data model:

![A sketch of the Argilla data model](/_static/images/main/argilla_data_model.svg)


## Dataset

A dataset is a collection of [records](#record) of a common type.
You can programmatically [build datasets](../guides/datasets.ipynb) with the Argilla client and [`log`](#rb-log) them to the web app.
In the web app you can [dive into your dataset](../reference/webapp/dataset.md) to explore and annotate your records.
You can also [`load`](#rb-load) your datasets back to the client and export it into various formats, or [prepare it for training](../guides/datasets.ipynb#prepare-dataset-for-training) a model.


## Record

A record is a data item composed of **text** inputs and, optionally, **predictions** and **annotations**.

Think of predictions as the classification that your system made over that input (for example: 'Virginia Woolf'), and think of annotations as the ground truth that you manually assign to that input (because you know that, in this case, it would be 'William Shakespeare').
Records are defined by the type of **task** they are related to. Let's see three different examples:

### Examples

#### Text classification record

Text classification deals with predicting in which categories a text fits. As if you're shown an image you could quickly tell if there's a dog or a cat in it, we build NLP models to distinguish between a Jane Austen's novel or a Charlotte Bronte's poem. It's all about feeding models with labelled examples and seeing how they start predicting over the very same labels.

Let's see examples of a spam classifier.

```python
record = rg.TextClassificationRecord(
    text="Access this link to get free discounts!",

    prediction = [('SPAM', 0.8), ('HAM', 0.2)],
    prediction_agent = "link or reference to agent",

    annotation = "SPAM",
    annotation_agent= "link or reference to annotator",

    # Extra information about this record
    metadata={
        "split": "train"
    },
)
```

#### Multi-label text classification record

Another similar task to Text Classification, but yet a bit different, is Multi-label Text Classification. Just one key difference: more than one label may be predicted. While in a regular Text Classification task we may decide that the tweet "I can't wait to travel to Egypts and visit the pyramids" fits into the hastag #Travel, which is accurate, in Multi-label Text Classification we can classify it as more than one hastag, like #Travel #History #Africa #Sightseeing #Desert.

```python
record = rg.TextClassificationRecord(
    text="I can't wait to travel to Egypts and visit the pyramids",

    multi_label = True,

    prediction = [('travel', 0.8), ('history', 0.6), ('economy', 0.3), ('sports', 0.2)],
    prediction_agent = "link or reference to agent",

    annotation = ['travel', 'history'],
    annotation_agent= "link or reference to annotator",
)
```


#### Token classification record

Token classification kind-of-tasks are NLP tasks aimed to divide the input text into words, or syllables, and assign certain values to them. Think about giving each word in a sentence its grammatical category, or highlight which parts of a medical report belong to a certain speciality. There are some popular ones like NER or POS-tagging.

```python
record = rg.TokenClassificationRecord(
    text = "Michael is a professor at Harvard",
    tokens = ["Micheal", "is", "a", "professor", "at", "Harvard"],

    # Predictions are a list of tuples with all your token labels and its starting and ending positions
    prediction = [('NAME', 0, 7), ('LOC', 26, 33)],
    prediction_agent = "link or reference to agent",

    # Annotations are a list of tuples with all your token labels and its starting and ending positions
    annotation = [('NAME', 0, 7), ('ORG', 26, 33)],
    annotation_agent = "link or reference to annotator",

    metadata={  # Information about this record
        "split": "train"
        },
    )
```

#### Text2Text record

Text2text tasks, like text generation, are tasks where the model receives and outputs a sequence of tokens. Examples of such tasks are machine translation, text summarization, paraphrase generation, etc.

```python
record = rg.Text2TextRecord(
    text = "Michael is a professor at Harvard",

    # The prediction is a list of texts or tuples if you want to add a score to a prediction
    prediction = ["Michael es profesor en Harvard", "Michael es un profesor de Harvard"],
    prediction_agent = "link or reference to agent",

    # The annotation a strings representing the expected output text for the given input text
    annotation = "Michael es profesor en Harvard"
)
```

### Annotation

An annotation is a piece information assigned to a record, a label, token-level tags, or a set of labels, and typically by a human agent.


### Prediction

A prediction is a piece information assigned to a record, a label or a set of labels and typically by a machine process.


### Metadata

Metadata will hold extra information that you want your record to have: if it belongs to the training or the test dataset, a quick fact about something regarding that specific record... Feel free to use it as you need!

## Task

A task defines the objective and shape of the predictions and annotations inside a record.
You can see our supported tasks at {ref}`tasks`.


## Settings

For now, only a set of the predefined labels (labels schema) is configurable. Still, other settings like annotators, and metadata schema, are planned to be supported as part of dataset settings.



