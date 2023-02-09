(install-from-develop)=
# Install from `develop`

If you want the cutting-edge version of *Argilla* with the latest changes and experimental features, follow the steps below in your terminal.
**Be aware that this version might be unstable!**

First, you need to install the master version of our python client:

```bash
 pip install -U git+https://github.com/argilla-io/argilla.git
```

Then, the easiest way to get the master version of our web app up and running is via docker-compose:

:::{note}
For now, we only provide the master version of our web app via docker.
If you want to run the web app of the master branch **without** docker, we refer you to our [development setup](development-setup).
:::

```bash
 # get the docker-compose yaml file
 mkdir argilla && cd argilla
 wget -O docker-compose.yml https://raw.githubusercontent.com/argilla-io/argilla/develop/docker-compose.yaml
 # use the master image of the argilla container instead of the latest
 sed -i 's/argilla:latest/argilla:master/' docker-compose.yml
 # start all services
 docker-compose up
 ```

If you want to use vanilla docker (and have your own Elasticsearch instance running), you can just use our master image:

```bash
docker run -p 6900:6900 -e "ELASTICSEARCH=<your-elasticsearch-endpoint>" --network argilla-net --name argilla argilla/argilla-server:develop
```