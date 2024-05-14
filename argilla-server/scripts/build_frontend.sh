#!/usr/bin/env bash

cd argilla/frontend \
&& npm install \
&& npm run-script lint \
&& npm run-script test \
&& BASE_URL=@@baseUrl@@ DIST_FOLDER=../../src/argilla_server/static npm run-script build \
