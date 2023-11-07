#!/usr/bin/env bash

cd frontend &&
	npm install &&
	BASE_URL=@@baseUrl@@ DIST_FOLDER=../src/argilla/server/static npm run-script build
