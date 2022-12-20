#!/usr/bin/bash
set -e

# Check elasticsearch response status
/wait-for-it.sh -t 60 -s `echo "${ARGILLA_ELASTICSEARCH}" | awk -F'^http[s]?://' '{print $2}'` -- echo "ElasticSearch connected"

# Run argilla-server
uvicorn argilla:app --host "0.0.0.0"
