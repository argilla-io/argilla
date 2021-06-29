#!/usr/bin/env bash

BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
API_URL="${RUBRIX_API_URL:-http://localhost:6900}"

RESULTS="$(cd $BASEDIR \
&& rm -rf sdk \
&& openapi-python-client --config config.yaml generate \
--url $API_URL/api/docs/spec.json \
--meta none \
--custom-template-path $BASEDIR/templates_fix/
)"

rsync -av --delete --exclude "**/_*.py" --exclude "**/stream_data.py" --exclude "**/client.py" $BASEDIR/sdk/ src/rubrix/sdk
rm -rf $BASEDIR/sdk
