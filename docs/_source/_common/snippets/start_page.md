Welcome to Argilla! 👋😁 We're thrilled to have you on board. Beginning with Argilla is as simple as it gets, and you've successfully taken the first step!

To start using Argilla, you need to create your first dataset. Let's get started. 🚀

[For in-depth user guides, check the documentation 📖.](https://docs.argilla.io/en/latest/)

## 1. Open an IDE, Jupyter or Collab

Open your favorite IDE, Jupyter or Collab. If you're a Collab user, you can directly use our [introductory tutorial](https://colab.research.google.com/github/argilla-io/argilla/blob/develop/docs/_source/getting_started/quickstart_workflow_feedback.ipynb).

## 2. Install the SDK with pip

To upload and read datasets from Argilla, you need to use the Argilla SDK. You can install the SDK with pip as follows:

```sh
pip install argilla -U
```

## 3. Connect to your Argilla server

1. Get your `ARGILLA_API_URL`:

   * If you are using Docker, it is the URL shown in your browser (by default `http://localhost:6900`)
   * If you are using HF Spaces, it should be constructed as follows: `https://[your-owner-name]-[your_space_name].hf.space`

2. Get your `ARGILLA_API_KEY` by clicking on your user icon in the top right corner of the Argilla UI, selecting ["My settings"](/user_settings) and copying the API key.

3. Connect the SDK with the server using `rg.init`. Make sure to replace `ARGILLA_API_URL` and `ARGILLA_API_KEY` with the values you obtained in the previous steps. If you are using a private HF Space, you also need to specify your `HF_TOKEN` that can be found [here](https://huggingface.co/settings/tokens).

```python
import argilla as rg

rg.init(
    api_url="ARGILLA_API_URL",
    api_key="ARGILLA_API_KEY",
    # extra_headers={"Authorization": f"Bearer {"HF_TOKEN"}"}
)
```

## 4. Create your first dataset

1. Specify a workspace where the dataset is to be saved and authorized users can collaborate. You can check your workspaces in the Argilla UI by clicking on "My settings". If you want to create a new workspace, check the [docs](https://docs.argilla.io/en/latest/getting_started/installation/configurations/workspace_management.html).

```python
rg.set_workspace("<your-workspace>")
```

1. Create a Dataset with two labels ("sadness" and "joy"). Don't forget to replace "<your-workspace>" with the workspace you want to use. In this example, we are using a default task template, check the docs to [create a fully custom dataset](https://docs.argilla.io/en/latest/practical_guides/create_update_dataset/create_dataset.html).

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

You can also use `pandas` or `load_dataset` to [read an existing dataset and create records like belows](https://docs.argilla.io/en/latest/practical_guides/create_update_dataset/records.html#add-records).

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

If you have any question, contact us at the [Argilla Slack community](https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g). We'd love to hear from you! 🙌
