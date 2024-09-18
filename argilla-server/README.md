<h1 align="center">
  <a href=""><img src="https://github.com/dvsrepo/imgs/raw/main/rg.svg" alt="Argilla" width="150"></a>
  <br>
  Argilla
  <br>
</h1>
<h3 align="center">Work on data together, make your model outputs better!</h2>

<p align="center">
<a  href="https://pypi.org/project/argilla/">
<img alt="CI" src="https://img.shields.io/pypi/v/argilla.svg?style=flat-round&logo=pypi&logoColor=white">
</a>
<img alt="Codecov" src="https://codecov.io/gh/argilla-io/argilla/branch/main/graph/badge.svg?token=VDVR29VOMG"/>
<a href="https://pepy.tech/project/argilla">
<img alt="CI" src="https://static.pepy.tech/personalized-badge/argilla?period=month&units=international_system&left_color=grey&right_color=blue&left_text=pypi%20downloads/month">
</a>
<a href="https://huggingface.co/new-space?template=argilla/argilla-template-space">
<img src="https://huggingface.co/datasets/huggingface/badges/raw/main/deploy-to-spaces-sm.svg"/>
</a>
</p>

<p align="center">
<a href="https://twitter.com/argilla_io">
<img src="https://img.shields.io/badge/twitter-black?logo=x"/>
</a>
<a href="https://www.linkedin.com/company/argilla-io">
<img src="https://img.shields.io/badge/linkedin-blue?logo=linkedin"/>
</a>
<a href="http://hf.co/join/discord">
<img src="https://img.shields.io/badge/Discord-7289DA?&logo=discord&logoColor=white"/>
</a>
</p>

Argilla is a collaboration tool for AI engineers and domain experts who need to build high-quality datasets for their projects.

