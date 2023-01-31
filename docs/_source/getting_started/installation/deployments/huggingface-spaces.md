# Hugging Face Spaces

Argilla nicely integrates with the Hugging Face stack (`datasets`, `transformers`, `hub`, and `setfit`), and now it can also be deployed using the Hub's Spaces.

In this guide, you'll learn to deploy your own Argilla app and use it for data labelling workflows right from the Hub.

In the next sections, you'll learn to deploy your own Argilla app and use it for data labelling workflows right from the Hub.

## Your first Argilla Space

In this section, you'll learn to deploy an Argilla Docker Space and use it for data annotation and training a sentiment classifier with [SetFit](https://github.com/huggingface/setfit/), a few-shot learning library.

You can find the final app at [this example Space](https://huggingface.co/spaces/dvilasuero/argilla-setfit) and the step-by-step tutorial in this [notebook](https://colab.research.google.com/drive/1GeBBuRw8CIZ6SYql5Vdx4Q2Vv74eFa1I?usp=sharing).

### Duplicate the Argilla Space Template and create your Space

The easiest way to get started is by [duplicating the Argilla Docker Template](https://huggingface.co/spaces/argilla/template-space-docker?duplicate=true). You need to define the **Owner** (your personal account or an organization you are part of), a **Space name**, and the **Visibility**, which we recommend to set up to Public if you want to interact with the Argilla app from the outside. Once you are all set, click "Duplicate Space".

<div class="flex justify-center">
<img src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/spaces-argilla-duplicate-space.png"/>
</div>

<Tip>
Although you can duplicate other existing Argilla Spaces, we recommend starting from the official [Argilla Docker Template](https://huggingface.co/spaces/argilla/template-space-docker?duplicate=true).
</Tip>

Note: You'll see a mention to the need of setting up environment variables (`API_KEY`) by adding a secret to your Space but will see this in a second.

### Setting up secret environment variables

The Space template provides a way to set up different **optional settings** focusing on securing your Argilla Space.

<Tip>
For quick experiments or you want others to see what datasets you've built, you can completely skip this step. If you do this, the default values from the [basic Argilla setup](https://docs.argilla.io/en/latest/getting_started/installation/installation.html) will be kept.
</Tip>

In order to set up these secrets, you need to go to the Settings tab on your newly created Space and make sure to remember these values for later use.

By default the Argilla Space has two users: `team` and `argilla`. The username `team` corresponds to the root user, who can upload datasets and access any workspace on your Argilla Space. The username `argilla` corresponds to a normal user, who has access to the `team` workspace and its own workspace called `argilla`.

Currently, these user names cannot be configured, but their passwords and API keys to upload, read, update, and delete datasets can be configured. The available secrets are following:

- `ARGILLA_API_KEY`: Argilla provides a Python library to interact with the app (read, write, and update data, log model predictions, etc.). If you don't set this variable, the library and your app will use the default API key. If you want to secure your Space for reading and writing data, we recommend you to set up this variable. The API key you choose can be any string of your choice and you can check an online generator if you like.

- `ARGILLA_PASSWORD`: This sets a custom password for login into the app with the `argilla` username. The default password is `1234`. By setting up a custom password you can use your own password to login into the app.

- `TEAM_API_KEY`: This sets the root user's API key. The API key you choose can be any string of your choice and you can check an online generator if you like.

- `TEAM_PASSWORD`: This sets a custom password for login into the app with the `argilla` username. The default password is `1234`. By setting up a custom password you can use your own password to login into the app.

The combination of these secret variables gives you the following setup options:

1. *I want to avoid that anyone without the API keys can add, delete, or update datasets using the Python client*: You need to setup `ARGILLA_API_KEY` and `TEAM_API_KEY`.
2. *Additionally, I want to avoid that the `argilla` username can delete datasets from the UI*: You need to setup `TEAM_PASSWORD` and use `TEAM_API_KEY` with the Python Client. This option might be interesting if you want to control dataset management but want anyone to browse your datasets using the `argilla` user.
3. *Additionally, I want to avoid that anyone without password can browse my datasets with the `argilla` user*: You need to setup `ARGILLA_PASSWORD`. In this case, you can use `ARGILLA_API_KEY` and/or `TEAM_API_KEY` with the Python Client depending on your needs for dataset deletion rights.

### Create your first dataset

Once your Argilla Space is running, you can start interacting with the it using the Direct URL you'll find in the "Embed this Space" option (top right). Let's say it's https://dvilasuero-argilla-setfit.hf.space. This URL will give you access to a full-screen, stable Argilla app, but will also serve as an endpoint for interacting with Argilla Python library.

<Tip>
You'll see the login screen where you need to use either `argilla` or `team` with the default passwords or the ones you've set up using secrets. If you get a `500` error when introducing the credentials, make sure you have correctly hashed the password before adding it to the secret environment variable.
</Tip>

If this is working, you are ready to start using the Argilla Python client from a Python IDE such as Colab, Jupyter, or VS Code, to upload your own datasets.

Let's see how to create our first dataset for labelling. From this point on, you can follow the tutorial using this end-to-end tutorial [Colab notebook](https://colab.research.google.com/drive/1GeBBuRw8CIZ6SYql5Vdx4Q2Vv74eFa1I?usp=sharing).

<Tip>
If you don't want to use Colab or install anything on your local machine, you can [duplicate the Jupyter Lab Space]() and run all your code there.
</Tip>

<div class="flex justify-center">
<img src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/spaces-argilla-embed-space.png"/>
</div>

First we need to pip install `datasets` and `argilla` on Colab or your local machine:

```bash
pip install datasets argilla
```

Then, you can read the example dataset using the `datasets` library (this dataset is just a CSV file uploaded to the Hub using the drag and drop feature).

```python
from datasets import load_dataset

dataset = load_dataset("dvilasuero/banking_app", split="train").shuffle()
```

Now you can create your first dataset by logging it into Argilla using your endpoint URL and (optionally) `API_KEY`:

```python
import argilla as rg

# connect to your app endpoint
rg.init(api_url="https://dvilasuero-argilla-setfit.hf.space", api_key="YOUR_SECRET_API_KEY")

# transform dataset into Argilla's format and log it
rg.log(rg.read_datasets(dataset, task="TextClassification"), name="bankingapp_sentiment")
```

If everything went well, you now have a dataset available from the Argilla UI to start browsing and labelling. In the code above, we've used one of the many integrations with Hugging Face libraries, which let you [read hundreds of datasets](https://docs.argilla.io/en/latest/guides/features/datasets.html#Importing-a-Dataset) available on the Hub.

### Data labelling and model training

At this point, you can label your data directly using your Argilla Space and read the training data to train your model of choice. In this [Colab notebook](https://colab.research.google.com/drive/1GeBBuRw8CIZ6SYql5Vdx4Q2Vv74eFa1I?usp=sharing), you can follow the full step-by-step tutorial, but let's see how we can retrieve data from our interactive data annotation session, and the code need to train a SetFit model.

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

## Feedback and support

If you have improvement suggestions or need specific support, please join [Argilla Slack community](https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g) or reach out on [Argilla's GitHub repository](https://github.com/argilla-io/argilla).