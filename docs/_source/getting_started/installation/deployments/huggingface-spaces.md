# Hugging Face Hub Spaces

Argilla nicely integrates with the Hugging Face stack (`datasets`, `transformers`, `hub`, and `setfit`), and now it can also be deployed using the Hub's Spaces.

In this guide, you'll learn to deploy your own Argilla app and use it for data labelling workflows right from the Hub.

## Your first Argilla Space

In this section, you'll learn to deploy an Argilla Space and use it for data annotation and training a sentiment classifier with [SetFit](https://github.com/huggingface/setfit/), an amazing few-shot learning library.

### Deploy Argilla on Spaces

You can deploy Argilla on Spaces with just a few clicks:

<a  href="https://huggingface.co/spaces/argilla/argilla-template-space">
    <img src="https://huggingface.co/datasets/huggingface/badges/raw/main/deploy-to-spaces-lg.svg" />
</a>

You need to define the **Owner** (your personal account or an organization), a **Space name**, and the **Visibility**. To interact with the Argilla app with Python, you need to setup the visibility to `Public`.

<div class="flex justify-center">
<img src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/spaces-argilla-duplicate-space.png"/>
</div>

You'll see the `Building` status and once it becomes `Running` your space is ready to go. If you don't see the Argilla login UI refresh the page.

For quick experimentation, you can jump directly into the next section. If you want to add access restrictions, go to the "Setting up secret environment variables" at the end of this document. Setting up secret variables is recommended for longer-term usage.


```{admonition} Tip
:class: important

    If you want to customize the title, emojis, and colors of your space, go to "Files and Versions" and edit the metadata of your README.md file.

```

### Create your first dataset

Once Argilla is running, you can use the UI with the Direct URL you'll find in the "Embed this Space" option (top right). You'll see a URL like this: `https://dvilasuero-argilla-setfit.hf.space`. This URL gives you access to a full-screen, stable Argilla instance, and is the `api_url` for reading and writing datasets using the Argilla Python library.

<div class="flex justify-center">
<img src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/spaces-argilla-embed-space.png"/>
</div>


```{admonition} Tip
:class: important

    You'll see the login screen where you need to use either argilla or team with the default passwords (1234). Remember you can change the passwords using secret variables. If you get a 500 error when introducing the credentials, make sure you have correctly introduce the password.

```


If everything went well, you are ready to use the Argilla Python client from an IDE such as Colab, Jupyter, or VS Code.

