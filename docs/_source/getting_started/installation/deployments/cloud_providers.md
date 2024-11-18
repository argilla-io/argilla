
# Cloud Providers and Kubernetes

This guide explains how to deploy the Argilla Server on different cloud providers and Kubernetes.

## Kubernetes

The [Kubernetes (k8s) folder](https://github.com/argilla-io/argilla/tree/main/k8s) in the repo holds several files for a minimal config on deploying Argilla to Kubernetes. These files also contain some resource requirement recommendations for hosting. For a more robust config, we recommend using [Helm](#helm-charts) charts.

- [argilla-server-deployment.yaml](https://github.com/argilla-io/argilla/tree/main/k8s/argilla-server-deployment.yaml): deploy main Argilla server,
- [argilla-server-hpa.yaml](https://github.com/argilla-io/argilla/tree/main/k8s/argilla-server-hpa.yaml): scaler to scale the server from 1 to 3 pods.
- [argilla-server-ingress.yaml](https://github.com/argilla-io/argilla/tree/main/k8s/argilla-server-ingress.yaml): server ingress config.
- [argilla-server-service.yaml](https://github.com/argilla-io/argilla/tree/main/k8s/argilla-server-service.yaml): server service config.
- [elasticsearch-deployment.yaml](https://github.com/argilla-io/argilla/tree/main/k8s/elasticsearch-deployment.yaml): a minimal Elastic Search config.
- [elasticsearch-pvc.yaml](https://github.com/argilla-io/argilla/tree/main/k8s/elasticsearch-pvc.yaml): a persistent volume claim to dynamically scale and retain data.
- [elasticsearch-service.yaml](https://github.com/argilla-io/argilla/tree/main/k8s/elasticsearch-service.yaml): an Elastic service config.

### Helm charts

For a more robust and modern set-up, we recommend using [official Kubernetes helm charts](https://github.com/elastic/helm-charts) in combination with the Argilla server Kubernetes `yaml`. Argilla itself doesn't have any helm support but it can still be used together with Helm-deployed ElasticSearch by setting the `ARGILLA_ELASTICSEARCH` environment variable to the endpoint where ElasticSearch is hosted.

(deploy-to-aws-instance-using-docker-machine)=
## Amazon Web Services (AWS)

### Setup an AWS profile

The `aws` command cli must be installed. Then, type:

```bash
aws configure --profile argilla
```

and follow command instructions. For more details, visit [AWS official documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html).

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

Available Amazon Machine Instance (AMI) depends on region. The provided AMI is available for eu-west regions and is an ubuntu-16.04-server image.
To find available recent images, go to the [AWS AMI Marketplace](https://console.aws.amazon.com/ec2/home), choose "Launch instance" and filter by `ubuntu`
(don't forget to choose your targeted region).

If you already have multiple instances and VPC in the targeted region, creating a new VPC before creating the Argilla instance is recommended.
Add the following parameter to specify the VPC you want to use for the instance:

```bash
--amazonec2-vpc-id vpc-1234abcd  # Replace vpc-1234abcd with the created VPC id
```

### Verify machine creation

```bash
$>docker-machine ls

NAME                   ACTIVE   DRIVER      STATE     URL                        SWARM   DOCKER     ERRORS
argilla-aws             -        amazonec2   Running   tcp://52.213.178.33:2376           v20.10.7
```

### Save assigned machine ip

In our case, the assigned ip is `52.213.178.33`

### Connect to remote docker machine

To enable the connection between the local docker client and the remote daemon, we must type the following command:

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

The easiest way to deploy Argilla on Azure is using the Azure Container Instances (ACI) service. This service allows you to run containers in a serverless way, without the need to manage the underlying infrastructure. This guide will take you through deploying Argilla using the Azure CLI tool, and is based on the [Azure documentation](https://learn.microsoft.com/en-us/azure/container-instances/container-instances-quickstart) for the same service.

<!-- breakout box -->
> 🚒  At the time of writing, it is still possible to deploy Argilla using the `docker run` command and `docker context` integration with Azure, but [this method](https://learn.microsoft.com/en-us/azure/container-instances/quickstart-docker-cli) is soon to be deprecated in the [docker cli](https://docs.docker.com/cloud/).

### 1. Authenticate to Azure

First, you need to authenticate to Azure using the `az` CLI:

```bash
az login
```

### 2. Setup an Azure resource group

Create a resource group where you want to deploy the Argilla Server:

```bash
az group create --name <resource-group> --location <location>
```

### 3. Create an Azure Container Instance

Create an Azure Container Instance with the `az container create` command:

```bash
az container create --resource-group <resource-group> --name <deployment-name> --image argilla/argilla-quickstart:latest --dns-name-label <dns-name> --ports 6900
```

Once the container is deployed you can check the deployment with:

```bash
az container show --resource-group <resource-group> --name argilla --query "{FQDN:ipAddress.fqdn,ProvisioningState:provisioningState}" --out table
```

Argilla should now be accessible at the FQDN provided in the output, on the port `6900`.

## Google Cloud Platform (GCP) via Cloud Run

First, we will deploy Argilla using Cloud Run, a managed platform that scales stateless containers. To deploy Argilla on GCP, you can use Cloud Run, a managed platform that scales stateless containers. This guide will take you through deploying Argilla using the `gcloud` CLI tool, and is based on the [GCP documentation](https://cloud.google.com/run/docs/quickstarts/deploy-container).

> 🚒 **We will deploy the Argilla quickstart image for simplicity which means we have a pre-packaged storage layer, and cannot use Cloud Run's horizontal scaling features.**

### 1. Authenticate to GCP

First, you need to authenticate to GCP using the `gcloud` CLI:

```bash
gcloud auth login
```

### 2. Build and deploy the container

We will use the `gcloud run deploy` command to deploy the Argilla container directly from the Docker Hub. We can point the cloud run url to the container's default port (6900) and define relevant compute resources.

```bash
gcloud run deploy <deployment-name> \
--region <region> \
--image argilla/argilla-quickstart:latest \
--allow-unauthenticated \
--port 6900 \
--cpu 2 \
--memory 4Gi \
--max-instances 1 \
--min-instances 1
```

Now you can access Argilla at the URL provided in the output or by running:

```bash
gcloud run services describe <deployment-name> \
--region <region> \
--format 'value(status.url)'
```

## Google Cloud Platform (GCP) on a Dedicated Virtual Machine

If [deploying via Cloud Run](#google-cloud-platform-gcp-via-cloud-run) is not suitable for your use case, you can deploy Argilla on a dedicated virtual machine via Cloud Compute. Deploying Argilla Server to Cloud Compute involves creating a compute instance, setting up Docker and Docker Compose, and configuring network settings for external traffic. Follow these steps:

### 1. Create an Instance

Create a new Google Cloud VM instance with the necessary specifications:

```bash
gcloud compute instances create "argilla-instance" \
  --machine-type "n1-standard-2" \
  --image-family "debian-10" \
  --image-project "debian-cloud" \
  --boot-disk-size "50GB" \
  --zone "asia-south2-a"
```

### 2. SSH into the Instance

Once the instance is running, connect to it using SSH:

```bash
gcloud compute ssh argilla-instance --zone asia-south2-a
```

### 3. Install Dependencies

Update the package manager and install necessary dependencies:

```bash
sudo apt-get update

sudo apt-get install apt-transport-https ca-certificates curl software-properties-common gnupg2 lsb-release
```

### 4. Install Docker and Docker Compose

Install Docker Engine and Docker Compose on the instance:

```bash
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### 5. Launch Argilla with Docker Compose

Grab the `docker-compose.yaml` file from the repository and start the Argilla Server:

```bash
mkdir argilla && cd argilla

wget -O docker-compose.yaml https://raw.githubusercontent.com/argilla-io/argilla/main/docker/docker-compose.yaml

sudo docker compose up -d
```

### 6. Allow External Traffic

Configure the firewall rules to allow incoming traffic on the required ports:

```bash
gcloud compute instances add-tags argilla-instance --zone asia-south2-a --tags=argilla-instance

gcloud compute firewall-rules create allow-6900 --allow tcp:6900 --target-tags argilla-instance --description "Allow incoming traffic on port 6900"
```

### 7. Assign a Static IP Address

Reserve and assign a static IP address to ensure that the server can be consistently accessed via the same IP:

```bash
gcloud compute addresses create my-static-ip --region asia-south2
```

### 8. Configure Instance with Static IP

Bind the static IP address to the instance:

```bash
STATIC_IP=$(gcloud compute addresses list --format="value(address)" --filter="name=my-static-ip")

gcloud compute instances delete-access-config argilla-instance --zone asia-south2-a --access-config-name "external-nat"

gcloud compute instances add-access-config argilla-instance --zone asia-south2-a --address $STATIC_IP
```

### 9. Test Connection

Confirm the server is accessible by making an HTTP request to the Argilla server:

```bash
curl -vI $STATIC_IP:6900
```

Now you can access the Argilla instance in your browser using the URL `http://[STATIC_IP]:6900`.

