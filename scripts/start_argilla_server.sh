#!/usr/bin/bash
set -e

# Check elasticsearch response status
/wait-for-it.sh -t 60 `echo "${ARGILLA_ELASTICSEARCH}" | awk -F'^http[s]?://' '{print $2}'` -- echo "ElasticSearch connected"

# Run argilla-server (See https://www.uvicorn.org/settings/#settings)
#
# From uvicorn docs:
#   You can also configure Uvicorn using environment variables
#   with the prefix UVICORN_. For example, in case you want to
#   run the app on port 5000, just set the environment variable
#   UVICORN_PORT to 5000.
uvicorn argilla:app --host "0.0.0.0"
