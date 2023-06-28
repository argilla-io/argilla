#!/usr/bin/env bash

cd frontend \
&& yarn install \
&& yarn lint \
&& yarn test \
&& BASE_URL=@@baseUrl@@ DIST_FOLDER=../src/argilla/server/static yarn build \