If you want to a quick step-by-step example, keep reading. If you want an end-to-end tutorial, go to this [tutorial and use Colab or Jupyter](https://docs.argilla.io/en/latest/tutorials/notebooks/training-textclassification-setfit-fewshot.html).

Let's create our first dataset for labelling!

First we need to pip install `datasets` and `argilla` on Colab or your local machine:

```bash
pip install datasets argilla
```

Then, you can read the example dataset using the `datasets` library. This dataset is a CSV file uploaded to the Hub using the drag and drop feature.

```python
from datasets import load_dataset

dataset = load_dataset("dvilasuero/banking_app", split="train").shuffle()
```

You can create your first dataset by logging it into Argilla using your endpoint URL:

```python
import argilla as rg

# connect to your app endpoint (uses default team API key)
rg.init(api_url="[your_space_url]", api_key="team.apikey")

# transform dataset into Argilla's format and log it
rg.log(rg.read_datasets(dataset, task="TextClassification"), name="bankingapp_sentiment")
```

Congrats! You now have a dataset available from the Argilla UI to start browsing and labelling. In the code above, we've used one of the many integrations with Hugging Face libraries, which let you [read hundreds of datasets](https://docs.argilla.io/en/latest/guides/features/datasets.html#Importing-a-Dataset) available on the Hub.

### Data labelling and model training

At this point, you can label your data directly using your Argilla Space and read the training data to train your model of choice.

```python
# this will read our current dataset and turn it into a clean dataset for training
dataset = rg.load("bankingapp_sentiment").prepare_for_training()
```

You can also get the full dataset and push it to the Hub for reproducibility and versioning:

```python
# save full argilla dataset for reproducibility
rg.load("bankingapp_sentiment").to_datasets().push_to_hub("bankingapp_sentiment")
```

Finally, this is how you can train a SetFit model using data from your Argilla Space:

```python
from sentence_transformers.losses import CosineSimilarityLoss

from setfit import SetFitModel, SetFitTrainer

# Create train test split
dataset = dataset.train_test_split()

# Load SetFit model from Hub
model = SetFitModel.from_pretrained("sentence-transformers/paraphrase-mpnet-base-v2")

# Create trainer
trainer = SetFitTrainer(
    model=model,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    loss_class=CosineSimilarityLoss,
    batch_size=8,
    num_iterations=20,
)

# Train and evaluate
trainer.train()
metrics = trainer.evaluate()
```

As a next step, you can check the [Argilla Tutorials](https://docs.argilla.io/en/latest/tutorials/tutorials.html) section. All the tutorials can be run using Colab or local Jupyter Notebooks, so you can start building datasets with Argilla and Spaces!

## Feedback and support

If you have improvement suggestions or need specific support, please join [Argilla Slack community](https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g) or reach out on [Argilla's GitHub repository](https://github.com/argilla-io/argilla).

## Setting up secret environment variables

The Space template provides a way to set up different **optional settings** focusing on securing your Argilla Space.

To set up these secrets, you can go to the Settings tab on your created Space. Make sure to save these values somewhere for later use.

The template space has two users: `team` and `argilla`. The username `team` corresponds to the root user, who can upload datasets and access any workspace within your Argilla Space. The username `argilla` is a normal user with access to the `team` workspace and its own workspace called `argilla`.

Currently, these user names can't be configured. The passwords and API keys to upload, read, update, and delete datasets can be configured using the following secrets:

- `ARGILLA_API_KEY`: Argilla provides a Python library to interact with the app (read, write, and update data, log model predictions, etc.). If you don't set this variable, the library and your app will use the default API key. If you want to secure your Space for reading and writing data, we recommend you to set up this variable. The API key you choose can be any string of your choice and you can check an online generator if you like.

- `ARGILLA_PASSWORD`: This sets a custom password for login into the app with the `argilla` username. The default password is `1234`. By setting up a custom password you can use your own password to login into the app.

- `TEAM_API_KEY`: This sets the root user's API key. The API key you choose can be any string of your choice and you can check an online generator if you like.

- `TEAM_PASSWORD`: This sets a custom password for login into the app with the `team` username. The default password is `1234`. By setting up a custom password you can use your own password to login into the app.

The combination of these secret variables gives you the following setup options:

1. *I want to avoid that anyone without the API keys can add, delete, or update datasets using the Python client*: You need to setup `ARGILLA_API_KEY` and `TEAM_API_KEY`.
2. *Additionally, I want to avoid that the `argilla` username can delete datasets from the UI*: You need to setup `TEAM_PASSWORD` and use `TEAM_API_KEY` with the Python Client. This option might be interesting if you want to control dataset management but want anyone to browse your datasets using the `argilla` user.
3. *Additionally, I want to avoid that anyone without password can browse my datasets with the `argilla` user*: You need to setup `ARGILLA_PASSWORD`. In this case, you can use `ARGILLA_API_KEY` and/or `TEAM_API_KEY` with the Python Client depending on your needs for dataset deletion rights.

Additionally, the `LOAD_DATASETS` will let you configure the sample datasets that will be pre-loaded. The default value is `single` and the supported values for this variable are:
    1. `single`: Load single datasets for TextClassification task.
    2. `full`: Load all the sample datasets for NLP tasks (TokenClassification, TextClassification, Text2Text)
    3. `none`: No datasets being loaded.