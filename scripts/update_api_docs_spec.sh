#!/usr/bin/env bash

rm -rf docs/reference/api/v1/openapi.json*

python -m rubrix &
RUBRIX_PID=$!

sleep 5 && wget http://localhost:6900/api/v1/openapi.json -P docs/reference/api/v1/

kill $RUBRIX_PID
