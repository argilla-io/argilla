## `argilla-sdk`

The argilla-sdk is an experimental project to rebuild Argilla's python client in a simpler and friendlier way. The goal is to have a minimal set of core features that are easy to use and understand, but also contribute to feedback task that build quality data.

!!! warning
    This project is still in development and is not yet ready for production use.

### Installation

Since this package is not yet published on PyPi, you can install it directly from the repository:

# TODO: Changed this to use the testpypi releases.
```console
pip install git+https://github.com/argilla-io/argilla-python.git
```

### Usage

To use the client, you need to import the `Argilla` class and instantiate it with the API URL and API key. You can use this SDK with any stable release of argilla server >= 1.27.

```python
import argilla as rg

client = rg.Argilla(api_url="http://localhost:6900", api_key="argilla.apikey")
```

### Developer documentation

If you want to contribute to the development of the SDK, you can follow the instructions below.

#### Installation

To install the development dependencies, run the following command:

```console
# install pdm https://github.com/pdm-project/pdm
pip install pdm

# install the package in editable mode
pip install -e .

# install the development dependencies with pdm
pdm install --dev
```

#### Generating Documentation

To generate the docs you will need to install the development dependencies, and run the following command to create the development server with `mkdocs`:

```console
mkdocs serve
```

You will find the built documentation in `http://localhost:8000/argilla-python/`.

The docs will be deployed for pull request branches automatically.
