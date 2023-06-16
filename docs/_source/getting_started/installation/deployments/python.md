(install-from-develop)=
# Python

As with other packages, we provide a simple and intuitive installment via `pypi`.

```bash
pip install argilla
```

## Package extras

Our Python package requires some extras that might be downloaded to facilitate more custom workflows.

- `pip install "argilla[listeners]"`: the [argilla.listeners-module](/guides/schedule_jobs_with_listeners) allows for the usage of background processes to monitor dataset changes and schedule jobs.
- `pip install "argilla[server]"`: the [Argilla FastAPI server](/getting_started/installation/configurations/server_configuration) can be deployed locally to test development changes or custom configs.
- `pip install "argilla[postgresql]"`: the default data management is done with built-in `sqlite` but can be replaced with a [PostgreSQL database](/getting_started/installation/configurations/server_configuration).
- `pip install "argilla[integrations]"`: [integrations](/tutorials/libraries) with other libraries/frameworks are available to use.
- `pip install "argilla[tests]"` When [running tests](/community/developer_docs) as a developer, you might need third-party integration packages to test end-to-end workflows.

## Install from `develop`

If you want the cutting-edge version of *Argilla* with the latest changes and experimental features, follow the steps below in your terminal.
**Be aware that this version might be unstable!**

First, you need to install the `develop` version of our Python client:

```bash
 pip install -U git+https://github.com/argilla-io/argilla.git
```

Then, the easiest way to get the `develop` version of our web app up and running is via docker-compose:

:::{note}
For now, we only provide the `develop` version of our web app via docker.
If you want to run the web app of the `develop` branch **without** docker, we refer you to our [development setup](development-setup).
:::

```bash
 # get the docker-compose yaml file
 mkdir argilla && cd argilla
 wget -O docker-compose.yaml https://raw.githubusercontent.com/argilla-io/argilla/develop/docker-compose.yaml
 # use the `develop` image of the argilla container instead of the latest
 sed -i 's/argilla:latest/argilla:develop/' docker-compose.yaml
 # start all services
 docker-compose up
 ```

If you want to use vanilla docker (and have your own Elasticsearch instance running), you can just use our `develop` image:

```bash
docker run -p 6900:6900 -e "ELASTICSEARCH=<your-elasticsearch-endpoint>" --network argilla-net --name argilla argilla/argilla-server:develop
```
