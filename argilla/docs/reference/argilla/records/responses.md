---
hide: footer
---
# `rg.Response`

Class for interacting with Argilla Responses of records. Responses are answers to questions by a user. Therefore, a question can have multiple responses, one for each user that has answered the question. A `Response` is typically created by a user in the UI or consumed from a data source as a label, unlike a `Suggestion` which is typically created by a model prediction.

## Usage Examples

Responses can be added to an instantiated `Record` directly or as a dictionary a dictionary. The following examples demonstrate how to add responses to a record object and how to access responses from a record object:

Instantiate the `Record` and related `Response` objects:

```python
dataset.records.log(
    [
        rg.Record(
            fields={"text": "Hello World, how are you?"},
            responses=[rg.Response("label", "negative", user_id=user.id)],
            external_id=str(uuid.uuid4()),
        )
    ]
)
```

Or, add a response from a dictionary where key is the question name and value is the response:

```python

dataset.records.log(
    [
        {
            "text": "Hello World, how are you?",
            "label.response": "negative",
        },
    ]
)
```

Responses can be accessed from a `Record` via their question name as an attribute of the record. So if a question is named `label`, the response can be accessed as `record.label`. The following example demonstrates how to access responses from a record object:

```python

# iterate over the records and responses

for record in dataset.records:
    for response in record.responses["label"]: # (1)
        print(response.value)
        print(response.user_id)

# validate that the record has a response

for record in dataset.records:
    if record.responses["label"]:
        for response in record.responses["label"]:
            print(response.value)
            print(response.user_id)
    else:
        record.responses.add(
            rg.Response("label", "positive", user_id=user.id)
        ) # (2)

```
    1. Access the responses for the question named `label` for each record like a dictionary containing a list of `Response` objects.
    2. Add a response to the record if it does not already have one.

## Format per `Question` type

Depending on the `Question` type, responses might need to be formatted in a slightly different way.

=== "For `LabelQuestion`"

    ```python
    rg.Response(
        question_name="label",
        value="positive",
        user_id=user.id,
        status="draft"
    )
    ```

=== "For `MultiLabelQuestion`"

    ```python
    rg.Response(
        question_name="multi-label",
        value=["positive", "negative"],
        user_id=user.id,
        status="draft"
    )
    ```

=== "For `RankingQuestion`"

    ```python
    rg.Response(
        question_name="rank",
        value=["1", "3", "2"],
        user_id=user.id,
        status="draft"
    )
    ```

=== "For `RatingQuestion`"

    ```python
    rg.Response(
        question_name="rating",
        value=4,
        user_id=user.id,
        status="draft"
    )
    ```

=== "For `SpanQuestion`"

    ```python
    rg.Response(
        question_name="span",
        value=[{"start": 0, "end": 9, "label": "MISC"}],
        user_id=user.id,
        status="draft"
    )
    ```

=== "For `TextQuestion`"

    ```python
    rg.Response(
        question_name="text",
        value="value",
        user_id=user.id,
        status="draft"
    )
    ```

---

::: src.argilla.responses.Response

