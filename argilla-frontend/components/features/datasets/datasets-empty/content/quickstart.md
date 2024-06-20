<div class="start-page__intro" markdown="1">

# Welcome to

## Argilla is a platform to build high-quality AI datasets

If you need support join the [Argilla Slack community](https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g)

</div>

<div class="start-page__content" markdown="1">

## Connect to the Argilla server

Get your `<api_url>`:

* If you are using Hugging Face Spaces, the URL should be constructed as follows: `https://[your-owner-name]-[your_space_name].hf.space`
* If you are using Docker, the URL is the URL shown in your browser (by default `http://localhost:6900`)

Get your `<api_key>` in `My Settings` in the Argilla UI (by default `owner.apikey`).

(Make sure to replace `<api_url>` and `<api_key>` with your actual values.)

```python
import argilla as rg

client = rg.Argilla(
    api_url="<api_url>",
    api_key="<api_key>"
    # extra_headers={"Authorization": f"Bearer {HF_TOKEN}"}
)
```

## Create your first dataset

To create a dataset with a simple text classification task, first, you need to define the dataset settings.

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
```

Now you can create the dataset with the settings you defined. Publish the dataset to make it available in the UI and add the records.

!!! note
    The `workspace` parameter is optional. If you don't specify it, the dataset will be created in the default workspace `admin`.

```python
dataset = rg.Dataset(
    name=f"my_first_dataset",
    settings=settings,
    client=client,
)
dataset.create()
```

## Add records to your dataset

Retrieve the data to be added to the dataset. We will use the IMDB dataset from the Hugging Face Datasets library.

```python
pip install -qqq datasets
```

```python
from datasets import load_dataset

data = load_dataset("imdb", split="train[:100]").to_list()
```

Now you can add the data to your dataset. Use a `mapping` to indicate which keys/columns in the source data correspond to the Argilla dataset fields.

```python
dataset.records.log(records=data, mapping={"text": "review"})
```

🎉 You have successfully created your first dataset with Argilla. You can now access it in the Argilla UI and start annotating the records.
