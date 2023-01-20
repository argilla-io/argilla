
# Cloud Providers

This guide explains how to deploy the Argilla Server on different cloud providers.

(deploy-to-aws-instance-using-docker-machine)=
## Amazon Web Services (AWS)

### Setup an AWS profile

The `aws` command cli must be installed. Then, type:

```bash
aws configure --profile argilla
```

and follow command instructions. For more details, visit [AWS official documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html).

Once the profile is created (a new entry should appear in file `~/.aws/config`), you can activate it via setting environment variable:

```bash
export AWS_PROFILE=argilla
```

### Create docker machine

```bash
docker-machine create --driver amazonec2 \
--amazonec2-root-size 60 \
--amazonec2-instance-type t2.large \
--amazonec2-open-port 80 \
--amazonec2-ami ami-0b541372 \
--amazonec2-region eu-west-1 \
argilla-aws
```

Available ami depends on region. The provided ami is available for eu-west regions

### Verify machine creation

```bash
$>docker-machine ls

NAME                   ACTIVE   DRIVER      STATE     URL                        SWARM   DOCKER     ERRORS
argilla-aws             -        amazonec2   Running   tcp://52.213.178.33:2376           v20.10.7
```

### Save assigned machine ip

In our case, the assigned ip is `52.213.178.33`

### Connect to remote docker machine

To enable the connection between the local docker client and the remote daemon, we must type following command:

```bash
eval $(docker-machine env argilla-aws)
```

### Define a docker-compose.yaml

{{ dockercomposeyaml }}

### Pull image

```bash
docker-compose pull
```

### Launch docker container

```bash
docker-compose up -d
```

### Accessing Argilla

In our case http://52.213.178.33

## Azure

The easiest way to deploy Argilla on Azure is using the Azure Container Instances (ACI) service. This service allows you to run containers in a serverless way, without the need to manage the underlying infrastructure. ACI integrates with Docker compose files, so you can easily deploy your application using the same file you use for local development.

### 1. Install Docker with compose

Install th latest Docker with the compose method described as described in the [official documentation](https://docs.docker.com/compose/install/). Note that this is not the independent `docker-compose` application.

### 2. Login to Azure

Using `docker` and `az` CLI, login to Azure:

```bash
docker login azure
```
You can install the `az` CLI using the [official documentation](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli).

### 3. Create an Azure context

Create a separate context with Azure credentials and the subscription where you want to deploy the Argilla Server:

```bash
docker context create aci azurecontext --subscription-id <subscription-id> --resource-group <resource-group> --location <location>
```
You can also switch back to the default context with:

```bash
docker context use default
```

### 4. Deploy the Argilla Server

To deploy the Argilla Server, you can use the Docker Compose file provided in the [Argilla repository](https://raw.githubusercontent.com/argilla-io/argilla/main/docker-compose.yaml) and the `docker compose up` command:

```bash
wget -O docker-compose.yml https://raw.githubusercontent.com/argilla-io/argilla/main/docker-compose.yaml && docker-compose up -d
```

This guide is adapted from this [blog post by Ben Burtenshaw](https://medium.com/@ben.burtenshaw/zero-to-demo-on-azure-with-docker-compose-and-container-instances-4e83b78003b). There's also an official [tutorial](https://learn.microsoft.com/en-us/azure/container-instances/tutorial-docker-compose) on Microsoft Learn.

## Google Cloud Platform (GCP)

Coming soon!

> 🚒 **If you'd like support with this and/or want to contribute this gude, join the [Slack Community](https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g)**

