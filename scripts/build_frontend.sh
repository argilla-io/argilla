#!/usr/bin/env bash

TAG=$(git rev-parse --short HEAD)

DIST_BUILD=$(cd frontend && npm install && npm run-script build)


