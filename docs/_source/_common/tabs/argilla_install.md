Before being able to use Argilla from our Python library, you first need to deploy our FastAPI server, Elastic Search and the Argilla UI. We also have a more extensive tutorial on [deployments](/getting_started/installation/deployments/deployments) and [configurations](/getting_started/installation/configurations/configurations).

::::{tab-set}

:::{tab-item} Docker
```bash
docker run -d --name argilla -p 6900:6900 argilla/argilla-quickstart:latest
```
:::

:::{tab-item} Docker Compose
```
wget -O docker-compose.yaml https://raw.githubusercontent.com/argilla-io/argilla/main/docker-compose.yaml && docker-compose up -d
```
:::

:::{tab-item} Hugging Face Spaces
```{warning}
HuggingFace Spaces don't have persistent storage and will automatically reset after 48 hours of inactivity, which means all the data within the Space will be lost. You can enable this via the Hugging Face Spaces settings.
```
<a  href="https://huggingface.co/new-space?template=argilla/argilla-template-space">
    <img src="https://huggingface.co/datasets/huggingface/badges/raw/main/deploy-to-spaces-lg.svg" />
</a>
:::

::::