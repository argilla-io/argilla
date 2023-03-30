# Developer documentation

Here we provide some guides for the development of *Argilla*.

## Requirements

### ElasticSearch or OpenSearch

Argilla supports ElasticSearch and OpenSearch as his main search engine. One of the two is required to correctly runs Argilla in your development environment.

For more information please visit our [Setup and Installation](./getting_started/installation.md) section.

### SQLite

By default Argilla will use SQLite to store information about users, workspaces, etc. Non additional configuration is required to start using SQLite.

By default the database file will be created at `~/.argilla/argilla.db`, this can be configured setting different values for `ARGILLA_DATABASE_URL` and `ARGILLA_HOME_PATH` environment variables.

## Development setup

### Forking and config your Argilla Git repository

To set up your system for *Argilla* development, you first of all have to
[fork](https://guides.github.com/activities/forking) our [repository](https://github.com/argilla-io/argilla)
and clone the fork to your computer:

```sh
git clone https://github.com/[your-github-username]/argilla.git
cd argilla
```

To keep your fork's master branch up to date with our repo you should add it as an
[upstream remote branch](https://dev.to/louhayes3/git-add-an-upstream-to-a-forked-repo-1mik>):

```sh
git remote add upstream https://github.com/argilla-io/argilla.git
```

Now go ahead and create a new conda environment in which the development will take place and activate it:

```sh
conda env create -f environment_dev.yml
conda activate argilla
```

In the new environment *Argilla* will already be installed in [editable mode](https://pip.pypa.io/en/stable/cli/pip_install/#install-editable) with all its server dependencies.

To keep a consistent code format, we use [pre-commit](https://pre-commit.com) hooks. You can install them by simply running:

```sh
pre-commit install
```

Install the `commit-msg` hook if you want to check your commit messages in your contributions:


```sh
pre-commit install --hook-type commit-msg
```

### Building Frontend static files

Build the static UI files in case you want to work on the UI:

```sh
bash scripts/build_frontend.sh
```

### Running database migrations

Run database migrations executing the following task:

```sh
python -m argilla.tasks.database.migrate
```

The default SQLite database will be created at `~/.argilla/argilla.db`. This can be changed setting different values for `ARGILLA_DATABASE_URL` and `ARGILLA_HOME_PATH` environment variables.

### Creating your first user

At least one user is required to interact with Argila API and web UI. You can create easily create your user executing the following task:

```sh
python -m argilla.tasks.users.create
```

This task will ask you for the required information to create your user, including `username`, `password` and so on.

### Running Argilla server

Finally to run the web app now simply execute:

```sh
python -m argilla
```

Congrats, you are ready to take *Argilla* to the next level 🚀

## Building the documentation

To build the documentation, make sure you set up your system for *Argilla* development.
Then go to the `docs/_source` folder in your cloned repo and execute the ``make html`` command:

```sh
cd docs/_source
make html
```

This will create a `_build/html` folder in which you can find the `index.html` file of the documentation.

Alternatively, you can use install and `sphinx-autobuild` to continuously deploy the webpage using the following command:

```sh
sphinx-autobuild docs/_source docs/_build/html
```
