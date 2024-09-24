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

After adding the repository, you can install the chart with the release name `my-argilla-server`:

```bash
helm install my-argilla-server examples/deployments/k8s/argilla-chart

TODO: Add information about any backwards incompatible changes and how to handle them.

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
