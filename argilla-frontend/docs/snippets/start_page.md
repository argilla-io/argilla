<div class="start-page__intro" markdown="1">

# Welcome to

## Argilla is a collaboration tool for building high-quality AI datasets

If you need support join the [Argilla Discord community](http://hf.co/join/discord)

</div>

<div class="start-page__content" markdown="1">

Get started by publishing your first dataset.

### 1. Install the SDK with pip

To work with Argilla datasets, you need to use the Argilla SDK. You can install the SDK with pip as follows:

```sh
pip install argilla
```

### 2. Connect to your Argilla server

[hf_] If you're using a private space, check the [HF docs](https://docs.argilla.io/latest/getting_started/how-to-configure-argilla-on-huggingface/#how-to-use-private-spaces).

```python
import argilla as rg

client = rg.Argilla(
    [local_]api_url="[LOCAL_HOST]",
    [hf_]api_url="https://[HF_HOST]",
    api_key="[USER_API_KEY]"
)
```

### 3. Create your first dataset

Specify a workspace where the dataset will be created. Check your workspaces in ["My settings"](/user-settings). To create a new workspace, check the [docs](https://docs.argilla.io/latest/how_to_guides/workspace/).

Here, we are defining a creating a dataset with a text field and a label question ("positive" and "negative"), check the docs to [create a fully custom dataset](https://docs.argilla.io/latest/how_to_guides/dataset/). Don't forget to replace "<your-workspace>".

```python
settings = rg.Settings(
    guidelines="Classify the reviews as positive or negative.",
    fields=[
        rg.TextField(
            name="review",
            title="Text from the review",
            use_markdown=False,
        ),
    ],
    questions=[
        rg.LabelQuestion(
            name="my_label",
            title="In which category does this article fit?",
            labels=["positive", "negative"],
        )
    ],
)
dataset = rg.Dataset(
    name=f"my_first_dataset",
    workspace="default", # change this to your workspace
    settings=settings,
    client=client,
)
dataset.create()
```

### 4. Add records

You can create a list with records that you want to add. Ensure that you match the fields with those specified in the question settings.

You can also use `pandas` or `datasets.load_dataset` to [read an existing dataset and create records from it](https://docs.argilla.io/latest/how_to_guides/record/).

```python
records = [
    rg.Record(
        fields={
            "review": "This is a great product.",
        },
    ),
    rg.Record(
        fields={
            "review": "This is a bad product.",
        },
    ),
]
dataset.records.log(records)
```

</div>
