# Argilla Helm Chart

This Helm chart deploys Argilla Server on Kubernetes.

## Prerequisites

- Kubernetes 1.12+
- Helm 3.0+
- PV provisioner support in the underlying infrastructure (if persistence is enabled)

## Installing Helm

Before you can use this chart, you need to have Helm installed. If you haven't installed Helm yet, follow these steps:

1. Use package manager to install [Helm](https://helm.sh/docs/intro/install/#through-package-managers).

2. (Optional) If you're using Helm for the first time, you may need to initialize it:

   ```bash
   helm init
   ```

For more detailed installation instructions, please refer to the [official Helm documentation](https://helm.sh/docs/intro/install/).

## Dependencies

- Redis
- Elasticsearch

## Adding the Helm Repository

To add the Argilla Helm repository to your Helm installation, run the following command:

```bash
helm repo add stable https://charts.helm.sh/stable
helm repo add elastic https://helm.elastic.co
helm repo update
```

## Minikube
> Assumes you have Docker Desktop installed
```bash
minikube stop
minikube delete
minikube config set memory 3g
minikube config set cpus 2
minikube start
```
## Enable Minikube Addons
```bash
minikube addons enable ingress
```

The ingress controller pod should be in the `Running` state.
```bash
kubectl get pods -n ingress-nginx
```

## Installing ECK
As we want to use the operator to manage our Elasticsearch cluster, we need to install the ECK operator.
```bash
helm install elastic-operator elastic/eck-operator -n elastic-system --create-namespace
```
The elastic-operator pod should be in the `Running` state.
```bash
kubectl get pods -n elastic-system
```

## Installing the Chart

After adding the repository, you can install the chart with the release name `my-argilla-server`:

```bash
helm install my-argilla-server examples/deployments/k8s/argilla-chart
```

Check the status of the pods:

```bash
kubectl get pods -w
```
All the pods should be in the `Running` state.

## Accessing Argilla

In a different terminal window, run the following command to access Argilla:
```bash
kubectl port-forward svc/my-argilla-server 6900
```
Argilla will be accessible at http://localhost:6900.

## Execute integration tests

Set the following environment variables:
```bash
export ARGILLA_API_URL=http://localhost:6900
export ARGILLA_API_KEY=argilla.apikey
```

Run the following command to execute the integration tests:
```bash
pytest tests/integration
```

## Uninstalling the Chart

To uninstall/delete the `my-argilla-server` deployment:

```bash
helm delete my-argilla-server
```

This command removes all the Kubernetes components associated with the chart and deletes the release.

## Running Unit Tests

This chart includes unit tests using the helm-unittest plugin. To run these tests, follow these steps:

### Installing helm-unittest plugin

1. Install the helm-unittest plugin:

```bash
helm plugin install https://github.com/helm-unittest/helm-unittest.git
```

2. Verify the installation:

```bash
helm unittest --help
```

### Running the tests

To execute the unit tests for this chart, run the following command from the root of the chart directory:

```bash
helm unittest examples/deployments/k8s/argilla-chart
```

This will run all the test files located in the `tests/` directory of the chart.

For more information on writing and running helm unit tests, please refer to the [helm-unittest documentation](https://github.com/helm-unittest/helm-unittest).
