#!/usr/bin/env bash

cd frontend \
&& npm install \
&& DIST_FOLDER=../src/rubrix/server/static npm run-script build
