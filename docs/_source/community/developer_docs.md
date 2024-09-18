# Developer Documentation

Being a developer in Argilla means that you are a part of the Argilla community, and you are contributing to the
development of Argilla. This page will guide you through the steps that you need to take to set up your development
environment and start contributing to Argilla. Argilla is built upon different core components:

- **Documentation**: The documentation for Argilla serves as an invaluable resource, providing a comprehensive and
in-depth guide for users seeking to explore, understand, and effectively harness the core components of the Argilla
ecosystem.

- **Python SDK**: A Python SDK which is installable with `pip install argilla`, to interact with the Argilla Server and
the Argilla UI. It provides an API to manage the data, configuration, and annotation workflows.

- **FastAPI Server**: The core of Argilla is a Python `FastAPI server` that manages the data, by pre-processing it and
storing it in the vector database. Also, it stores application information in the relational database. It provides a
REST API to interact with the data from the Python SDK and the Argilla UI. It also provides a web interface to visualize
the data.

- **Relational Database**: A relational database to store the metadata of the records and the annotations. `SQLite` is
used as the default built-in option and is deployed separately with the Argilla Server but a separate `PostgreSQL`
can be used too.

- **Redis**: [Redis](https://redis.io) is used to store information about background jobs and it's a required dependency of Argilla server.

- **Vector Database**: A vector database to store the records data and perform scalable vector similarity searches and
basic document searches. We currently support `ElasticSearch` and `AWS OpenSearch` and they can be deployed as separate
Docker images.

- **Vue.js UI**: A web application to visualize and annotate your data, users, and teams. It is built with `Vue.js` and
is directly deployed alongside the Argilla Server within our Argilla Docker image.

The Argilla repository has a monorepo structure, which means that all the components live in the same repository:
`argilla-io/argilla`. This repo is divided into the following folders:

- [`argilla`](/argilla): The python SDK project
- [`argilla-server`](/argilla-server): The FastAPI server project
- [`argilla-frontend`](/argilla-frontend): The Vue.js UI project
- [`docs`](/docs): The documentation project
- [`examples`](/examples): Example resources for deployments, scripts and notebooks

For a proper installation, you will need to:

- [Set up the Documentation Environment](#set-up-the-documentation-environment),
- [Set up the Python Environment](#set-up-the-python-environment),
- [Set up the Databases](#set-up-the-databases),
- [Set up the Frontend](#set-up-the-frontend),
- [Set up the Server](#set-up-the-server),

And, you can start to [make your contribution](#make-your-contribution)!

## Set up the Documentation Environment

To kickstart your journey in contributing to Argilla, immersing yourself in the documentation is highly recommended. To
do so, we recommend you create a virtual environment and follow the steps below. To build the documentation, a reduced
set of dependencies is needed.

### Clone the Argilla Repository

First of all, you have to fork our repository and clone the fork to your computer. For more information, you can check
our [guide](/community/contributing.md#work-with-a-fork).

```sh
git clone https://github.com/[your-github-username]/argilla.git
cd argilla
```

To keep your fork’s main branch up to date with our repo you should add it as an [upstream remote branch](https://dev.to/louhayes3/git-add-an-upstream-to-a-forked-repo-1mik):

```sh
git remote add upstream https://github.com/argilla-io/argilla.git
```

> Remember that to work on documentation, you'll work using a branch created from `main`.

### Install Dependencies

To build the documentation, make sure you set up your system by installing the required dependencies.

```sh
pip install -r docs/_source/requirements.txt
```

During the installation, you may encounter the following error: Microsoft Visual C++ 14.0 or greater is required. To
solve it easily, check this [link](https://learn.microsoft.com/en-us/answers/questions/136595/error-microsoft-visual-c-14-0-or-greater-is-requir).

### Build the documentation

To build the documentation, it is used [`sphinx`](https://www.sphinx-doc.org/en/master/),an open-source documentation generator, that is, it uses
reStructuredText for writing documentation. Using Sphinx's command-line tool, it takes a collection of source files
in plain text and generate them in HTML format. It also automatically creates a table of contents, index pages, and
search features, enhancing navigation. To do so, the following files are required:

- **index.rst**: This serves as the main entry point for our documentation, accessible at the root URL. It typically
includes a table of contents (using the toc trees), connecting users to other documentation sections.
- **conf.py**: This file enables customization of the documentation's output.
- **Makefile**: A crucial component provided by Sphinx, serving as the primary tool for local development.
- **Other .rst files**: These are intended for specific subsections of the documentation.
- **Markdown files**: The source files with plain text.

In our case, we rely on [`MyST-Parser`](https://myst-parser.readthedocs.io/en/latest/) to facilitate our work with Markdown. So, it's essential that when writing
the documentation, we utilize [proper cross-references](https://docs.readthedocs.io/en/stable/guides/cross-referencing-with-sphinx.html) to connect various sections and documents. Below, you can
find a typical illustration of commonly used cross-references:

```md
# To reference a previous section

[](#explicit-targets).

# To reference a section in another document

(my_target)= ## Explicit targets
Reference [](my_target).

# To add explicit references

- {ref}`my target`.
- {ref}`Target to paragraph <target_to_paragraph>`.

# To link to a page in the same directory

- {doc}`reference`
- {doc}`/guides/reference`
- {doc}`Custom title </guides/reference>`
```

So, once the documentation is written or fixed, if the installation was smooth, then use `sphinx-autobuild` to
continuously deploy the webpage using the following command:

```sh
sphinx-autobuild docs/_source docs/_build/html
```

This will create a _build/html folder that is served at [http://127.0.0.1:8000](http://127.0.0.1:8000). Also, it starts watching for
changes in the docs/source directory. When a change is detected in docs/source, the documentation is rebuilt and any
open browser windows are reloaded automatically. Make sure that all files are indexed correctly. KeyboardInterrupt (ctrl+c)
will stop the server. Below is an example of the server output running and stopping:

```sh
The HTML pages are in docs\_build\html.
[I 231024 10:58:36 server:335] Serving on http://127.0.0.1:8000
[I 231024 10:58:36 handlers:62] Start watching changes
[I 231024 10:58:36 handlers:64] Start detecting changes
[I 231024 11:00:53 server:358] Shutting down...
```

> **Troubleshooting**
> If you get warnings while building documentation then you can handle them this way:
>
> - If they are toctree or title underline warnings then they can be ignored.
> - If they are import errors then they can be resolved by reinstalling autodoc and argilla from docs/\_source/requirements.txt

## Set up the Development Environment

To work and develop for the core product of Argilla, you need to have all of Argilla's subsystem correctly running. In
this section, we'll show how to install the Argilla package, the databases and the server. The frontend is optional
and only required for running the UI, but you can also find how to run it here.

### Creating the Python Environment

#### Clone the Argilla Repository

To set up your system for Argilla development, you, first of all, have to [fork](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) our repository and [clone](https://github.com/argilla-io/argilla)
the fork to your computer.

```sh
git clone https://github.com/[your-github-username]/argilla.git
cd argilla
```

To keep your fork’s main/develop branch up to date with our repo you should add it as an [upstream remote branch](https://dev.to/louhayes3/git-add-an-upstream-to-a-forked-repo-1mik):

```sh
git remote add upstream https://github.com/argilla-io/argilla.git
```

#### Install Dependencies

You will need to install `argilla` and the extra dependencies that you prefer to be able to use Argilla in your Python
client or Command Line Interface (CLI). There are two ways to install it and you can opt for one of them depending on
your use case:

- Install `argilla` with `pip`: Recommended for non-extensive, one-time contributions as it will only install the
required packages.

- Install `argilla` with `conda`: Recommended for comprehensive, continuous contributions as it will create an
all-inclusive environment for development.

##### Install with `pip`

If you choose to install Argilla via `pip`, you can do it easily on your terminal. Firstly, direct to the `argilla`
folder in your terminal by:

```sh
cd argilla
```

Now, it is recommended to create a Python virtual environment, following these commands:

```sh
python -m venv .env
source .env/bin/activate
```

Then, you just need to install Argilla with the command below. Note that we will install it in editable mode using the
-e/--editable flag in the `pip` command to avoid having to re-install it on every code modification, but if you’re not
planning to modify the code, you can just omit the -e/--editable flag.

```sh
pip install -e .
```

Or installing just the `server` extra:

```sh
pip install -e ".[server]"
```

Or you can install all the extras, which are also required to run the tests via pytest to make sure that the implemented
features or the bug fixes work as expected, and that the unit/integration tests are passing. If you encounter any package
or dependency problems, please consider upgrading or downgrading the related packages to solve the problem.

```sh
pip install -e ".[server,listeners,postgresql,integrations,tests]"
```

##### Install with `conda`

If you want to go with `conda` to install Argilla, firstly make sure that you have the latest version of conda on your
system. You can go to the [anaconda page](https://conda.io/projects/conda/en/latest/user-guide/install/index.html#regular-installation) and follow the tutorial there to make a clean install of `conda` on
your system.

Make sure that you are in the argilla folder. Then, you can go ahead and create a new conda development environment, and
then, activate it:

```sh
conda env create -f environment_dev.yml
conda activate argilla
```

In the new Conda environment, Argilla will already be installed in editable mode with all the server dependencies. But
if you’re willing to install any other dependency you can do so via `pip` to install your own, or just see the available
extras besides the `server` extras, which are: `listeners`, `postgresql`, and `tests`; all those installable as
`pip install -e ".[<EXTRA_NAME>]"`.

Now, the Argilla package is set up on your system and you need to make further installations for a thorough development
setup.

#### Install Code Formatting Tools

To keep a consistent code format, we use [pre-commit](https://pre-commit.com/) hooks. So, you first need to install `pre-commit` if not
installed already, via pip as follows:

```sh
pip install pre-commit
```

Then, you can proceed with the `pre-commit` hooks installation by simply running:

```sh
pre-commit install
```

### Set up the Databases

Argilla is built upon two databases: vector database and relational database. The vector database stores all the record
data and is the component that performs scalable vector similarity searches as well as basic vector searches. On the
other hand, the relational database stores the metadata of the records and annotations besides user and workspace
information.

#### Vector Database

Argilla supports ElasticSearch and OpenSearch as its main search engine for the vector database. One of the two is
required to correctly run Argilla in your development environment.

To install Elasticsearch or Opensearch, and to work with Argilla on your server later, you first need to install Docker
on your system. You can find the Docker installation guides for [Windows](https://docs.docker.com/desktop/install/windows-install/), [macOS](https://docs.docker.com/desktop/install/mac-install/) and [Linux](https://docs.docker.com/desktop/install/linux-install/) on
Docker website.

To install ElasticSearch or OpenSearch, you can refer to the [Setup and Installation](/getting_started/installation/deployments/docker.md) guide.

:::{note}
Argilla supports ElasticSearch versions >=8.5, and OpenSearch versions >=2.4.
:::

:::{note}
For vector search in OpenSearch, the filtering applied is using a `post_filter` step, since there is a bug that makes
queries fail using filtering + knn from Argilla.
See https://github.com/opensearch-project/k-NN/issues/1286

This may result in unexpected results when combining filtering with vector search with this engine.
:::

#### Relational Database and Migration

Argilla will use SQLite as the default built-in option to store information about users, workspaces, etc. for the
relational database. No additional configuration is required to start using SQLite.

By default, the database file will be created at `~/.argilla/argilla.db`, this can be configured by setting different
values for `ARGILLA_DATABASE_URL` and `ARGILLA_HOME_PATH` environment variables.

##### Run Database Migration

Starting from Argilla 1.16.0, the data of the FeedbackDataset along with the user and workspace information are stored
in an SQL database (SQLite or PostgreSQL). With each Argilla release, you may need to update the database schema to
the newer version. Here, you can find how to do this database migration.

You can run database migrations by executing the following command:

```sh
argilla server database migrate
```

The default SQLite database will be created at `~/.argilla/argilla.db`. This can be changed by setting different values
for `ARGILLA_DATABASE_URL` and `ARGILLA_HOME_PATH` environment variables.

##### Create the Default User

To run the Argilla database and server on your system, you should at least create the default user. Alternatively, you
may skip a default user and directly create user(s) whose credentials you will set up. You can refer to the
[user management](../getting_started/installation/configurations/user_management.md#create-a-user) page for detailed information.

To create a default user, you can run the following command:

```sh
argilla server database users create_default
```

##### Recreate the Database

Occasionally, it may be necessary to recreate the database from scratch to ensure a clean state in your development
environment. For instance, to run the Argilla test suite or troubleshoot issues that could be related to database
inconsistencies.

First, you need to delete the Argilla database with the following command:

```sh
rm ~/.argilla/argilla.db
```

After deleting the database, you will need to run the [database migration](#run-database-migration) task. By following these steps, you’ll
have a fresh and clean database to work with.

### Set up Argilla Server

If you want to work on the server of Argilla, please visit the `argilla-server` [README.md](/argilla-server/README.md)
file to see how to set up the server and run it on your local machine.

### Set up Argilla Frontend

If you want to work on the frontend of Argilla, please visit the `argilla-frontend` [README.md](/argilla-frontend/README.md)
file to see how to set up the frontend and run it on your local machine.

## Make Your Contribution

Now that everything is up and running, you can start to develop and contribute to Argilla! You can refer to
our [contributor guide](/community/contributing.md) to have an understanding of how you can structure your contribution and upload it
to the repository.

### Run Tests

#### Running Tests for the Argilla Python SDK
Running tests at the end of every development cycle is indispensable to make sure that there are no breaking changes. In
your Argilla environment, you can run all the tests as follows (Under the argilla project folder)

```sh
pytest tests
```

You can also run only the unit tests by providing the proper path:

```sh
pytest tests/unit
```

For running more heavy integration tests you can just run pytest with the `tests/integration` folder:

```sh
pytest tests/integration
```

#### Running tests for the Argilla Server

To run the tests for the Argilla Server, you can use the following command (Under the argilla project folder):

```sh
pdm test test/unit
```

You can also set up a PostgreSQL database instead of the default sqlite backend:

```sh
ARGILLA_DATABASE_URL=postgresql://postgres:postgres@localhost:5432 pdm test tests/unit
```

#### Running tests for the Argilla Frontend

To run the tests for the Argilla Frontend, you can use the following command (Under the argilla project folder):

```sh
npm run test
```
