# Getting started with Argilla

Welcome to Argilla! 👋😁 We're thrilled to have you on board. Starting with Argilla is as simple as it gets, and you've successfully taken the first step!

To start annotating your data, you need to create a `FeedbackDataset`. Let's set things in motion. 🚀

[For a more in-depth understanding of Argilla, you can check our documentation 📖.](https://docs.argilla.io/en/latest/)


## 1. Open an IDE, Jupyter or Collab

1. Open your favorite IDE, Jupyter or Collab. You can also open our [introductory tutorial](https://colab.research.google.com/github/argilla-io/argilla/blob/develop/docs/_source/getting_started/quickstart_workflow_feedback.ipynb).

2. Get your `API_URL`:

   * If you are using Docker, it is the URL shown in your browser (by default `http://localhost:6900`)
   * If you are using HF Spaces, it should be constructed as follows: `https://[your-owner-name]-[your_space_name].hf.space`

3. Get your `API_KEY` by clicking on your user icon in the top right corner of the Argilla UI, selecting "My settings" and copying the API key.

## 2. Install the SDK with pip

```sh
pip install argilla
```

## 3. Connect to your Argilla server

Connect the SDK with the server using `rg.init`. Make sure to replace "<your-api-url>" and "<your-api-key>" with the values you obtained in the first step.

```python
import argilla as rg

rg.init(
    api_url="<your-api-url>",
    api_key="<your-api-key>"
)
```

## 4. Create your first dataset

1. Specify a workspace where the dataset is to be saved. You can check the available workspaces with the following snippet:

```python
workspaces = rg.Workspace.list()
workspace_names = [workspace.name for workspace in workspaces]
workspace_names
```

2. Create a FeedbackDataset with two labels ("sadness" and "joy"). Don't forget to replace "<your-workspace>" with the workspace you want to use:

```python
dataset = rg.FeedbackDataset.for_text_classification(
    labels=['sadness', 'joy'],
    multi_label=False,
    use_markdown=True,
    guidelines=None,
    metadata_properties=None,
    vectors_settings=None,
)
dataset.push_to_argilla(name="my-first-dataset", workspace="<your-workspace>")
```

## 5. Add records

Create a list with the records you want to add. Ensure that you match the fields with the ones specified in the previous step.

```python
records = [
    rg.FeedbackRecord(
        fields={
            "text": "I am so happy today",
        },
    ),
    rg.FeedbackRecord(
        fields={
            "text": "I feel sad today",
        },
    )
]
dataset.add_records(records)
```
You can also use `pandas` or `load_dataset` to read an existing dataset and create records like above.

We hope you enjoy using Argilla as much as we enjoyed building it. If you have any questions, don't hesitate to contact us at the [Argilla Slack community](https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g). We'd love to hear from you! 🙌