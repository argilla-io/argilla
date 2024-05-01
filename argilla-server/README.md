<h1 align="center">
  <a href=""><img src="https://github.com/dvsrepo/imgs/raw/main/rg.svg" alt="Argilla" width="150"></a>
  <br>
  Argilla-Server
  <br>
</h1>
<h3 align="center">The repository for the Python native FastAPI server for Argilla backend.</h2>


<p align="center">
<a  href="https://pypi.org/project/argilla-server/">
<img alt="CI" src="https://img.shields.io/pypi/v/argilla.svg?style=flat-round&logo=pypi&logoColor=white">
</a>
<img alt="Codecov" src="https://codecov.io/gh/argilla-io/argilla-server/branch/main/graph/badge.svg?token=VDVR29VOMG"/>
<a href="https://pepy.tech/project/argilla-server">
<img alt="CI" src="https://static.pepy.tech/personalized-badge/argilla-server?period=month&units=international_system&left_color=grey&right_color=blue&left_text=pypi%20downloads/month">
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
<a href="https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g">
<img src="https://img.shields.io/badge/slack-purple?logo=slack"/>
</a>
</p>

Argilla is a **collaboration platform for AI engineers and domain experts** that require **high-quality outputs, full data ownership, and overall efficiency**.

This repository only contains developer info about the backend server. If you want to get started, we recommend taking a look at our [main repository](https://github.com/argilla-io/argilla) or our [documentation](https://docs.argilla.io/).

Are you a contributor or do you want to understand what is going on under the hood, please keep reading the documentation below.

## Clone repository

`argilla-server` is using `argilla` repository as submodule to build frontend statics so when cloning use the following command:

```sh
git clone --recurse-submodules git@github.com:argilla-io/argilla-server.git
```

If you already cloned the repository without using `--recurse-submodules` you can init and update the submodules with:

```sh
git submodule update --remote --recursive --init
```

> [!IMPORTANT]
> By default `argilla` submodule is using `develop` branch so the previous command will get the latest commit from that branch.

### Specify a tag for argilla submodule

When doing a release we should change `argilla` submodule to use an specific tag. In the following example we are setting tag `v1.22.0`:

```sh
cd argilla
git fetch --tags
git checkout v1.22.0
```

> [!NOTE]
> You should see some changes on the `argilla-server` root folder where the subproject commit is now changed to the one from the tag version. Feel free to commit these changes.

## Development environment

By default all commands executed with `pdm run` will get environment variables from `.env.dev` except command `pdm test` that will overwrite some of them using values coming from `.env.test` file.

These environment variables can be overrided if necessary so feel free to defined your own ones locally.

### Run cli

```sh
pdm cli
```

### Run database migrations

By default a SQLite located at `~/.argilla/argilla.db` will be used. You can create the database and run migrations with the following custom PDM command:

```sh
pdm migrate
```

### Run tests

A SQLite database located at `~/.argilla/argilla-test.db` will be automatically created to run tests. You can run the entire test suite using the following custom PDM command:

```sh
pdm test
```

## Run development server

### Build frontend static files

Before running Argilla development server we need to build the frontend static files. Node version 18 is required for this action:

```sh
brew install node@18
```

After that you can build the frontend static files:

```sh
./scripts/build_frontend.sh
```

After running the previous script you should have a folder at `src/argilla_server/static` with all the frontend static files successfully generated.

### Run uvicorn development server

```sh
pdm server
```
