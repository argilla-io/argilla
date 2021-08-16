#!/usr/bin/env bash

cd frontend \
&& npm install \
&& npm run-script lint \
&& DIST_FOLDER=../src/rubrix/server/static npm run-script build \

