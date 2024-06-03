---
hide: footer
---
# `rg.Response`

Class for interacting with Argilla Responses of records. Responses are answers to questions by a user. Therefore, a recod question can have multiple responses, one for each user that has answered the question. A `Response` is typically created by a user in the UI or consumed from a data source as a label, unlike a `Suggestion` which is typically created by a model prediction.

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
    for response in record.responses.label:
        print(response.value)
        print(response.user_id)

# validate that the record has a response

for record in dataset.records:
    if record.responses.label:
        for response in record.responses.label:
            print(response.value)
            print(response.user_id)

```

---

## Class Reference

### `rg.Response`

::: argilla_sdk.responses.Response
    options:
        heading_level: 3