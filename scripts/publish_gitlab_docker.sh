#!/usr/bin/env bash

TAG=$(git rev-parse --short HEAD)

BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

DISTRIBUTION="$( $BASEDIR/build_distribution.sh )"

docker build -t registry.gitlab.com/recognai-team/biome/rubrix:${TAG} .
docker push registry.gitlab.com/recognai-team/biome/rubrix:${TAG}
