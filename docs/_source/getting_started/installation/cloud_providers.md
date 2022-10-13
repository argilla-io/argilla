
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

### Create docker machine (aws)

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

## Google Cloud Platform (GCP)

Coming soon!

> 🚒 **If you'd like support with this and/or want to contribute this gude, join the [Slack Community](https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g)**

## Azure

Coming soon!

> 🚒 **If you'd like support with this and/or want to contribute this gude, join the [Slack Community](https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g)**

