---
description: In this section, we will provide a step-by-step guide to show how to manage records.
---

# Add, update, and delete records

This guide provides an overview of records, explaining the basics of how to define and manage them in Argilla.

A **record** in Argilla is a data item that requires annotation, consisting of one or more fields. These are the pieces of information displayed to the user in the UI to facilitate the completion of the annotation task. Each record also includes questions that annotators are required to answer, with the option of adding suggestions and responses to assist them. Guidelines are also provided to help annotators effectively complete their tasks.

> A record is part of a dataset, so you will need to create a dataset before adding records. Check these guides to learn how to [create a dataset](dataset.md).

!!! info "Main Class"

    ```python
    rg.Record(
        external_id="1234",
        fields={
            "question": "Do you need oxygen to breathe?",
            "answer": "Yes"
        },
        metadata={
            "category": "A"
        },
        vectors={
            "my_vector": [0.1, 0.2, 0.3],
        },
        suggestions=[
            rg.suggestion("my_label", "positive", score=0.9, agent="model_name")
        ],
        responses=[
            rg.response("label", "positive", user_id=user_id)
        ],
    )
    ```
    > Check the [Record - Python Reference](../../reference/argilla_sdk/records/records.md) to see the attributes, arguments, and methods of the `Record` class in detail.

## Add records

You can add records to a dataset in two different ways: either by using a dictionary or by directly initializing a `Record` object. You should ensure that fields, metadata and vectors match those configured in the dataset settings. In both cases, are added via the `Dataset.records.log` method. As soon as you add the records, these will be available in the Argilla UI. If they do not appear in the UI, you may need to click the refresh button to update the view.

!!! tip
    Take some time to inspect the data before adding it to the dataset in case this triggers changes in the `questions` or `fields`.