This repository only contains developer info about the backend server. If you want to get started, we recommend taking a
look at our [main repository](https://github.com/argilla-io/argilla) or our [documentation](https://docs.argilla.io/latest/).

Are you a contributor or do you want to understand what is going on under the hood, please keep reading the
documentation below.

## Source code folder structure

The following is a high-level overview of relevant folders and files in the argilla-server source code:

```
/argilla_server
  /api # Including all the API endpoints and related code
    /errors # Custom exceptions and error handlers
      /v1
    /handlers # Request FastAPI handlers
      /v1
    /policies # Authorization policies for resources
      /v1
    /schemas # Pydantic schemas for request and response bodies
      /v1
  /contexts # Domain contexts for the application including business logic
    accounts.py
    datasets.py
    search.py
    ...
  /models # SQLAlchemy ORM models for the database
    database.py
```

Folders inside `/api` are organized by API version, having right now only v1 implemented. This is in contrast to `/contexts` and `/models` folders that are not versioned. This is because the business logic and canonical database models are not exposed directly to the API, and therefore are not subject to versioning.

## Development environment

By default all commands executed with `pdm run` will get environment variables from `.env.dev` except the command `pdm test` which will overwrite some of them using values coming from `.env.test` file.

These environment variables can be overridden if necessary so feel free to define your own ones locally.

### Run development server

This single command prepares the development server to run locally. It does so by chaining commands to migrate the databse, create default users and launch the server on the right port.

```sh
pdm server-dev
```

### Run tests

A SQLite database located at `~/.argilla/argilla-test.db` will be automatically created to run tests. You can run the
entire test suite using the following custom PDM command:

```sh
pdm test
```

### Run frontend

If you need to run the frontend server you can follow the instructions at the [argilla-frontend](/argilla-frontend/README.md) project.

## Development commands

### Run cli

```sh
pdm cli
```

### Run database migrations

By default, the SQLite database located at `~/.argilla/argilla.db` will be used. You can create the database and run migrations with
the following custom PDM command:

```sh
pdm migrate
```

### Run uvicorn FastAPI server

```sh
pdm server
```

### Run RQ background workers

```sh
pdm worker
```

## CLI commands

This section list and describe the commands offered by the `argilla_server` Python package. If you need more information about the available
commands in the CLI you can use the `--help` option:

```sh
python -m argilla_server --help
```

If you need more information about a specific command you can use the `--help` option too:

```sh
python -m argilla_server database --help
```

### Start the server

The `argilla_server start` command will start the Argilla server blocking the current terminal. You can use the following command to start the server:

```sh
python -m argilla_server start
```

The following options can be provided:

- `--host`: The host where the Argilla server will be bound. Default value is `0.0.0.0`.
- `--port`: The port where the Argilla server will be bound. Default value is `6900`.
- `--access-log/--no-access-log`: Enable/disable the server access log. Default value is `True`.

#### Running with `uvicorn`

You can also launch the argilla server using `uvicorn`:

```sh

uvicorn argilla_server:app --port 6900

```

> [!NOTE]
> For more details about FastAPI and uvicorn, see [here](https://fastapi.tiangolo.com/deployment/manually/#run-a-server-manually-uvicorn).
> You can also visit the uvicorn official documentation [here](https://www.uvicorn.org/#usage).

### Database

The `argilla_server database` group of commands offers functionality for managing the Argilla server database:

- `python -m argilla_server database migrate`: applies the database migrations.
- `python -m argilla_server database revisions`: list the different revisions to which the database can be migrated.

#### Database Migrations

Since Argilla 1.6.0, the information about users and workspaces, and the data of the `Dataset`s is stored in an SQL database (SQLite or PostgreSQL). That being said,
every release of Argilla may require a database migration to update the database schema to the new version. This section explains how to perform the database migrations.

To apply the migrations, a connection to the database needs to be established. In the case that SQLite is used, then the only way to apply the migrations is by
executing the migration command from the same machine where the Argilla server is running. In the case that PostgreSQL is used, then the migration command can be executed
from any machine that has access to the PostgreSQL database setting the `ARGILLA_DATABASE_URL` environment variable to the URL of the database.

##### Database revisions

To list the available database revisions/migrations, the `argilla_server database revisions` command can be used. This command will list the different revisions to which
the database can be migrated. As several revisions could be generated for a single release, the command will also show the latest revision that was generated for each release.

```sh
python -m argilla_server database revisions
```

```sh
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.

Tagged revisions
-----------------
• 1.7 (revision: '1769ee58fbb4')
• 1.8 (revision: 'ae5522b4c674')
• 1.11 (revision: '3ff6484f8b37')
• 1.13 (revision: '1e629a913727')
• 1.17 (revision: '84f6b9ff6076')
• 1.18 (revision: 'bda6fe24314e')
• 1.28 (revision: 'ca7293c38970')
• 2.0 (revision: '237f7c674d74')

Alembic revisions
-----------------
45a12f74448b -> 237f7c674d74 (head), add status column to records table
d00f819ccc67 -> 45a12f74448b, add distribution column to datasets table
ca7293c38970 -> d00f819ccc67, update responses user_id foreign key
bda6fe24314e -> ca7293c38970, change suggestions score column to json
7850ab5b42d9 -> bda6fe24314e, create vectors table
84f6b9ff6076 -> 7850ab5b42d9, create vectors settings table
b8458008b60e -> 84f6b9ff6076, add last_activity_at to datasets table
7cbcccf8b57a -> b8458008b60e, add allow_extra_metadata column to datasets table
1e629a913727 -> 7cbcccf8b57a, create metadata_properties table
3fc3c0839959 -> 1e629a913727, fix suggestions type enum values
8c574ada5e5f -> 3fc3c0839959, create suggestions table
3ff6484f8b37 -> 8c574ada5e5f, update_enum_columns
ae5522b4c674 -> 3ff6484f8b37, add metadata column to records table
e402e9d9245e -> ae5522b4c674, create fields table
8be56284dac0 -> e402e9d9245e, create responses table
3a8e2f9b5dea -> 8be56284dac0, create records table
b9099dc08489 -> 3a8e2f9b5dea, create questions table
1769ee58fbb4 -> b9099dc08489, create datasets table
82a5a88a3fa5 -> 1769ee58fbb4, create workspaces_users table
74694870197c -> 82a5a88a3fa5, create workspaces table
<base> -> 74694870197c, create users table

Current revision
----------------
Current revision(s) for sqlite:////Users/root/.argilla/argilla.db?check_same_thread=False:
Rev: 237f7c674d74 (head)
Parent: 45a12f74448b
Path: /Users/root/argilla/argilla-server/src/argilla_server/alembic/versions/237f7c674d74_add_status_column_to_records_table.py

    add status column to records table

    Revision ID: 237f7c674d74
    Revises: 45a12f74448b
    Create Date: 2024-06-18 17:59:36.992165
```

##### Apply database migrations

If the `argilla_server database migrate` command is called without any argument, then all the unapplied migrations will be applied:

```sh
python -m argilla_server database migrate
```

##### Apply a specific database migration

The `argilla_server database migrate` command can also be used to apply a specific migration. To do so, the `--revision` option needs to be provided with the name of the revision or the Argilla
version to which the database will be migrated.

```sh
python -m argilla_server database migrate --revision 2.0
```

> [!WARNING]
> Applying a revision that is older than the current revision of the database will revert the database to the state of that revision, which means that the data could be lost.

#### Users management

The `argilla_server database users` group of commands offers functionality for managing the users of the Argilla server.

- `python -m argilla_server database users create`: creates a new user in the Argilla server database.
- `python -m argilla_server database users create_default`: creates the default users in the Argilla server database.
- `python -m argilla_server database users migrate`: migrates the users from the old `YAML` file to the Argilla server database.
- `python -m argilla_server database users update`: updates a user in the Argilla server database.

### Search engine

The `argilla_server search-engine` group of commands offers functionality to work with the search engine used by Argilla.

- `python -m argilla_server search-engine reindex`: reindex all Argilla entities into search engine.

### Background Jobs

Argilla uses [RQ](https://python-rq.org) as background job manager. RQ depends on [Redis](https://redis.io) to store and retrieve information about the jobs to be processed.

Once that you have correctly installed Redis on your system, you can start the RQ worker by running the following CLI command:

```sh
python -m argilla_server worker
```

## 🫱🏾‍🫲🏼 Contribute

To help our community with the creation of contributions, we have created our [community](https://docs.argilla.io/latest/community/) docs. Additionally, you can always [schedule a meeting](https://calendly.com/david-berenstein-huggingface/30min) with our Developer Advocacy team so they can get you up to speed.

<a  href="https://github.com/argilla-io/argilla/graphs/contributors">

<img  src="https://contrib.rocks/image?repo=argilla-io/argilla" />

</a>

## 🗺️ Roadmap

We continuously work on updating [our plans and our roadmap](https://github.com/orgs/argilla-io/projects/10/views/1) and we love to discuss those with our community. Feel encouraged to participate.
