#!/usr/bin/env bash

IMAGE_NAME="registry.gitlab.com/recognai-team/biome/rubrix"
COMMIT=$(git rev-parse --short HEAD)
TAG=$(git describe --exact-match ${COMMIT})
BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

DISTRIBUTION="$( $BASEDIR/build_distribution.sh )"

BUILD_TAGS="-t ${IMAGE_NAME}:${COMMIT} -t ${IMAGE_NAME}:latest "
if [ ! -z "${TAG}" ]
then
  BUILD_TAGS="${BUILD_TAGS} -t ${IMAGE_NAME}:${TAG}"
fi

docker build ${BUILD_TAGS}  .
docker push ${IMAGE_NAME} --all-tags