!!! note
    If you are planning to use public data, the [Datasets page](https://huggingface.co/datasets) of the Hugging Face Hub is a good place to start. Remember to always check the license to make sure you can legally use it for your specific use case.

=== "As `Record` objects"

    You can add records to a dataset by initializing a `Record` object directly. This is ideal if you need to apply logic to the data before defining the record. If the data is already structured, you should consider adding it directly as a dictionary or Hugging Face dataset.

    ```python
    import argilla_sdk as rg

    client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

    dataset = client.datasets(name="my_dataset")

    records = [
        rg.Record(
            fields={
                "question": "Do you need oxygen to breathe?",
                "answer": "Yes"
            },
        ),
        rg.Record(
            fields={
                "question": "What is the boiling point of water?",
                "answer": "100 degrees Celsius"
            },
        ), # (1)
    ]

    dataset.records.log(records)
    ```
    1. This is an illustration of a definition. In a real world scenario, you would iterate over a data structure and create `Record` objects for each iteration. 

=== "From a generic data structure"

    You can add the data directly as a dictionary like structure, where the keys correspond to the names of fields, questions, metadata or vectors in the dataset and the values are the data to be added. 
    
    If your data structure does not correspond to your Argilla dataset names, you can use a `mapping` to indicate which keys in the source data correspond to the dataset fields.

    We illustrate this python dictionaries that represent your data, but we would not advise you to to define dictionaries. Instead use the `Record` object for instatiating records.

    ```python	
    import argilla_sdk as rg

    client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

    dataset = client.datasets(name="my_dataset")

    # Add records to the dataset with the fields 'question' and 'answer'
    data = [
        {
            "question": "Do you need oxygen to breathe?",
            "answer": "Yes",
        },
        {
            "question": "What is the boiling point of water?",
            "answer": "100 degrees Celsius",
        }, # (2)
    ]
    dataset.records.log(data)

    # Add records to the dataset with the a mapping of the fields 'question' and 'answer'
    data = [
        {
            "query": "Do you need oxygen to breathe?",
            "response": "Yes",
        },
        {
            "query": "What is the boiling point of water?",
            "response": "100 degrees Celsius",
        },
    ]
    dataset.records.log(data, mapping={"query": "question", "response": "answer"}) # (3)
    ```

    1. The data structure's keys must match the fields or questions in the Argilla dataset. In this case, there are fields named `question` and `answer`. 
    2. The data structure has keys `query` and `response` and the Argilla dataset has `question` and `answer`. You can use the `mapping` parameter to map the keys in the data structure to the fields in the Argilla dataset.


=== "From a Hugging Face dataset"

    You can also add records to a dataset using a Hugging Face dataset. This is useful when you want to use a dataset from the Hugging Face Hub and add it to your Argilla dataset.

    You can add the dataset where the column names correspond to the names of fields, questions, metadata or vectors in the Argilla dataset. 
    
    If the dataset's schema does not correspond to your Argilla dataset names, you can use a `mapping` to indicate which columns in the dataset correspond to the Argilla dataset fields.

    ```python
    from uuid import uuid4

    import argilla_sdk as rg
    from datasets import load_dataset

    client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")
    dataset = client.datasets(name="my_dataset") # (1)

    hf_dataset = load_dataset("imdb", split="train[:100]") # (2)

    dataset.records.log(records=hf_dataset)
    ```	

    1. In this case, we are using the `my_dataset` dataset from the Argilla workspace. The dataset has a `text` field and a `label` question.

    2. In this example, the Hugging Face dataset matches the Argilla dataset schema. If that is not the case, you could use the `.map` of the `datasets` library to prepare the data before adding it to the Argilla dataset.

    Here we use the `mapping` parameter to specify the relationship between the Hugging Face dataset and the Argilla dataset.
    
    ```python
    dataset.records.log(records=hf_dataset, mapping={"txt": "text", "y": "label"}) # (1)
    ```

    1. In this case, the `txt` key in the Hugging Face dataset corresponds to the `text` field in the Argilla dataset, and the `y` key in the Hugging Face dataset corresponds to the `label` field in the Argilla dataset.


### Metadata

Record metadata can include any information about the record that is not part of the fields in the form of a dictionary. To use metadata for filtering and sorting records, make sure that the key of the dictionary corresponds with the metadata property `name`. When the key doesn't correspond, this will be considered extra metadata that will get stored with the record (as long as `allow_extra_metadata` is set to `True` for the dataset), but will not be usable for filtering and sorting.

!!! note
    Remember that to use metadata within a dataset, you must define a metadata property in the [dataset settings](dataset.md).

=== "As `Record` objects"

    You can add metadata to a record in an initialized `Record` object. 

    ```python
    # Add records to the dataset with the metadata 'category'
    records = [
        rg.Record(
            fields={
                "question": "Do you need oxygen to breathe?",
                "answer": "Yes"
            },
            metadata={"category": "A"},
        ),
        rg.Record(
            fields={
                "question": "What is the boiling point of water?",
                "answer": "100 degrees Celsius"
            },
            metadata={"category": "B"},
        ),
    ]
    dataset.records.log(records)
    ```

=== "From a generic data structure"
    You can add metadata to a record directly as a dictionary structure, where the keys correspond to the names of metadata properties in the dataset and the values are the metadata to be added. Remember that you can also use the `mapping` parameter to specify the data structure.

    ```python
    # Add records to the dataset with the metadata 'category'
    data = [
        {
            "question": "Do you need oxygen to breathe?",
            "answer": "Yes",
            "category": "A",
        },
        {
            "question": "What is the boiling point of water?",
            "answer": "100 degrees Celsius",
            "category": "B",
        },
    ]
    dataset.records.log(data)
    ```


### Vectors

You can associate vectors, like text embeddings, to your records. They can be used for semantic search in the UI and the Python SDK. Make sure that the length of the list corresponds to the dimensions set in the vector settings.

!!! note
    Remember that to use vectors within a dataset, you must define them in the [dataset settings](dataset.md).


=== "As `Record` objects"

    You can also add vectors to a record in an initialized `Record` object.

    > Check the [Vector - Python Reference](../../reference/argilla_sdk/records/vectors.md) to see the attributes, arguments, and methods of the `Vector` class in detail.

    ```python
    # Add records to the dataset with the vector 'my_vector' and dimension=3
    records = [
        rg.Record(
            fields={
                "question": "Do you need oxygen to breathe?",
                "answer": "Yes"
            },
            vectors=[
                rg.Vector("my_vector", [0.1, 0.2, 0.3])
            ],
        ),
        rg.Record(
            fields={
                "question": "What is the boiling point of water?",
                "answer": "100 degrees Celsius"
            },
            vectors=[
                rg.Vector("my_vector", [0.2, 0.5, 0.3])
            ],
        ),
    ]
    dataset.records.log(records)
    ```

=== "From a generic data structure"

    You can add vectors from a dictionary like structure, where the keys correspond to the `name`s of the vector settings that were configured for your dataset and the value is a list of floats. Remember that you can also use the `mapping` parameter to specify the data structure.

    ```python
    # Add records to the dataset with the vector 'my_vector' and dimension=3
    data = [
        {
            "question": "Do you need oxygen to breathe?",
            "answer": "Yes",
            "my_vector": [0.1, 0.2, 0.3],
        },
        {
            "question": "What is the boiling point of water?",
            "answer": "100 degrees Celsius",
            "my_vector": [0.2, 0.5, 0.3],
        },
    ]
    dataset.records.log(data)
    ```

### Suggestions

Suggestions refer to suggested responses (e.g. model predictions) that you can add to your records to make the annotation process faster. These can be added during the creation of the record or at a later stage. Only one suggestion can be provided for each question, and suggestion values must be compliant with the pre-defined questions e.g. if we have a `RatingQuestion` between 1 and 5, the suggestion should have a valid value within that range.

=== "As `Record objects"
    You can also add suggestions to a record in an initialized `Record` object.

    > Check the [Suggestions - Python Reference](../../reference/argilla_sdk/records/suggestions.md) to see the attributes, arguments, and methods of the `Suggestion` class in detail.

    ```python
    # Add records to the dataset with the label 'my_label'
    records = [
        rg.Record(
            fields={
                "question": "Do you need oxygen to breathe?",
                "answer": "Yes"
            },
            suggestions=[
                rg.Suggestion(
                    "my_label",
                    "positive",
                    score=0.9,
                    agent="model_name"
                )
            ],
        ),
        rg.Record(
            fields={
                "question": "What is the boiling point of water?",
                "answer": "100 degrees Celsius"
            },
            suggestions=[
                rg.Suggestion(
                    "my_label",
                    "negative",
                    score=0.9,
                    agent="model_name"
                )
            ],
        ),
    ]
    dataset.records.log(records)
    ```

=== "From a generic data structure"
    You can add suggestions as a dictionary, where the keys correspond to the `name`s of the labels that were configured for your dataset. Remember that you can also use the `mapping` parameter to specify the data structure.

    ```python
    # Add records to the dataset with the label 'my_label'
    data = [
        {
            "question": "Do you need oxygen to breathe?",
            "answer": "Yes",
            "my_label.suggestion": "positive",
            "my_label.suggestion.score": 0.9,
            "my_label.suggestion.agent": "model_name"
        },
        {
            "question": "What is the boiling point of water?",
            "answer": "100 degrees Celsius",
            "my_label.suggestion": "negative",
            "my_label.suggestion.score": 0.9,
            "my_label.suggestion.agent": "model_name"
        },
    ]
    dataset.records.log(data)
    ```

### Responses

If your dataset includes some annotations, you can add those to the records as you create them. Make sure that the responses adhere to the same format as Argilla's output and meet the schema requirements for the specific type of question being answered. Make sure to include the `user_id` in case you're planning to add more than one response for the same question, if not responses will apply to all the annotators.

!!! note
    Keep in mind that records with responses will be displayed as "Draft" in the UI.

=== "As `Record` objects"
    You can also add suggestions to a record in an initialized `Record` object.

    > Check the [Responses - Python Reference](../../reference/argilla_sdk/records/responses.md) to see the attributes, arguments, and methods of the `Suggestion` class in detail.

    ```python
    # Add records to the dataset with the label 'my_label'
    records = [
        rg.Record(
            fields={
                "question": "Do you need oxygen to breathe?",
                "answer": "Yes"
            },
            responses=[
                rg.Response("my_label", "positive", user_id=user.id)
            ]
        ),
        rg.Record(
            fields={
                "question": "What is the boiling point of water?",
                "answer": "100 degrees Celsius"
            },
            responses=[
                rg.Response("my_label", "negative", user_id=user.id)
            ]
        ),
    ]
    dataset.records.log(records)
    ```

=== "From a generic data structure"

    You can add suggestions as a dictionary, where the keys correspond to the `name`s of the labels that were configured for your dataset. Remember that you can also use the `mapping` parameter to specify the data structure. If you want to specify the user that added the response, you can use the `user_id` parameter.

    ```python
    # Add records to the dataset with the label 'my_label'
    data = [
        {
            "question": "Do you need oxygen to breathe?",
            "answer": "Yes",
            "my_label.response": "positive",
        },
        {
            "question": "What is the boiling point of water?",
            "answer": "100 degrees Celsius",
            "my_label.response": "negative",
        },
    ]
    dataset.records.log(data, user_id=user.id)
    ```



## List records

To list records in a dataset, you can use the `records` method on the `Dataset` object. This method returns a list of `Record` objects that can be iterated over to access the record properties.

```python
for record in dataset.records(
    with_suggestions=True,
    with_responses=True,
    with_vectors=True
    ):

    # Access the record properties
    print(record.metadata)
    print(record.vectors)
    print(record.suggestions)
    print(record.responses)

    # Access the responses of the record
    for response in record.responses:
        print(record.question_name.value)
```

## Update records

You can update records in a dataset calling the `update` method on the `Dataset` object. To update a record, you need to provide the record `id` and the new data to be updated.

```python
data = dataset.records.to_list(flatten=True)

updated_data = [
    {
        "text": sample["text"],
        "label": "positive",
        "id": sample["id"],
    }
    for sample in data
]
dataset.records.log(records=updated_data)

```
!!! note "Update the metadata"
    The `metadata` of `Record` object is a python dictionary. So to update the metadata of a record, you can iterate over the records and update the metadata by key or using `metadata.update`. After that, you should update the records in the dataset.

    ```python
    updated_records = []
    
    for record in dataset.records():

        record.metadata["my_metadata"] = "new_value"
        record.metadata["my_new_metadata"] = "new_value"
        
        updated_records.append(record)

    dataset.records.log(records=updated_records)
    ```