---
description: This is a step-by-step guide to help you contribute to the Argilla project as a developer. We are excited to have you on board! 🚀
hide:
 - footer
---

As an Argilla developer, you are already part of the community, and your contribution is to our development. This guide will help you set up your development environment and start contributing.

!!! note "Argilla core components"

    - **Documentation**: Argilla's documentation serves as an invaluable resource, providing a comprehensive and in-depth guide for users seeking to explore, understand, and effectively harness the core components of the Argilla ecosystem.

    - **Python SDK**: A Python SDK installable with `pip install argilla` to interact with the Argilla Server and the Argilla UI. It provides an API to manage the data, configuration, and annotation workflows.

    - **FastAPI Server**: The core of Argilla is a Python `FastAPI server` that manages the data by pre-processing it and storing it in the vector database. Also, it stores application information in the relational database. It provides an REST API that interacts with the data from the Python SDK and the Argilla UI. It also provides a web interface to visualize the data.

    - **Relational Database**: A relational database to store the metadata of the records and the annotations. `SQLite` is used as the default built-in option and is deployed separately with the Argilla Server, but a separate `PostgreSQL` can be used.

    - **Vector Database**: A vector database to store the records data and perform scalable vector similarity searches and basic document searches. We currently support `ElasticSearch` and `OpenSearch`, which can be deployed as separate Docker images.

    - **Vue.js UI**: A web application to visualize and annotate your data, users, and teams. It is built with `Vue.js` and is directly deployed alongside the Argilla Server within our Argilla Docker image.


## The Argilla repository

The Argilla repository has a monorepo structure, which means that all the components are located in the same repository: [`argilla-io/argilla`](https://github.com/argilla-io/argilla). This repo is divided into the following folders:

- [`argilla`](https://github.com/argilla-io/argilla/tree/develop/argilla): The python SDK project
- [`argilla-server`](https://github.com/argilla-io/argilla/tree/develop/argilla-server): The FastAPI server project
- [`argilla-frontend`](https://github.com/argilla-io/argilla/tree/develop/argilla-frontend): The Vue.js UI project
- [`argilla/docs`](https://github.com/argilla-io/argilla/tree/develop/argilla/docs): The documentation project
- [`examples`](https://github.com/argilla-io/argilla/tree/develop/examples): Example resources for deployments, scripts and notebooks

!!! note "How to contribute?"
    Before starting to develop, we recommend reading our [contribution guide](contributor.md) to understand the contribution process and the guidelines to follow. Once you have [cloned the Argilla repository](contributor.md#fork-the-argilla-repository) and [checked out to the correct branch](contributor.md#create-a-new-branch), you can start setting up your development environment.


## Set up the Python environment

To work on the Argilla Python SDK, you must install the Argilla package on your system.

!!! tip "Create a virtual environment"
    We recommend creating a dedicated virtual environment for SDK development to prevent conflicts. For this, you can use the manager of your choice, such as `venv`, `conda`, `pyenv`, or `uv`.

From the root of the cloned Argilla repository, you should move to the `argilla` folder in your terminal.

```sh
cd argilla
```

Next, activate your virtual environment and make the required installations:

```sh
# Install the `pdm` package manager
pip install pdm

# Install argilla in editable mode and the development dependencies
pdm install --dev
```

### Linting and formatting

To maintain a consistent code format, install the `pre-commit` hooks to run before each commit automatically.

```sh
pre-commit install
```

In addition, run the following scripts to check the code formatting and linting:

```sh
pdm run format
pdm run lint
```

### Running tests

Running tests at the end of every development cycle is indispensable to ensure no breaking changes.

```sh
# Run all tests
pdm run tests

# Run specific tests
pytest tests/integration
pytest tests/unit
```

??? tip "Running linting, formatting, and tests"
    You can run all the checks at once by using the following command:

    ```sh
        pdm run all
    ```

## Set up the databases

To run your development environment, you need to set up Argilla's databases.

#### Vector database

Argilla supports ElasticSearch as its primary search engine for the vector database by default. For more information about setting OpenSearch, check the [Server configuration](../reference/argilla-server/configuration.md).

You can run ElasticSearch locally using Docker:

```sh
# Argilla supports ElasticSearch versions >=8.5
docker run -d --name elasticsearch-for-argilla -p 9200:9200 -p 9300:9300 -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" -e "discovery.type=single-node" -e "xpack.security.enabled=false" docker.elastic.co/elasticsearch/elasticsearch:8.5.3
```

!!! tip "Install Docker"
    You can find the Docker installation guides for [Windows](https://docs.docker.com/desktop/install/windows-install/), [macOS](https://docs.docker.com/desktop/install/mac-install/) and [Linux](https://docs.docker.com/desktop/install/linux-install/) on Docker website.

#### Relational database

Argilla will use SQLite as the default built-in option to store information about users, workspaces, etc., for the
relational database. No additional configuration is required to start using SQLite.

By default, the database file will be created at `~/.argilla/argilla.db`; this can be configured by setting different
values for `ARGILLA_DATABASE_URL` and `ARGILLA_HOME_PATH` environment variables.

!!! note "Manage the database"
    For more information about the database migration and user management, refer to the [Argilla server README](https://github.com/argilla-io/argilla/blob/develop/argilla-server/README.md).


## Set up the server

Once you have set up the databases, you can start the Argilla server. To run the server, you can check the [Argilla server README](https://github.com/argilla-io/argilla/blob/develop/argilla-server/README.md) file.

## Set up the frontend

Optionally, if you need to run the Argilla frontend, you can follow the instructions in the [Argilla frontend README](https://github.com/argilla-io/argilla/blob/develop/argilla-frontend/README.md).


## Set up the documentation

Documentation is essential to provide users with a comprehensive guide about Argilla.

!!! note "From `main` or `develop`?"
    If you are updating, improving, or fixing the current documentation without a code change, work on the `main` branch. For new features or bug fixes that require documentation, use the `develop` branch.

To contribute to the documentation and generate it locally, ensure you installed the development dependencies as shown in the ["Set up the Python environment"](#set-up-the-python-environment) section, and run the following command to create the development server with `mkdocs`:

```sh
mkdocs serve
```

### Documentation guidelines

As mentioned, we use [`mkdocs`](https://www.mkdocs.org/) to build the documentation. You can write the documentation in [`markdown`](https://www.markdownguide.org/getting-started/) format, and it will automatically be converted to HTML. In addition, you can include elements such as tables, tabs, images, and others, as shown in this [guide](https://squidfunk.github.io/mkdocs-material/reference/). We recommend following these guidelines:

- **Use clear and concise language**: Ensure the documentation is easy to understand for all users by using straightforward language and including meaningful examples. Images are not easy to maintain, so use them only when necessary and place them in the appropriate folder within the `docs/assets/images` directory.
- **Verify code snippets**: Double-check that all code snippets are correct and runnable.
- **Review spelling and grammar**: Check the spelling and grammar of the documentation.
- **Update the table of contents**: If you add a new page, include it in the relevant `index.md` or the `mkdocs.yml` file.

!!! note "Contribute with a tutorial"
    You can also contribute a tutorial (`.ipynb`) to the "Community" section. We recommend aligning the tutorial with the structure of the existing tutorials. For an example, check [this tutorial](../tutorials/text_classification.ipynb).
