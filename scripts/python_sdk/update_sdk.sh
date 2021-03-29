#!/usr/bin/env bash

BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
API_URL="${RUBRIX_API_URL:-http://localhost:6900/openapi.json}"

RESULTS="$(cd $BASEDIR \
&& rm -rf sdk \
&& openapi-python-client --config config.yaml generate \
--url $API_URL \
--meta none \
--custom-template-path $BASEDIR/templates_fix/
)"

rsync -av --delete $BASEDIR/sdk/ src/rubrix/sdk
rm -rf $BASEDIR/sdk


