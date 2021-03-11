#!/usr/bin/env bash

TAG=$(git rev-parse --short HEAD)

docker build -t registry.gitlab.com/recognai-team/biome/rubrix:${TAG} .
docker push registry.gitlab.com/recognai-team/biome/rubrix:${TAG}
