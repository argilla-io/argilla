#!/usr/bin/bash
set -e

# Check elasticsearch response status
status_code=$(curl -s -o /dev/null -w "%{http_code}" "$ARGILLA_ELASTICSEARCH")

if [[ "$status_code" -ne 200 ]]; then
  echo "ElasticSearch connection error. Returned status code: $status_code"
  exit 1
else
  echo "ElasticSearch connected"
fi

# Run argilla-server
uvicorn argilla:app --host "0.0.0.0" --port 6900
