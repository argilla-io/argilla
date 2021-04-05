#!/usr/bin/env bash

TAG=$(git rev-parse --short HEAD)

DIST_BUILD=$(cd frontend && npm install && ENABLE_SECURITY=1 DIST_FOLDER=../src/rubrix/server/static/secured npm run-script build)
DIST_BUILD=$(cd frontend && npm install && ENABLE_SECURITY=0 DIST_FOLDER=../src/rubrix/server/static/unsecured npm run-script build)
