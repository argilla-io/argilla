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

## Installing the Chart

After adding the repository, you can install the chart with the release name `my-release`:

```bash
helm install my-release examples/deployments/k8s/argilla-chart
```

## Configuration

To override default values, override the values in `values.yaml` file and install the chart using:

```bash
helm install my-release examples/deployments/k8s/argilla-chart
```

## Upgrading

To upgrade the chart to a newer version:

```bash
helm repo update
helm upgrade my-release argilla/argilla
```

TODO: Add information about any backwards incompatible changes and how to handle them.

## Uninstalling the Chart

To uninstall/delete the `my-release` deployment:

```bash
helm delete my-release
```

This command removes all the Kubernetes components associated with the chart and deletes the release.
