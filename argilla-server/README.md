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

Argilla is a **collaboration platform for AI engineers and domain experts** that require **high-quality outputs, full data ownership, and overall efficiency**.

> [!NOTE]
> This README represents the release candidate for the 2.0.0 SDK version. The README for the last stable version of the 1x SDK can be found [1.x](../argilla-v1/README.md)

This repository only contains developer info about the backend server. If you want to get started, we recommend taking a
look at our [main repository](https://github.com/argilla-io/argilla) or our [documentation](https://argilla-io.github.io/argilla/latest/).

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

By default, the SQLite database is located at `~/.argilla/argilla.db` will be used. You can create the database and run migrations with
the following custom PDM command:

```sh
pdm migrate
```

### Run uvicorn FastAPI server

```sh
pdm server
```


## 🫱🏾‍🫲🏼 Contribute

To help our community with the creation of contributions, we have created our [community](https://argilla-io.github.io/argilla/latest/community/) docs. Additionally, you can always [schedule a meeting](https://calendly.com/david-berenstein-huggingface/30min) with our Developer Advocacy team so they can get you up to speed.

<a  href="https://github.com/argilla-io/argilla/graphs/contributors">

<img  src="https://contrib.rocks/image?repo=argilla-io/argilla" />

</a>

## 🗺️ Roadmap

We continuously work on updating [our plans and our roadmap](https://github.com/orgs/argilla-io/projects/10/views/1) and we love to discuss those with our community. Feel encouraged to participate.
