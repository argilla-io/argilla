# Developer documentation

On this page, you can find all the guides that you will need to install and develop Argilla.
For a proper installation, you will need to;

- [Clone the Argilla repository](#clone-the-argilla-repository),
- [Install the dependencies](#install-dependencies),
- [Install Docker and either ElasticSearch or OpenSearch](#elasticsearch-or-opensearch-with-docker),
- [Perform database migration](#migrate-database)

And if you want to work on the backend, you need to;
- [Run the backend server](#run-the-argilla-backend-server),
- [Create users](#create-the-default-user),
- [Launch the server](#launch-argilla-server),

And if you want to work on the frontend, you need to;
- [Build the frontend static files](#build-frontend-static-files),
- [Run the frontend files](#run-frontend-files).

## Setting up your development environment

### Clone the Argilla repository

To set up your system for Argilla development, you, first of all, have to [fork](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) our repository and [clone](https://github.com/argilla-io/argilla) the fork to your computer.
```sh
git clone https://github.com/[your-github-username]/argilla.git
cd argilla
```
To keep your fork’s main/develop branch up to date with our repo you should add it as an [upstream remote branch](https://dev.to/louhayes3/git-add-an-upstream-to-a-forked-repo-1mik):
```sh
git remote add upstream https://github.com/argilla-io/argilla.git

```

### Install dependencies

You will need to install `argilla` and the extra dependencies that you prefer to be able to use Argilla in your Python client or Command Line Interface (CLI). There are two ways to install it and you can opt for one of them depending on your use case:

- Install `argilla` with `pip`: Recommended for non-extensive, one-time contributions as it will only install the required packages.

- Install `argilla` with `conda`: Recommended for comprehensive, continuous contributions as it will create an all-inclusive environment for development.

#### Install with `pip`

If you choose to install Argilla via `pip`, you can do it easily on your terminal. Firstly, direct to the `argilla` folder in your terminal by:
```sh
cd argilla
```

Then, you just need to install Argilla with the command below. Note that we will install it in editable mode using the -e/--editable flag in the `pip` command to avoid having to re-install it on every code modification, but if you’re not planning to modify the code, you can just omit the -e/--editable flag.
```sh
pip install -e .
```

Or installing just the `server` extra:
```sh
pip install -e ".[server]"
```

Or you can install all the extras, which are also required to run the tests via pytest to make sure that the implemented features or the bug fixes work as expected, and that the unit/integration tests are passing. If you encounter any package or dependency problems, please consider upgrading or downgrading the related packages to solve the problem.
```sh
pip install -e ".[server,listeners,postgresql,integrations,tests]"
```

#### Install with `conda`

If you want to go with `conda` to install Argilla, firstly make sure that you have the latest version of conda on your system. You can go to the [anaconda page](https://conda.io/projects/conda/en/latest/user-guide/install/index.html#regular-installation) and follow the tutorial there to make a clean install of `conda` on your system.

Make sure that you are in the argilla folder.
```sh
cd argilla
```

Then, you can go ahead and create a new conda development environment, and then, activate it:
```sh
conda env create -f environment_dev.yml
conda activate argilla
```

In the new Conda environment, Argilla will already be installed in editable mode with all the server dependencies. But if you’re willing to install any other dependency you can do so via `pip` to install your own, or just see the available extras besides the `server` extras, which are: `listeners`, `postgresql`, and `tests`; all those installable as `pip install -e ".[<EXTRA_NAME>]"`.

Now, the Argilla environment is set up on your system and you need to make further installments for a thorough development setup.

### ElasticSearch or OpenSearch with Docker

Argilla supports ElasticSearch and OpenSearch as its main search engine. One of the two is required to correctly run Argilla in your development environment.

To install Elasticsearch or Opensearch, and to work with Argilla on your server later, you first need to install Docker on your system. You can find the Docker installation guides for [Windows](https://docs.docker.com/desktop/install/windows-install/), [macOS](https://docs.docker.com/desktop/install/mac-install/) and [Linux](https://docs.docker.com/desktop/install/linux-install/) on Docker website.

To install ElasticSearch or OpenSearch, you can refer to the [Setup and Installation](/getting_started/installation/deployments/docker.md) guide.

:::{note}
Argilla supports ElasticSearch versions 8.8, 8.5, 8.0, and 7.17 and OpenSearch versions 1.3 and 2.3.
:::

#### SQLite
By default, Argilla will use SQLite to store information about users, workspaces, etc. No additional configuration is required to start using SQLite.

By default, the database file will be created at `~/.argilla/argilla.db`, this can be configured by setting different values for `ARGILLA_DATABASE_URL` and `ARGILLA_HOME_PATH` environment variables.

### Migrate Database

Starting from Argilla 1.16.0, the data of the FeedbackDataset along with the user and workspace information are stored in an SQL database (SQLite or PostgreSQL). With each Argilla release, you may need to update the database schema to the newer version. Here, you can find how to do this database migration.

#### Run Database Migration

You can run database migrations by executing the following command:
```sh
argilla server database migrate
```

The default SQLite database will be created at `~/.argilla/argilla.db`. This can be changed by setting different values for `ARGILLA_DATABASE_URL` and `ARGILLA_HOME_PATH` environment variables.

#### Recreate the Database

Occasionally, it may be necessary to recreate the database from scratch to ensure a clean state in your development environment. For instance, to run the Argilla test suite or troubleshoot issues that could be related to database inconsistencies.

First, you need to delete the Argilla database with the following command:
```sh
rm ~/.argilla/argilla.db
```

After deleting the database, you will need to run the database migration task:
```sh
argilla server database migrate
```

By following these steps, you’ll have a fresh and clean database to work with.

### Run the Argilla backend server

Before running the Argilla server, it is recommended to build the frontend files to be able to access the UI on your local host:
```sh
bash scripts/build_frontend.sh
```
Then, to run Argilla backend, you will need an ElasticSearch instance up and running for the time being. You can get one running using Docker with the following command:
```sh
docker run -d --name elasticsearch-for-argilla -p 9200:9200 -p 9300:9300 -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" -e "discovery.type=single-node" -e "xpack.security.enabled=false" docker.elastic.co/elasticsearch/elasticsearch:8.5.3
```

### Create the default user

To run the Argilla server on your system, you should at least create the default user. Alternatively, you may skip a default user and directly create user(s) whose credentials you will set up. You can refer to the [user management](/getting_started/installation/configurations/user_management.md#create-a-user) page for detailed information.

To create a default user, you can run the following command:
```sh
argilla server database users create_default
```

### Launch Argilla Server

Now that your system has Argilla backend server, you are ready to start your server and access Argilla:
```sh
ARGILLA_ENABLE_TELEMETRY=0 uvicorn argilla.server.app:app --port 6900 --host 0.0.0.0 --reload
```

With this command, you will activate reloading the backend files after every change. This way, whenever you make a change and save it, it will automatically be reflected in your server.

Note that we start the server with `ARGILLA_ENABLE_TELEMETRY=0` to stop anonymous reporting for our development environment. You can read more about telemetry settings on the [telemetry page](/reference/telemetry.md).

### Install Code Formatting Tools

To keep a consistent code format, we use [pre-commit](https://pre-commit.com/) hooks. So, you first need to install `pre-commit` if not installed already, via pip as follows:
```sh
pip install pre-commit
```

Then, you can proceed with the `pre-commit` hooks installation by simply running:
```sh
pre-commit install
```

### Implement Updates

After installing the requirements, you can start making your amazing and well-appreciated contribution to Argilla! The installments up to this point will suffice to work on the backend. You can refer to our [contributer guide](/community/contributing.md) to have an understanding of how you can upload your contribution to the repository.

### Run tests
To make sure there are no breaking changes, you should run all the tests as follows:
```sh
pytest tests
```

You can also run only the unit tests by providing the proper path:
```sh
pytest tests/unit
```

For the unit tests, you can also set up a PostgreSQL database instead of the default sqlite backend:
```sh
ARGILLA_DATABASE_URL=postgresql://postgres:postgres@localhost:5432 pytest tests/unit
```

For running more heavy integration tests you can just run pytest with the `tests/integration` folder:
```sh
pytest tests/integration
```

### Troubleshooting

If you get warnings while building documentation then you can handle them this way: If they are `toctree` warnings then they can be ignored and If they are import errors then they can be resolved by installing `autodoc` and `argilla` from `docs/_source/requirements.txt`

## Running the Frontend

If you want to work on the frontend of Argilla, you can do so by following the steps below in addition to the steps above until the `Run the Argilla backend server` section.

### Build Frontend static files

Build the static UI files in case you want to work on the UI:

```sh
bash scripts/build_frontend.sh
```

### Run Frontend files

Run the Argilla backend using Docker with the following command:

```sh
docker run -d --name quickstart -p 6900:6900 argilla/argilla-quickstart:latest
```

Navigate to the `frontend` folder from your project's root directory.

Then, execute the command:

```sh
npm run dev
```

To log in, use the username `admin` and the password `12345678`. If you need more information, please check [here](/getting_started/quickstart_installation.ipynb).
