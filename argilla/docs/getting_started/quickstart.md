---
description: Get started with Argilla in under 10 minutes
---

# Quickstart

Argilla is a free, open-source, self-hosted tool. This means you need to deploy its server to start using it. There is two main ways to deploy Argilla:

!!! huggingface "Deploy on the Hugging Face Hub"

    The **recommended choice to get started**. You can get up and running in under 5 minutes and don't need to maintain a server or run any commands. 
    
    If you're just getting started with Argilla, you need to click the button below and:

    - Leave the default Space owner (your personal account)
    - Leave the `USERNAME` and `PASSWORD` Space secrets empty, you'll be able to sign in as Argilla owner with your HF user so you don't need a username and password.
    - Set the Space to public, click create Space to launch Argilla 🚀.
    - It will take a couple of minutes and once you see the Argilla UI [go to this section](#sign-in-into-the-argilla-ui)

    <div style="margin: 5px">
	<a href="http://huggingface.co/new-space?template=argilla/argilla-template-space" target="_blank">
	    <img src="https://huggingface.co/datasets/huggingface/badges/raw/main/deploy-to-spaces-lg.svg" />
	</a>
    </div>

    !!! warning "Persistent storage"
        Not setting persistent storage to `Small` means that **you will loose your data when the Space restarts**. Spaces get restarted due to maintainance, inactivity, and every time you change your Spaces settings. 
        
        If you plan to **use the Argilla Space beyond testing**, it's highly recommended to **set persistent storage to `Small`**.
    If you want to deploy Argilla within a Hugging Face organization, setup a more stable Space, or understand the settings, [check out the HF Spaces settings guide](how-to-configure-argilla-on-huggingface.md).

!!! docker "Deploy with Docker"
     If you want to run Argilla locally on your machine or a server, or tune the server configuration, choose this option. To use this option, [check this guide](how-to-deploy-argilla-with-docker.md).

## Sign in into the Argilla UI
If everything went well, you should see the Argilla sign in page that looks like this:

**TODO** add login page image

!!! info "Building errors"
    If you get a build error, sometimes restarting the Space from the Settings page works, otherwise [check the HF Spaces settings guide](how-to-configure-argilla-on-huggingface.md).


You need to:

1. Click on **Sign in with Hugging Face**
2. **Authorize the application** and you should see the home page of Argilla

!!! info "Unauthorized error"
    Sometimes, after granting permissions you'll see an unauthorized error, and get redirected to the sign in page. Typically, clicking the Sign in button solves the issue.

Congrats! Your Argilla server is ready to start your first project using the Python SDK. Follow the instructions in the home page, or keep reading this guide if you want a more detailed explanation.

## Install the Python SDK

To manage users, workspaces, and datasets in Argilla, you need to use the Argilla Python SDK. You can install it with pip as follows:

```console
pip install argilla
```

## Create your first dataset using the SDK
For getting started with Argilla and its SDK, we highly recommend you to use Jupyter Notebook or online notebooks like Google Colab.

To start interacting with your Argilla server, you need to create a client using the API key and the API URL of your Argilla Server. 

You can find your `<api_key>` in the `My Settings` page of your Argilla 

The `<api_url>` is the URL shown in your browser if it ends with `*.hf.space`.

!!! info "Find out your API URL"
    If you're using Spaces, sometimes the Argilla UI is embedded into the Hub UI so the URL of the browser won't match the API URL. In these scenarios, there are two options:
        1. Click on the three points menu at the top of the Space, select "Embed this Space", and open the direct URL.
        2. Write it following this pattern: `https://[your-owner-name]-[your_space_name].hf.space`.  

!!! note
    Make sure to replace `<api_url>` and `<api_key>` with your actual values.

Then run:

```python
import argilla as rg

client = rg.Argilla(
    api_url="<api_url>",
    api_key="<api_key>"
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

## More references

* [Installation guide](installation.md)
* [How-to guides](../how_to_guides/index.md)
* [API reference](../reference//argilla/client.md)
