# Developer documentation

Here we provide some guides for the development of _Argilla_.

## Requirements

### ElasticSearch or OpenSearch

Argilla supports ElasticSearch and OpenSearch as his main search engine. One of the two is required to correctly run Argilla in your development environment.

:::{note}
Argilla supports ElasticSearch versions 8.8, 8.5, 8.0, and 7.17 and OpenSearch versions 1.3 and 2.3.
:::

For more information please visit our [Setup and Installation](../getting_started/installation/deployments/deployments.md) section.

### SQLite

By default Argilla will use SQLite to store information about users, workspaces, etc. Non additional configuration is required to start using SQLite.

By default the database file will be created at `~/.argilla/argilla.db`, this can be configured setting different values for `ARGILLA_DATABASE_URL` and `ARGILLA_HOME_PATH` environment variables.

## Development setup

### Forking and config your Argilla Git repository

To set up your system for _Argilla_ development, you first of all have to
[fork](https://guides.github.com/activities/forking) our [repository](https://github.com/argilla-io/argilla)
and clone the fork to your computer:

```sh
git clone https://github.com/[your-github-username]/argilla.git
cd argilla
```

To keep your fork's main/develop branch up to date with our repo you should add it as an
[upstream remote branch](https://dev.to/louhayes3/git-add-an-upstream-to-a-forked-repo-1mik>):

```sh
git remote add upstream https://github.com/argilla-io/argilla.git
```

### Install dependencies

To be able to use Argilla via either the Python client or the Python Command Line Interface (CLI), you'll need to
install `argilla` and its extra dependencies, if applicable. To do so, you can either install it via `pip` or setup
a Conda environment with all the required dependencies.

#### Via `pip`

If you're using `pip`, you can either install just `argilla` or `argilla` with any combination or all the extras available.
We'll install it in [editable mode](https://pip.pypa.io/en/stable/cli/pip_install/#install-editable) using the `-e/--editable` flag
in the `pip` command to avoid having to re-install it on every code modification, but if you're not planning to modify the code, you
can just omit the `-e/--editable` flag.

```sh
pip install -e .
```

Or installing just the `server` extra:

```sh
pip install -e ".[server]"
```

Or installing all the extras, that are also required to run the tests via `pytest` to make sure that the implemented features or the bug fixes work as expected, and that the unit/integration tests are passing.

```sh
pip install -e ".[server,listeners,postgresql,integrations,tests]"
```

#### Via `conda`

If you're using `conda`, you can go ahead and create a new conda development environment, and then, activate it:

```sh
conda env create -f environment_dev.yml
conda activate argilla
```

In the new Conda environment, _Argilla_ will already be installed in [editable mode](https://pip.pypa.io/en/stable/cli/pip_install/#install-editable)
with all the server dependencies. But if you're willing to install any other dependency you can do so via `pip` to install your own, or just
see the available extras besides the `server` extras, which are: `listeners`, `postgresql`, and `tests`; all those installable as `pip install -e ".[<EXTRA_NAME>]"`.

### Code formatting tools

To keep a consistent code format, we use [pre-commit](https://pre-commit.com) hooks. So on, you first need to install
`pre-commit` if not installed already, via pip as follows:

```sh
pip install pre-commit
```

Then, you can proceed with the `pre-commit` hooks installation by simply running:

```sh
pre-commit install
```

### Building Frontend static files

Build the static UI files in case you want to work on the UI:

```sh
bash scripts/build_frontend.sh
```

### Running database migrations

Run database migrations executing the following task:

```sh
python -m argilla database migrate
```

The default SQLite database will be created at `~/.argilla/argilla.db`. This can be changed setting different values for `ARGILLA_DATABASE_URL` and `ARGILLA_HOME_PATH` environment variables.

### Generating a database migration

If you have updated one of the SQLAlchemy ORM classes in `src/argilla/server/models/models.py` or added a new one, then you will need to generate a new migration script that you can later apply to the database. To generate a new migration script execute the following command:

```sh
alembic -c src/argilla/alembic.ini revision --autogenerate -m "descriptive message here"
```

`alembic` will automatically detect the changes made and generate a new migration script in the `src/argilla/server/alembic/versions` directory.

<div class="alert alert-info">

Note

After generating a new migration script, you will need to apply the migrations as described in [running database migrations](#running-database-migrations).

</div>

### Recreating the database

Occasionally, it may be necessary to recreate the database from scratch to ensure a clean state in your development environment. For instance, to run the Argilla test suite or troubleshoot issues that could be related to database inconsistencies.

First you need to delete the Argilla database with the following command:

```sh
rm ~/.argilla/argilla.db
```

After deleting the database, you will need to run the database migrate task:

```sh
python -m argilla database migrate
```

By following these steps, you'll have a fresh and clean database to work with.

### Creating your first user

At least one user is required to interact with Argila API and web UI. You can create easily create your user executing the following task:

```sh
python -m argilla users create
```

This task will ask you for the required information to create your user, including `username`, `password` and so on.

### Running Argilla server

Finally to run the web app now simply execute:

```sh
python -m argilla server
```

Congrats, you are ready to take _Argilla_ to the next level 🚀

## Building the documentation

To build the documentation, make sure you set up your system by installing the required dependencies:

```
pip install -r docs/_source/requirements.txt
```

Then use `sphinx-autobuild` to continuously deploy the webpage using the following command:

```
sphinx-autobuild docs/_source docs/_build/html
```

This will create a `_build/html` folder that is served at [http://127.0.0.1:8000](http://127.0.0.1:8000). Also, it starts watching for changes in the `docs/source` directory. When a change is detected in `docs/source`, the documentation is rebuilt and any open browser windows are reloaded automatically. KeyboardInterrupt (ctrl+c) will stop the server.

### Troubleshooting

If you get warnings while building documentation then you can handle them this way: If they are `toctree` warnings then they can be ignored and If they are import errors then they can be resolved by installing `autodoc` and `argilla` from `docs/_source/requirements.txt`
