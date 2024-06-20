<div class="start-page__intro" markdown="1">

# Welcome to

## Argilla is a platform for building high-quality AI datasets

If you need support join the [Argilla Slack community](https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g)

</div>

<div class="start-page__content" markdown="1">

Get started by publishing your first dataset.

### 1. Install the SDK with pip

To work with Argilla datasets, you need to use the Argilla SDK. You can install the SDK with pip as follows:

```sh
pip install argilla -U --pre
```

### 2. Connect to your Argilla server

Get your `ARGILLA_API_URL`:

- If you are using Docker, it is the URL shown in your browser (by default `http://localhost:6900`)
- If you are using HF Spaces, it should be constructed as follows: `https://[your-owner-name]-[your_space_name].hf.space`

Get your `ARGILLA_API_KEY` you find in ["My settings"](/user-settings) and copy the API key.

Make sure to replace `ARGILLA_API_URL` and `ARGILLA_API_KEY` in the code below. If you are using a private HF Space, you need to specify your `HF_TOKEN` which can be found [here](https://huggingface.co/settings/tokens).

```python
import argilla as rg

client = rg.Argilla(
    api_url="<api_url>",
    api_key="<api_key>"
    # extra_headers={"Authorization": f"Bearer {HF_TOKEN}"}
)
```

### 3. Create your first dataset

Specify a workspace where the dataset will be created. Check your workspaces in ["My settings"](/user-settings). To create a new workspace, check the [docs](https://argilla-io.github.io/argilla/latest/how_to_guides/workspace/).

Create a Dataset with two labels ("positive" and "negative"). Don't forget to replace "<your-workspace>". Here, we are using a task template, check the docs to [create a fully custom dataset](https://argilla-io.github.io/argilla/latest/how_to_guides/dataset/).

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
    workspace="<your-workspace>",
    settings=settings,
    client=client,
)
dataset.create()
```

### 4. Add records

You canCreate a list with the records you want to add. Ensure that you match the fields with the ones specified in the previous step.

You can also use `pandas` or `datasets.load_dataset` to [read an existing dataset and create records from it](https://argilla-io.github.io/argilla/latest/how_to_guides/record/).

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
