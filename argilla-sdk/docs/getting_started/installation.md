---
description: Installation of Argilla-python.
---

# Installation

## Install the SDK with pip

Since this package is not yet published on PyPi, you can install it directly from the repository:

```console
pip install git+https://github.com/argilla-io/argilla-python.git
```

## Run the Argilla server

If you have already deployed Argilla Server, you can skip this step. Otherwise, you can quickly deploy it in two different ways:

!!! note
    You can use this SDK with any stable release of argilla server >= 1.27.

* Using a [HF Space](https://huggingface.co/new-space?template=argilla/argilla-template-space).
* Locally with Docker.

```console
docker run -d --name quickstart -p 6900:6900 argilla/argilla-quickstart:latest
```

## Connect to the Argilla server

Get your `<api_url>`:

* If you are using HF Spaces, it should be constructed as follows: `https://[your-owner-name]-[your_space_name].hf.space`
* If you are using Docker, it is the URL shown in your browser (by default `http://localhost:6900`)

Get your `<api_key>` in `My Settings` in the Argilla UI (by default owner.apikey).

!!! note
    Make sure to replace `<api_url>` and `<api_key>` with your actual values. If you are using a private HF Space, you need to specify your `HF_TOKEN` which can be found [here](https://huggingface.co/settings/tokens).

```python
import argilla_sdk as rg

client = rg.Argilla(
    api_url="<api_url>",
    api_key="<api_key>",
    # extra_headers={"Authorization": f"Bearer {HF_TOKEN}"}
)
```

## Developer documentation

If you want to contribute to the development of the SDK, you can follow the instructions below.

### Installation

To install the development dependencies, run the following commands:

```console
# Install pdm (https://github.com/pdm-project/pdm)
pip install pdm

# Install the package in editable mode
pip install -e .

# Install the development dependencies with pdm
pdm install --dev
```

### Generating documentation

To generate the docs you will need to install the development dependencies, and run the following command to create the development server with `mkdocs`:

```console
mkdocs serve
```

You will find the built documentation in `http://localhost:8000/argilla-python/`.
